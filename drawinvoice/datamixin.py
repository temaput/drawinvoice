#set encoding=utf-8
from decimal import Decimal as D
from decimal import getcontext
from babel.numbers import format_decimal

class Extract:
    def __init__(self, dct):
        self.__dict__.update(dct)
    def __getattr__(self, _):
        return ""


class Parameters: pass

def getVat(amount):
    return amount / D('118.00') * D('18')

def getTax(amount, item=None):
    tax = None
    if item:
        tax = item.get('tax', None)
    if tax is None:
        return getVat(amount)
    return tax

class Item(object):
    def __init__(self, item, pos=None):
        self.units = item.get('units', None) or u'шт'
        self.price = D(item.get('price', 0))
        self.quantity = D(item.get('quantity', 0))
        self.amount =  D(item.get('amount', 0))
        if not self.amount and self.price and self.quantity:
            self.amount = self.price * self.quantity
        elif not self.price and self.amount and self.quantity:
            self.price = self.amount / self.quantity
        elif not self.quantity and self.price and self.amount:
            self.quantity = D(self.amount / self.price).quantize(0)
        self.tax = getTax(self.amount, item)
        self.name = item.get('name', '')
        self.position = pos



class DataMixin(object):
    """Manages requisites and calculations for invoice"""

    def __init__(self):
        self.data = Parameters()
        self.data.invoiceNumber = ""
        self.data.beneficiary = {}
        self.data.customer = {}
        self.data.order = {}

        self.goods = []
        self.totals = Parameters()


    def setInvoiceNumber(self, num):
        self.data.invoiceNumber = str(num)

    def parseGoods(self):
        i= 0
        total = D(0)
        for item in self.data.goods:
            i += 1
            line = Item(item, pos=i)
            self.goods.append(line)
            total += line.amount
        self.totals.total = total
        self.totals.quantity = i
        self.totals.tax = getTax(total, self.data.order)
        self.totals.due = None


    def feed(self, **kwargs):
        self.data.__dict__.update(kwargs)
        if 'goods' in kwargs:
            self.parseGoods()
        if 'order' in kwargs:
            if not self.data.invoiceNumber:
                self.data.invoiceNumber = self.data.order.get('number', '')


