import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

CRM_DIR = BASE_DIR / "03_CRM"

CUSTOMERS_FILE = CRM_DIR / "customers.json"
INQUIRIES_FILE = CRM_DIR / "inquiries.json"


# =========================================================
# FILE HELPERS
# =========================================================

def load_json(file_path):

    if not file_path.exists():
        return []

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_json(file_path, data):

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# ID GENERATION
# =========================================================

def generate_id(prefix, records, field):

    numbers = []

    for record in records:

        value = record.get(field, "")

        if value.startswith(prefix):

            try:
                number = int(
                    value.replace(prefix, "")
                )

                numbers.append(number)

            except ValueError:
                pass

    next_number = max(numbers, default=0) + 1

    return f"{prefix}{next_number:04d}"


# =========================================================
# FIND CUSTOMER
# =========================================================

def find_customer(
    customers,
    email="",
    company_name=""
):

    email = email.strip().lower()
    company_name = company_name.strip().lower()

    for customer in customers:

        customer_email = (
            customer.get("email", "")
            .strip()
            .lower()
        )

        customer_company = (
            customer.get("company_name", "")
            .strip()
            .lower()
        )

        # Match by email
        if email and customer_email == email:
            return customer

        # Match by company
        if (
            company_name
            and customer_company
            and company_name == customer_company
        ):
            return customer

    return None


# =========================================================
# CREATE OR UPDATE CUSTOMER
# =========================================================

def create_or_update_customer(analysis):

    customers = load_json(
        CUSTOMERS_FILE
    )

    email = analysis.get(
        "email",
        ""
    )

    company_name = analysis.get(
        "company_name",
        ""
    )

    existing_customer = find_customer(
        customers,
        email=email,
        company_name=company_name
    )

    now = datetime.now().isoformat()

    # -----------------------------------------------------
    # Existing customer
    # -----------------------------------------------------

    if existing_customer:

        existing_customer["updated_at"] = now

        # Update only fields that contain information
        fields = [
            "customer_name",
            "company_name",
            "email",
            "country"
        ]

        for field in fields:

            value = analysis.get(
                field,
                ""
            )

            if value:
                existing_customer[field] = value

        save_json(
            CUSTOMERS_FILE,
            customers
        )

        return existing_customer, False

    # -----------------------------------------------------
    # New customer
    # -----------------------------------------------------

    customer_id = generate_id(
        "AG-CUST-",
        customers,
        "customer_id"
    )

    customer = {

        "customer_id": customer_id,

        "customer_type": analysis.get(
            "customer_type",
            "Unknown"
        ),

        "customer_name": analysis.get(
            "customer_name",
            ""
        ),

        "company_name": analysis.get(
            "company_name",
            ""
        ),

        "email": analysis.get(
            "email",
            ""
        ),

        "country": analysis.get(
            "country",
            ""
        ),

        "status": "LEAD",

        "source": "EMAIL",

        "created_at": now,

        "updated_at": now
    }

    customers.append(customer)

    save_json(
        CUSTOMERS_FILE,
        customers
    )

    return customer, True


# =========================================================
# CREATE INQUIRY
# =========================================================

def create_inquiry(
    analysis,
    customer
):

    inquiries = load_json(
        INQUIRIES_FILE
    )

    inquiry_id = generate_id(
        "AG-INQ-",
        inquiries,
        "inquiry_id"
    )

    now = datetime.now().isoformat()

    inquiry = {

        "inquiry_id": inquiry_id,

        "customer_id": customer.get(
            "customer_id",
            ""
        ),

        "classification": analysis.get(
            "classification",
            ""
        ),

        "product": analysis.get(
            "product",
            ""
        ),

        "quantity": analysis.get(
            "quantity",
            ""
        ),

        "specifications": analysis.get(
            "specifications",
            ""
        ),

        "packaging": analysis.get(
            "packaging",
            ""
        ),

        "destination": analysis.get(
            "destination",
            ""
        ),

        "shipment_date": analysis.get(
            "shipment_date",
            ""
        ),

        "incoterm": analysis.get(
            "incoterm",
            ""
        ),

        "payment_terms": analysis.get(
            "payment_terms",
            ""
        ),

        "request": analysis.get(
            "request",
            ""
        ),

        "missing_information": analysis.get(
            "missing_information",
            []
        ),

        "confidence": analysis.get(
            "confidence",
            "LOW"
        ),

        "status": "NEW",

        "created_at": now,

        "updated_at": now
    }

    inquiries.append(inquiry)

    save_json(
        INQUIRIES_FILE,
        inquiries
    )

    return inquiry


# =========================================================
# PROCESS AI ANALYSIS
# =========================================================

def process_analysis(analysis):

    customer, is_new_customer = (
        create_or_update_customer(
            analysis
        )
    )

    inquiry = create_inquiry(
        analysis,
        customer
    )

    return {
        "customer": customer,
        "new_customer": is_new_customer,
        "inquiry": inquiry
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_analysis = {

        "classification": "BUSINESS_INQUIRY",

        "customer_type": "Potential Customer",

        "customer_name": "Ahmed",

        "company_name": "",

        "email": "gamelmohmed4@gmail.com",

        "country": "Saudi Arabia",

        "product": "Egyptian oranges",

        "quantity": "10 tons",

        "specifications": "",

        "packaging": "",

        "destination": "Jeddah, Saudi Arabia",

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
            "payment_terms"
        ],

        "confidence": "HIGH"
    }

    result = process_analysis(
        test_analysis
    )

    print("=" * 70)
    print("AL-GAMEL CRM TEST")
    print("=" * 70)

    print()
    print("CUSTOMER:")
    print(
        json.dumps(
            result["customer"],
            indent=4,
            ensure_ascii=False
        )
    )

    print()
    print(
        "NEW CUSTOMER:",
        result["new_customer"]
    )

    print()
    print("INQUIRY:")
    print(
        json.dumps(
            result["inquiry"],
            indent=4,
            ensure_ascii=False
        )
    )

    print()
    print("=" * 70)