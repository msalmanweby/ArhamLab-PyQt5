from datetime import datetime
import json
from PyQt5.QtWidgets import (
    QVBoxLayout, 
    QFormLayout, 
    QLineEdit, 
    QComboBox, 
    QWidget, 
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem, 
    QCheckBox,
    QLabel,
    QDateEdit,
    QDialogButtonBox,
    QDialog,
    QFileDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QObject
from lab_modules import tests_list
from app_config import time_zone, cursor, connection, resource_path
from report_modules import PDFGenerator
import os
from pathlib import Path
import threading

class PDFGeneratorThread(QObject, threading.Thread):
    success_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, pdf_generator, payload, case_no):
        QObject.__init__(self)  # Initialize QObject
        threading.Thread.__init__(self)  # Initialize threading.Thread
        self.pdf_generator = pdf_generator
        self.payload = payload
        self.case_no = case_no

    def run(self):
        try:
            self.pdf_generator.render_pdf(self.payload)
            self.success_signal.emit(f"PDF generation completed: {self.case_no}")
        except Exception as e:
            self.error_signal.emit(f"Error during PDF generation for {self.case_no}")

class DialogMixin:
    def show_dialog(self, title, message, dialog_type="information"):
        """Shows a custom dialog with the given title, message, and type (Error, Information, Warning, Confirmation)."""
        
        # Check if the dialog is a confirmation
        if dialog_type == "confirmation":
            confirm = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                return True
            else:
                return False
        
        # Create a custom dialog for other types (Information, Warning, etc.)
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QIcon(resource_path("assets/icon.png")))
        
        # Set a fixed width for the dialog
        dialog.setFixedWidth(400)
        
        # Create the layout
        layout = QVBoxLayout()
        
        # Add the message text
        label = QLabel(message)
        layout.addWidget(label)
        
        # Create a button box and add the necessary buttons
        button_box = QDialogButtonBox()
        
        # Depending on the dialog type, add the appropriate buttons
        # if dialog_type == "Warning":
        #     button_box.addButton(QDialogButtonBox.Ok)
        #     button_box.addButton(QDialogButtonBox.Cancel)
        # else:
        button_box.addButton(QDialogButtonBox.Ok)  # Default for other types
        
        # Handle button clicks
        button_box.accepted.connect(dialog.accept)  # OK button clicked, close the dialog
        button_box.rejected.connect(dialog.reject)  # Cancel button clicked, close the dialog
        
        layout.addWidget(button_box)
        
        # Set the layout for the dialog
        dialog.setLayout(layout)
        
        # Show the dialog
        dialog.exec_()

