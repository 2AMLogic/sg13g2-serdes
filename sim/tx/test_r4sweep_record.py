"""Exercise partial batch recovery using the recorded WCS stage-3 report shapes."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TX = Path(__file__).resolve().parent
STAGE3 = TX / "records/20261126-094722-5c4eac5-r4sweep-wcs-stage3"


class RecordTest(unittest.TestCase):
    def test_partial_batch(self):
        with tempfile.TemporaryDirectory(dir=TX / "records") as tmp:
            out = Path(tmp)
            shutil.copy(STAGE3 / "exit-codes.txt", out)
            batch = out / "batch"
            shutil.copytree(STAGE3 / "batch", batch)
            shutil.rmtree(batch / "r4sweep_c_p80_r400_wcs")

            path = batch / "r4sweep_c_p80_r600_wcs/report.json"
            report = json.loads(path.read_text())
            error = next(c for c in report["corners"] if c["status"] == "error")
            report["corners"] = [dict(error, corner_id=c["corner_id"]) for c in report["corners"]]
            path.write_text(json.dumps(report))

            path = batch / "r4sweep_c_p80_r300_wcs/report.json"
            report = json.loads(path.read_text())
            cold = report["corners"][0]
            cold["measurements"] = [m for m in cold["measurements"] if m["name"] != "r7_rise_20_80_s"]
            report["corners"].pop(1)
            path.write_text(json.dumps(report))

            result = subprocess.run([sys.executable, "-I", TX / "make_record_r4sweep.py", out, "wcs"])
            self.assertEqual(result.returncode, 2)
            md = (out / "record.md").read_text()
            for expected in ("| c_p80_r600 | 0/0/9/0 | n/a | n/a | n/a | n/a |",
                             "| c_p80_r400 | 0/0/0/9 (missing report) |",
                             "c_p80_r300 wcs/1.080V/-40C: missing measurements: r7_rise_20_80_s",
                             "c_p80_r300 wcs/1.080V/27C: missing corner",
                             "| n/a/", "| ctl | +0 | 1.00 | 208.3 |", "timestep_too_small"):
                with self.subTest(expected=expected):
                    self.assertIn(expected, md)


if __name__ == "__main__":
    unittest.main()
