#set encoding=utf-8
from collections import namedtuple
from decimal import Decimal as D
from datetime import date

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
#from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.pagesizes import A4 
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

class Parameters: pass

debug = True

class SbrfSlip:
    def __init__(self, filename):
        self.canvas = Canvas(filename)
        pdfmetrics.registerFont(TTFont('Ubuntu', 'UbuntuMono-R.ttf'))
        pdfmetrics.registerFont(TTFont('Ubuntu Bold', 'UbuntuMono-B.ttf'))
        pdfmetrics.registerFont(TTFont('Ubuntu Italic', 'UbuntuMono-RI.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSansMono.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu Bold', 'DejaVuSansMono-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu Italic', 'DejaVuSansMono-Oblique.ttf'))
        pdfmetrics.registerFont(TTFont('Arial Bold', 'arialbd.ttf'))
        pdfmetrics.registerFont(TTFont('Arial Italic', 'ariali.ttf'))
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial Bold', 'arialbd.ttf'))
        pdfmetrics.registerFont(TTFont('Arial Italic', 'ariali.ttf'))
        #registerFontFamily('Arial', normal='Arial', bold='Arial Bold')
        self.debug = debug
        self.setParams()

    def setParams(self):
        p = Parameters()
        p.baseFont = "Ubuntu"
        p.boldFont = "Ubuntu Bold"
        p.italicFont = "Ubuntu Italic"
        p.baseFont = "Arial"
        p.boldFont = "Arial Bold"
        p.italicFont = "Arial Italic"
        p.digitsFont = "DejaVu"
        p.normalSize = 9
        p.minSize = 6
        p.bigSize = 12 
        p.lineColor = colors.black
        p.numSquareSideWidth = 3 * mm
        p.leading = 6 * mm
        

        self.param = p
        self.canvas.setFont(self.param.baseFont, self.param.normalSize)
        self.canvas.setPageSize = A4
        self.date = date.today()

        self.setTemplates()

    def setTemplates(self):
        self.templates = Parameters()
        self.templates.entities = dict(
                laquo =  u'\u00AB',
                raquo = u'\u00BB'
                )
        self.templates.warn = (
            u"С условиями приема указанной в платежном документе "
            u"суммы, в т.ч. с суммой взимаемой платы \n" 
            u"за услуги банка, ознакомлен и согласен"
            )
        self.templates.year = self.date.strftime(u"%Y г.".encode('utf-8'))
        self.beneficiary = dict(
            name = u"ООО {laquo}Издательский дом {laquo}Практика{raquo}".format(
                laquo = self.templates.entities['laquo'],
                raquo = self.templates.entities['raquo']),
            INN = "7705166992",
            BIK = "044525225",
            correspondentAccount = "30101810400000000225",
            beneficiaryAccount = "40702810138040103580",
            bankName = (u"Сбербанк России ОАО, г.Москва, "
                        u"Московский банк Сбербанка России ОАО"),
            )

    def feed(self, req, payment):
        Story = namedtuple("Story", ('rub',
                                    'kop',
                                    'address',
                                    'customerName',
                                    'paymentName'))

        amount = D(payment.get('amount')).quantize(D('0.01'))
        _, digits, _ = amount.as_tuple()
        kop = ''.join(str(digit) for digit in digits[-2:])
        rub = ''.join(str(digit) for digit in digits[:-2])

        self.story = Story(
                rub,
                kop,
                req.get('address'),
                req.get('name'),
                payment.get('name')
                )

    def writeKvit(self, x, y):
        c = self.canvas
        c.saveState()
        c.translate(x,y)
        x = y = 0
        left = 1 * mm
        right = 125 * mm
        y = 1.5 * mm
        c.line(101 * mm, y, right, y)
        y = 2 * mm
        c.setFont(self.param.boldFont, self.param.normalSize)
        c.drawString(62 * mm, y, u'Подпись плательщика')

        def nextLine(canvas, y):
            canvas.setFont(self.param.baseFont, self.param.normalSize)
            y += self.param.leading
            return canvas, y

        c, y = nextLine(c, y)
        c.setFont(self.param.baseFont, self.param.minSize)
        txt = c.beginText()
        txt.setTextOrigin(left, y)
        txt.setLeading(self.param.normalSize * 1)

        txt.textLines(self.templates.warn)
        c.drawText(txt)
        y -= 3 * mm

        def writeSumm(canvas, x, y, withAmount=False):
            c = canvas
            c.saveState()
            c.translate(x, y)
            y = -2
            c.line(0, y, 9 * mm, y)
            c.line(17 * mm, y, 23 * mm, y)
            y = 0
            c.drawString(10 * mm, y, u'руб.')
            c.drawString(24 * mm, y, u'коп.')
            if withAmount:
                c.setFont(self.param.italicFont, self.param.normalSize)
                c.drawCentredString(5 * mm, y, self.story.rub)
                c.drawCentredString(20 * mm, y, self.story.kop)
            c.restoreState()

        c, y = nextLine(c, y)
        writeSumm(c, 11 * mm, y, withAmount=True)
        c.line(74 * mm, y, 79 * mm, y)
        c.line(84 * mm, y, 113 * mm, y)

        c.drawString(left, y, u'Итого')
        c.drawString(70 * mm, y, self.templates.entities['laquo'])
        c.drawString(81 * mm, y, self.templates.entities['raquo'])
        c.drawRightString(right, y, self.templates.year)

        c, y = nextLine(c, y)
        c.drawString(left, y, u'Сумма платежа')
        writeSumm(c, 26 * mm, y, withAmount=True)
        c.drawString(60 * mm, y, u'Сумма платы за услуги')
        writeSumm(c, 96 * mm, y)

        c, y = nextLine(c, y)
        c.drawString(left, y, u'Адрес плательщика')
        c.setFont(self.param.italicFont, self.param.normalSize)
        c.drawString(32 * mm, y, self.story.address)
        c.setFont(self.param.baseFont, self.param.normalSize)
        c.line(32 * mm, y-2, right, y-2)

        c, y = nextLine(c, y)
        c.drawString(left, y, u'Ф.,и.,о. плательщика')
        c.setFont(self.param.italicFont, self.param.normalSize)
        c.drawString(34 * mm, y, self.story.customerName)
        c.setFont(self.param.baseFont, self.param.normalSize)
        c.line(34 * mm, y-2, right, y-2)

        c, y = nextLine(c, y)
        c.line(left, y, 65 * mm, y)
        c.line(71 * mm, y, right, y)
        _y = y - self.param.minSize
        c.setFontSize(self.param.minSize)
        x = left + ((65 * mm - left) / 2)
        c.drawCentredString(x, _y, u"(наименование платежа)")
        x = 71 * mm + ((right - 71 * mm) / 2)
        c.drawCentredString(x, _y, u"(номер лицевого счета (код) плательщика)")
        _y = y + 2
        c.setFont(self.param.italicFont, self.param.normalSize)
        c.drawString(left, _y, self.story.paymentName)


        def writeNumbersInSquares(canvas, x, y, numbers, align="right"):
            c = canvas
            c.saveState()
            c.translate(x, y)
            c.setFont(self.param.digitsFont, self.param.normalSize)
            _y = 0.3 * mm
            _right = self.param.numSquareSideWidth - 0.5 * mm
            _left = 0.5 * mm
            gridX = []

            def _writeRightNumbersInSquares(numbers):
                _x = 0
                for n in reversed(numbers):
                    gridX.insert(0,_x)
                    c.drawString(_x - _right, _y, n)
                    _x -= self.param.numSquareSideWidth
                gridX.insert(0, _x)
                c.grid(gridX, (0, self.param.numSquareSideWidth))

            def _writeLeftNumbersInSquares(numbers):
                _x = 0
                for n in numbers:
                    gridX.append(_x)
                    c.drawString(_left + _x, _y, n)
                    _x += self.param.numSquareSideWidth
                gridX.append(_x)

            if align == "right":
                _writeRightNumbersInSquares(numbers)
            else:
                _writeLeftNumbersInSquares(numbers)
            c.grid(gridX, (0, self.param.numSquareSideWidth))
            c.restoreState()

        c, y = nextLine(c, y)
        c.drawString(left, y, u"Номер кор./сч. банка получателя платежа")
        writeNumbersInSquares(c, right, y, self.beneficiary.get(
                                            "correspondentAccount"))

        c, y = nextLine(c, y)
        c.drawString(left, y, u"В")
        c.drawString(90 * mm, y, u"БИК")
        c.line(6 * mm, y, 80 * mm, y)
        writeNumbersInSquares(c, right, y, self.beneficiary.get("BIK"))
        c.setFont(self.param.baseFont, self.param.minSize)
        c.drawString(6 * mm, y + 1, self.beneficiary.get("bankName"))

        c, y = nextLine(c, y)
        writeNumbersInSquares(c, left, y, self.beneficiary.get("INN"), 
                align="left")
        writeNumbersInSquares(c, right, y, self.beneficiary.get(
                                                "beneficiaryAccount"))
        


        _y = y - self.param.minSize
        c.setFontSize(self.param.minSize)

        c.drawString(left, _y, u"(ИНН получателя платежа)")
        c.drawString(75 * mm, _y, u"(номер счета получателя платежа)")

        c, y = nextLine(c, y)
        c.line(left, y, right, y)
        c.setFont(self.param.italicFont, self.param.bigSize)
        x = left + (right - left) / 2
        c.drawCentredString(x, y + 1, self.beneficiary.get("name"))

        _y = y - self.param.minSize
        c.setFont(self.param.baseFont, self.param.minSize)
        c.drawCentredString(x, _y, u"(наименование получателя)")
        c.restoreState()

    def write(self):
        c = self.canvas
        c.translate(10*mm, 140 * mm)
        c.grid((0, 50 * mm, 180 * mm), (0, 80 * mm, 145 * mm))
        c.setFont(self.param.boldFont, self.param.normalSize)
        x = 25 * mm
        c.drawCentredString(x, 135 * mm, u"И з в е щ е н и е")
        c.drawCentredString(x, 93 * mm, u"Кассир")
        c.drawCentredString(x, 20 * mm, u"К в и т а н ц и я")
        c.drawCentredString(x, 10 * mm, u"Кассир")

        self.param.leading = 7 * mm
        self.writeKvit(50 * mm, 0)
        self.param.leading = 6 * mm
        self.writeKvit(50 * mm, 80 * mm)
        self.canvas.showPage()
        self.canvas.save()

