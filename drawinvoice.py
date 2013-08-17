#set encoding=utf-8
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4 
from reportlab.pdfgen.canvas import Canvas
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial Bold', 'arialbd.ttf'))
pagesize = A4
width, height = pagesize
normalSize = 9
minSize = 7
bigSize = 12

Warn = u"""Внимание! Оплата данного счета означает согласие с условиями поставки товара. Уедомление об оплате
обязательно. В противном случае не гарантируется наличие товара на складе. Товар отпускается по факту
прихода денег на р/с Поставщика. самовывозом при наличии доверенности и паспорта"""

def setDefaultParams(canvas):
    c = canvas
    c.setFont('Arial', minSize)
    return c

def writeCenteredLine(canvas, y, line):
    c = canvas
    x = width / 2
    c.drawCentredString(x, y, line)

c = Canvas('test.pdf',
        pagesize=pagesize)

c = setDefaultParams(c)

def writeWarn(canvas, warn):
    c = canvas
    c.saveState()
    warnsplit = warn.split('\n')
    count = 1
    start = 285*mm
    for i in warnsplit:
        writeCenteredLine(c, start-count*9, i)
        count += 1
    c.restoreState()

class Extract:
    def __init__(self, dct):
        self.__dict__.update(dct)

writeWarn(c, Warn)

def writeName(canvas, x, y, name):
    text = c.beginText()
    text.setTextOrigin(x, y)
    text.setLeading(normalSize + 1)
    text.textLines(name)
    return text
def writeRequisites(canvas, requisites):
    req = Extract(requisites)
    c = canvas
    c.saveState()
    c.translate(10*mm, 235*mm)
    x = (0, 43*mm, 86*mm, 100*mm, 175*mm)
    y = (0, 11*mm, 15*mm, 21*mm, 25*mm)
    c.grid((x[0], x[2], x[3], x[4]), (y[0], y[2], y[4]))
    c.grid((x[0], x[1], x[2]), (y[1], y[2]))
    c.line(x[2], y[3], x[3], y[3])
    c.drawString(mm, y[2] + mm, u"Банк получателя")
    c.drawString(mm, mm, u"Получатель")
    c.setFontSize(normalSize)
    c.drawString(x[2] + mm, y[3] - normalSize, u"Сч. №")
    c.drawString(x[2] + mm, y[2] - normalSize, u"Сч. №")
    c.drawString(mm, y[1]+0.5*mm, u"ИНН   %s" % req.INN)
    c.drawString(x[1] + mm, y[1]+0.5*mm, u"КПП   %s" % req.KPP)
    c.drawString(x[2] + mm, y[3] + mm, u"БИК")
    c.drawString(x[3] + mm, y[3] + mm, req.BIK)
    c.drawString(x[3] + mm, y[3] - normalSize, req.correspondentAccount)
    c.drawString(x[3] + mm, y[2] - normalSize, req.beneficiaryAccount)
    c.drawText(writeName(c, mm, y[-1] - normalSize, req.bankName))
    c.drawText(writeName(c, mm, y[1] - normalSize, req.name))

    

    c.restoreState()

beneficiary = dict(
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
    tel = u"8(861)945-55-11"
    )


writeRequisites(c, beneficiary)

x = (10*mm, width / 2, 185*mm)
def writeInvoiceTitle(canvas, invoiceNum):
    c = canvas
    c.saveState()
    c.setFont('Arial Bold', bigSize)
    from datetime import date as d
    import locale
    locale.resetlocale()
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    c.drawString(x[0], 225*mm,
        u"Счет на оплату №%s от %s" % (invoiceNum, d.today().strftime("%x")))
    c.setLineWidth(0.5*mm)
    c.line(x[0], 222*mm, x[-1], 222*mm)
    c.restoreState()

writeInvoiceTitle(c, 63)

from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('Arial', normal='Arial', bold='Arial Bold')
from reportlab.platypus import Paragraph, Frame
f = Frame(x[0], 10*mm, 175*mm, 210*mm, showBoundary=True)
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
pStyle = getSampleStyleSheet()['Normal']
pStyle.fontName = 'Arial'

def writeMembers(customer):
    memberTemplate = u"""<b>{name}, ИНН {INN}, КПП {KPP},
        {address}, тел.: {tel}</b>""" 

    beneficiaryData = memberTemplate.format(**beneficiary)
    customerData = memberTemplate.format(**customer)

    data = (
            (u"Поставщик:", Paragraph(beneficiaryData, pStyle)),
            (u"Покупатель:", Paragraph(customerData, pStyle))
            )
    memberTableStyle = TableStyle(
            [('FONTNAME',(0,0), (-1,-1), "Arial"),
            ('VALIGN', (0,0), (0,-1), "TOP"),
            ('ALIGN', (0,0), (0,-1), "LEFT"),
            ])

    t = Table(data, colWidths=(30*mm, 145*mm))
    t.setStyle(memberTableStyle)
    return t

customer = dict(
            name=u"""Общество с ограниченной ответственностью "Издательство ГРАНАТ" """,
            address=u"""121471, Москва г, Рябиновая ул, дом №44, кв.1""",
            INN="7729707288",
            KPP="772901001",
            tel="(499)391-48-04",
            )
membersTable = writeMembers(customer)

item = dict(
        name = u"""2618.Антимикробная терапия""",
        amount = "{:d}".format(2000),
        units = u"шт",
        price = "{:.2f}".format(54.92),
        total = "{:.2f}".format(109840)
        )
