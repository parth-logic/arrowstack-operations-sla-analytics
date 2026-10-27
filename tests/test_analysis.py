import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analyze_sla import analyze, validate_data

class TestSLAAnalysis(unittest.TestCase):
    def sample(self):
        return pd.DataFrame([
            {"ticket_id":"A","created_at":"2025-01-01","resolved_at":"2025-01-02","priority":"High","channel":"Email","team":"Billing","category":"Payment","status":"Resolved","sla_hours":24,"resolution_hours":25},
            {"ticket_id":"B","created_at":"2025-01-02","resolved_at":"2025-01-02","priority":"Low","channel":"Chat","team":"General","category":"How-to","status":"Resolved","sla_hours":72,"resolution_hours":12},
            {"ticket_id":"C","created_at":"2025-01-03","resolved_at":"","priority":"Medium","channel":"Web","team":"Technical Support","category":"Bug","status":"Open","sla_hours":48,"resolution_hours":float("nan")},
        ])

    def test_breach_definition_and_open_exclusion(self):
        valid, resolved, kpis, *_ = analyze(self.sample())
        self.assertEqual(len(valid), 3)
        self.assertEqual(len(resolved), 2)
        self.assertEqual(int(resolved["sla_breached"].sum()), 1)
        self.assertAlmostEqual(float(kpis.loc[kpis.kpi.eq("SLA breach rate (%)"),"value"].iloc[0]), 50.0)

    def test_duplicate_ids_detected(self):
        df=self.sample()
        df.loc[1,"ticket_id"]="A"
        qa=validate_data(df)
        self.assertFalse(bool(qa.loc[qa.check.eq("ticket IDs unique"),"passed"].iloc[0]))

if __name__ == "__main__":
    unittest.main()
