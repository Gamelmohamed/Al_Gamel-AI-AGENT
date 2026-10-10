import sys
import re
import json
import base64
from pathlib import Path
from email.message import EmailMessage

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import (
    CREDENTIALS_FILE,
    CUSTOMERS_FILE,
    FOLLOWUPS_FILE,
    GMAIL_SCOPES,
    INQUIRIES_FILE,
    TOKEN_FILE,
)
from gemini_client import generate_content
from knowledge import load_knowledge_base
from activity_logger import log_event

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

EMAIL_PATTERN = r"[^@\s]+@[^@\s]+\.[^@\s]+"


def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_inquiry_id(inquiry):
    for field in ("inquiry_id", "id", "inquiry_number"):
        value = inquiry.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def find_customer(customers, customer_id):
    for customer in customers:
        if str(customer.get("customer_id", "")).strip() == str(
            customer_id
        ).strip():
            return customer
    return None


def get_customer_email(customer):
    possible_fields = [
        "email",
        "email_address",
        "customer_email",
        "contact_email",
    ]

    for field in possible_fields:
        value = customer.get(field)
        if isinstance(value, str):
            address = value.strip()
            if re.fullmatch(EMAIL_PATTERN, address):
                return address

    return ""


def get_followup_record(inquiry_id):
    if not FOLLOWUPS_FILE.exists():
        return {}

    records = load_json(FOLLOWUPS_FILE)

    if not isinstance(records, list):
        raise ValueError("follow_ups.json must contain a JSON list.")

    for record in records:
        if str(record.get("inquiry_id", "")).strip() == inquiry_id:
            return record

    return {}


def get_latest_inquiry():
    inquiries = load_json(INQUIRIES_FILE)
    customers = load_json(CUSTOMERS_FILE)

    if not isinstance(inquiries, list):
        raise ValueError("inquiries.json must contain a JSON list.")

    if not isinstance(customers, list):
        raise ValueError("customers.json must contain a JSON list.")

    if not inquiries:
        raise ValueError("No CRM inquiries found.")

    available = []

    print("\nAVAILABLE CRM INQUIRIES")
    print("-" * 76)

    for inquiry in inquiries:
        inquiry_id = get_inquiry_id(inquiry)

        if not inquiry_id:
            print("Warning: An inquiry has no recognized ID.")
            continue

        customer = find_customer(
            customers,
            inquiry.get("customer_id", "")
        )

        customer_name = (
            (customer or {}).get("customer_name")
            or (customer or {}).get("name")
            or "Unknown customer"
        )

        product = inquiry.get("product") or "Not provided"

        print(f"{inquiry_id} | {customer_name} | {product}")
        available.append((inquiry_id, inquiry, customer))

    if not available:
        raise ValueError("No inquiries with recognized IDs were found.")

    selected_id = input(
        "\nEnter the inquiry ID to prepare an email for: "
    ).strip()

    selected = next(
        (
            item for item in available
            if item[0].casefold() == selected_id.casefold()
        ),
        None
    )

    if selected is None:
        raise ValueError(
            f"Inquiry ID '{selected_id}' was not found. "
            "Nothing was saved."
        )

    inquiry_id, inquiry, customer = selected

    if not customer:
        raise ValueError(
            "The customer linked to this inquiry was not found. "
            "Nothing was saved."
        )

    followup = get_followup_record(inquiry_id)
    return inquiry_id, inquiry, customer, followup


def get_gmail_service():
    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            GMAIL_SCOPES
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                "credentials.json was not found in the project root."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            GMAIL_SCOPES
        )
        credentials = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    return build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False
    )


