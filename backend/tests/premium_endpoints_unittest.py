import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient

from main import app
from tools.report_store import get_all_reports


class PremiumEndpointsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def _get_any_report_id(self):
        reports = list(get_all_reports() or [])
        if not reports:
            self.skipTest("No reports available in backend/data/reports.json")
        rid = reports[0].get("report_id")
        if not rid:
            self.skipTest("Invalid report format")
        return rid

    def test_format_report_fallback_works(self):
        # Ensure we don't rely on external DashScope for the test.
        if "DASHSCOPE_API_KEY" in os.environ:
            os.environ.pop("DASHSCOPE_API_KEY")

        payload = {
            "data": {
                "main_problem": "conversion optimization",
                "key_insight": "Users drop at checkout",
                "strategy": {"points": ["Improve checkout UX", "Add trust signals"]},
                "action_plan": [{"step": 1, "title": "Fix checkout", "timeline": "3 days"}],
                "campaign_plan": {"message": "Better UX = more sales", "goal": "Increase conversions", "channels": ["facebook"]},
            }
        }
        res = self.client.post("/api/format-report", json=payload)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        text = body.get("formatted_text", "")
        self.assertIn("Main Problem:", text)
        self.assertIn("Strategy:", text)
        self.assertIn("Execution Plan:", text)
        self.assertTrue(len(text.strip()) > 0)

    def test_pdf_download(self):
        rid = self._get_any_report_id()
        res = self.client.get(f"/api/reports/{rid}/pdf")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/pdf")
        self.assertIn('attachment; filename="report.pdf"', res.headers.get("content-disposition", ""))
        self.assertTrue(res.content.startswith(b"%PDF"))

    def test_share_link_roundtrip(self):
        rid = self._get_any_report_id()
        res = self.client.post(f"/api/reports/{rid}/share")
        self.assertEqual(res.status_code, 200)
        share_url = res.json().get("share_url", "")
        self.assertTrue(share_url.startswith("/share/"))
        share_id = share_url.split("/share/")[-1]

        res2 = self.client.get(f"/api/share/{share_id}")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json().get("report_id"), rid)


if __name__ == "__main__":
    unittest.main()

