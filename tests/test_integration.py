import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
EMAIL_DIR = ROOT / "02_Email_Agent"
CRM_DIR = ROOT / "03_CRM"

for path in (ROOT, EMAIL_DIR, CRM_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import config
import knowledge
import gemini_client
import crm_manager
import follow_up_manager
import email_analyzer
import email_draft_generator
from email_classifier import classify_email


SYNTHETIC_SENDER = "Sara Ali <sara.ali.test@example.com>"
SYNTHETIC_SUBJECT = "Request for Egyptian oranges quotation"
SYNTHETIC_BODY = (
    "Hello Al-Gamel,\n\n"
    "We need 12 tons of Egyptian oranges for Dubai.\n"
    "Please send a quotation and available packaging options.\n\n"
    "Regards,\nSara Ali"
)
SYNTHETIC_MESSAGE_ID = "synthetic-test-msg-001"

MOCK_GEMINI_ANALYSIS = json.dumps({
    "classification": "BUSINESS_INQUIRY",
    "customer_type": "Potential Customer",
    "customer_name": "Sara Ali",
    "company_name": "",
    "email": "ignored@example.com",
    "country": "",
    "product": "Egyptian oranges",
    "quantity": "12 tons",
    "specifications": "",
    "packaging": "",
    "destination": "Dubai",
    "shipment_date": "",
    "incoterm": "",
    "payment_terms": "",
    "request": "Quotation and available packaging options",
    "missing_information": [
        "company_name",
        "specifications",
        "packaging",
        "shipment_date",
        "incoterm",
        "payment_terms",
    ],
    "confidence": "HIGH",
})

MOCK_GEMINI_DRAFT = (
    "Subject: Your inquiry about Egyptian oranges\n\n"
    "Dear Sara Ali,\n\n"
    "Thank you for your inquiry regarding 12 tons of Egyptian oranges "
    "for Dubai.\n\n"
    "To prepare a quotation, please confirm packaging, shipment date, "
    "Incoterm, and payment terms. Prices and commercial terms require "
    "human approval.\n\n"
    "Best regards,\n"
    "Al-Gamel Team"
)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class IsolatedCrmMixin:
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)
        self.customers_file = self.tmpdir / "customers.json"
        self.inquiries_file = self.tmpdir / "inquiries.json"
        self.followups_file = self.tmpdir / "follow_ups.json"
        self.processed_file = self.tmpdir / "processed_email_ids.json"
        write_json(self.customers_file, [])
        write_json(self.inquiries_file, [])
        write_json(self.followups_file, [])
        write_json(self.processed_file, [])

        self._patches = [
            patch.object(crm_manager, "CUSTOMERS_FILE", self.customers_file),
            patch.object(crm_manager, "INQUIRIES_FILE", self.inquiries_file),
            patch.object(follow_up_manager, "CUSTOMERS_FILE", self.customers_file),
            patch.object(follow_up_manager, "INQUIRIES_FILE", self.inquiries_file),
            patch.object(follow_up_manager, "FOLLOWUPS_FILE", self.followups_file),
            patch.object(email_analyzer, "PROCESSED_EMAILS_FILE", self.processed_file),
            patch.object(email_draft_generator, "CUSTOMERS_FILE", self.customers_file),
            patch.object(email_draft_generator, "INQUIRIES_FILE", self.inquiries_file),
            patch.object(email_draft_generator, "FOLLOWUPS_FILE", self.followups_file),
            patch("email_analyzer.log_event", return_value={}),
            patch("email_draft_generator.log_event", return_value={}),
        ]
        for item in self._patches:
            item.start()

    def tearDown(self):
        for item in self._patches:
            item.stop()
        self._tmp.cleanup()


