import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMAIL_DIR = ROOT / "02_Email_Agent"
CRM_DIR = ROOT / "03_CRM"

for path in (ROOT, EMAIL_DIR, CRM_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import config
import knowledge
from email_classifier import classify_email
from email_draft_generator import split_email_draft, get_customer_email
from email_analyzer import clean_html
from crm_manager import find_customer, generate_id, load_json
from follow_up_manager import classify_record, get_inquiry_id


class KnowledgeTests(unittest.TestCase):
    def test_knowledge_directory_exists(self):
        self.assertTrue(config.KNOWLEDGE_DIR.exists())
        self.assertEqual(config.KNOWLEDGE_DIR.name, "1_Knowledge")

    def test_knowledge_base_loads_markdown(self):
        status = knowledge.knowledge_status()
        content = knowledge.load_knowledge_base()
        self.assertGreaterEqual(status["markdown_files"], 5)
        self.assertIn("Al-Gamel", content)
        self.assertIn("company_profile.md", content)
        self.assertNotIn("01_Knowledge", str(config.KNOWLEDGE_DIR))


class ClassifierTests(unittest.TestCase):
    def test_business_inquiry(self):
        category = classify_email(
            "buyer@example.com",
            "Request for orange quotation",
            "Please send a price for 10 tons of oranges."
        )
        self.assertEqual(category, "BUSINESS_INQUIRY")

    def test_security_email(self):
        category = classify_email(
            "no-reply@accounts.google.com",
            "Security alert",
            "New sign-in on your account."
        )
        self.assertEqual(category, "SECURITY")

    def test_social_email(self):
        category = classify_email(
            "updates@linkedin.com",
            "You have a new invitation",
            "Connect with a new member."
        )
        self.assertEqual(category, "SOCIAL")

    def test_unknown_email(self):
        category = classify_email(
            "someone@example.com",
            "Hello",
            "Just saying hello."
        )
        self.assertEqual(category, "UNKNOWN")


class AnalyzerHelperTests(unittest.TestCase):
    def test_clean_html_strips_tags(self):
        text = clean_html("<p>Hello <b>Al-Gamel</b></p><script>bad()</script>")
        self.assertIn("Hello", text)
        self.assertIn("Al-Gamel", text)
        self.assertNotIn("script", text.lower())


class DraftTests(unittest.TestCase):
    def test_split_email_draft(self):
        subject, body = split_email_draft(
            "Subject: Orange inquiry\n\nDear Ahmed,\nPlease confirm quantity."
        )
        self.assertEqual(subject, "Orange inquiry")
        self.assertIn("Dear Ahmed", body)

    def test_customer_email_from_crm_record(self):
        customer = {"email": "buyer@example.com"}
        self.assertEqual(get_customer_email(customer), "buyer@example.com")

    def test_invalid_customer_email(self):
        customer = {"email": "not-an-email"}
        self.assertEqual(get_customer_email(customer), "")


class CrmReadOnlyTests(unittest.TestCase):
    def test_existing_customer_json_is_readable(self):
        customers = load_json(config.CUSTOMERS_FILE)
        inquiries = load_json(config.INQUIRIES_FILE)
        self.assertIsInstance(customers, list)
        self.assertIsInstance(inquiries, list)
        self.assertGreaterEqual(len(customers), 1)
        self.assertGreaterEqual(len(inquiries), 1)
        self.assertEqual(customers[0]["customer_id"], "AG-CUST-0001")

    def test_find_customer_by_email(self):
        customers = load_json(config.CUSTOMERS_FILE)
        found = find_customer(customers, email=customers[0]["email"])
        self.assertIsNotNone(found)
        self.assertEqual(found["customer_id"], customers[0]["customer_id"])

    def test_generate_id_increments(self):
        records = [{"inquiry_id": "AG-INQ-0002"}]
        next_id = generate_id("AG-INQ-", records, "inquiry_id")
        self.assertEqual(next_id, "AG-INQ-0003")

    def test_crm_json_files_unchanged_by_this_test(self):
        before_customers = config.CUSTOMERS_FILE.read_text(encoding="utf-8")
        before_inquiries = config.INQUIRIES_FILE.read_text(encoding="utf-8")
        load_json(config.CUSTOMERS_FILE)
        load_json(config.INQUIRIES_FILE)
        self.assertEqual(
            before_customers,
            config.CUSTOMERS_FILE.read_text(encoding="utf-8")
        )
        self.assertEqual(
            before_inquiries,
            config.INQUIRIES_FILE.read_text(encoding="utf-8")
        )


class FollowUpTests(unittest.TestCase):
    def test_inquiry_id_fields(self):
        self.assertEqual(get_inquiry_id({"inquiry_id": "AG-INQ-0001"}), "AG-INQ-0001")
        self.assertEqual(get_inquiry_id({"id": "X-1"}), "X-1")

    def test_classify_closed_record(self):
        state = classify_record({"status": "Closed - Won"})
        self.assertEqual(state, "CLOSED")


class GitignoreTests(unittest.TestCase):
    def test_secret_files_are_ignored(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore)
        self.assertIn("credentials.json", gitignore)
        self.assertIn("token.json", gitignore)


if __name__ == "__main__":
    unittest.main()