class AddResultDialog(QDialog, DialogMixin):
    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.case_no = record[0]
        self.setWindowTitle(f"Case No: {self.case_no}")
        self.setMinimumSize(300, 200)

        # Set up the layout
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.test_results = json.loads(record[12])
        self.scheduled_tests = json.loads(record[11])
        if not self.test_results:
            self.initialize_test_results()


        self.test_name = QComboBox()
        self.test_name.addItems(test["name"] for test in self.test_results)
        form_layout.addRow("Test Name:", self.test_name)

        self.test_type = QComboBox()
        form_layout.addRow("Test Type:", self.test_type)
        self.update_test_types()
        self.test_name.currentIndexChanged.connect(self.update_test_types)

        self.min_value = QLineEdit()
        self.min_value.setReadOnly(True)
        form_layout.addRow("Minimum Value:", self.min_value)

        self.max_value = QLineEdit()
        self.max_value.setReadOnly(True)
        form_layout.addRow("Maximum Value:", self.max_value)

        self.unit = QLineEdit()
        self.unit.setReadOnly(True)
        form_layout.addRow("Unit:", self.unit)

        self.result = QLineEdit()
        form_layout.addRow("Result:", self.result)

        self.update_test_measurements()
        self.test_type.currentIndexChanged.connect(self.update_test_measurements)

        update_result = QPushButton("Update")
        update_result.clicked.connect(self.update_results_in_db)
        form_layout.addRow(update_result)        

        main_layout.addLayout(form_layout)

        self.setLayout(main_layout)

    def initialize_test_results(self): 
        for scheduled_test in self.scheduled_tests:
            test_name = scheduled_test["name"]
            test_type = scheduled_test["type"]
            
            # Find the corresponding test in tests_list
            test_data = next((test for test in tests_list if test["name"] == test_name), None)
            
            if test_data:
                # Get the type information for the specific test type
                types_info = [t for t in test_data["types"] if t["name"] == test_type]
                
                # Check if this test_name already exists in self.test_results
                existing_test = next((test for test in self.test_results if test["name"] == test_name), None)
                
                if existing_test:
                    # If the test already exists, extend its types list with new types
                    existing_test["types"].extend(
                        {
                            "name": t["name"],
                            "minValue": t["minValue"],
                            "maxValue": t["maxValue"],
                            "unit": t["unit"],
                            "result": ""  # Initialize result as an empty string
                        } for t in types_info
                    )
                else:
                    # If the test doesn't exist, add a new entry
                    self.test_results.append({
                        "name": test_name,
                        "types": [
                            {
                                "name": t["name"],
                                "minValue": t["minValue"],
                                "maxValue": t["maxValue"],
                                "unit": t["unit"],
                                "result": ""  # Initialize result as an empty string
                            } for t in types_info
                        ]
                    })

    def update_results_in_db(self):
        # Retrieve selected test and type
        selected_test_name = self.test_name.currentText()
        selected_test_type = self.test_type.currentText()
        entered_result = self.result.text()

        # Find the selected test in self.test_results
        selected_test = next((test for test in self.test_results if test["name"] == selected_test_name), None)

        if selected_test:
            # Find the specific type within the selected test
            selected_type = next((t for t in selected_test["types"] if t["name"] == selected_test_type), None)

            if selected_type:
                # Update the result for this test type
                selected_type["result"] = entered_result

        cursor.execute("""
            UPDATE LabReport
            SET test_results = ?
            WHERE id = ?
        """, (json.dumps(self.test_results), self.case_no))

        # Commit the changes to the database
        connection.commit()

        self.show_dialog("Success", f"Result added successfully!")


    def update_test_types(self):
        self.test_type.clear()
        selected_test_name = self.test_name.currentText()
        for test in self.test_results:
            if test["name"] == selected_test_name:
                self.test_type.addItems(test_type["name"] for test_type in test["types"])
                break
    
    def update_test_measurements(self):
        """Update min_value, max_value and unit when the test type changes"""
        self.min_value.clear()
        self.max_value.clear()
        self.unit.clear()
        self.result.clear()

        selected_test_name = self.test_name.currentText()
        selected_test_type = self.test_type.currentText()

        for test in self.test_results:
            if test["name"] == selected_test_name:
                for test_type in test["types"]:
                    if test_type["name"] == selected_test_type:
                        self.min_value.setText(test_type["minValue"])
                        self.max_value.setText(test_type["maxValue"])
                        self.unit.setText(test_type["unit"])
                        self.result.setText(test_type["result"])
                        break

