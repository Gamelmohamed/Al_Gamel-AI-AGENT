# Al-Gamel Email Agent Workflow

## Purpose

This document defines how the Al-Gamel AI Email Agent should process incoming and outgoing emails.

The AI Agent should analyze customer emails, extract relevant information, update the CRM, prepare appropriate responses, and request human approval when required.

---

# 1. New Email Received

When a new email arrives, the AI Agent should:

1. Identify the sender.
2. Identify the sender's company.
3. Identify the email subject.
4. Read and understand the message.
5. Identify whether the email is business-related.
6. Determine whether it is a new inquiry or an existing conversation.
7. Search the CRM for the sender or company.
8. Create or update the customer record.
9. Create or update the related inquiry.

---

# 2. Email Classification

The AI Agent should classify incoming emails into categories such as:

* New Customer Inquiry
* Existing Customer Inquiry
* Product Request
* Price Request
* Quotation Response
* Negotiation
* Order Confirmation
* Shipment Inquiry
* Documentation Request
* Complaint
* Follow-Up
* General Business Communication
* Spam / Irrelevant
* Unknown

If the category is uncertain, the AI Agent should flag the email for human review.

---

# 3. Information Extraction

For customer inquiries, the AI Agent should extract:

* Customer Name
* Company Name
* Country
* City
* Email
* Phone
* Product
* Variety
* Quantity
* Size
* Grade
* Packaging
* Destination
* Delivery Date
* Shipping Method
* Incoterm
* Payment Terms
* Required Documents
* Other Requirements

The AI Agent must preserve the customer's original information.

---

# 4. Missing Information Detection

The AI Agent should compare the extracted information with the requirements defined in:

`customer_requirements.md`

If critical information is missing, the AI Agent should:

1. Identify the missing information.
2. Create a clarification draft.
3. Update the CRM.
4. Request human approval if required.
5. Send the email only according to the approved automation policy.

The AI Agent must not guess missing information.

---

# 5. Product Verification

The AI Agent should compare the customer's requested product against:

`products.md`

It should verify:

* Product availability
* Season
* Variety
* Size
* Packaging
* MOQ
* Shipping method

If information is unavailable, the AI Agent should mark it as:

**To Be Confirmed**

The AI Agent must never invent product specifications.

---

# 6. Customer Qualification

The AI Agent should determine whether the customer appears to be:

* Importer
* Distributor
* Wholesaler
* Retailer
* Trading Company
* Other

It should also identify:

* New or existing customer
* Potential recurring requirement
* Requested products
* Destination market
* Estimated order frequency

The AI Agent should not make unsupported assumptions.

---

# 7. Pricing Request

If the customer requests a price, the AI Agent should:

1. Extract all available requirements.
2. Check product information.
3. Check MOQ.
4. Identify destination.
5. Identify packaging.
6. Identify shipping requirements.
7. Identify Incoterm.
8. Identify payment terms.
9. Collect available cost information.
10. Prepare a draft quotation.

The AI Agent must not send a price without the required human approval.

---

# 8. Quotation Preparation

The AI Agent may prepare a quotation containing:

* Customer
* Product
* Variety
* Quantity
* Size / Grade
* Packaging
* Price
* Currency
* Incoterm
* Destination
* Payment Terms
* Quotation Validity
* Delivery Information

The quotation should be marked:

**DRAFT – PENDING HUMAN APPROVAL**

until approved.

---

# 9. Human Approval

Human approval is required before sending emails containing:

* Prices
* Discounts
* Payment Terms
* Contracts
* Order Confirmations
* Commercial Commitments
* Shipping Commitments
* Important Legal or Financial Information

The approval workflow should be:

Email Received
→ AI Analysis
→ Draft Prepared
→ Human Review
→ Approved / Rejected
→ Send / Modify

---

# 10. Routine Emails

Some routine emails may eventually be automated after the company approves the automation policy.

Possible examples:

* Acknowledgment of receiving an inquiry
* Request for basic missing information
* Follow-up reminders
* Shipment status notifications based on verified data

Automatic sending should only be enabled after testing and approval.

---

# 11. Existing Customer Email

If the sender already exists in the CRM, the AI Agent should:

1. Match the email to the existing customer.
2. Retrieve relevant customer history.
3. Identify the related inquiry, quotation, order, or shipment.
4. Update the communication history.
5. Prepare the appropriate response.

