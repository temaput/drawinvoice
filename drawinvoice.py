#set encoding=utf-8
from collections import namedtuple

from reportlab.platypus import PageTemplate
from reportlab.platypus import Frame
from reportlab.lib.units import mm
from reportlab.platypus import Table
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import BaseDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.pagesizes import A4 
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

class Extract:
    def __init__(self, dct):
        self.__dict__.update(dct)

Line = namedtuple("Line", 
        ('position', 'name', 'quantity', 'units', 'price', 'amount'))


class Parameters: pass


class InvoiceDataMixin:
    """Manages requisites and calculations for invoice"""

    warn = u"""Внимание! Оплата данного счета означает согласие с условиями поставки товара. Уедомление об оплате
    обязательно. В противном случае не гарантируется наличие товара на складе. Товар отпускается по факту
    прихода денег на р/с Поставщика. самовывозом при наличии доверенности и паспорта"""

    req = Parameters()
    req.beneficiary = dict(
        INN = "5028015253",
        KPP = "502801001",
        bankName = u"""Филиал "Краснодарский" ООО КБ "Нэклис-Банк"
        г. КРАСНОДАР""",
        name = u"""ОАО "Можайский полиграфический комбинат"
        (Среднерусский банк ОАО "Сбербанк России")""",
        BIK = "044525225",
        correspondentAccount = "30101810400000000225",
        beneficiaryAccount = "40702810140370172033",
        address = u"""353250, Краснодарский край, Северский р-н,
        Новодмитриевская ст-ца, Шверника ул, дом №56""",
        tel = u"8(861)945-55-11",
        manager = u"Сысоев В.И."
        )

    def setCustomerRequisites(self, customer):
        self.req.customer = {}
        self.req.customer.update(customer)

    def setInvoiceNumber(self, num):
        self.req.invoiceNumber = str(num)

    def feed(self, goods):
        i= 0
        total = 0
        self.goods = []
        for item in goods:
            i += 1
            units = item.get('units', None) or u'шт'
            item = Extract(item)
            amount = item.price * item.quantity
            line = Line(i, item.name, item.quantity, units, item.price, amount)
            self.goods.append(line)
            total += amount
        self.totals = Parameters()
        self.totals.total = total
        self.totals.amount = i
        self.totals.vat = self.getVat(goods)
        self.totals.due = self.getDue(goods)

    def getVat(self, goods):
        return self.totals.total / 118.00 * 18
    def getDue(self, goods):
        return None

debug = False

