from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from bidi.algorithm import get_display
from io import BytesIO
import arabic_reshaper
import qrcode
import barcode

class PDFGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.logo_path = "logo.png"
        self.canvas = canvas.Canvas(self.filename, pagesize=A4)
        self.width, self.height = A4

        # Register the Urdu font
        try:
            pdfmetrics.registerFont(TTFont('UrduFont', './fonts/Amiri-Regular.ttf'))  # Replace with 'Nafees Nastaleeq.ttf' or 'Alvi Nastaleeq.ttf' if available
        except Exception as e:
            print(e)
        self.create_pdf()

    def set_text_style(self, font_name="UrduFont", font_size=20, color=(0, 0, 0)):
        """Sets the font style, size, and color."""
        self.canvas.setFont(font_name, font_size)
        r, g, b = color
        self.canvas.setFillColorRGB(r, g, b)

    def create_pdf(self):
        # Set header color
        self.canvas.setFillColorRGB(7/255, 141/255, 218/255)
        
        # Draw header rectangle
        self.padding = 20
        header_height = 20
        self.canvas.rect(self.padding, self.height - header_height - self.padding, self.width - 2 * self.padding, header_height, fill=1, stroke=0)
        
        # Add logo inside the boundary (left side)
        logo_width = 160  
        logo_height = 80  
        logo_x = self.padding  # Add some margin from the left
        logo_y = self.height - header_height - self.padding - logo_height + 10  # Start 10 units below the top of the boundary
        
        self.canvas.drawImage(self.logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
        
        # Original Urdu text
        urdu_text = "الارحم لیبارٹری"
        
        # Reshape and apply bidi to the Urdu text
        reshaped_text = arabic_reshaper.reshape(urdu_text)
        bidi_text = get_display(reshaped_text)
        
        # Set style for Urdu text
        self.set_text_style(font_name="UrduFont", font_size=16, color=(0, 0, 0))
        
        # Position the Urdu text on the right side of the boundary
        # Justify the text position to the right
        text_x = self.width - self.padding - self.canvas.stringWidth(bidi_text, "UrduFont", 16)  # 10 units margin from the right
        text_y = self.height - header_height - self.padding - 1.5 * 10 # Vertically center the text in the boundary
        
        # Draw the Urdu text on the canvas
        self.canvas.drawString(text_x, text_y, bidi_text)

        # Generate QR code using the qrcode library
        qr_code_data = "Name: Muhammad Salman"  # Replace this with your URL or data
        
        # Create a QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code_data)
        qr.make(fit=True)

        # Convert the QR code into an image
        img = qr.make_image(fill='black', back_color='white')

        # Save the image to a BytesIO object
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)  # Reset cursor to the beginning of the BytesIO stream

        # Use ImageReader to read the image from BytesIO object
        qr_image = ImageReader(img_bytes)

        # Create a canvas image for the QR code
        qr_width = 60  # Set QR code size
        qr_height = 60
        qr_x = self.width - self.padding - qr_width  # Center the QR code horizontally
        qr_y = self.height - header_height - self.padding - 1.5 * 10 - qr_height - 10  # Position it below the text

        # Draw the QR code from the ImageReader object
        self.canvas.drawImage(qr_image, qr_x, qr_y, width=qr_width, height=qr_height)

        # Save the PDF
        self.canvas.save()

# Generate the PDF
pdf = PDFGenerator("output.pdf")
