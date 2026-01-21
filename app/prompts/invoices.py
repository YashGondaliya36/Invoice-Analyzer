"""
Invoice Processing Prompts.
Contains prompts related to invoice extraction and data parsing.
"""

INVOICE_EXTRACTION_PROMPT = """
Now be serious. I have given you various images of invoices. Your task is to extract all the information from the invoices
and give me the structured output like the below example. Make sure you use entities that are common in all the invoices.

1. Required Fields (Use exact field names):
- "Invoice No" - Extract invoice number/reference exactly as shown
- "Product Name" - Include full product description 
- "Qty" - Convert all quantities to numbers only
- "Amount" - Extract as number only (no currency symbols)
- "Date" - Convert all dates to DD-MM-YY format

2. Quality Control Steps:
- Double-check all extracted values against original
- Verify no data was missed or incorrectly parsed
- Ensure numbers make mathematical sense
- Confirm date is logically valid
- Verify invoice number format is consistent
- ex. Qty : 20.00 -> 20 (keep only integer value)
      amount : 3000.3500 -> 3000.35(keep two digit after .)

Example of structured response:
[
    {"Invoice No": "INV001", "Product Name": "Pipe A", "Qty": 25, "Amount": 3593.10, "Date": "2025-01-01"},
    {"Invoice No": "INV002", "Product Name": "Pipe B", "Qty": 50, "Amount": 3849.76, "Date": "2025-01-02"}
]

IMPORTANT: Return ONLY the JSON array, no other text or markdown formatting.
"""