class Invoice(InvoiceDataMixin):
    """draws the invoice"""
    def __init__(self, filename):
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial Bold', 'arialbd.ttf'))
        registerFontFamily('Arial', normal='Arial', bold='Arial Bold')
        self.filename = filename
        self.setParams()

    def setParams(self):
        p = Parameters()
        p.baseFont = "Arial"
        p.tablePadding = 1
        p.normalSize = 9
        p.minSize = 8
        p.bigSize = 14

        p.firstFrameWidth = 175*mm
        p.firstFrameHeight = 210*mm
        p.lineColor = colors.black

        p.normalStyle = getSampleStyleSheet()['Normal']
        p.normalStyle.fontName = p.baseFont

        p.minStyle = getSampleStyleSheet()['Normal']
        p.minStyle.fontName = p.baseFont
        p.minStyle.fontSize = p.minSize
        p.minStyle.leading = p.minSize * 1.2

        self.param = p
        self.setupDoc()
        self.setupTableStyles()
        self.setupTemplates()

    def setupTemplates(self):
        self.templates = Parameters()
        self.templates.memberTemplate = u"""<b>{name}, ИНН {INN}, КПП {KPP},
                {address}, тел.: {tel}</b>""" 

        def itemTemplate(item):
            pStyle = self.param.minStyle
            return Line(
                    item.position,
                    Paragraph(item.name, pStyle),
                    "{:d}".format(item.quantity),
                    item.units,
                    "{:.2f}".format(item.price),
                    "{:.2f}".format(item.amount)
                    )
        self.templates.itemTemplate = itemTemplate

        self.templates.amountTemplate = lambda amount, due: Paragraph(
                u"Всего наименований {amount}, на сумму {due:.2f} руб.".format(
                    amount=amount, due=due), self.param.normalStyle)

        def spellTotal(total):
            template = u"{rubles} {kopnum:02d} {kopstr}"
            from pytils import numeral
            n = {}
            n['rubles'] = numeral.rubles(int(total)).capitalize()
            n['kopnum'] = int(total * 100) - int(total)*100
            n['kopstr'] = numeral.choose_plural(
                    n['kopnum'], 
                    (u"копейка", u"копейки", u"копеек")
                    )
            return template.format(**n)

        self.templates.spellTotal = lambda due: Paragraph(
                u"<b>{}</b>".format(spellTotal(due)), 
                self.param.normalStyle)


    def setupDoc(self):
        self.doc = BaseDocTemplate(
            self.filename,
            pagesize = A4,
            leftMargin = 15*mm,
            bottomMargin = 10*mm,
            rightMargin = 20*mm,
            topMargin = 10*mm
            )

        firstFrame = Frame(self.doc.leftMargin, self.doc.bottomMargin, 
            self.param.firstFrameWidth, self.param.firstFrameHeight,
            id='first', showBoundary=debug)
        laterFrame = Frame(self.doc.leftMargin, self.doc.bottomMargin, 
            self.doc.width, self.doc.height, id='later')

        def changeTemplate(canvas, document):
            document.handle_nextPageTemplate('Later')

        def writeHead(canvas, document):
            self.writeHead(canvas)

        self.doc.addPageTemplates((
            PageTemplate(id='First', frames=firstFrame, onPage=writeHead,
                onPageEnd=changeTemplate),
            PageTemplate(id='Later', frames=laterFrame)
            ))

    def setupTableStyles(self):
        from reportlab.platypus import TableStyle
        base = TableStyle((
            ('FONTNAME', (0,0), (-1,-1), self.param.baseFont),
            ('LEFTPADDING', (0,0), (-1,-1), self.param.tablePadding + 1),
            ('RIGHTPADDING', (0,0), (-1,-1),self.param.tablePadding + 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), self.param.tablePadding),
            ('TOPPADDING', (0,0), (-1,-1), self.param.tablePadding),
            ('VALIGN', (0,0), (-1,-1), "BOTTOM")
            ))
        self.param.signaturesTableStyle = TableStyle((
            ('FONTNAME', (0,0), (0,0), "Arial Bold"),
            ('FONTNAME', (2,0), (2,0), "Arial Bold"),
            ('FONTNAME', (1,0), (1,0), "Arial"),
            ('FONTNAME', (3,0), (3,0), "Arial"),
            ('ALIGN', (0,0), (0,0), "LEFT"),
            ('ALIGN', (2,0), (2,0), "LEFT"),
            ('ALIGN', (1,0), (1,0), "RIGHT"),
            ('ALIGN', (3,0), (3,0), "RIGHT"),
            ('FONTSIZE', (1,0), (1,0), self.param.minSize),
            ('FONTSIZE', (3,0), (3,0), self.param.minSize),
            ('LINEABOVE', (0,0), (-1,0), 2, self.param.lineColor),
            ('LINEBELOW', (1,0), (1,0), 1, self.param.lineColor),
            ('LINEBELOW', (3,0), (3,0), 1, self.param.lineColor),
            ('TOPPADDING', (0,0), (0,-1), 5 * mm),
            ('LEFTPADDING', (2,0), (2,0), 10*mm)
            ), parent=base)
        self.param.totalsTableStyle = TableStyle((
            ('TOPPADDING', (0,0), (-1, 0), 3*mm),
            ('FONTNAME', (0, 0), (-1, -1), "Arial Bold"),
            ('ALIGN', (1,0), (-1, -1), "RIGHT"),
            ), parent=base)
        self.param.goodsTableStyle = TableStyle(
            (('FONTNAME', (0,0), (-1,-1), "Arial"),
            ('FONTNAME', (0,0), (-1,0), "Arial Bold"),
            ('FONTSIZE', (0,1), (-1, -1), self.param.minSize),
            ('LEADING', (0,1), (-1, -1), self.param.minSize * 1.2),
            ('ALIGN', (0,0), (-1, 0), "CENTRE"),
            ('ALIGN', (0,1), (0,-1), "CENTRE"),
            ('ALIGN', (2,1), (2,-1), "RIGHT"),
            ('ALIGN', (4,1), (-1,-1), "RIGHT"),
            ('INNERGRID', (0,0), (-1,-1), 1, self.param.lineColor),
            ('BOX', (0,0), (-1,-1), 2, self.param.lineColor)), parent=base)
        self.param.memberTableStyle = TableStyle((
                ('FONTNAME',(0,0), (-1,-1), "Arial"),
                ('VALIGN', (0,0), (0,-1), "TOP"),
                ('BOTTOMPADDING', (0,0), (-1, 0), 4 * mm),
                ('ALIGN', (0,0), (0,-1), "LEFT")
                ), parent=base)

    def writeHead(self, canvas): 

        canvas.setFont(self.param.baseFont, self.param.normalSize)

        def writeWarn(warn):
            c = canvas
            c.saveState()
            c.setFontSize(self.param.minSize)
            warnsplit = warn.split('\n')
            count = 1
            start = 275*mm
            x = self.doc.pagesize[0] / 2
            for line in warnsplit:
                y = start-count*self.param.minSize
                c.drawCentredString(x, y, line)
                count += 1
            c.restoreState()

        writeWarn(self.warn)

        def writeName(x, y, name):
            c = canvas
            text = c.beginText()
            text.setTextOrigin(x, y)
            text.setLeading(self.param.normalSize + 1)
            text.textLines(name)
            return text

        def writeRequisites(requisites):
            req = Extract(requisites)
            c = canvas
            c.saveState()
            c.translate(self.doc.leftMargin, 235*mm)
            x = (0, 43*mm, 86*mm, 100*mm, 175*mm)
            y = (0, 11*mm, 15*mm, 21*mm, 25*mm)
            c.grid((x[0], x[2], x[3], x[4]), (y[0], y[2], y[4]))
            c.grid((x[0], x[1], x[2]), (y[1], y[2]))
            c.line(x[2], y[3], x[3], y[3])
            c.setFontSize(self.param.minSize)
            c.drawString(mm, y[2] + mm, u"Банк получателя")
            c.drawString(mm, mm, u"Получатель")
            c.setFontSize(self.param.normalSize)
            c.drawString(x[2] + mm, y[3] - self.param.normalSize, u"Сч. №")
            c.drawString(x[2] + mm, y[2] - self.param.normalSize, u"Сч. №")
            c.drawString(mm, y[1]+0.5*mm, u"ИНН   %s" % req.INN)
            c.drawString(x[1] + mm, y[1]+0.5*mm, u"КПП   %s" % req.KPP)
            c.drawString(x[2] + mm, y[3] + mm, u"БИК")
            c.drawString(x[3] + mm, y[3] + mm, req.BIK)
            c.drawString(x[3] + mm, y[3] - self.param.normalSize, req.correspondentAccount)
            c.drawString(x[3] + mm, y[2] - self.param.normalSize, req.beneficiaryAccount)
            c.drawText(writeName(mm, y[-1] - self.param.normalSize, req.bankName))
            c.drawText(writeName(mm, y[1] - self.param.normalSize, req.name))
            c.restoreState()


        writeRequisites(self.req.beneficiary)

        x = (self.doc.leftMargin, self.doc.width / 2, self.doc.pagesize[0] - self.doc.rightMargin)

        def writeInvoiceTitle(invoiceNum):
            c = canvas
            c.saveState()
            c.setFont('Arial Bold', self.param.bigSize)
            from datetime import date as d
            import locale
            locale.resetlocale()
            locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
            c.drawString(x[0], 225*mm,
                u"Счет на оплату №%s от %s" % (invoiceNum, d.today().strftime("%x")))
            c.setLineWidth(0.5*mm)
            c.line(x[0], 222*mm, x[-1], 222*mm)
            c.restoreState()

        writeInvoiceTitle(self.req.invoiceNumber)



