import os
import json
import logging
import base64
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import qrcode
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from PIL import Image

class PDFGenerator:
    def __init__(self, output_filename):
        self.output_filename = output_filename
        self.logo_path = os.path.abspath("logo.png")
        self.css_path = os.path.abspath("styles.css")

    def get_base64_image(self, path):
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"

    def get_qr_code_base64(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color="transparent")

        byte_io = BytesIO()
        qr_img.save(byte_io, format='PNG')
        byte_io.seek(0)

        encoded_qr = base64.b64encode(byte_io.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded_qr}"

    def get_barcode_base64(self, data):
        # Generate the barcode and save it to a BytesIO object
        barcode_obj = barcode.Code128(data, writer=ImageWriter())
        byte_io = BytesIO()
        # Disable text by setting write_text to False
        barcode_obj.write(byte_io, options={"module_width": 1, "module_height": 2.0, "write_text": False})
        byte_io.seek(0)

        # Open the barcode image with Pillow
        barcode_image = Image.open(byte_io).convert("RGBA")

        # Make the white background transparent
        datas = barcode_image.getdata()
        new_data = []
        for item in datas:
            # Change all white (also shades of white) pixels to transparent
            if item[:3] == (255, 255, 255):  # Detect white pixel
                new_data.append((255, 255, 255, 0))  # Make it transparent
            else:
                new_data.append(item)  # Keep other colors the same
        barcode_image.putdata(new_data)

        # Crop the transparent padding
        bbox = barcode_image.getbbox()
        cropped_image = barcode_image.crop(bbox)

        # Save the updated image back to BytesIO
        transparent_io = BytesIO()
        cropped_image.save(transparent_io, format="PNG")
        transparent_io.seek(0)

        # Encode as base64
        encoded_barcode = base64.b64encode(transparent_io.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded_barcode}"
    
    def paginate_results(self, test_results, items_per_page=5):
        print(test_results)
        print(type(test_results))
        # Check if test_results is None or empty
        if not test_results:
            return []  # Return an empty list if no test results are provided

        # Ensure test_results is a list
        if not isinstance(test_results, list):
            raise ValueError("test_results should be a list.")

        # Split the test results into multiple pages (chunks)
        return [test_results[i:i + items_per_page] for i in range(0, len(test_results), items_per_page)]



    def render_pdf(self, payload):
        patient_name =  payload[1]
        father_husband_name =  payload[2]
        age =  payload[3]
        gender =  payload[4]
        nic_number =  payload[5]
        address =  payload[6]
        registration_date =  payload[7]
        registration_center =  payload[8]
        specimen =  payload[9]
        consultant_name =  payload[10]
        test_results =  json.loads(payload[12])

        
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("report_template.html")

        logo_base64 = self.get_base64_image(self.logo_path)
        qr_code_data = "https://example.com"
        qr_code_base64 = self.get_qr_code_base64(qr_code_data)

        # Generate barcodes
        barcode_data_1 = "2367 - 10 / 2024"
        barcode_data_2 = "4 - 31 / 10"
        barcode_1_base64 = self.get_barcode_base64(barcode_data_1)
        barcode_2_base64 = self.get_barcode_base64(barcode_data_2)

        # print(self.test_results)
        # paginated_results = self.paginate_results(test_results=test_results)
        # Render HTML template
        html_out = template.render(
            doc_name = patient_name,
            logo_path=logo_base64,
            qr_code_path=qr_code_base64,
            barcode_1_path=barcode_1_base64,
            barcode_2_path=barcode_2_base64,
            patient_name=patient_name,
            father_husband_name=father_husband_name,
            age=age,
            gender=gender,
            nic_number=nic_number,
            address=address,
            registration_date=registration_date,
            registration_center=registration_center,
            specimen=specimen,
            consultant_name=consultant_name,
            test_results=test_results
        )

        HTML(string=html_out).write_pdf(self.output_filename)

