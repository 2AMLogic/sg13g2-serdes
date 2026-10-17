# DR-002: Error-rate methodology and labelling

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-10-17
- **Decided by**: Builder agent, issue #2
- **Fixes rows**: target-spec R15

## Context

A 1e-12 BER cannot be observed in a transistor-level transient (about
1e12 bits, 100 s of simulated time at 10 Gb/s). `CLAUDE.md` requires the
chain: transistor-level PVT results per stage → behavioural models fitted to
them → statistical link simulation over the declared channel → extrapolated
bathtub, with every model citing the record it was fitted to.

## Options considered

- **Long time-domain transient of the whole link.** Intractable in ngspice
  (and the open question of ngspice at 5 GHz HBT CML is still open, #3).
- **Peak-distortion / worst-case ISI only.** Pessimistic and ignores random
  jitter and noise; cannot produce a BER.
- **Statistical eye (pulse-response convolution of ISI, Gaussian noise and
  dual-Dirac jitter) plus a time-domain behavioural bang-bang CDR run.** Chosen.

## Decision

1. **Pattern**: PRBS-31 target; PRBS-7 fallback (also the on-chip default
   during bring-up). Pulse response from the channel in
   [`spec/channel/`](../channel/README.md) with the TX FFE and RX CTLE models.
2. **Method**: (a) per stage, transistor-level ngspice runs at the corner
   sets in target-spec.md produce jitter, gain, bandwidth, offset and noise
   records; (b) a behavioural model of each stage is fitted to those records
   and cites the record id; (c) a statistical-eye simulator computes the
   bathtub over the channel; (d) the CDR loop is run as a time-domain
   behavioural bang-bang model to get its recovered-clock jitter and the
   jitter-tolerance curve, and that jitter feeds (c).
3. **Fit validation**: a model is fitted on a subset of corners and
   stimuli and **validated on held-out ones**; the validation error is
   recorded with the model. Proposed acceptance: eye height within 10 % and
   eye width within 0.05 UI of the transistor-level result on every held-out
   point. A model outside this is not used for a claim.
4. **Extrapolation**: the bathtub is computed directly down to the lowest BER
   the statistics support (about 1e-9 from the time-domain CDR run) and
   extended to 1e-12 by a Gaussian-tail (dual-Dirac) fit of the bathtub
   walls; the fit residual and the tail-fit range are recorded with the
   number.
5. **Labels**: every BER, eye or bathtub figure carries exactly one of
   `simulated (transistor-level)`, `simulated (behavioural, fitted to
   <record id>)` or `extrapolated (<method>, <fit range>)`. **No figure is
   called `measured` until silicon exists** and is read from a measurements
   record. A figure without its label, or without the record chain, is not
   evidence.

## Consequences

- The behavioural-model fit and its validation are the weak link; the CDR
  needs its own transistor-level latch records (metastability window, aperture
  jitter) before the model is credible. This answers open question 2 as a
  *procedure*; whether the fit passes is unknown until the records exist.
- Results are append-only records under `sim/`; supersede, do not edit.
