"""Export contract test: the portfolio's fields must survive every export change (#88).

Rebuilds the export from the committed data in a throwaway folder (generate_export.py is
copied there, so the real exports/ folder is never touched) and checks it against
monitoring/export-contract.json. Fails if a field the portfolio reads disappears or changes type.

Run: python -m unittest monitoring/test_export_contract.py   (also run in CI)
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


CONTRACT = read_json(os.path.join(ROOT, "monitoring", "export-contract.json"))
SECTORS = ["AI", "Biotech", "Crypto", "Defence", "Energy", "MegaCap", "Tech"]

TYPES = {
    "str": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "bool": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
    "object": lambda v: isinstance(v, dict),
    "list": lambda v: isinstance(v, list),
}


def check_rows(rows, fields, where):
    """Every row must carry every field, with one of the allowed types."""
    errors = []
    if not isinstance(rows, list) or not rows:
        return [f"{where}: missing or empty"]
    for i, row in enumerate(rows):
        for field, allowed in fields.items():
            label = row.get("ticker", i) if isinstance(row, dict) else i
            if not isinstance(row, dict) or field not in row:
                errors.append(f"{where}[{label}]: missing {field}")
            elif not any(TYPES[t](row[field]) for t in allowed):
                errors.append(f"{where}[{label}].{field}: {type(row[field]).__name__}, want {'|'.join(allowed)}")
    return errors


def check_macro(macro, spec):
    if not isinstance(macro, dict):
        return ["macro: missing"]
    lower = {k.lower(): v for k, v in macro.items()}
    errors = []
    for key, fields in spec.items():
        block = lower.get(key)
        if not isinstance(block, dict):
            errors.append(f"macro.{key}: missing")
            continue
        errors += check_rows([block], fields, f"macro.{key}")
    return errors


def check_export(payload, manifest):
    """All contract problems in one export payload + manifest (empty list = OK)."""
    errors = check_rows(manifest.get("snapshots"), CONTRACT["manifest"]["snapshots[]"], "manifest.snapshots")
    errors += check_rows(payload.get("stocks"), CONTRACT["stocks[]"], "stocks")
    # momentum_picks may be legitimately empty on a quiet day; only its shape is checked
    picks = payload.get("momentum_picks")
    if not isinstance(picks, list):
        errors.append("momentum_picks: missing")
    elif picks:
        errors += check_rows(picks, CONTRACT["momentum_picks[]"], "momentum_picks")
    errors += check_macro(payload.get("macro"), CONTRACT["macro (keys in any case)"])
    return errors


def build_export(workdir):
    """Run generate_export.py on a copy of the committed inputs; return (payload, manifest)."""
    shutil.copy(os.path.join(ROOT, "generate_export.py"), workdir)
    for sector in SECTORS:
        os.makedirs(os.path.join(workdir, sector))
        for name in ("prices-data.js", "signals-local.json"):
            shutil.copy(os.path.join(ROOT, sector, name), os.path.join(workdir, sector))
    shutil.copy(os.path.join(ROOT, "market.json"), workdir)
    os.makedirs(os.path.join(workdir, "exports"))
    shutil.copy(os.path.join(ROOT, "exports", "manifest.json"), os.path.join(workdir, "exports"))
    env = {k: v for k, v in os.environ.items() if k != "T212_API_KEY"}   # never the portfolio branch
    subprocess.run([sys.executable, "-I", "generate_export.py"], cwd=workdir, env=env,
                   check=True, capture_output=True, text=True)
    manifest = read_json(os.path.join(workdir, "exports", "manifest.json"))
    newest = manifest["snapshots"][0]["json"]
    payload = read_json(os.path.join(workdir, "exports", newest))
    return payload, manifest


class ExportContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.payload, cls.manifest = build_export(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_export_meets_contract(self):
        errors = check_export(self.payload, self.manifest)
        self.assertEqual(errors[:20], [], f"{len(errors)} contract problem(s)")

    def test_manifest_newest_first(self):
        dates = [s["date"] for s in self.manifest["snapshots"]]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "exports", self.manifest["snapshots"][0]["json"])))

    def test_no_portfolio_data(self):
        self.assertFalse(self.payload["has_portfolio"])
        self.assertNotIn("portfolio", self.payload)

    # The checker itself must catch the breakages it exists for.
    def test_catches_removed_field(self):
        broken = copy.deepcopy(self.payload)
        del broken["stocks"][0]["signal"]
        self.assertTrue(any("missing signal" in e for e in check_export(broken, self.manifest)))

    def test_catches_changed_type(self):
        broken = copy.deepcopy(self.payload)
        broken["stocks"][0]["pct_1d"] = "1.2%"
        self.assertTrue(any(".pct_1d: str" in e for e in check_export(broken, self.manifest)))

    def test_catches_missing_macro(self):
        broken = copy.deepcopy(self.payload)
        del broken["macro"]["vix"]
        self.assertIn("macro.vix: missing", check_export(broken, self.manifest))

    def test_macro_keys_any_case(self):
        upper = copy.deepcopy(self.payload)
        upper["macro"] = {k.upper(): v for k, v in upper["macro"].items()}
        self.assertEqual(check_export(upper, self.manifest), [])


if __name__ == "__main__":
    unittest.main()
