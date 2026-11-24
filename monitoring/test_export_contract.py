"""Export contract test: the portfolio's fields must survive every export change (#88).

Rebuilds the export from the committed data in a throwaway folder (generate_export.py is
copied there, so the real exports/ folder is never touched) and checks it against
monitoring/export-contract.json. Fails if a field the portfolio reads disappears or changes type.

Run: python -m unittest monitoring/test_export_contract.py   (also run in CI)
"""
import copy
import glob
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
THEMES = ["AI", "Crypto", "Defence"]   # folders with files (#88 retired Biotech, Energy, Mega-Cap, Tech)

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
    runs = payload.get("signal_runs")
    if not isinstance(runs, dict) or not runs:
        errors.append("signal_runs: missing")
    else:
        errors += check_rows(list(runs.values()), CONTRACT["signal_runs (object, one entry per live run)"], "signal_runs")
    return errors


def build_export(workdir):
    """Run generate_export.py on a copy of the committed inputs; return (payload, manifest)."""
    shutil.copy(os.path.join(ROOT, "generate_export.py"), workdir)
    for theme in THEMES:
        os.makedirs(os.path.join(workdir, theme))
        for name in ("prices-data.js", "signals-local.json"):
            shutil.copy(os.path.join(ROOT, theme, name), os.path.join(workdir, theme))
    # #88: the market and sector groups' price and signal files
    for path in glob.glob(os.path.join(ROOT, "markets", "*", "*")) + glob.glob(os.path.join(ROOT, "sectors", "*", "*")):
        if os.path.basename(path) in ("prices-data.js", "signals-local.json"):
            rel = os.path.relpath(path, ROOT)
            os.makedirs(os.path.join(workdir, os.path.dirname(rel)), exist_ok=True)
            shutil.copy(path, os.path.join(workdir, rel))
    shutil.copy(os.path.join(ROOT, "asset-links.js"), workdir)
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

    # #88: one row per stock; every live run's picks land on a row; derived market pages not counted
    def test_one_row_per_stock(self):
        tickers = [s["ticker"] for s in self.payload["stocks"]]
        self.assertEqual(len(tickers), len(set(tickers)))
        self.assertGreater(len(tickers), 600)

    def test_every_pick_lands_once(self):
        offered = sum(r["picks"] for r in self.payload["signal_runs"].values())
        attached = sum(len(s["picked_by"]) for s in self.payload["stocks"])
        self.assertEqual(attached, offered)
        self.assertNotIn("S&P 500", self.payload["signal_runs"])
        for s in self.payload["stocks"]:
            if s["picked_by"]:
                self.assertEqual(s["signal_run"], s["picked_by"][0]["run"])
                self.assertEqual(s["signal_confidence"], s["picked_by"][0]["confidence"])
            else:
                self.assertIsNone(s["signal"])

    def test_isin_valid_where_present(self):
        sys.path.insert(0, ROOT)
        from universe import isin_ok
        isins = [s["isin"] for s in self.payload["stocks"] if s["isin"] is not None]
        self.assertTrue(all(isin_ok(i) for i in isins))
        self.assertTrue(all(s["isin"] is None for s in self.payload["stocks"] if s["sector"] == "Crypto"))

    def test_sector_is_official(self):
        allowed = {"Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials",
                   "Health Care", "Industrials", "Materials", "Real Estate", "Technology", "Utilities", "Crypto",
                   "Unclassified"}
        self.assertLessEqual({s["sector"] for s in self.payload["stocks"]}, allowed)

    def test_macro_keys_any_case(self):
        upper = copy.deepcopy(self.payload)
        upper["macro"] = {k.upper(): v for k, v in upper["macro"].items()}
        self.assertEqual(check_export(upper, self.manifest), [])


if __name__ == "__main__":
    unittest.main()
