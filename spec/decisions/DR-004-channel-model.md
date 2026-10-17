# DR-004: Channel model

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-10-17
- **Decided by**: Builder agent, issue #2
- **Fixes rows**: target-spec R14

## Context

The link must close over a stated loss at Nyquist, as a model the simulations
use. No measured board or cable data is available to the repo.

## Options considered

- **Third-party S-parameters** (a standard's reference channel): would be
  traceable, but nothing is committed or pinned and fetching an arbitrary file
  would not be reproducible.
- **Analytic skin-effect + dielectric loss with pure delay** (chosen): small,
  reviewable, reproducible, generates a Touchstone file on demand.

## Decision

[`spec/channel/channel_model.py`](../channel/channel_model.py) defines CH-A
(10.18 dB at 5 GHz) as the 10 Gb/s target channel, CH-B (5.09 dB at 5 GHz) as
the fallback; CH-A at 5 Gb/s is 5.65 dB at 2.5 GHz and at 12.5 Gb/s 12.38 dB at
6.25 GHz. The coefficients are a proposal, not a measurement.

## Consequences

- No reflections or crosstalk: closing over this channel does not show closure
  over a real one. A variant with a stub/connector reflection and a causal
  response is a follow-up, and a result over it supersedes none of the
  CH-A/CH-B results.
- The 10 dB figure is a judgement for an equalizer of 2-tap FFE + CTLE; the
  operator may change it by superseding record.
