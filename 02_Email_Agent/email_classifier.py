from pathlib import Path
from email.utils import parseaddr

from gmail_reader import get_gmail_service, get_header, extract_body


MAX_EMAILS = 20


def classify_email(sender, subject, body):
    sender_email = parseaddr(sender)[1].lower()

    subject_lower = subject.lower()
    body_lower = body.lower()

    # =========================================================
    # 1. SECURITY
    # =========================================================

    security_domains = [
        "accounts.google.com",
        "google.com",
        "microsoft.com",
        "apple.com"
    ]

    security_words = [
        "security alert",
        "تنبيه أمني",
        "عملية تسجيل دخول جديدة",
        "new sign-in",
        "password changed",
        "تغيير كلمة المرور"
    ]

    if any(domain in sender_email for domain in security_domains):
        if any(
            word.lower() in subject_lower or word.lower() in body_lower
            for word in security_words
        ):
            return "SECURITY"

    # =========================================================
    # 2. SOCIAL MEDIA
    # =========================================================

    social_domains = [
        "linkedin.com",
        "instagram.com",
        "facebook.com",
        "facebookmail.com",
        "priority.facebookmail.com",
        "twitter.com",
        "x.com"
    ]

    if any(domain in sender_email for domain in social_domains):
        return "SOCIAL"

    # =========================================================
    # 3. DELIVERY FAILURE
    # =========================================================

    delivery_failure_words = [
        "delivery status notification",
        "delivery failure",
        "delivery failed",
        "mail delivery failed",
        "undeliverable",
        "address not found",
        "message not delivered",
        "recipient address rejected",
        "failure notice",
        "فشل التسليم",
        "تعذر تسليم الرسالة"
    ]

    if any(
        word.lower() in subject_lower or word.lower() in body_lower
        for word in delivery_failure_words
    ):
        return "DELIVERY_FAILURE"

    # =========================================================
    # 4. NEWSLETTER / MARKETING
    # =========================================================

    newsletter_words = [
        "unsubscribe",
        "إلغاء الاشتراك",
        "newsletter",
        "weekly update",
        "special offer",
        "عرض خاص",
        "marketing",
        "promotion",
        "promotional"
    ]

    if any(
        word.lower() in subject_lower or word.lower() in body_lower
        for word in newsletter_words
    ):
        return "NEWSLETTER"

    # =========================================================
    # 5. BUSINESS INQUIRY
    # =========================================================

    business_words = [
        "quotation",
        "quote",
        "price",
        "pricing",
        "order",
        "purchase",
        "buy",
        "export",
        "import",
        "fresh fruit",
        "fresh vegetable",
        "fresh fruits",
        "fresh vegetables",
        "fruits",
        "vegetables",
        "orange",
        "oranges",
        "mango",
        "mangoes",
        "grape",
        "grapes",
        "pomegranate",
        "pomegranates",
        "potato",
        "potatoes",
        "onion",
        "onions",
        "garlic",
        "sweet potato",
        "sweet potatoes",
        "طلب عرض سعر",
        "عرض سعر",
        "سعر",
        "طلب شراء",
        "شراء",
        "تصدير",
        "استيراد"
    ]

    if any(
        word.lower() in subject_lower or word.lower() in body_lower
        for word in business_words
    ):
        return "BUSINESS_INQUIRY"

    # =========================================================
    # 6. UNKNOWN
    # =========================================================

    return "UNKNOWN"


def main():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        maxResults=MAX_EMAILS
    ).execute()

    messages = results.get("messages", [])

    print("=" * 70)
    print("AL-GAMEL AI - EMAIL CLASSIFIER")
    print("=" * 70)

    category_counts = {}

    for index, message in enumerate(messages, start=1):

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])

        sender = get_header(headers, "From")
        subject = get_header(headers, "Subject")
        date = get_header(headers, "Date")

        body = extract_body(payload)

        category = classify_email(
            sender,
            subject,
            body
        )

        category_counts[category] = category_counts.get(category, 0) + 1

        print()
        print(f"EMAIL #{index}")
        print("-" * 70)
        print(f"From     : {sender}")
        print(f"Subject  : {subject}")
        print(f"Date     : {date}")
        print(f"Category : {category}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for category, count in category_counts.items():
        print(f"{category:<20} : {count}")

    print("=" * 70)


if __name__ == "__main__":
    main()