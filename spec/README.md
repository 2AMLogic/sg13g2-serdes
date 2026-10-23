# spec

Target specification for `sg13g2-serdes`. **Status: PROPOSED — not ratified.**
Ratification is the operator's act on merge (issue #2); until then nothing
here binds design work, and agents do not relax a ratified row to make
results pass (`CLAUDE.md`).

| File | Content |
|---|---|
| [`target-spec.md`](target-spec.md) | Every parameter: target / fallback / stretch, verification, PVT corners, basis; pads and ESD; open-question dispositions |
| [`clock-requirement.md`](clock-requirement.md) | The clock this block needs, compared with `sg13g2-vco`, `sg13g2-pll` and `sg13g2-lc-pll` at pinned commits |
| [`channel/`](channel/README.md) | The channel model (`channel_model.py`) and its loss at Nyquist |
| [`decisions/`](decisions/) | Decision records, append-only: DR-001 architecture, DR-002 error-rate methodology, DR-003 supplies and HBT breakdown, DR-004 channel model |

Spec changes go through a new decision record; a ratified record is
superseded, never edited.
