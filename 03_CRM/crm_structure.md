# Al-Gamel CRM Structure

## Purpose

This document defines the proposed CRM structure for Al-Gamel.

The CRM will be used by the AI Agent to organize customer information, inquiries, quotations, orders, shipments, follow-ups, and customer history.

---

# 1. Customer Information

Each customer record should contain:

* Customer ID
* Customer Name
* Company Name
* Country
* City
* Email
* Phone
* Website
* Job Title
* Customer Type
* Preferred Contact Method
* Date Added
* Customer Status
* Notes

---

# 2. Customer Type

Possible customer types:

* Importer
* Distributor
* Wholesaler
* Retailer
* Trading Company
* Supermarket
* Other

If the customer type is unknown:

**Unknown**

The AI Agent must not guess the customer type.

---

# 3. Customer Status

Possible statuses:

* New Lead
* Qualified Lead
* Quotation Sent
* Negotiation
* Order Confirmed
* Shipment in Progress
* Delivered
* Repeat Customer
* Inactive
* Lost

---

# 4. Customer Inquiry

Each inquiry should contain:

* Inquiry ID
* Customer ID
* Date Received
* Product
* Variety
* Quantity
* Size / Grade
* Packaging
* Destination
* Required Delivery Date
* Shipping Method
* Incoterm
* Payment Terms
* Required Documents
* Customer Message
* Inquiry Status
* Assigned Person
* Notes

---

# 5. Inquiry Status

Possible statuses:

* New
* Information Required
* Under Review
* Ready for Quotation
* Quotation Prepared
* Quotation Sent
* Customer Responded
* Closed
* Lost

---

# 6. Quotation

Each quotation should contain:

* Quotation ID
* Customer ID
* Inquiry ID
* Quotation Date
* Product
* Variety
* Quantity
* Size / Grade
* Packaging
* Unit Price
* Total Price
* Currency
* Incoterm
* Destination
* Payment Terms
* Quotation Validity
* Status
* Approval Status
* Approved By
* Notes

---

# 7. Quotation Status

Possible statuses:

* Draft
* Pending Approval
* Approved
* Sent
* Under Negotiation
* Accepted
* Rejected
* Expired
* Cancelled

---

# 8. Order

Each confirmed order should contain:

* Order ID
* Customer ID
* Quotation ID
* Order Date
* Product
* Variety
* Quantity
* Size / Grade
* Packaging
* Unit Price
* Total Value
* Currency
* Incoterm
* Destination
* Payment Terms
* Delivery Date
* Order Status
* Notes

---

# 9. Order Status

Possible statuses:

* Pending Approval
* Confirmed
* Preparing
* Ready for Shipment
* Shipped
* Delivered
* Cancelled

---

# 10. Shipment

Each shipment should contain:

* Shipment ID
* Order ID
* Customer ID
* Product
* Quantity
* Shipping Method
* Container / Vehicle Number
* Port of Loading
* Port of Destination
* Freight Forwarder
* Shipping Company
* Estimated Departure
* Actual Departure
* Estimated Arrival
* Actual Arrival
* Tracking Information
* Shipment Status
* Notes

---

# 11. Shipment Status

Possible statuses:

* Planned
* Preparing
* Booked
* Loaded
* In Transit
* Arrived
* Delivered
* Delayed
* Cancelled

---

# 12. Follow-Up

Each follow-up should contain:

* Follow-Up ID
* Customer ID
* Related Inquiry / Quotation / Order
* Follow-Up Date
* Follow-Up Type
* Message
* Response Status
* Next Follow-Up Date
* Responsible Person
* Notes

---

# 13. Communication History

The CRM should record important communications:

* Date
* Customer
* Communication Channel
* Subject
* Message Summary
* Related Inquiry
* Related Quotation
* Related Order
* AI Generated
* Human Approved
* Action Required

Communication channels may include:

* Email
* Phone
* WhatsApp
* Website
* Social Media
* Other

---

# 14. Customer Feedback

After delivery, the CRM may record:

* Product Quality
* Packaging Quality
* Delivery Performance
* Customer Satisfaction
* Complaints
* Suggestions
* Future Requirements

---

# 15. AI Agent Rules

The AI Agent may:

* Create new leads
* Extract customer information from emails
* Create inquiries
* Update inquiry status
* Prepare quotation records
* Schedule follow-ups
* Record communication history
* Update shipment information when verified

The AI Agent must not:

* Delete important customer records without approval
* Change approved prices
* Confirm orders independently
* Modify financial information without approval
* Mark payments as received without verification
* Mark shipments as delivered without verified information

---

# 16. Customer ID

Each customer should have a unique Customer ID.

Example:

AG-CUST-0001

The numbering system may be changed later.

---

# 17. Inquiry ID

Each inquiry should have a unique Inquiry ID.

Example:

AG-INQ-0001

---

# 18. Quotation ID

Each quotation should have a unique Quotation ID.

Example:

AG-QUO-0001

---

# 19. Order ID

Each order should have a unique Order ID.

Example:

AG-ORD-0001

---

# 20. Shipment ID

Each shipment should have a unique Shipment ID.

Example:

AG-SHP-0001

---

# 21. Data Quality

The AI Agent must distinguish between:

* Verified Information
* Customer-Provided Information
* AI Extracted Information
* Estimated Information
* Missing Information

The source of important information should be recorded whenever possible.

---

# 22. Privacy

Customer information is confidential.

The AI Agent must not expose customer information to unauthorized parties.

Sensitive commercial information such as:

* Internal Costs
* Profit Margins
* Supplier Prices
* Internal Discounts
* Internal Commercial Policies

must remain confidential.

---

# 23. Future CRM Integration

The CRM structure may later be implemented using:

* Spreadsheet
* Database
* CRM Software
* Cloud Database
* Custom Web Application

The final implementation will be selected after the Email Agent workflow is completed.
