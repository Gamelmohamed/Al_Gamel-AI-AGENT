# AL-GAMEL AI Agent

AI assistant for Al-Gamel, an Egyptian fresh produce export company.

The agent can read Gmail, classify emails, extract inquiry data, update the local CRM, and prepare Gmail drafts. It does not send emails automatically.

## What is included

- Email Agent: Gmail reader, classifier, Gemini analyzer, draft generator
- CRM: customers, inquiries, follow-up tracker
- Knowledge base: company profile, products, export process, pricing policy
- Activity log: `06_Logs/agent_activity.jsonl` (created at runtime)

## Requirements

- Python 3.11 or later
- A Gemini API key in `.env`
- Gmail API files `credentials.json` and `token.json` in the project root for Gmail features

## Windows setup

```bat
cd /d D:\AL-GAMEL\AL-GAMEL AI

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
```

Edit `.env` and add your Gemini key:

```
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-3.7-flash
```

Place `credentials.json` in the project root. Do not commit `.env`, `credentials.json`, or `token.json`.

## Windows run commands

```bat
.venv\Scripts\activate

python tests\test_project.py
python tests\test_integration.py

python 03_CRM\crm_manager.py
python 03_CRM\follow_up_manager.py

python 02_Email_Agent\email_classifier.py
python 02_Email_Agent\email_analyzer.py
python 02_Email_Agent\email_draft_generator.py
python 02_Email_Agent\email_agent.py
```

`email_draft_generator.py` creates a Gmail draft only after you type `SAVE`. It does not send the email.

## Safety rules

- No automatic email sending
- Prices, discounts, payment terms, contracts, and order confirmations need human approval
- The agent must not invent prices, specifications, certificates, or shipping facts