def build_prompt(inquiry, customer, knowledge, followup=None):
    customer_data = json.dumps(customer, ensure_ascii=False, indent=2)
    inquiry_data = json.dumps(inquiry, ensure_ascii=False, indent=2)
    followup_data = json.dumps(followup or {}, ensure_ascii=False, indent=2)

    return f"""
You are the professional export sales assistant for Al-Gamel,
an Egyptian fresh produce export company.

Your task is to prepare an accurate, professional English email.

APPROVED COMPANY KNOWLEDGE:
{knowledge}

CRM CUSTOMER DATA:
{customer_data}

CRM INQUIRY DATA:
{inquiry_data}

FOLLOW-UP RECORD:
{followup_data}

STRICT RULES:
1. Never invent prices, discounts, certifications, specifications,
   available quantities, production capacity, shipment dates,
   payment terms, or commercial commitments.
2. Use only facts supported by the CRM or approved knowledge.
3. If information is missing, politely ask the customer for it.
4. Never claim that a shipment, payment, or order is confirmed
   unless the supplied records explicitly establish that fact.
5. Never expose internal costs, profit margins, internal notes,
   or confidential company information.
6. Use clear, courteous, professional business English.
7. Keep the email concise and easy to answer.
8. Do not include Markdown formatting in the email itself.
9. Do not send the email. Return a draft only.
10. If a follow-up note exists, use it to understand the context.
    Do not claim that a previous email was sent unless the records
    explicitly confirm it.
11. Do not invent a recipient name, company name, or prior contact.
12. Prices, discounts, payment terms, contracts, order confirmations,
    and commercial commitments require human approval and must not
    be stated as final.

EMAIL TYPE:
If the follow-up record has a note indicating that customer details
are awaited, prepare a polite follow-up requesting the missing details.
Otherwise, prepare an appropriate initial response to the inquiry.

OUTPUT FORMAT:
The first line must be:
Subject: [email subject]

Then a blank line, followed by the complete email body.

Do not include explanations before or after the email.
"""


def generate_draft(prompt):
    draft = generate_content(prompt)
    if not draft or not draft.strip():
        raise RuntimeError("Gemini returned an empty response.")
    return draft.strip()


def build_fallback_draft(customer_name, product, quantity, destination, missing_information=None):
    missing = missing_information or []
    missing_lines = ""
    if missing:
        items = "\n".join(f"- {item}" for item in missing)
        missing_lines = (
            "To prepare an accurate response, please confirm:\n"
            f"{items}\n\n"
        )

    return (
        f"Subject: Follow-up on {product} Inquiry\n\n"
        f"Dear {customer_name},\n\n"
        "I hope you are doing well.\n\n"
        f"I am following up on your inquiry regarding "
        f"{quantity} of {product} for {destination}.\n\n"
        f"{missing_lines}"
        "Prices, payment terms, and delivery commitments require "
        "human approval and will be confirmed separately.\n\n"
        "Please let us know if you have any questions or "
        "additional requirements. We will be happy to assist.\n\n"
        "Best regards,\n"
        "Al-Gamel Team"
    )


def prepare_draft_text(inquiry, customer, knowledge, followup=None):
    prompt = build_prompt(
        inquiry=inquiry,
        customer=customer,
        knowledge=knowledge,
        followup=followup,
    )
    try:
        return generate_draft(prompt), False
    except Exception:
        customer_name = (
            customer.get("customer_name")
            or customer.get("name")
            or "Not provided"
        )
        return build_fallback_draft(
            customer_name=customer_name,
            product=inquiry.get("product") or "Not provided",
            quantity=inquiry.get("quantity") or "Not provided",
            destination=inquiry.get("destination") or "Not provided",
            missing_information=inquiry.get("missing_information") or [],
        ), True


def split_email_draft(draft):
    lines = draft.strip().splitlines()

    for index, line in enumerate(lines):
        if line.strip().lower().startswith("subject:"):
            subject = line.strip().split(":", 1)[1].strip()
            body = "\n".join(lines[index + 1:]).strip()

            if not subject:
                raise ValueError("The generated email subject is empty.")

            if not body:
                raise ValueError("The generated email body is empty.")

            return subject, body

    raise ValueError("Gemini did not return a valid Subject: line.")


