import sys
from datetime import datetime
import pytz
import json
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QDockWidget, 
    QListWidget, 
    QVBoxLayout, 
    QFormLayout, 
    QLineEdit, 
    QComboBox, 
    QWidget, 
    QStackedWidget, 
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QHeaderView,
    QDesktopWidget,
    QMessageBox,
    QTableWidgetItem, 
    QCheckBox,
    QLabel
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import sqlite3
from lab_modules import tests_list

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlArham Laboratory")
        self.setWindowIcon(QIcon("logo.png"))
        self.time_zone = pytz.timezone('Asia/Karachi')
        screen_rect = QDesktopWidget().screenGeometry()
        self.resize(screen_rect.width(), screen_rect.height())
        # Maximize the window
        self.showMaximized()

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        # Create different pages
        self.create_pages()

        # Create the left menu
        self.create_left_menu()

        # Initialize Database
        self.init_db()

    def init_db(self):
        """Initialize SQLite database and create tables if not exists."""
        self.conn = sqlite3.connect("lab_reports.db")
        self.cursor = self.conn.cursor()

        # Create LabReport table if it doesn't exist
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS LabReport (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                father_husband_name TEXT,
                age INTEGER,
                gender TEXT,
                nic_number TEXT,
                address TEXT,
                registration_date TEXT,
                registration_center TEXT,
                specimen TEXT,
                consultant_name TEXT,
                scheduled_tests TEXT,
                test_results TEXT
            )
        """)
        self.conn.commit()

    def create_pages(self):
        # self.add_entry_page = QWidget()
        self.create_patient_info_form()
        # self.create_test_results_form()

        # self.pages.addWidget(self.add_entry_page)

        # Add the other pages to the QStackedWidget
               

        # Set the initial page to "Create Patient Record"
        self.pages.setCurrentIndex(0)

    def create_patient_info_form(self):
        self.patient_info_form = QWidget()
        main_layout = QVBoxLayout(self.patient_info_form)

        # obj = {
        #     "patient_name" : QLineEdit()
        # }

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

        page_label = QLabel("Add Patient Info")
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

        self.test_name_label = QLabel("Test Name:")
        self.test_name = QComboBox()
        self.test_name.setFixedWidth(400)
        self.test_name.addItems(test["name"] for test in tests_list)

        self.test_type_label = QLabel("Test Type:")
        self.test_type = QComboBox()
        self.test_type.setFixedWidth(400)
        self.update_test_types()
        self.test_name.currentIndexChanged.connect(self.update_test_types)

        self.price_label = QLabel("Price:")
        self.price = QLineEdit()
        self.price.setReadOnly(True)
        self.update_test_price()
        self.test_type.currentIndexChanged.connect(self.update_test_price)
        self.scheduled_tests = []

        row_layout_0.addWidget(page_label)
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

        row_layout_4.addWidget(self.test_name_label)
        row_layout_4.addWidget(self.test_name)
        row_layout_4.addWidget(self.test_type_label)
        row_layout_4.addWidget(self.test_type)
        row_layout_4.addWidget(self.price_label)
        row_layout_4.addWidget(self.price)
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
        main_layout.addLayout(row_layout_0)
        main_layout.addLayout(form_layout)

        self.schedule_test_table = QTableWidget()
        self.schedule_test_table.setColumnCount(4)
        self.schedule_test_table.setHorizontalHeaderLabels(["Select", "Test Name", "Test Type", "Price"])
        header = self.schedule_test_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.schedule_test_table)

        self.pages.addWidget(self.patient_info_form)

    def create_test_results_form(self):
        self.test_results_form = QWidget()
        main_layout = QVBoxLayout(self.test_results_form)  # Attach main_layout to test_results_form directly

        # Form layout for input fields
        form_layout = QFormLayout()
        action_buttons_layout = QHBoxLayout()
        
        # Adding input fields to form layout
        self.case_no = QLineEdit()
        self.case_no.setReadOnly(True)
        form_layout.addRow("Case No:", self.case_no)

        self.test_name = QComboBox()
        self.test_name.addItems(test["name"] for test in tests_list)
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


        add_record = QPushButton("Add Record")
        add_record.clicked.connect(self.add_results_in_table)

        save_button = QPushButton("Save Records")
        save_button.clicked.connect(self.update_entry_into_db)


        action_buttons_layout.addWidget(add_record)
        action_buttons_layout.addWidget(save_button)
        form_layout.addRow(action_buttons_layout)

        # Add form layout to the main layout
        main_layout.addLayout(form_layout)

        # Create and add the QTableWidget outside the form layout
        self.schedule_test_table = QTableWidget()
        self.schedule_test_table.setColumnCount(7)
        self.schedule_test_table.setHorizontalHeaderLabels(["Select", "Test Name", "Test Type", "Min Value", "Max Value", "Unit", "Result"])
        header = self.schedule_test_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.schedule_test_table)  # Add the table as a widget

        delete_button = QPushButton("Remove Records")
        delete_button.clicked.connect(self.remove_results_from_table)
        main_layout.addWidget(delete_button)

        # Finally, add everything to the main page
        self.add_entry_page.addWidget(self.test_results_form)

    def swap_generate_report_forms(self, index):
        """Switch to the next form in the stack."""
        self.add_entry_page.setCurrentIndex(index)  # Switch to the next form (Test Results)
    
    def create_entry_into_db(self):
        """Initial Entry for saving patient info"""
        if not self.patient_name.text().strip():
            # Show error message if patient name is empty
            self.show_error_dialog("Error", "Patient name cannot be empty!")
            return
        if not self.scheduled_tests:
            # Show error message if patient name is empty
            self.show_error_dialog("Error", "No entries found for Scheduled test")
            return
        
        

        patient_data = {
            "patient_name": self.patient_name.text(),
            "father_husband_name": self.father_husband_name.text(),
            "age": self.age.text(),
            "gender": self.gender.currentText(),
            "nic_number": self.nic_number.text(),
            "address": self.address.text(),
            "registration_date": datetime.now(self.time_zone).strftime('%Y-%m-%d %H:%M:%S'),
            "registration_center": self.registration_center.text(),
            "specimen": self.specimen.currentText(),
            "consultant_name": self.consultant_name.currentText(),
            "scheduled_tests": json.dumps(self.scheduled_tests),  # JSON data as string
            "test_results": json.dumps([]),  # JSON data as string
        }
        try:
            self.cursor.execute("""
                INSERT INTO LabReport (
                    patient_name, father_husband_name, age, gender, nic_number,
                    address, registration_date, registration_center, specimen,
                    consultant_name, scheduled_tests, test_results
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(patient_data.values()))
            self.conn.commit()
            if self.cursor.lastrowid:
                self.show_error_dialog("Success", f"Case {self.cursor.lastrowid} registration successfull!")
        except Exception as e:
            self.show_error_dialog("Error", "Something went wrong, Try Again!")
            print(e)
            return
        # if self.cursor.lastrowid:
        #     self.case_no.setText(str(self.cursor.lastrowid))
        #     self.swap_generate_report_forms(index=1)

    def update_entry_into_db(self):
        """Save the test results added into test results list into db"""
        if not self.test_results_list:
            self.show_error_dialog("Error", "No records have been added!")
            return
        patient_data = {
            "test_results": json.dumps(self.test_results_list),  # JSON data as string
        }
        try:
            self.cursor.execute("""
                UPDATE LabReport 
                SET test_results = ? 
                WHERE id = ?
                """, (patient_data["test_results"], self.case_no.text()))
            self.conn.commit()
            self.show_error_dialog("Sucess", "Report saved successfully!")
        except Exception as e:
            self.show_error_dialog("Error", f"{e}")
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

    def update_test_measurements(self):
        """Update min_value, max_value and unit when the test type changes"""
        self.min_value.clear()
        self.max_value.clear()
        self.unit.clear()
        self.result.clear()

        selected_test_name = self.test_name.currentText()
        selected_test_type = self.test_type.currentText()

        for test in tests_list:
            if test["name"] == selected_test_name:
                for test_type in test["types"]:
                    if test_type["name"] == selected_test_type:
                        self.min_value.setText(test_type["minValue"])
                        self.max_value.setText(test_type["maxValue"])
                        self.unit.setText(test_type["unit"])
                        break

    def add_results_in_table(self):
        """Add the done test results in the table to view"""

        test = {
            "name": self.test_name.currentText(),
            "type": self.test_type.currentText(),
            "price": self.price.text(),
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
        self.schedule_test_table.setItem(row_position, 3, QTableWidgetItem(test["price"]))

        # Set text alignment for all columns with test data
        for column in range(1, self.schedule_test_table.columnCount()):
            item = self.schedule_test_table.item(row_position, column)
            if item:
                item.setTextAlignment(Qt.AlignCenter)

        # Optionally, clear the input fields after adding the result to the table
        # self.result.clear()

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
            self.show_error_dialog("Error", "Please select at least one record to delete.")
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


    def show_error_dialog(self, title, message):
        """Shows an error message box with the given title and message."""
        error_dialog = QMessageBox()
        error_dialog.setFixedWidth(400)
        if title == "Error":
            error_dialog.setIcon(QMessageBox.Critical)
        else:
            error_dialog.setIcon(QMessageBox.Information)
        error_dialog.setWindowIcon(QIcon("logo.png"))
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()

    def create_left_menu(self):
        # Create a dock widget for the menu
        self.left_menu = QDockWidget("Menu", self)
        self.left_menu.setAllowedAreas(Qt.LeftDockWidgetArea)  # Restrict to the left side

        # Create a widget for the dock content
        menu_widget = QWidget()
        menu_layout = QVBoxLayout(menu_widget)

        # Add a list of menu items
        menu_list = QListWidget()
        menu_list.addItem("Add Entry")
        menu_list.addItem("Generate Test")
        menu_list.addItem("Backup Data")

        # Set default selection to "Create Patient Record"
        menu_list.setCurrentRow(0)

        # Handle menu item selection
        menu_list.currentRowChanged.connect(self.pages.setCurrentIndex)

        # Add the menu list to the layout
        menu_layout.addWidget(menu_list)
        self.left_menu.setWidget(menu_widget)

        # Add the dock widget to the main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_menu)

    def submit_test_results(self):
        """Submit the test results to the database."""
        # Handle test results submission (similar to patient info submission)
        test_name = self.test_name.currentText()
        print(f"Test Name: {test_name}")  # Print to console for testing

        # Optionally clear the form after submission
        self.test_name.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
