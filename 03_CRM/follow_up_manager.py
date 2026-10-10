
import json
from datetime import date, datetime, timedelta
from pathlib import Path


# ============================================================
# AL-GAMEL AI - CRM FOLLOW-UP MANAGER
# Tracks customer inquiries and follow-up dates.
# Does not send emails or modify existing CRM records.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CRM_DIR = BASE_DIR / "03_CRM"

INQUIRIES_FILE = CRM_DIR / "inquiries.json"
CUSTOMERS_FILE = CRM_DIR / "customers.json"
FOLLOWUPS_FILE = CRM_DIR / "follow_ups.json"


# ------------------------------------------------------------
# FILE HELPERS
# ------------------------------------------------------------

def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_followups(records):
    """Save to a separate file without changing the original CRM."""

    temporary_file = FOLLOWUPS_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=2
        )

    temporary_file.replace(FOLLOWUPS_FILE)


def get_inquiry_id(inquiry):
    return (
        inquiry.get("inquiry_id")
        or inquiry.get("id")
        or inquiry.get("inquiry_number")
    )


def parse_creation_date(value):
    if isinstance(value, str) and value.strip():
        try:
            return datetime.fromisoformat(
                value.strip().replace("Z", "+00:00")
            ).date()
        except ValueError:
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                pass

    return None


def find_customer(customers, customer_id):
    for customer in customers:
        if customer.get("customer_id") == customer_id:
            return customer

    return {}


def customer_name(customer):
    return (
        customer.get("customer_name")
        or customer.get("name")
        or "Unknown customer"
    )


# ------------------------------------------------------------
# CRM SYNCHRONIZATION
# ------------------------------------------------------------

def sync_inquiries():
    """
    Add inquiries that do not yet have a follow-up record.
    Existing follow-up statuses and notes are preserved.
    """

    inquiries = load_json(INQUIRIES_FILE)
    customers = load_json(CUSTOMERS_FILE)

    if not isinstance(inquiries, list):
        raise ValueError(
            "inquiries.json must contain a JSON list."
        )

    if not isinstance(customers, list):
        raise ValueError(
            "customers.json must contain a JSON list."
        )

    if FOLLOWUPS_FILE.exists():
        records = load_json(FOLLOWUPS_FILE)
    else:
        records = []

    if not isinstance(records, list):
        raise ValueError(
            "follow_ups.json must contain a JSON list."
        )

    existing_ids = {
        record.get("inquiry_id")
        for record in records
    }

    added = 0

    for inquiry in inquiries:
        inquiry_id = get_inquiry_id(inquiry)

        if not inquiry_id:
            raise ValueError(
                "An inquiry has no inquiry_id, id, or "
                "inquiry_number. No records were saved. "
                "Check the CRM inquiry schema."
            )

        inquiry_id = str(inquiry_id)

        if inquiry_id in existing_ids:
            continue

        customer = find_customer(
            customers,
            inquiry.get("customer_id")
        )

        created_date = parse_creation_date(
            inquiry.get("created_at")
        )

        if created_date is None:
            created_date = date.today()

        first_followup = created_date + timedelta(days=3)

        records.append({
            "inquiry_id": inquiry_id,
            "customer_id": inquiry.get("customer_id"),
            "customer_name": customer_name(customer),
            "company_name": customer.get(
                "company_name", "Not provided"
            ),
            "customer_email": (
                customer.get("email")
                or customer.get("email_address")
                or customer.get("customer_email")
                or ""
            ),
            "product": inquiry.get("product", "Not provided"),
            "quantity": inquiry.get("quantity", "Not provided"),
            "destination": inquiry.get(
                "destination", "Not provided"
            ),
            "status": "New",
            "created_date": created_date.isoformat(),
            "last_contact_date": None,
            "next_follow_up_date": first_followup.isoformat(),
            "notes": []
        })

        existing_ids.add(inquiry_id)
        added += 1

    save_followups(records)

    print(f"\nNew follow-up records created: {added}")
    print(f"Total tracked inquiries: {len(records)}")

    return records


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------

def classify_record(record):
    if record.get("status") in (
        "Closed - Won",
        "Closed - Lost"
    ):
        return "CLOSED"

    due_value = record.get("next_follow_up_date")

    if not due_value:
        return "UNSCHEDULED"

    try:
        due_date = date.fromisoformat(due_value)
    except (ValueError, TypeError):
        return "CHECK DATE"

    if due_date < date.today():
        return "OVERDUE"

    if due_date == date.today():
        return "DUE TODAY"

    return "UPCOMING"


