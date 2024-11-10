from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFGenerator:
    def __init__(self, file_name):
        self.file_name = file_name
        self.pdf_canvas = None

        