goodsTableStyle = TableStyle(
        (('FONTNAME', (0,0), (-1,-1), "Arial"),
        ('FONTNAME', (0,0), (-1,0), "Arial Bold"),
        ('FONTSIZE', (0,1), (-1, -1), minSize),
        ('ALIGN', (0,0), (-1, 0), "CENTRE"),
        ('ALIGN', (0,1), (0,-1), "CENTRE"),
        ('ALIGN', (2,1), (2,-1), "RIGHT"),
        ('ALIGN', (4,1), (-1,-1), "RIGHT"),
        ('INNERGRID', (0,0), (-1,-1), 1, colors.black),
        ('BOX', (0,0), (-1,-1), 2, colors.black))
        )

def writeGoods(goods):
    header = (u"№", u"Товары (работы, услуги)", u"Кол-во", u"Ед.", u"Цена", u"Сумма")
    goodsTable = []
    goodsTable.append(header)
    i = 1
    pStyle.fontSize = minSize
    for item in goods:
        item = Extract(item)
        goodsTable.append((i, Paragraph(item.name, pStyle), item.amount, item.units, item.price, item.total))
        i += 1
    t = Table(goodsTable, colWidths=(10*mm, 100*mm, 15*mm, 8*mm, 17*mm, 25*mm))
    t.setStyle(goodsTableStyle)
    return t

goods = (item for i in range(100))
goodsTable = writeGoods(goods)

totalsTableStyle = TableStyle((
    ('FONTNAME', (0, 0), (-1, -1), "Arial Bold"),
    ('FONTNAME', (0, 3), (0, 3), "Arial"),
    ('ALIGN', (1,0), (-1, -1), "RIGHT"),
    ('ALIGN', (0,0), (0, -1), "LEFT")
    ))
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

def writeTotals(amount, total, vat, due=None):
    due = due or total
    amountTemplate = u"Всего наименований {amount}, на сумму {due:.2f} руб."
    totalsTable = (
            ("", u"Итого:", '{:.2f}'.format(total)),
            ("", u"В том числе НДС:", '{:.2f}'.format(vat)),
            ("", u"Всего к оплате:", '{:.2f}'.format(due)),
            (amountTemplate.format(amount=amount, due=due),"",""),
            (spellTotal(due), "", "")
            )
    return Table(totalsTable, 
            colWidths=(125*mm, 30*mm, 20*mm), 
            style=totalsTableStyle)

totalsTable = writeTotals(2, 109840, 16755.25)

signaturesTableStyle = TableStyle((
    ('FONTNAME', (0,0), (0,0), "Arial Bold"),
    ('FONTNAME', (2,0), (2,0), "Arial Bold"),
    ('FONTNAME', (1,0), (1,0), "Arial"),
    ('FONTNAME', (3,0), (3,0), "Arial"),
    ('ALIGN', (0,0), (0,0), "LEFT"),
    ('ALIGN', (2,0), (2,0), "LEFT"),
    ('ALIGN', (1,0), (1,0), "RIGHT"),
    ('ALIGN', (3,0), (3,0), "RIGHT"),
    ('FONTSIZE', (1,0), (1,0), minSize),
    ('FONTSIZE', (3,0), (3,0), minSize),
    ('LINEABOVE', (0,0), (-1,0), 2, colors.black),
    ('LINEBELOW', (1,0), (1,0), 1, colors.black),
    ('LINEBELOW', (3,0), (3,0), 1, colors.black)
    ))
manager = u"Сысоев В.С."
accountant = manager
signaturesTable = Table(
        ((u"Руководитель", manager, u"Бухгалтер", accountant),),
        colWidths = (25*mm, 70*mm, 20*mm, 60*mm),
        style = signaturesTableStyle)
from reportlab.platypus import Spacer
f.addFromList([
    membersTable, 
    Spacer(0, normalSize), 
    goodsTable, 
    totalsTable, 
    Spacer(0, minSize),
    signaturesTable], c)

c.showPage()
c.save()

from reportlab.platypus import BaseDocTemplate
class InvoiceDataMixin:
    """Manages requisites and calculations for invoice"""
    def writeHead(self): pass

class Parameters: pass

class Invoice(BaseDocTemplate, InvoiceDataMixin):
    """draws the invoice"""
    def setParams(self):
        self.pagesize = A4
        self.leftMargin = 15*mm
        self.bottomMargin = 10*mm
        self.rightMargin = 20*mm
        self.topMargin = 10*mm
        p = Parameters()
        p.baseFont = "Arial"
        p.tablePadding = 1

        self.param = p
        self._calc()
    def afterInit(self):
        self.setParams()
        firstFrame = Frame(self.leftMargin, self.bottomMargin, 
            self.param.firstFrameWidth, self.param.firstFrameHeight,
            id='first')
        laterFrame = Frame(self.leftMargin, self.bottomMargin, 
            self.width, self.height, id='later')
        from reportlab.platypus import PageTemplate
        self.addPageTemplates((
            PageTemplate(id='First', frames=firstFrame, onPage=self.writeHead,
                pagesize=self.pagesize),
            PageTemplate(id='Later', frames=laterFrame, pagesize=self.pagesize)
            ))
    def setupTableStyles(self):
        base = TableStyle((
            ('FONTNAME', (0,0), (-1,-1), self.param.baseFont),
            ('LEFTPADDING', (0,0), (-1,-1), self.param.tablePadding),
            ('RIGHTPADDING', (0,0), (-1,-1),self.param.tablePadding),
            ('BOTTOMPADDING', (0,0), (-1,-1), self.param.tablePadding),
            ('TOPPADDING', (0,0), (-1,-1), self.param.tablePadding)
            ))

    def writeHead(self): pass
story = [
    membersTable, 
    Spacer(0, normalSize), 
    goodsTable, 
    totalsTable, 
    Spacer(0, minSize),
    signaturesTable]





