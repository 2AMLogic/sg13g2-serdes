#!/usr/bin/env bash
# Run klt extract (+parasitics) and klt drc on a pad record, with and without the bondpad.
#   source scripts/env.sh; layout/analog/pads/verify.sh layout/analog/pads/records/<date>-<sha>
# Writes extract-*.json / drc-*.json into the record (append-only: refuses to overwrite).
set -euo pipefail
rec="${1:?usage: verify.sh <record-dir>}"
[ -e "$rec/extract-pad_esd.json" ] && { echo "verify.sh: $rec already verified (append-only)" >&2; exit 2; }
# Variant with the two bondpad instances (TopMetal2 + Passiv + pad opening) removed, so the
# budget split between pad metal and the rest of the pad net stays visible.
python3 -I - "$rec/pad_esd.gds" "$rec/pad_esd_nobondpad.gds" <<'PY'
import sys, klayout.db as db
ly = db.Layout(); ly.read(sys.argv[1])
top = ly.cell("pad_esd")
for i in list(top.each_inst()):
    if i.cell.name.endswith("__bondpad"):
        i.delete()
ly.write(sys.argv[2])
PY
ext() { # <gds> <top> <out>
  klt extract --deck sg13g2 --parasitics --top "$2" "$1" --format json > "$3" 2>/dev/null
}
ext "$rec/pad_esd.gds" pad_esd "$rec/extract-pad_esd.json"
ext "$rec/pad_esd_nobondpad.gds" pad_esd "$rec/extract-pad_esd_nobondpad.json"
ext "$rec/rx_term_pad.gds" rx_term_pad "$rec/extract-rx_term_pad.json"
klt drc --deck sg13g2 --top pad_esd "$rec/pad_esd.gds" --format json > "$rec/drc-pad_esd.json" 2>/dev/null
klt drc --deck sg13g2 --top rx_term_pad "$rec/rx_term_pad.gds" --format json > "$rec/drc-rx_term_pad.json" 2>/dev/null
rm -f "$rec"/*.spice
