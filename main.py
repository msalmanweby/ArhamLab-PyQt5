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
    QCheckBox
)
from PyQt5.QtGui import QIcon
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
                test_results TEXT
            )
        """)
        self.conn.commit()

    def create_pages(self):
        self.add_entry_page = QStackedWidget()
        self.create_patient_info_form()
        self.create_test_results_form()

        self.pages.addWidget(self.add_entry_page)

        # Add the other pages to the QStackedWidget
               

        # Set the initial page to "Create Patient Record"
        self.pages.setCurrentIndex(0)

    def create_patient_info_form(self):
        self.patient_info_form = QWidget()
        form_layout = QFormLayout(self.patient_info_form)

        # Add input fields
        self.patient_name = QLineEdit()
        form_layout.addRow("Patient Name:", self.patient_name)

        self.father_husband_name = QLineEdit()
        form_layout.addRow("Father/Husband Name:", self.father_husband_name)

        self.age = QLineEdit()
        form_layout.addRow("Age:", self.age)

        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female", "Other"])
        form_layout.addRow("Gender:", self.gender)

        self.nic_number = QLineEdit()
        form_layout.addRow("NIC Number:", self.nic_number)

        self.address = QLineEdit()
        form_layout.addRow("Address:", self.address)

        self.registration_center = QLineEdit()
        form_layout.addRow("Registration Center:", self.registration_center)

        self.specimen = QLineEdit()
        form_layout.addRow("Specimen:", self.specimen)

        self.consultant_name = QLineEdit()
        form_layout.addRow("Consultant Name:", self.consultant_name)

        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.create_entry_into_db)
        form_layout.addRow(proceed_button)

        self.add_entry_page.addWidget(self.patient_info_form)

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

        # Action buttons
        backward_button = QPushButton("Previous")
        backward_button.clicked.connect(lambda: self.swap_generate_report_forms(index=0))

        add_record = QPushButton("Add Record")
        add_record.clicked.connect(self.add_results_in_table)

        action_buttons_layout.addWidget(backward_button)
        action_buttons_layout.addWidget(add_record)
        form_layout.addRow(action_buttons_layout)

        # Add form layout to the main layout
        main_layout.addLayout(form_layout)

        # Create and add the QTableWidget outside the form layout
        self.test_results_table = QTableWidget()
        self.test_results_table.setColumnCount(7)
        self.test_results_table.setHorizontalHeaderLabels(["Select", "Test Name", "Test Type", "Min Value", "Max Value", "Unit", "Result"])
        header = self.test_results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.test_results_table)  # Add the table as a widget

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
        
        self.test_results_list = []

        patient_data = {
            "patient_name": self.patient_name.text(),
            "father_husband_name": self.father_husband_name.text(),
            "age": self.age.text(),
            "gender": self.gender.currentText(),
            "nic_number": self.nic_number.text(),
            "address": self.address.text(),
            "registration_date": datetime.now(self.time_zone).strftime('%Y-%m-%d %H:%M:%S'),
            "registration_center": self.registration_center.text(),
            "specimen": self.specimen.text(),
            "consultant_name": self.consultant_name.text(),
            "test_results": json.dumps(self.test_results_list),  # JSON data as string
        }
        self.cursor.execute("""
            INSERT INTO LabReport (
                patient_name, father_husband_name, age, gender, nic_number,
                address, registration_date, registration_center, specimen,
                consultant_name, test_results
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(patient_data.values()))
        self.conn.commit()
        if self.cursor.lastrowid:
            self.case_no.setText(str(self.cursor.lastrowid))
            self.swap_generate_report_forms(index=1)

    def update_test_types(self):
        """Update the test type options the test name changes""" 
        self.test_type.clear()
        selected_test_name = self.test_name.currentText()
        for test in tests_list:
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
        if not self.result.text().strip():
            # Show error message if the result field is empty
            self.show_error_dialog("Error", "Please enter the test results")
            return

        test_result = {
            "name": self.test_name.currentText(),
            "type": self.test_type.currentText(),
            "minValue": self.min_value.text(),
            "maxValue": self.max_value.text(),
            "unit": self.unit.text(),
            "result": self.result.text()
        }

        self.test_results_list.append(test_result)
        row_position = self.test_results_table.rowCount()

        # Insert a new row
        self.test_results_table.insertRow(row_position)

        # Create a checkbox widget for row selection (first column)
        checkbox_widget = QWidget()
        checkbox = QCheckBox()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignCenter)  # Center the checkbox in the cell
        checkbox_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
        self.test_results_table.setCellWidget(row_position, 0, checkbox_widget)

        # Set the checkbox column width
        self.test_results_table.setColumnWidth(0, 30)

        # Insert the test data in the remaining columns (starting from column 1)
        self.test_results_table.setItem(row_position, 1, QTableWidgetItem(test_result["name"]))
        self.test_results_table.setItem(row_position, 2, QTableWidgetItem(test_result["type"]))
        self.test_results_table.setItem(row_position, 3, QTableWidgetItem(test_result["minValue"]))
        self.test_results_table.setItem(row_position, 4, QTableWidgetItem(test_result["maxValue"]))
        self.test_results_table.setItem(row_position, 5, QTableWidgetItem(test_result["unit"]))
        self.test_results_table.setItem(row_position, 6, QTableWidgetItem(test_result["result"]))

        # Set text alignment for all columns with test data
        for column in range(1, self.test_results_table.columnCount()):
            item = self.test_results_table.item(row_position, column)
            if item:
                item.setTextAlignment(Qt.AlignCenter)

        # Optionally, clear the input fields after adding the result to the table
        self.result.clear()

    def remove_results_from_table(self):
        """Delete rows that are selected via checkboxes"""
        rows_to_delete = []
        
        # Check which rows are selected for deletion
        for row in range(self.test_results_table.rowCount()):
            checkbox_widget = self.test_results_table.cellWidget(row, 0)  # The checkbox is in the first column
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
            del self.test_results_list[row]

            # Remove the row from the table
            self.test_results_table.removeRow(row)

    def show_error_dialog(self, title, message):
        """Shows an error message box with the given title and message."""
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
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
