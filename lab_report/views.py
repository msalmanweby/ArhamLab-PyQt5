from django.http import HttpResponse
from rest_framework.views import APIView
from .models import LabReport
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

class GenerateLabReport(APIView):
    def post(self, request):
        payload = request.data

        patient_name = payload["patientName"]
        father_husband_name = payload["fatherHusbandName"]
        age = payload["age"]
        gender = payload["gender"]
        nic_number = payload["nicNumber"]
        address = payload["address"]
        registration_center = payload["registrationCenter"]
        specimen = payload["specimen"]
        consultant_name = payload["consultantName"] 
        test_results = payload["testResults"]

        lab_report = LabReport.objects.create(
            patient_name = patient_name,
            father_husband_name = father_husband_name,
            age = age,
            gender = gender,
            nic_number = nic_number,
            address = address,
            registration_center = registration_center,
            specimen = specimen,
            consultant_name = consultant_name,
            test_results = test_results,
        )

        lab_report.save()


        # Generate PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "Lab Report")

        # Patient Information
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 100, f"Patient's Name: {patient_name}")
        p.drawString(50, height - 120, f"Father/Husband Name: {father_husband_name}")
        p.drawString(50, height - 140, f"Age/Sex: {age} Years / {gender}")
        p.drawString(50, height - 160, f"NIC No: {nic_number}")
        p.drawString(50, height - 180, f"Address: {address}")

        # Registration Information
        p.drawString(300, height - 100, f"Reg. Date: {lab_report.registration_date.strftime('%d-%b-%y %I:%M:%S %p')}")
        p.drawString(300, height - 120, f"Reg. Centre: {registration_center}")
        p.drawString(300, height - 140, f"Specimen: {specimen}")
        p.drawString(300, height - 160, f"Consultant: {consultant_name}")

        # Test Results
        p.drawString(50, height - 220, "Blood Glucose Report")
        p.line(50, height - 225, 500, height - 225)  # Divider line
        p.drawString(50, height - 240, "Tests")
        p.drawString(200, height - 240, "Normal Range")
        p.drawString(400, height - 240, "Result")

        # Example of adding test results (assuming test_results is a dictionary)
        y_position = height - 260
        for test, result in test_results.items():
            p.drawString(50, y_position, test)
            p.drawString(200, y_position, result.get("normal_range", ""))
            p.drawString(400, y_position, str(result.get("value", "")))
            y_position -= 20

        # Finalize and save the PDF
        p.showPage()
        p.save()

        # Send the PDF as a response
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="LabReport_{patient_name}.pdf"'
        
        return response

