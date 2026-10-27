# rtl

CMOS digital partition of the single-lane SerDes: everything at or below the
625 MHz word clock (DR-001 decision 3). T1 item 1 (design sources, *Digital*),
issue #23. The spec is still PROPOSED (#2); rows R11, R13, R15 and R22 are read
as the draft. **Nothing here is a measurement**, and nothing here is a PLL or VCO.

## Modules

| File | Function |
|---|---|
| `serdes_prbs_gen.v` | PRBS-7 / PRBS-31 generator, 16 bits per clock |
| `serdes_prbs_chk.v` | self-synchronising PRBS-7 / PRBS-31 checker, lock, error and bit counters |
| `serdes_cdr_pd.v` | word-level Alexander (bang-bang) phase-detector reduction |
| `serdes_cdr_filter.v` | CDR digital loop filter (proportional + integral, fixed point) |
| `serdes_loopback.v` | TX source mux, registered TX word, parallel-loopback mux |
| `serdes_eye_mon.v` | eye-monitor dwell controller (host steps phase / sampler offset) |
| `serdes_ctrl.v` | SPI control/readout interface and register file |
| `serdes_digital_top.v` | the partition; boundary ports to the analog partition |

Conventions that cross the analog boundary (also in the module headers):

- A word is 16 bits at 625 MHz; **bit 0 is the first bit on the line**, both directions.
- PRBS polynomials (the spec does not name them): PRBS-7 `x^7+x^6+1`, PRBS-31 `x^31+x^28+1`,
  seed all-ones. Registers and reset values: header of `serdes_ctrl.v`.
- `edge[k]` is the edge sample between `data[k-1]` and `data[k]`. `corr > 0` asks the loop to
  delay the sampling clock (raise the PI code). The PI code is 7 bits, 128 codes per 5 GHz
  clock period (2 UI).
- Pins (R22, at most 8): `clk, rst_n, spi_cs_n, spi_sclk, spi_mosi, spi_miso, spi_miso_oe, status_o`.
  `test_top.pin_budget` parses the port list and enforces it.
- Scope: the CML last two serialiser stages, the 5 GHz clock path and the samplers are
  analog (#21, #22). The only serialiser state here is the 16-bit TX word register; the
  bit-0-first serialiser and the deserialiser are **bench models** in `tests/test_top.py`
  that check word ordering at every misalignment.

## Verification

```
rtl/tests/run.sh            # all benches, one at a time (about 15 s)
rtl/tests/run.sh prbs_chk   # one bench
```

cocotb is provisioned per run in a throwaway `uvx` environment at the version pinned in
`layout/tools.json`; Icarus and Yosys come from the worker and their versions are checked
against the same file. Each module is compared **bit-exact against `tests/serdes_ref.py`**
(plain Python, no dependencies): PRBS sequences, checker lock and counts, phase-detector
votes, loop-filter fixed-point arithmetic. Beyond the reference:

- PRBS-7 period 127 and balance; lock from arbitrary seed and bit alignment; each injected
  line error counted exactly once; stuck-at-0 never locks; loss of lock and re-lock;
  counter saturation.
- Loop filter saturation, hold, clear; a +-300 ppm (R13) run of 62 500 words (1e6 UI) around a
  bench plant with no slip, at the filter input and again through PD + filter in the top.
  **This checks the filter arithmetic and tracking only. It is not the behavioural CDR model
  of DR-002 and is not link evidence.**
- SPI: reset values, round trips, field masking, write-1 pulses, snapshot, aborted frames.
- `top_gl` runs the top bench against the committed gate-level netlist (functional
  `sg13g2_stdcell` models from the repo-local PDK fetch, `scripts/setup-env.sh`). It passes
  with the same closed-loop numbers as the RTL.

## Synthesis (`synth/`)

`synth/request.json` is the `klt synthesize` request (`sg13g2_stdcell`, `typ_1p20V_25C`, 1.6 ns
target = 625 MHz). Committed beside it: the gate-level netlist `serdes_digital_top_synth.v` and
the envelope `serdes_digital_top.synth.json`.

```
scripts/synth-regen.sh         # after ANY edit under rtl/*.v or to the request; then commit rtl/synth/
scripts/check-synth-fresh.sh   # exit 0 fresh, 3 stale (klt synthesize --check); also checks the netlist hash
```

Both run the klt pinned in `layout/toolchain.json` through `uvx`, never the host install.
The check hashes the RTL files byte for byte, so even a comment edit needs a regenerate.

Last regeneration (pinned klt `267ea83`, Yosys 0.67): 3674 cells, 51 291 um2 (21 800 um2
sequential), no latches, loops or multiple drivers. **Timing is not demonstrated.** ABC's own
estimate (no wires, no placement) puts the longest path near 3.0 ns against the 1.6 ns target;
the pinned install has no gate-level STA (`sta` is null), so 625 MHz is an open item, not a
result. The per-module estimates when synthesised alone were: checker 3.1 ns, phase detector
2.6 ns, eye monitor 2.1 ns, loop filter 1.7 ns, PRBS generator 1.2 ns, control 1.3 ns.
