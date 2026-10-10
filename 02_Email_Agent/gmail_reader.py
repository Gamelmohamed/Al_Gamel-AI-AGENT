from pathlib import Path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_gmail_service():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(
            creds.to_json(),
            encoding="utf-8"
        )

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


def decode_body(data):
    """Decode Gmail message body."""

    if not data:
        return ""

    decoded = base64.urlsafe_b64decode(
        data + "=" * (-len(data) % 4)
    )

    return decoded.decode(
        "utf-8",
        errors="replace"
    )


def extract_body(payload):

    # Simple message
    if payload.get("body", {}).get("data"):
        return decode_body(
            payload["body"]["data"]
        )

    # Multipart message
    for part in payload.get("parts", []):

        if part.get("mimeType") == "text/plain":

            data = part.get("body", {}).get("data")

            if data:
                return decode_body(data)

        # Check nested parts
        if part.get("parts"):

            body = extract_body(part)

            if body:
                return body

    return ""


def get_header(headers, name):

    for header in headers:

        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def main():

    print("=================================")
    print("       AL-GAMEL AI")
    print("        GMAIL READER")
    print("=================================")

    print("\nConnecting to Gmail...")

    service = get_gmail_service()

    result = service.users().messages().list(
        userId="me",
        maxResults=5
    ).execute()

    messages = result.get("messages", [])

    print(f"\nFound {len(messages)} messages\n")

    print("=" * 70)

    for index, message in enumerate(messages, start=1):

        message_id = message["id"]

        email = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        payload = email.get("payload", {})

        headers = payload.get("headers", [])

        sender = get_header(headers, "From")
        subject = get_header(headers, "Subject")
        date = get_header(headers, "Date")

        body = extract_body(payload)

        print(f"\nEMAIL #{index}")
        print("-" * 70)

        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")

        print("\nBody:")
        print(body[:3000])

        print("\n" + "=" * 70)


if __name__ == "__main__":
    main()