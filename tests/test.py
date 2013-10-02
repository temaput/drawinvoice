#set encoding=utf-8
import unittest
import logging
import sys
from os.path import dirname, pardir, realpath, join, exists
sys.path.insert(0, realpath(join(dirname(__file__), pardir)))
testdir = realpath(join(dirname(__file__), 'result'))
from os import makedirs
if not exists(testdir):
    makedirs(testdir)

logger = logging.getLogger(__name__)

from drawinvoice.simpleinvoice import Invoice
from drawinvoice.sbrfslip import SbrfSlip
from decimal import Decimal as D



class EmptyInvoice(unittest.TestCase):
    def test(self):
        logger.info("====================%s===================================",self.__class__)
        invoice = Invoice(join(testdir,'emptyInvoice.pdf'))
        invoice.write()


class SimpleInvoice(unittest.TestCase):
    customer = dict(
                name=u"""Общество с ограниченной ответственностью "Издательство ГРАНАТ" """,
                address=u"""121471, Москва г, Рябиновая ул, дом №44, кв.1""",
                INN="7729707288",
                KPP="772901001",
                tel="(499)391-48-04",
                )
    beneficiary = dict(
            name = u"ООО {laquo}Издательский дом {laquo}Практика{raquo}".format(
                laquo =  u'\u00AB',
                raquo = u'\u00BB'),
            INN = "7705166992",
            BIK = "044525225",
            correspondentAccount = "30101810400000000225",
            beneficiaryAccount = "40702810138040103580",
            bankName = (u"Сбербанк России ОАО, г.Москва,\n"
                        u"Московский банк Сбербанка России ОАО"),
            address=u"121471, Москва г, Рябиновая ул, дом №44, кв.1",
            manager = u"Ананич Владимир Анатольевич" 
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
        logger.info("====================%s===================================",self.__class__)
        goods = ((lambda i: (self.item, self.item2)[i % 2])(i) for i in range(100))
        invoice = Invoice(join(testdir, 'testInvoice.pdf'))
        invoice.setInvoiceNumber(24)
        invoice.feed(goods = goods)
        invoice.feed(customer=self.customer, beneficiary=self.beneficiary)
        invoice.write()

class CalculationsTest(unittest.TestCase):
    item = dict(
            name = u"""2618.Антимикробная терапия""",
            quantity = 2,
            units = u"шт",
            price = 54.63
            )

    def test(self):
        logger.info("====================%s===================================",self.__class__)
        goods = (self.item for i in range(7))
        invoice = Invoice('/dev/null')
        invoice.feed(goods=goods)
        invoice.write()
        self.assertEqual(invoice.totals.total.quantize(D('0.01')), D('764.82'))
        self.assertEqual(invoice.totals.quantity, 7)
        self.assertEqual(invoice.totals.tax.quantize(D('0.01')), D('116.67'))

class SimpleKvit(unittest.TestCase):
    beneficiary = dict(
            name = u"ООО {laquo}Издательский дом {laquo}Практика{raquo}".format(
                laquo =  u'\u00AB',
                raquo = u'\u00BB'),
            INN = "7705166992",
            BIK = "044525225",
            correspondentAccount = "30101810400000000225",
            beneficiaryAccount = "40702810138040103580",
            bankName = (u"Сбербанк России ОАО, г.Москва, "
                        u"Московский банк Сбербанка России ОАО"),
            address=u"121471, Москва г, Рябиновая ул, дом №44, кв.1",
            manager = u"Ананич Владимир Анатольевич" 
            )
    customer = dict(
            name = u'Путилов Артем Петрович',
            address = u'111402, Аллея Жемчуговой, д.5, корп.4, кв. 187'
            )

    order = dict(
            amount = 2445.21,
            name = u'Оплата заказа №12'
            )
    def test(self):
        logger.info("====================%s===================================",self.__class__)
        kvit = SbrfSlip(join(testdir, 'testKvit.pdf'))
        kvit.feed(customer = self.customer, order=self.order, beneficiary=self.beneficiary)
        kvit.write()

class EmptyKvit(unittest.TestCase):
    def test(self):
        logger.info("====================%s===================================",self.__class__)
        kvit = SbrfSlip(join(testdir, 'testEmptyKvit.pdf'))
        kvit.write()

if __name__ == '__main__':
    unittest.main()