def save_gmail_draft(recipient, subject, body):
    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    service = get_gmail_service()

    result = service.users().drafts().create(
        userId="me",
        body={
            "message": {
                "raw": encoded_message
            }
        }
    ).execute()

    draft_id = result.get("id")

    if not draft_id:
        raise RuntimeError("Gmail did not return a draft ID.")

    return draft_id


def main():
    print("=" * 68)
    print("AL-GAMEL AI - EMAIL DRAFT GENERATOR")
    print("Specific inquiry | Human approval | Drafts only")
    print("=" * 68)

    try:
        inquiry_id, inquiry, customer, followup = get_latest_inquiry()
        knowledge = load_knowledge_base()

        customer_name = (
            customer.get("customer_name")
            or customer.get("name")
            or "Not provided"
        )
        company_name = customer.get("company_name") or "Not provided"
        product = inquiry.get("product") or "Not provided"
        quantity = inquiry.get("quantity") or "Not provided"
        destination = inquiry.get("destination") or "Not provided"

        print(f"\nInquiry ID  : {inquiry_id}")
        print(f"Customer    : {customer_name}")
        print(f"Company     : {company_name}")
        print(f"Product     : {product}")
        print(f"Quantity    : {quantity}")
        print(f"Destination : {destination}")

        if followup:
            print(
                f"Follow-up status: "
                f"{followup.get('status', 'Not recorded')}"
            )
            print(
                f"Next follow-up  : "
                f"{followup.get('next_follow_up_date', 'Not scheduled')}"
            )

        print("\nGenerating draft with Gemini...\n")

        draft, used_fallback = prepare_draft_text(
            inquiry=inquiry,
            customer=customer,
            knowledge=knowledge,
            followup=followup,
        )
        if used_fallback:
            print("Gemini is unavailable. Using a basic template instead.\n")

        subject, body = split_email_draft(draft)

        print("=" * 68)
        print("GENERATED EMAIL DRAFT - REVIEW BEFORE USE")
        print("=" * 68)
        print(f"Subject: {subject}\n")
        print(body)
        print("=" * 68)

        recipient = get_customer_email(customer)

        if not recipient:
            print("\nNo valid customer email was found in the CRM.")
            recipient = input(
                "Enter the recipient email address manually: "
            ).strip()

        if not re.fullmatch(EMAIL_PATTERN, recipient):
            print(
                "\nInvalid email address. "
                "Nothing was saved or sent."
            )
            return

        print("\nGMAIL DRAFT REVIEW")
        print("-" * 68)
        print(f"Inquiry ID: {inquiry_id}")
        print(f"Recipient : {recipient}")
        print(f"Subject   : {subject}")
        print("-" * 68)
        print("\nVerify the recipient and email content carefully.")
        print(
            "Typing SAVE creates a Gmail draft only. "
            "It does not send the email."
        )

        confirmation = input(
            "\nType SAVE to save this draft to Gmail: "
        ).strip()

        if confirmation != "SAVE":
            print("\nCancelled. No draft was saved or sent.")
            return

        draft_id = save_gmail_draft(
            recipient=recipient,
            subject=subject,
            body=body
        )

        log_event(
            "gmail_draft_created",
            inquiry_id=inquiry_id,
            draft_id=draft_id,
        )

        print("\n" + "=" * 68)
        print("SUCCESS: Gmail draft created.")
        print(f"Inquiry ID: {inquiry_id}")
        print(f"Draft ID  : {draft_id}")
        print("Check Gmail > Drafts.")
        print("The email was NOT sent.")
        print("=" * 68)

    except KeyboardInterrupt:
        print("\nOperation cancelled. No email was sent.")

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError
    ) as error:
        print(f"\nERROR: {error}")
        print("No email was sent.")

    except Exception as error:
        print(f"\nUNEXPECTED ERROR: {error}")
        print("Check the error before trying again.")
        print("No email was intentionally sent by this program.")


if __name__ == "__main__":
    main()
