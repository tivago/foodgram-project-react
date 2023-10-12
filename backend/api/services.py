import reportlab
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

reportlab.rl_config.TTFSearchPath.append(
    str(settings.BASE_DIR) + '/ingredients/data'
)


def creating_a_shopping_list(data):
    """Функция для формирования списка покупок."""
    shopping_list = {}
    for i, (name, mu, amount) in enumerate(data):
        if name in shopping_list:
            shopping_list[name][0] += amount
        else:
            shopping_list[name] = [amount, mu]
    pdfmetrics.registerFont(TTFont(
        'Poetsen', 'Poetsen-One.ttf', 'UTF-8'
    ))
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'
    ] = 'attachment; filename="shopping_list.pdf"'
    pdf = canvas.Canvas(response)
    pdf.setFont('Poetsen', 14)
    step = 720
    indent = 30
    count = 1
    for key, value in shopping_list.items():
        pdf.drawString(
            indent, step,
            f'{count}. {key} - {value[0]}, {value[1]}'
        )
        step -= 30
        count += 1
    pdf.showPage()
    pdf.save()
    return response