The AI Agent should avoid creating duplicate customer records.

---

# 12. New Customer

If the sender does not exist in the CRM:

1. Create a new Lead.
2. Assign a Customer ID.
3. Extract available customer information.
4. Create the related inquiry.
5. Classify the lead.
6. Prepare the appropriate response.

Example Customer ID:

`AG-CUST-0001`

---

# 13. Email Thread Management

The AI Agent should understand email conversations as threads.

It should maintain:

* Original inquiry
* Customer replies
* Al-Gamel replies
* Quotation
* Negotiation
* Follow-ups
* Final outcome

The AI Agent should avoid losing context between messages.

---

# 14. Attachments

If an email contains attachments, the AI Agent should identify:

* File name
* File type
* Document type
* Related customer
* Related inquiry / quotation / order

Possible documents include:

* Purchase Order
* Product Specification
* Company Profile
* Certificate
* Packing Requirements
* Shipping Documents

The AI Agent must not treat an attachment as authentic or verified unless it has been reviewed or comes from a trusted source.

---

# 15. Email Attachments With Commercial Information

If an attachment contains:

* Purchase Order
* Contract
* Price Agreement
* Payment Terms
* Shipping Instructions

the AI Agent should flag it for human review.

It must not independently accept or confirm the document.

---

# 16. Customer Complaints

If an email appears to contain a complaint, the AI Agent should:

1. Identify the complaint.
2. Identify the affected order or shipment.
3. Record the complaint in the CRM.
4. Extract relevant facts.
5. Prepare a professional acknowledgment.
6. Escalate the complaint to the responsible person.

The AI Agent must not admit liability or offer compensation without approval.

---

# 17. Shipment Requests

If a customer asks for shipment information, the AI Agent should check verified shipment data.

It may provide:

* Shipment Status
* Estimated Departure
* Estimated Arrival
* Tracking Information

The AI Agent must not invent shipment updates.

---

# 18. Unknown or Suspicious Emails

If an email appears suspicious, fraudulent, irrelevant, or unclear:

* Do not provide sensitive company information.
* Do not open suspicious links automatically.
* Do not send confidential documents.
* Flag the email for human review.

---

# 19. Email Priority

The AI Agent should assign priority:

### High Priority

* New customer price request
* Order confirmation
* Contract
* Payment issue
* Shipment problem
* Customer complaint
* Urgent delivery issue

### Medium Priority

* Product inquiry
* Quotation follow-up
* Documentation request
* Existing customer request

### Low Priority

* General inquiry
* Marketing email
* Non-urgent communication

---

# 20. CRM Synchronization

Important email events should update the CRM.

Examples:

New inquiry
→ Create Lead / Inquiry

Quotation sent
→ Update Quotation Status

Customer accepts quotation
→ Update status to Pending Human Approval

Order approved
→ Create Order

Shipment created
→ Create Shipment

Customer feedback
→ Update Customer Record

---

# 21. Email Logging

Important email actions should be recorded in:

`06_Logs`

The log may contain:

* Date
* Time
* Sender
* Customer
* Email Subject
* Email Type
* AI Action
* Human Approval
* Final Action
* Status
* Error, if any

---

# 22. AI Safety Rules

The Email Agent must follow these rules:

1. Never invent information.
2. Never invent prices.
3. Never invent shipment status.
4. Never fabricate documents.
5. Never expose confidential information.
6. Never accept contracts independently.
7. Never confirm orders independently.
8. Never make financial commitments.
9. Never approve discounts independently.
10. Ask for clarification when information is missing.
11. Clearly distinguish verified information from assumptions.
12. Keep an audit trail of important actions.

---

# 23. Main Workflow

The complete workflow is:

New Email
↓
Identify Sender
↓
Search CRM
↓
Classify Email
↓
Extract Information
↓
Identify Missing Information
↓
Check Product Knowledge
↓
Update CRM
↓
Determine Required Action
↓
Prepare Response
↓
Human Approval if Required
↓
Send Email
↓
Update CRM
↓
Log Action

---

# 24. Human-in-the-Loop Principle

The AI Agent is an assistant, not the final decision maker.

The AI Agent should:

**Read → Understand → Extract → Analyze → Prepare → Ask for Approval → Execute**

The responsible person at Al-Gamel remains responsible for:

* Prices
* Commercial terms
* Discounts
* Contracts
* Orders
* Payments
* Financial commitments
* Major customer decisions
