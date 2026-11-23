* R18 pad-capacitance bench (issue #94): ESD clamp diodes only, AC at 0.1 and 5 GHz.
* WHAT THIS MEASURES: the capacitance the PDK ESD diode models (diodevdd_2kv /
* diodevss_2kv, one pair per pad leg, as in design/tx/netlists/pad_esd.spice)
* present at the pad, per PVT corner. It is the ESD share of the R18 budget.
* WHAT IT DOES NOT MEASURE: bondpad + pad-metal capacitance. The PDK bondpad
* model is empty, and the current pad GDS (layout/analog/pads/records/2026-11-11-835e58e)
* extracts to ~0.78 fF on padp (metal0 only; bondpad and diodes unrecognised), so no
* extracted total exists. See spec/decisions/DR-011-pad-model-source.md.
* The 4.57 ohm series rsil is omitted (r3_cmc OSDI model, not simulated here, sim/README.md);
* cp is left open, so the pad sees the clamp diodes alone.
Vdd vdd 0 1.2
Vp padp 0 dc 0.6 ac 1
XDh vdd padp 0 diodevdd_2kv m=1
XDl vdd padp 0 diodevss_2kv m=1
* ESD share per clamp, to show the budget split
Vph padh 0 dc 0.6 ac 1
XDh2 vdd padh 0 diodevdd_2kv m=1
Vpl padl 0 dc 0.6 ac 1
XDl2 vdd padl 0 diodevss_2kv m=1
* Current probes (H sources, value = branch current in A for 1 V ac). Imag part of the
* branch current at f gives C = Im(I) / (2 pi f); the record converts it (a B-source
* conversion errors on ngspice's ac imag(); measurements[].expr is unreliable, klayout-tools#4217).
Hip iz 0 Vp 1
Hih izh 0 Vph 1
Hil izl 0 Vpl 1
