from io import BytesIO
from django.http import HttpResponseRedirect,HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.conf import settings
import uuid
# def save_pdf(data:dict):

    # template=get_template("pdfs/invoice.html")
    # html=template.render(data)
    # # response = HttpResponse(content_type='application/pdf')
    # # pisa_status = pisa.CreatePDF(html, dest=response)
    # # if pisa_status.err:
    # #     return "render-error"
    # # return response


    # response= BytesIO()
    # pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)
    # file_name = uuid.uuid4()
    # try:
    #     with open(str(settings.BASE_DIR) + f"/public/static/{file_name}.pdf", 'wb') as output:
    #         # pdf = pisa.pisaDocument (BytesIO(html.encode('UTF-8'))), output
    #         pdf_result, _ = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), output)

    #         if pdf_result.error:
    #             return '', False


    # except Exception as e:
    #     print(e)
    # # if pdf_result.error:
    # #     return '', False
    # # if pdf.error:
    # #     return '', False
    # return file_name, True


def save_pdf(data: dict):
    template = get_template("pdfs/invoice.html")
    html = template.render(data)
    response = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)

    if not pdf.err:
        file_name = str(uuid.uuid4())
        file_path = str(settings.BASE_DIR) + f"/public/static/{file_name}.pdf"

        with open(file_path, 'wb') as output:
            output.write(response.getvalue())

        return file_name, True

    return '', False