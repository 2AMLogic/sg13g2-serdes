# Digital partition ERC supply record, 2026-11-23 (source commit 51dde9f)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/erc-regen.sh`). T1 item 11, Digital column (`11.digital`). Structural
check only: no number here is a measurement. Supersedes
`../2026-11-20-9f98e1e/` for freshness (that record was run on the
2026-11-14 GDS; PR #215's slow-corner P&R record
`layout/digital/records/2026-11-21-eec180f/` is the newest routed GDS).

| Item | Value |
|---|---|
| Layout | `layout/digital/records/2026-11-21-eec180f/serdes_digital_top.gds`, sha256 `2d781d74…` |
| Spec | `erc.spec.json`, unchanged copy of `layout/erc/digital.erc.json` |
| Run | `scripts/erc-regen.sh` (`klt erc <gds> erc.spec.json --top serdes_digital_top --deck sg13g2 --findings-only --omit-antenna-tables`), `klayout-tools==0.9.0` |
| `erc_status` | `clean`, 0 `erc_findings` |
| Supplies | `VDD` 1 island, `VSS` 1 island |
| Ties | both declared ties checked, none skipped |

The spec-coverage disclosure, tapless explanation and negative controls of the
2026-11-20 record apply unchanged to this run's spec and rule set; they were not
re-run on the new GDS. `klt erc` exited 4 on this run (the tool's
coverage-disclosure code, with `erc_status: clean`).
