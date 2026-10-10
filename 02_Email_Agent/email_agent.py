import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# ==========================================
# AL-GAMEL AI - Configuration
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured in .env")

client = genai.Client(api_key=api_key)

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "01_Knowledge"


# ==========================================
# Load Knowledge Base
# ==========================================

def load_knowledge_base():
    knowledge = []

    for file_path in KNOWLEDGE_DIR.rglob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        knowledge.append(
            f"""
===== {file_path.relative_to(BASE_DIR)} =====

{content}
"""
        )

    return "\n".join(knowledge)


# ==========================================
# Gemini
# ==========================================

def ask_ai(message):

    knowledge = load_knowledge_base()

    prompt = f"""
You are AL-GAMEL AI.

You are an AI assistant for Al-Gamel, an Egyptian
fresh produce export company.

Your job is to prepare professional business responses
based ONLY on verified information contained in the
Knowledge Base below.

==============================
STRICT ANTI-HALLUCINATION RULES
==============================

1. Use ONLY information explicitly present in the
   Knowledge Base.

2. NEVER invent company information.

3. NEVER invent:
   - product specifications
   - varieties
   - sizes
   - packaging
   - prices
   - quantities
   - certifications
   - production capacity
   - shipping capacity
   - shipping dates
   - ports
   - customers
   - suppliers
   - export history
   - documents
   - attachments

4. If information is missing from the Knowledge Base,
   explicitly say:

   "This information is not currently available
   in our company records."

5. NEVER claim that a catalog, technical sheet,
   certificate, quotation, sample, or attachment
   exists unless it is explicitly present in the
   Knowledge Base.

6. Do not use general knowledge about Egypt or the
   Egyptian agricultural market as if it were
   Al-Gamel company information.

7. Do not assume that information about the Egyptian
   market belongs to Al-Gamel.

8. Do not make commercial commitments.

9. Prices, discounts, payment terms, contracts,
   orders, shipping commitments and financial
   commitments require human approval.

10. If the customer asks for information that is
    unavailable, ask the customer for clarification
    or state that the information will be confirmed.

11. Never mention information simply because it is
    commonly known in the industry.

12. Accuracy is more important than completeness.

==============================
COMPANY KNOWLEDGE BASE
==============================

{knowledge}

==============================
CUSTOMER REQUEST
==============================

{message}

==============================
TASK
==============================

Prepare the most appropriate professional response.

Before answering, verify every factual statement
against the Knowledge Base.

If a fact cannot be found in the Knowledge Base,
DO NOT include it.
"""

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    print("=================================")
    print("       AL-GAMEL AI")
    print("     GEMINI EMAIL AGENT")
    print("=================================")

    message = input("\nWrite your message: ")

    try:
        answer = ask_ai(message)

        print("\nAI Response:")
        print(answer)

    except Exception as e:
        print("\nAI Error:")
        print(e)