class ConfigAndSafetyTests(unittest.TestCase):
    def test_knowledge_path_is_actual_directory(self):
        self.assertEqual(config.KNOWLEDGE_DIR.name, "1_Knowledge")
        self.assertTrue(config.KNOWLEDGE_DIR.exists())

    def test_env_example_has_placeholders_only(self):
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("your-gemini-api-key-here", text)
        self.assertNotRegex(text, r"AIza[0-9A-Za-z_-]{10,}")

    def test_gitignore_covers_secrets(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", text)
        self.assertIn("credentials.json", text)
        self.assertIn("token.json", text)

    def test_no_send_api_in_python_sources(self):
        for path in ROOT.rglob("*.py"):
            if any(part in path.parts for part in (".venv", "__pycache__", "tests")):
                continue
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("messages().send", content)
            self.assertNotIn("drafts().send", content)

    def test_missing_gemini_key_raises_without_api_call(self):
        with patch.object(gemini_client, "GEMINI_API_KEY", ""):
            with self.assertRaises(ValueError):
                gemini_client.get_client()

    def test_configured_model_name_is_overridable(self):
        self.assertTrue(config.GEMINI_MODEL)
        self.assertIn("gemini-", config.GEMINI_MODEL)


class WorkflowIntegrationTests(IsolatedCrmMixin, unittest.TestCase):
    def test_full_email_to_crm_to_draft_workflow(self):
        category = classify_email(
            SYNTHETIC_SENDER,
            SYNTHETIC_SUBJECT,
            SYNTHETIC_BODY,
        )
        self.assertEqual(category, "BUSINESS_INQUIRY")

        kb = knowledge.load_knowledge_base()
        self.assertIn("Al-Gamel", kb)
        self.assertIn("Oranges", kb)

        with patch.object(
            email_analyzer,
            "generate_content",
            return_value=MOCK_GEMINI_ANALYSIS,
        ):
            first = email_analyzer.process_incoming_email(
                message_id=SYNTHETIC_MESSAGE_ID,
                sender=SYNTHETIC_SENDER,
                subject=SYNTHETIC_SUBJECT,
                date="Sat, 10 Oct 2026 12:00:00 +0000",
                body=SYNTHETIC_BODY,
            )

        self.assertEqual(first["status"], "analyzed")
        self.assertFalse(first["used_fallback"])
        analysis = first["analysis"]
        self.assertEqual(analysis["email"], "sara.ali.test@example.com")
        self.assertEqual(analysis["customer_name"], "Sara Ali")
        self.assertEqual(analysis["product"], "Egyptian oranges")
        self.assertEqual(analysis["quantity"], "12 tons")
        self.assertEqual(analysis["destination"], "Dubai")
        self.assertIn("packaging", analysis["missing_information"])
        self.assertIn("payment_terms", analysis["missing_information"])

        crm_result = first["crm"]
        self.assertIsNotNone(crm_result)
        self.assertTrue(crm_result["new_customer"])
        inquiry_id = crm_result["inquiry"]["inquiry_id"]
        self.assertTrue(inquiry_id.startswith("AG-INQ-"))
        self.assertEqual(first["follow_ups_added"], 1)

        customers = read_json(self.customers_file)
        inquiries = read_json(self.inquiries_file)
        followups = read_json(self.followups_file)
        processed = read_json(self.processed_file)
        self.assertEqual(len(customers), 1)
        self.assertEqual(len(inquiries), 1)
        self.assertEqual(len(followups), 1)
        self.assertEqual(processed, [SYNTHETIC_MESSAGE_ID])
        self.assertEqual(followups[0]["inquiry_id"], inquiry_id)
        self.assertEqual(followups[0]["status"], "New")

        with patch.object(
            email_analyzer,
            "generate_content",
            return_value=MOCK_GEMINI_ANALYSIS,
        ) as mocked_gemini:
            second = email_analyzer.process_incoming_email(
                message_id=SYNTHETIC_MESSAGE_ID,
                sender=SYNTHETIC_SENDER,
                subject=SYNTHETIC_SUBJECT,
                date="Sat, 10 Oct 2026 12:00:00 +0000",
                body=SYNTHETIC_BODY,
            )

        self.assertEqual(second["status"], "skipped")
        self.assertEqual(second["reason"], "already_processed")
        mocked_gemini.assert_not_called()
        self.assertEqual(len(read_json(self.inquiries_file)), 1)
        self.assertEqual(len(read_json(self.customers_file)), 1)
        self.assertEqual(len(read_json(self.followups_file)), 1)

        with patch.object(
            email_draft_generator,
            "generate_content",
            return_value=MOCK_GEMINI_DRAFT,
        ):
            draft, used_fallback = email_draft_generator.prepare_draft_text(
                inquiry=crm_result["inquiry"],
                customer=crm_result["customer"],
                knowledge=kb,
                followup=followups[0],
            )

        self.assertFalse(used_fallback)
        subject, body = email_draft_generator.split_email_draft(draft)
        self.assertTrue(subject)
        self.assertIn("Sara Ali", body)
        self.assertIn("human approval", body.lower())
        self.assertNotIn("USD", body)
        self.assertNotIn("$", body)

        source = (EMAIL_DIR / "email_draft_generator.py").read_text(encoding="utf-8")
        self.assertIn('confirmation != "SAVE"', source)
        self.assertIn("does not send", source.lower())
        self.assertIn("drafts().create", source)
        self.assertNotIn("messages().send", source)

    def test_fallback_when_gemini_unavailable(self):
        with patch.object(
            email_analyzer,
            "generate_content",
            side_effect=RuntimeError("quota exceeded"),
        ):
            result = email_analyzer.process_incoming_email(
                message_id="synthetic-fallback-001",
                sender=SYNTHETIC_SENDER,
                subject=SYNTHETIC_SUBJECT,
                date="Sat, 10 Oct 2026 12:00:00 +0000",
                body=SYNTHETIC_BODY,
            )

        self.assertTrue(result["used_fallback"])
        self.assertEqual(result["status"], "analyzed")
        analysis = result["analysis"]
        self.assertEqual(analysis["email"], "sara.ali.test@example.com")
        self.assertEqual(analysis["product"], "oranges")
        self.assertEqual(analysis["quantity"], "12 tons")
        self.assertEqual(analysis["destination"], "Dubai")
        self.assertEqual(analysis["analysis_source"], "fallback")
        self.assertIsNotNone(result["crm"])
        self.assertEqual(len(read_json(self.inquiries_file)), 1)

        draft, used_fallback = email_draft_generator.prepare_draft_text(
            inquiry=result["crm"]["inquiry"],
            customer=result["crm"]["customer"],
            knowledge=knowledge.load_knowledge_base(),
        )
        self.assertTrue(used_fallback)
        subject, body = email_draft_generator.split_email_draft(draft)
        self.assertIn("human approval", body.lower())
        self.assertNotIn("CIF", body)
        self.assertNotIn("FOB", body)

    def test_non_business_email_is_not_saved_to_crm(self):
        with patch.object(email_analyzer, "generate_content") as mocked:
            result = email_analyzer.process_incoming_email(
                message_id="synthetic-social-001",
                sender="updates@linkedin.com",
                subject="You have a new invitation",
                date="Sat, 10 Oct 2026 12:00:00 +0000",
                body="Connect with a new member.",
            )

        mocked.assert_not_called()
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason"], "classifier")
        self.assertEqual(read_json(self.customers_file), [])
        self.assertEqual(read_json(self.inquiries_file), [])


class ProductionCrmUntouchedTests(unittest.TestCase):
    def test_live_crm_files_were_not_changed_by_integration_setup(self):
        customers = json.loads(config.CUSTOMERS_FILE.read_text(encoding="utf-8"))
        inquiries = json.loads(config.INQUIRIES_FILE.read_text(encoding="utf-8"))
        followups = json.loads(config.FOLLOWUPS_FILE.read_text(encoding="utf-8"))
        processed = json.loads(config.PROCESSED_EMAILS_FILE.read_text(encoding="utf-8"))
        self.assertEqual([c["customer_id"] for c in customers], ["AG-CUST-0001"])
        self.assertEqual(
            [i["inquiry_id"] for i in inquiries],
            ["AG-INQ-0001", "AG-INQ-0002"],
        )
        self.assertEqual(
            [f["inquiry_id"] for f in followups],
            ["AG-INQ-0001", "AG-INQ-0002"],
        )
        self.assertEqual(len(processed), 20)


if __name__ == "__main__":
    unittest.main()
