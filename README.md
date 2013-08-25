drawinvoice
===========

several modules for printing the invoices and sales slips

works with reportlab.py
invocations:
<pre>from drawinvoice import Invoice
invoice = Invoice(filename)
invoice.feed(invoice_data)
invoice.write()</pre>

modules
-------
+ drawinvoice: draws simple invoice form aka 1C
+ drawkvit: draws sales slip for Sberbank RF