#========================================
    def writeSignatures(self):
        manager = self.req.beneficiary['manager']
        accountant = manager
        signaturesTable = Table(
                ((u"Руководитель", manager, u"Бухгалтер", accountant),),
                colWidths = (29*mm, 61*mm, 30*mm, 55*mm),
                style = self.param.signaturesTableStyle)
        self.story.append(signaturesTable)

    def writeMembers(self):
        beneficiaryData = self.templates.memberTemplate.format(**self.req.beneficiary)
        customerData = self.templates.memberTemplate.format(**self.req.customer)
        data = (
                (u"Поставщик:", Paragraph(beneficiaryData, self.param.normalStyle)),
                (u"Покупатель:", Paragraph(customerData, self.param.normalStyle))
                )
        self.story.append(Table(data, 
                colWidths=(30*mm, 145*mm),
                style=self.param.memberTableStyle))

    def writeGoods(self):
        header = (u"№", u"Товары (работы, услуги)", u"Кол-во", u"Ед.", u"Цена", u"Сумма")
        goodsTable = [self.templates.itemTemplate(item) for item in self.goods]
        goodsTable.insert(0, header)

        t = Table(goodsTable, colWidths=(10*mm, 100*mm, 15*mm, 8*mm, 17*mm, 25*mm))
        t.setStyle(self.param.goodsTableStyle)
        self.story.append(t)

    def writeTotals(self):
        amount = self.totals.amount
        total = self.totals.total
        vat = self.totals.vat
        due = self.totals.due or total
        totalsTable = (
                ("", u"Итого:", '{:.2f}'.format(total)),
                ("", u"В том числе НДС:", '{:.2f}'.format(vat)),
                ("", u"Всего к оплате:", '{:.2f}'.format(due)),
                )
        t = Table(totalsTable, 
                colWidths=(125*mm, 25*mm, 25*mm), 
                style=self.param.totalsTableStyle)
        self.story.append(t)
        self.story.append(self.templates.amountTemplate(amount, due))
        self.story.append(self.templates.spellTotal(due))

    def write(self):
        spacer = Spacer(0, self.param.normalSize)
        self.story = []
        self.writeMembers()
        self.story.append(spacer)
        self.writeGoods()
        self.writeTotals()
        self.story.append(spacer)
        self.writeSignatures()
        self.doc.build(self.story)

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

goods = ((lambda i: (item, item2)[i % 2])(i) for i in range(100))

invoice = Invoice('invoice.pdf')
invoice.setCustomerRequisites(customer)
invoice.setInvoiceNumber(24)
invoice.feed(goods)
invoice.write()