def show_dashboard(records):
    print("\n" + "=" * 90)
    print("AL-GAMEL AI - CUSTOMER FOLLOW-UP DASHBOARD")
    print("=" * 90)

    if not records:
        print("No inquiries are currently tracked.")
        return

    for record in records:
        state = classify_record(record)

        print(f"\nInquiry ID : {record.get('inquiry_id')}")
        print(f"Customer   : {record.get('customer_name')}")
        print(f"Company    : {record.get('company_name')}")
        print(f"Product    : {record.get('product')}")
        print(f"Quantity   : {record.get('quantity')}")
        print(f"Destination: {record.get('destination')}")
        print(f"Status     : {record.get('status')}")
        print(f"Next date  : {record.get('next_follow_up_date') or 'Not scheduled'}")
        print(f"Priority   : {state}")

        if record.get("notes"):
            print(f"Latest note: {record['notes'][-1]}")

        print("-" * 90)

    active = [
        record for record in records
        if classify_record(record) != "CLOSED"
    ]

    overdue = sum(
        classify_record(record) == "OVERDUE"
        for record in active
    )

    due_today = sum(
        classify_record(record) == "DUE TODAY"
        for record in active
    )

    print("\nSUMMARY")
    print(f"Active inquiries : {len(active)}")
    print(f"Overdue          : {overdue}")
    print(f"Due today        : {due_today}")
    print("=" * 90)


# ------------------------------------------------------------
# UPDATE FOLLOW-UP
# ------------------------------------------------------------

def find_record(records, inquiry_id):
    for record in records:
        if str(record.get("inquiry_id")) == str(inquiry_id):
            return record

    return None


def record_followup(records):
    inquiry_id = input(
        "\nEnter the inquiry ID: "
    ).strip()

    record = find_record(records, inquiry_id)

    if not record:
        print("Inquiry not found.")
        return

    print(f"\nCustomer: {record.get('customer_name')}")
    print(f"Current status: {record.get('status')}")

    print("\nSelect the updated status:")
    print("1. Waiting for customer")
    print("2. Follow-up scheduled")
    print("3. Qualified - needs commercial review")
    print("4. Closed - Won")
    print("5. Closed - Lost")

    choice = input("Choice (1-5): ").strip()

    status_options = {
        "1": "Waiting for customer",
        "2": "Follow-up scheduled",
        "3": "Qualified - needs commercial review",
        "4": "Closed - Won",
        "5": "Closed - Lost"
    }

    if choice not in status_options:
        print("Invalid choice. Nothing changed.")
        return

    new_status = status_options[choice]
    note = input(
        "Enter a note about the contact or next action: "
    ).strip()

    record["status"] = new_status
    record["last_contact_date"] = date.today().isoformat()

    if note:
        record.setdefault("notes", []).append(
            f"{date.today().isoformat()}: {note}"
        )

    if new_status in ("Closed - Won", "Closed - Lost"):
        record["next_follow_up_date"] = None
        record["closed_date"] = date.today().isoformat()

    else:
        next_date = input(
            "Next follow-up date (YYYY-MM-DD), "
            "or press Enter to leave unscheduled: "
        ).strip()

        if next_date:
            try:
                parsed_date = date.fromisoformat(next_date)

                if parsed_date < date.today():
                    print(
                        "The date is in the past. "
                        "Update cancelled; choose a future date "
                        "or today's date."
                    )
                    return

                record["next_follow_up_date"] = (
                    parsed_date.isoformat()
                )

            except ValueError:
                print("Invalid date format. Nothing was saved.")
                return
        else:
            record["next_follow_up_date"] = None

        record.pop("closed_date", None)

    save_followups(records)
    print("\nFollow-up record updated successfully.")


# ------------------------------------------------------------
# MAIN MENU
# ------------------------------------------------------------

def main():
    print("=" * 68)
    print("AL-GAMEL AI - FOLLOW-UP MANAGER")
    print("CRM tracking | No email sending")
    print("=" * 68)

    try:
        records = sync_inquiries()

        while True:
            print("\nMAIN MENU")
            print("1. Show follow-up dashboard")
            print("2. Record customer follow-up")
            print("3. Sync new CRM inquiries")
            print("4. Exit")

            choice = input("\nChoose (1-4): ").strip()

            if choice == "1":
                show_dashboard(records)

            elif choice == "2":
                record_followup(records)
                records = load_json(FOLLOWUPS_FILE)

            elif choice == "3":
                records = sync_inquiries()

            elif choice == "4":
                print("Follow-up manager closed.")
                break

            else:
                print("Invalid choice. Enter 1, 2, 3, or 4.")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"\nDATA ERROR: {error}")
        raise SystemExit(1)

    except Exception as error:
        print(f"\nERROR: {type(error).__name__}: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()