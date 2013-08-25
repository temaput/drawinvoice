drawinvoice
===========

several modules for printing the invoices and sales slips

works with reportlab.py
invocations:
<pre>from drawinvoice.simpleinvoice import Invoice
invoice = Invoice(filename)
invoice.feed(invoice_data)
invoice.write()</pre>

modules
-------
+ simpleinvoice: draws simple invoice form aka 1C
+ sprfslip: draws sales slip for Sberbank RF

