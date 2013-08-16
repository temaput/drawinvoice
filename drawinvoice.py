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
def writeRequisites(canvas, **kwargs):
    req = Extract(kwargs)
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
    c.drawText(writeName(c, mm, y[1] - normalSize, req.beneficiaryName))

    

    c.restoreState()




writeRequisites(
    c,
    INN = "5028015253",
    KPP = "502801001",
    bankName = u"""Филиал "Краснодарский" ООО КБ "Нэклис-Банк"
    г. КРАСНОДАР""",
    beneficiaryName = u"""ОАО "Можайский полиграфический комбинат"
    (Среднерусский банк ОАО "Сбербанк России")""",
    BIK = "044525225",
    correspondentAccount = "30101810400000000225",
    beneficiaryAccount = "40702810140370172033"
    )

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

from reportlab.platypus import Paragraph, Frame
story = []
f = Frame(x[0], 10*mm, 175*mm, 200*mm, showBoundary=1)
beneficiaryTemplate = u"""Поставщик:&nbsp;&nbsp;&nbsp;&nbsp;<b>{beneficiaryName}, ИНН {INN}, КПП {KPP}, 
        {beneficiaryAddress}, тел.: {beneficiaryTel}</b>"""
payerTemplate = u"""Плательщик:{tab}<b>{payerName}, ИНН {INN}, КПП {KPP},
    {payerAddress}, тел.: {payerTel}"""
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('Arial', normal='Arial', bold='Arial Bold')
from reportlab.lib.styles import getSampleStyleSheet
normalStyle = getSampleStyleSheet()['Normal']
normalStyle.fontName = 'Arial'
normalStyle.leftIndent = 23*mm
normalStyle.firstLineIndent = -23*mm
normalStyle.spaceAfter = normalSize*1.4

txt = beneficiaryTemplate.format(
    INN = "5028015253",
    KPP = "502801001",
    bankName = u"""Филиал "Краснодарский" ООО КБ "Нэклис-Банк"
    г. КРАСНОДАР""",
    beneficiaryName = u"""ОАО "Можайский полиграфический комбинат"
    (Среднерусский банк ОАО "Сбербанк России")""",
    beneficiaryAddress = u"""353250, Краснодарский край, Северский р-н,
    Новодмитриевская ст-ца, Шверника ул, дом №56""",
    beneficiaryTel = "8(861)945-55-11"
    )

story.append(Paragraph(txt, normalStyle))
txt = payerTemplate.format(
        payerName=u"""Общество с ограниченной ответственностью "Издательство ГРАНАТ" """,
        payerAddress=u"""121471, Москва г, Рябиновая ул, дом №44, кв.1""",
        INN="7729707288",
        KPP="772901001",
        payerTel="(499)391-48-04",
        tab="&nbsp;&nbsp;&nbsp;&nbsp;"
        )
story.append(Paragraph(txt, normalStyle))
f.addFromList(story, c)

c.showPage()
c.save()








