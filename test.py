#set encoding=utf-8
import unittest
from drawinvoice import Invoice
from drawkvit import SbrfKvit
from decimal import Decimal as D

class SimpleInvoice(unittest.TestCase):
    customer = dict(
                name=u"""Общество с ограниченной ответственностью "Издательство ГРАНАТ" """,
                address=u"""121471, Москва г, Рябиновая ул, дом №44, кв.1""",
                INN="7729707288",
                KPP="772901001",
                tel="(499)391-48-04",
                )

    item = dict(
            name = u"""2618.Антимикробная терапия""",
            quantity = 2000,
            units = u"шт",
            price = 54.63
            )
    item2 = dict(
            name = u"""Керамзитобетонные стеновые блоки 390х190х188 с
            прямоугольными пустотами и  квадратными заглотами""",
            quantity = 6000,
            price = 35.63
            )


    def test(self):
        goods = ((lambda i: (self.item, self.item2)[i % 2])(i) for i in range(100))
        invoice = Invoice('testInvoice.pdf')
        invoice.setCustomerRequisites(self.customer)
        invoice.setInvoiceNumber(24)
        invoice.feed(goods)
        invoice.write()

class CalculationsTest(unittest.TestCase):
    item = dict(
            name = u"""2618.Антимикробная терапия""",
            quantity = 2,
            units = u"шт",
            price = 54.63
            )

    def test(self):
        goods = (self.item for i in range(7))
        invoice = Invoice('/dev/null')
        invoice.feed(goods)
        self.assertEqual(invoice.totals.total.quantize(D('0.01')), D('764.82'))
        self.assertEqual(invoice.totals.quantity, 7)
        self.assertEqual(invoice.totals.vat.quantize(D('0.01')), D('116.67'))
        invoice.writeTotals()

class SimpleKvit(unittest.TestCase):
    req = dict(
            name = u'Путилов Артем Петрович',
            address = u'111402, Аллея Жемчуговой, д.5, корп.4, кв. 187'
            )

    payment = dict(
            amount = 2445.21,
            name = u'Оплата заказа №12'
            )
    def test(self):
        kvit = SbrfKvit('testKvit.pdf')
        kvit.feed(self.req, self.payment)
        kvit.write()


if __name__ == '__main__':
    unittest.main()

