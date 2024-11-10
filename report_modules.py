from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFGenerator:
    def __init__(self, test_results):
        self.test_results = test_results
        print(self.test_results)
