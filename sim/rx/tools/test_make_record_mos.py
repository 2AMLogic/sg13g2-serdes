"""Render the saved RX grid and exercise missing measurements in a scratch record."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parent
RECORD = TOOLS.parent / "records" / "20261123-025944-cd608e7-mos"
REPORT = "lvl_cml2cmos.report.json"


def render(report, directory):
    (directory / REPORT).write_text(json.dumps(report))
    subprocess.run([sys.executable, "-I", str(TOOLS / "make_record_mos.py"), str(directory)],
                   check=True, stdout=subprocess.DEVNULL)
    return (directory / "record.md").read_text()


class RecordTest(unittest.TestCase):
    def test_partial_grid(self):
        report = json.loads((RECORD / REPORT).read_text())
        corners = {c["corner_id"]: c for c in report["corners"]}
        with tempfile.TemporaryDirectory(dir=RECORD.parent) as scratch:
            directory = Path(scratch)
            shutil.copy(RECORD / "exit-codes.txt", directory)
            original = render(report, directory)
            self.assertIn("2 of 45 graded corners", original)
            self.assertIn("over the 27 corners", original)
            self.assertIn("over the 31 corners", original)

            corners["tt_typ/1.200V/27C"].update(
                status="error", measurements=[],
                diagnostics=[{"code": "simulation_error", "message": "solver stopped"}])
            report.update(passed=0, failed=42, errored=1, inconclusive=2)
            for cid, missing in [
                ("ff_bcs/1.320V/-40C", {"lvl_out_lo_v", "lvl_tck_hl10_s"}),
                ("ff_bcs/1.320V/27C", {"lvl_out_hi_v", "lvl_tck_lh90_s"}),
            ]:
                c = corners[cid]
                c["status"] = "inconclusive"
                c["measurements"] = [m for m in c["measurements"] if m["name"] not in missing]
            partial = render(report, directory)

        self.assertIn("simulation_error solver stopped", partial)
        self.assertIn("0 of 42 graded corners", partial)
        self.assertIn("over the 25 corners", partial)
        self.assertIn("over the 28 corners", partial)
        for cid in ("ff_bcs/1.320V/-40C", "ff_bcs/1.320V/27C"):
            row = next(line for line in partial.splitlines() if line.startswith(f"| {cid} |"))
            self.assertIn("timing unavailable", row)
            self.assertNotIn("edge stops", row)
        for cid, c in corners.items():
            prefix = f"| {cid} |"
            row = next(line for line in partial.splitlines() if line.startswith(prefix))
            if c["status"] == "error":
                self.assertIn("error", row)
            elif c["status"] in ("pass", "fail"):
                self.assertIn(row, original)


if __name__ == "__main__":
    unittest.main()
