# Channel model

**Status: PROPOSED** (part of the spec proposal for issue #2; ratification is the operator's act on merge).

The link must close over a channel given as a model the simulations use, not
prose. The model is analytic and committed: [`channel_model.py`](channel_model.py)
(standard library only; it prints the table below and writes a Touchstone
`.s2p` on demand, so no generated file is stored).

```
IL(f) = k_skin * sqrt(f_GHz) + k_diel * f_GHz     [dB]
S21   = 10^(-IL/20) * exp(-j*2*pi*f*1.0 ns)       (pure 1.0 ns delay)
S11 = S22 = 0                                      (ideal, matched to 100 ohm differential)
```

| Channel | k_skin (dB/√GHz) | k_diel (dB/GHz) | Role |
|---|---|---|---|
| CH-A | 1.2 | 1.5 | the 10 Gb/s target channel |
| CH-B | 0.6 | 0.75 | the "short channel" fallback |

Loss at Nyquist (output of `python3 -I channel_model.py table`):

| Channel | 5 Gb/s (Nyquist 2.5 GHz) | 10 Gb/s (Nyquist 5.0 GHz) | 12.5 Gb/s (Nyquist 6.25 GHz) |
|---|---|---|---|
| CH-A | 5.65 dB | 10.18 dB | 12.38 dB |
| CH-B | 2.82 dB | 5.09 dB | 6.19 dB |

## Basis and limits

- The coefficients are a **proposal**: a loss-versus-frequency curve of the
  skin-effect-plus-dielectric form typical of a PCB trace, chosen so CH-A
  loses about 10 dB at 5 GHz. They are not fitted to a named board, cable or
  standard, and no S-parameter measurement backs them. See
  [DR-004](../decisions/DR-004-channel-model.md).
- The model has **no reflections and no crosstalk** (S11 = S22 = 0) and a
  pure-delay phase rather than a causal minimum-phase response. A link that
  closes over it is not shown to close over a real channel with connector
  discontinuities. DR-004 records this and the follow-up variant.
- Any result that uses a different channel must say so and cite it; a result
  over this model names the channel (`CH-A` / `CH-B`) and the script's commit.