class PatientInfoPage(QWidget, DialogMixin):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()

        # Form layout for input fields
        form_layout = QFormLayout()
        action_buttons_layout = QHBoxLayout()

        row_layout_0 = QHBoxLayout()
        # First row (Patient Name and Father/Husband Name)
        row_layout_1 = QHBoxLayout()
        # Second row (Age, Gender, Nic, Address)
        row_layout_2 = QHBoxLayout()
        # Third row (Registration Center, Specimen, Consultant Name)
        row_layout_3 = QHBoxLayout()
        # Fourth row (Test Name, Test Result, Price)
        row_layout_4 = QHBoxLayout()

        reset_entry = QPushButton("Clear Entries")
        reset_entry.setFixedWidth(100)
        reset_entry.clicked.connect(self.reset_patient_info)

        self.patient_name_label = QLabel("Patient Name:")
        self.patient_name = QLineEdit()

        self.father_husband_name_label = QLabel("Father/Husband Name:")
        self.father_husband_name = QLineEdit()

        self.age_label = QLabel("Age:")
        self.age = QLineEdit()

        self.gender_label = QLabel("Gender:")
        self.gender = QComboBox()
        self.gender.setFixedWidth(200)
        self.gender.addItems(["Male", "Female", "Other"])

        self.nic_number_label = QLabel("NIC Number:")
        self.nic_number = QLineEdit()

        self.address_label = QLabel("Address:")
        self.address = QLineEdit()

        

        self.registration_center_label = QLabel("Registration Center:")
        self.registration_center = QLineEdit()

        self.specimen_label = QLabel("Specimen:")
        self.specimen = QComboBox()
        self.specimen.setFixedWidth(200)
        self.specimen.addItems(["","Brought to Lab"])

        self.consultant_name_label = QLabel("Consultant Name:")
        self.consultant_name = QComboBox()
        self.consultant_name.setFixedWidth(200)
        self.consultant_name.addItems(["","Hamza"])


        self.phone_number_label = QLabel("Phone Number:")
        self.phone_number = QLineEdit()
        self.phone_number.setFixedWidth(200)


        self.test_name_label = QLabel("Test Name:")
        self.test_name = QComboBox()
        self.test_name.setFixedWidth(320)
        self.test_name.addItems(test["name"] for test in tests_list)

        self.test_type_label = QLabel("Test Type:")
        self.test_type = QComboBox()
        self.test_type.setFixedWidth(320)
        self.update_test_types()
        self.test_name.currentIndexChanged.connect(self.update_test_types)
        self.scheduled_tests = []

        row_layout_0.addStretch(1)
        row_layout_0.addWidget(reset_entry)

        row_layout_1.addWidget(self.patient_name_label)
        row_layout_1.addWidget(self.patient_name)
        row_layout_1.addWidget(self.father_husband_name_label)
        row_layout_1.addWidget(self.father_husband_name)
        row_layout_1.addWidget(self.nic_number_label)
        row_layout_1.addWidget(self.nic_number)
        form_layout.addRow(row_layout_1)

        row_layout_2.addWidget(self.age_label)
        row_layout_2.addWidget(self.age)
        row_layout_2.addWidget(self.gender_label)
        row_layout_2.addWidget(self.gender)
        row_layout_2.addWidget(self.address_label)
        row_layout_2.addWidget(self.address)
        
        form_layout.addRow(row_layout_2)

        row_layout_3.addWidget(self.registration_center_label)
        row_layout_3.addWidget(self.registration_center)
        row_layout_3.addWidget(self.specimen_label)
        row_layout_3.addWidget(self.specimen)
        row_layout_3.addWidget(self.consultant_name_label)
        row_layout_3.addWidget(self.consultant_name)
        form_layout.addRow(row_layout_3)

        row_layout_4.addWidget(self.phone_number_label)
        row_layout_4.addWidget(self.phone_number)
        row_layout_4.addWidget(self.test_name_label)
        row_layout_4.addWidget(self.test_name)
        row_layout_4.addWidget(self.test_type_label)
        row_layout_4.addWidget(self.test_type)
        form_layout.addRow(row_layout_4)

        add_entry = QPushButton("Add Entry")
        add_entry.clicked.connect(self.add_results_in_table)

        remove_entry = QPushButton("Remove Entry")
        remove_entry.clicked.connect(self.remove_results_from_table)

        save_record = QPushButton("Save Record")
        save_record.clicked.connect(self.create_entry_into_db)
        
        action_buttons_layout.addWidget(add_entry)
        action_buttons_layout.addWidget(remove_entry)
        action_buttons_layout.addWidget(save_record)
        form_layout.addRow(action_buttons_layout)

        # Add form layout to the main layout
        self.main_layout.addLayout(row_layout_0)
        self.main_layout.addLayout(form_layout)

        self.schedule_test_table = QTableWidget()
        self.schedule_test_table.setColumnCount(3)
        self.schedule_test_table.setHorizontalHeaderLabels(["Select", "Test Name", "Test Type"])
        self.schedule_test_table.verticalHeader().setVisible(False)

        # Set a fixed width for the "Select" column (the first column)
        self.schedule_test_table.setColumnWidth(0, 80)  # Set a fixed width for "Select" column

        # Set resizing behavior for the other columns
        header = self.schedule_test_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # "Test Name" column
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # "Test Type" column
        # header.setSectionResizeMode(3, QHeaderView.Stretch)  # "Price" column
        
        # Ensure the last section stretches to fill remaining space
        self.main_layout.addWidget(self.schedule_test_table)

        self.setLayout(self.main_layout)
    
    def create_entry_into_db(self):
        """Initial Entry for saving patient info"""
        if not self.patient_name.text().strip():
            # Show error message if patient name is empty
            self.show_dialog("Error", "Patient name cannot be empty!")
            return
        if not self.scheduled_tests:
            # Show error message if patient name is empty
            self.show_dialog("Error", "No entries found for Scheduled test")
            return
        

        patient_data = {
            "patient_name": self.patient_name.text(),
            "father_husband_name": self.father_husband_name.text(),
            "age": self.age.text(),
            "gender": self.gender.currentText(),
            "nic_number": self.nic_number.text(),
            "address": self.address.text(),
            "registration_date": datetime.now(time_zone).strftime('%Y-%m-%d'),
            "registration_center": self.registration_center.text(),
            "specimen": self.specimen.currentText(),
            "consultant_name": self.consultant_name.currentText(),
            "scheduled_tests": json.dumps(self.scheduled_tests),  # JSON data as string
            "test_results": json.dumps([]),  # JSON data as string
            "phone_number": self.phone_number.text(),
        }
        try:
            cursor.execute("""
                INSERT INTO LabReport (
                    patient_name, father_husband_name, age, gender, nic_number,
                    address, registration_date, registration_center, specimen,
                    consultant_name, scheduled_tests, test_results, phone_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(patient_data.values()))
            connection.commit()
            if cursor.lastrowid:
                self.reset_patient_info()
                self.show_dialog("Success", f"Case {cursor.lastrowid} registration successfull!")
        except Exception as e:
            self.show_dialog("Error", "Something went wrong, Try Again!")
            print(e)
            return
        
    def update_test_types(self):
        """Update the test type options the test name changes""" 
        self.test_type.clear()
        selected_test_name = self.test_name.currentText()
        for test in tests_list:
            if test["name"] == selected_test_name:
                self.test_type.addItems(test_type["name"] for test_type in test["types"])
                break

    def update_test_price(self):
        """Update the test price options the test type changes""" 
        self.price.clear()
        selected_test_name = self.test_name.currentText()
        selected_test_type = self.test_type.currentText()

        for test in tests_list:
            if test["name"] == selected_test_name:
                for test_type in test["types"]:
                    if test_type["name"] == selected_test_type:
                        self.price.setText(test_type["price"])
                        break
    def add_results_in_table(self):
        """Add the done test results in the table to view"""

        test = {
            "name": self.test_name.currentText(),
            "type": self.test_type.currentText(),
            # "price": self.price.text(),
        }

        self.scheduled_tests.append(test)
        row_position = self.schedule_test_table.rowCount()

        # Insert a new row
        self.schedule_test_table.insertRow(row_position)

        # Create a checkbox widget for row selection (first column)
        checkbox_widget = QWidget()
        checkbox = QCheckBox()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignCenter)  # Center the checkbox in the cell
        checkbox_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
        self.schedule_test_table.setCellWidget(row_position, 0, checkbox_widget)

        # Set the checkbox column width
        self.schedule_test_table.setColumnWidth(0, 30)

        # Insert the test data in the remaining columns (starting from column 1)
        self.schedule_test_table.setItem(row_position, 1, QTableWidgetItem(test["name"]))
        self.schedule_test_table.setItem(row_position, 2, QTableWidgetItem(test["type"]))

        # Set text alignment for all columns with test data
        for column in range(1, self.schedule_test_table.columnCount()):
            item = self.schedule_test_table.item(row_position, column)
            if item:
                item.setTextAlignment(Qt.AlignCenter)

    def remove_results_from_table(self):
        """Delete rows that are selected via checkboxes"""
        rows_to_delete = []
        
        # Check which rows are selected for deletion
        for row in range(self.schedule_test_table.rowCount()):
            checkbox_widget = self.schedule_test_table.cellWidget(row, 0)  # The checkbox is in the first column
            if checkbox_widget is not None:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    rows_to_delete.append(row)
        
        # If no rows are selected, show an error message
        if not rows_to_delete:
            self.show_dialog("Error", "Please select at least one record to delete.")
            return

        # Delete selected rows in reverse order to avoid index shifting
        for row in reversed(rows_to_delete):
            # Remove from test_results_list as well
            del self.scheduled_tests[row]

            # Remove the row from the table
            self.schedule_test_table.removeRow(row)

    def reset_patient_info(self):
        """Reset scheduled tests and clear the table"""

        # Clear the list of scheduled tests
        self.scheduled_tests = []  # Reset the list of scheduled tests

        # Clear all rows in the table (except for the headers)
        row_count = self.schedule_test_table.rowCount()
        for row in range(row_count):
            self.schedule_test_table.removeRow(0)  # Remove each row starting from the top
            
        self.test_name.setCurrentIndex(0)

        # Optional: You can also reset any other widgets related to scheduled tests
        self.patient_name.setText("")
        self.father_husband_name.setText("")
        self.age.setText("")
        self.gender.setCurrentIndex(0)
        self.nic_number.setText("")
        self.address.setText("")
        self.registration_center.setText("")
        self.specimen.setCurrentIndex(0)
        self.consultant_name.setCurrentIndex(0)
        self.test_name.setCurrentIndex(0)

class AddResultsPage(QWidget, DialogMixin):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        row_layout_0 = QHBoxLayout()
        
        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)  # Show a calendar popup for easier date selection
        self.date_input.setDate(QDate.currentDate())  # Set the default date to today
        self.date_input.setFixedWidth(270)
        
        # Search record button
        search_button = QPushButton("Search Record")
        search_button.clicked.connect(lambda: self.search_records(show_dialog=True))
        search_button.setFixedWidth(100)

        add_results = QPushButton("Add Results")
        add_results.clicked.connect(self.add_scheduled_test_result)
        add_results.setFixedWidth(100)

        delete_entry = QPushButton("Delete Entry")
        delete_entry.clicked.connect(self.delete_record_from_database)
        delete_entry.setFixedWidth(100)

        generate_report = QPushButton("Generate Report")
        generate_report.clicked.connect(self.generate_patient_report)
        generate_report.setFixedWidth(100)
        
        
        row_layout_0.addWidget(self.date_input)
        row_layout_0.addWidget(search_button)
        row_layout_0.addWidget(add_results)
        row_layout_0.addWidget(delete_entry)
        row_layout_0.addWidget(generate_report)

        form_layout.addRow(row_layout_0)

        self.main_layout.addLayout(form_layout)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(["Select", "Case No", "Patient Name", "Father/Husband Name", "Nic Number", "Test", "Status"])
        # Set a fixed width for the "Select" column (the first column)
        self.results_table.setColumnWidth(0, 80)  # Adjust the value as needed
        self.results_table.setColumnWidth(1, 80)  # Adjust the value as needed
        # In your table initialization code, hide the row numbers:
        self.results_table.verticalHeader().setVisible(False)
        # Set section resize mode for other columns to stretch
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Patient Name column
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Actions column
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Case No column
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Case No column
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Case No column

        self.main_layout.addWidget(self.results_table)

        # Set layout
        self.setLayout(self.main_layout)

    def on_pdf_success(self, message):
        self.show_dialog("Success", message)

    def on_pdf_error(self, message):
        self.show_dialog("Error", message)

    def search_records(self, show_dialog=True):
        try:
            cursor.execute("""
                                SELECT * FROM LabReport 
                                WHERE registration_date = ?""", 
                                (self.date_input.date().toString('yyyy-MM-dd'),))
            self.rows = cursor.fetchall()
            if self.rows:
                if show_dialog:  # Show dialog only if it's not an update
                    self.show_dialog("Success", f"{len(self.rows)} results fetched.")
                self.add_results_in_table(rows=self.rows)
            else:
                self.results_table.setRowCount(0)  # Clear the table
                if show_dialog:
                    self.show_dialog("Error", "No records found for the selected date.")
                return
        except Exception as e:
            self.show_dialog("Error" , "Unable to fetch results")
            print(e)
            return
        
    def add_results_in_table(self, rows):
        # Clear the table before populating it
        self.results_table.setRowCount(0)

        # Loop through each row and add it to the table
        for row in rows:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)

            # Create a checkbox widget for row selection (first column)
            checkbox_widget = QWidget()
            checkbox = QCheckBox()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)  # Center the checkbox in the cell
            checkbox_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
            self.results_table.setCellWidget(row_position, 0, checkbox_widget)

            # Connect the checkbox click event to handle single selection
            checkbox.clicked.connect(lambda state, row=row_position: self.on_checkbox_clicked(row))
            
            # Add data to each column (0: Select, 1: Case No, 2: Patient Name, 3: Father/Husband Name, 4: Nic Number, 5: Test)
            self.results_table.setItem(row_position, 1, QTableWidgetItem(str(row[0])))  # Case No (ID)
            self.results_table.setItem(row_position, 2, QTableWidgetItem(row[1]))  # Patient Name
            self.results_table.setItem(row_position, 3, QTableWidgetItem(row[2]))  # Father/Husband Name
            self.results_table.setItem(row_position, 4, QTableWidgetItem(row[5]))  # NIC Number
            
            # Parse the JSON data in the scheduled_tests column and extract the test names
            try:
                scheduled_tests = json.loads(row[11])  # Scheduled tests column
                # test_names = [test['name'] for test in scheduled_tests if 'name' in test]
                # test_names_str = ", ".join(test_names)  # Join test names with commas
                
                # Add the test names to the table in the "Test" column
                self.results_table.setItem(row_position, 5, QTableWidgetItem(str(len(scheduled_tests))))
            except (json.JSONDecodeError, KeyError) as e:
                # If there's an error parsing the JSON or accessing 'name', handle it gracefully
                self.results_table.setItem(row_position, 5, QTableWidgetItem("Invalid data"))

            # Set the report status
            test_results = json.loads(row[12])
            if not test_results:
                self.results_table.setItem(row_position, 6, QTableWidgetItem("Pending"))
            else:
                has_empty_result = any(
                    type_info["result"] == "" 
                    for test in test_results 
                    for type_info in test["types"]
                )

                if has_empty_result:
                    self.results_table.setItem(row_position, 6, QTableWidgetItem("Pending"))
                else:
                    self.results_table.setItem(row_position, 6, QTableWidgetItem("Completed"))

            # Set text alignment for all columns with test data
            for column in range(1, self.results_table.columnCount()):
                item = self.results_table.item(row_position, column)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
    
    def on_checkbox_clicked(self, row_position):
        # Uncheck all other checkboxes
        for i in range(self.results_table.rowCount()):
            checkbox_widget = self.results_table.cellWidget(i, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and i != row_position:
                    checkbox.setChecked(False)

        # Select the row programmatically
        self.results_table.selectRow(row_position)


    def add_scheduled_test_result(self):
        selected_case_no = self.get_case_no()
        
        if selected_case_no is None:
            # Error message is already shown in get_case_no, no need to duplicate it here
            return

        # try:
        # Query the database using the selected "Case No"
        cursor.execute("SELECT * FROM LabReport WHERE id = ?", (selected_case_no,))
        result = cursor.fetchone()
        
        if result:
            # Process the result, e.g., open a dialog to display it
            dialog = AddResultDialog(result, self)
            dialog.exec_()
            self.search_records(show_dialog=False)
        else:
            self.show_dialog("Error", "No record found for the selected Case No.")

    def get_case_no(self):
        # Loop through each row to check if the checkbox in the first column is checked
        for row in range(self.results_table.rowCount()):
            checkbox_widget = self.results_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    # Retrieve "Case No" from the selected row (assuming it's in column 1)
                    case_no_item = self.results_table.item(row, 1)
                    if case_no_item:
                        return case_no_item.text()  # Return the Case No as a string
        # If no checkbox is checked, show an error and return None
        self.show_dialog("Error", "Please select at least one record.")
        return None
    
    def get_selected_row(self):
        # Loop through each row to check if the checkbox in the first column is checked
        for row in range(self.results_table.rowCount()):
            checkbox_widget = self.results_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    return row  # Return the row index of the selected row
        # If no checkbox is checked, show an error and return None
        self.show_dialog("Error", "Please select at least one record.")
        return None

    def delete_record_from_database(self):
        try:
            # Get the selected row's Case No using the get_case_no method
            case_no = self.get_case_no()
            
            # If no row is selected, the get_case_no will return None and show an error dialog
            if case_no is None:
                return  # Early exit as an error dialog has already been shown

            # Ask the user to confirm the deletion action using the show_dialog method
            confirm = self.show_dialog("Confirm Delete", 
                                    f"Are you sure you want to delete the Case No {case_no}?", 
                                    dialog_type="confirmation")
            if not confirm:
                return  # Exit if the user cancels the deletion
            
            # Delete the record from the database based on the Case No
            cursor.execute("DELETE FROM LabReport WHERE id = ?", (case_no,))
            connection.commit()
            
            # Show a success message
            self.show_dialog("Success", f"Record with Case No {case_no} has been deleted.")
            
            # Refresh the table to reflect the change
            self.search_records(show_dialog=False)  # Pass show_dialog=False to prevent an additional success message
            
        except Exception as e:
            # Handle any exceptions and display an error dialog
            self.show_dialog("Error", "Failed to delete the record.")
            print(e)
        
    def generate_patient_report(self):
        # Get the selected row number
        row = self.get_selected_row()
        if row is None:
            return  # Early exit if no row is selected

        # Retrieve the "Status" from column 5 of the selected row
        status_item = self.results_table.item(int(row), 6)
        if status_item:
            status = status_item.text()  # Get the text from the QTableWidgetItem

            # Check if the status is "Pending"
            if status == "Pending":
                self.show_dialog("Error", "Failed to create the report for a pending case.")
                return

        # Get the case number
        case_no = self.get_case_no()
        if case_no is None:
            return  # Early exit if no case number is retrieved

        # Query the database for the case number
        cursor.execute("SELECT * FROM LabReport WHERE id = ?", (case_no,))
        result = cursor.fetchone()

        if not result:
            self.show_dialog("Error", f"No report found for Case No: {case_no}")
            return

        # Predefine a directory (e.g., Documents folder)
        documents_dir = str(Path.home() / "Documents")
        default_file_name = f"Patient_Report_{case_no}.pdf"

        # Open a directory selection dialog
        selected_dir = QFileDialog.getExistingDirectory(
            self,  # Parent widget
            "Select Directory to Save Report",  # Dialog title
            documents_dir  # Default directory
        )

        if not selected_dir:
            return  # User cancelled the selection

        # Combine the selected directory with the default file name
        save_path = os.path.join(selected_dir, default_file_name)

        # Generate the PDF
        pdf_generator = PDFGenerator(save_path)

        # Create and start the PDF generation thread
        pdf_thread = PDFGeneratorThread(pdf_generator, result, case_no)
        # Connect signals to dialog methods
        pdf_thread.success_signal.connect(self.on_pdf_success)
        pdf_thread.error_signal.connect(self.on_pdf_error)

        # Start the thread
        pdf_thread.start()

    

        
