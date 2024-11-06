import sys
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QDockWidget, 
    QListWidget, 
    QLabel, 
    QVBoxLayout, 
    QFormLayout, 
    QLineEdit, 
    QComboBox, 
    QWidget, 
    QStackedWidget, 
    QPushButton,
    QHBoxLayout
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
        self.showFullScreen()
        # screen_rect = QDesktopWidget().screenGeometry()
        # self.resize(screen_rect.width(), screen_rect.height())

        # Create the stacked widget for pages
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
                consultant_name TEXT
            )
        """)
        self.conn.commit()

    def create_pages(self):
        self.generate_report_page = QStackedWidget()
        self.create_patient_info_form()
        self.create_test_results_form()

        # Add the pages to the QStackedWidget
        self.pages.addWidget(self.generate_report_page)   # index 0
        # self.pages.addWidget(self.test_results_form)   # index 1

        # Additional placeholder pages
        self.search_patient_record_page = QLabel("This is the Search Patient Record page")
        self.view_test_results_page = QLabel("This is the View Test Results page")
        self.generate_test_report_page = QLabel("This is the Generate Test Report page")
        self.billing_payments_page = QLabel("This is the Billing and Payments page")
        self.backup_data_page = QLabel("This is the Backup Data page")

        # Add the other pages to the QStackedWidget
        self.pages.addWidget(self.search_patient_record_page)    # index 2
        self.pages.addWidget(self.view_test_results_page)        # index 3
        self.pages.addWidget(self.generate_test_report_page)     # index 4
        self.pages.addWidget(self.billing_payments_page)         # index 5
        self.pages.addWidget(self.backup_data_page)              # index 6

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
        proceed_button.clicked.connect(lambda: self.swap_generate_report_forms(index=1))
        form_layout.addRow(proceed_button)

        self.generate_report_page.addWidget(self.patient_info_form)

    def create_test_results_form(self):
        self.test_results_form = QWidget()
        form_layout = QFormLayout(self.test_results_form)
        action_buttons_layout = QHBoxLayout()
        
        self.test_name = QComboBox()
        self.test_name.addItems(test["name"] for test in tests_list)
        form_layout.addRow("Test Name:", self.test_name)

        self.test_type = QComboBox()
        form_layout.addRow("Test Type:", self.test_type)
        self.update_test_types()
        self.test_name.currentIndexChanged.connect(self.update_test_types)

        self.min_value = QLineEdit()
        form_layout.addRow("Minimum Value:", self.min_value)

        self.max_value = QLineEdit()
        form_layout.addRow("Minimum Value:", self.max_value)

        self.unit = QLineEdit()
        form_layout.addRow("Unit:", self.unit)

        self.result = QLineEdit()
        form_layout.addRow("Result:", self.result)

        self.update_test_measurements()
        self.test_type.currentIndexChanged.connect(self.update_test_measurements)

        backward_button = QPushButton("Previous")
        backward_button.clicked.connect(lambda: self.swap_generate_report_forms(index=0))

        add_record = QPushButton("Add Record")
        add_record.clicked.connect(self.submit_test_results)

        action_buttons_layout.addWidget(backward_button)
        action_buttons_layout.addWidget(add_record)
        form_layout.addRow(action_buttons_layout)

        self.generate_report_page.addWidget(self.test_results_form)

    def swap_generate_report_forms(self, index):
        """Switch to the next form in the stack."""
        self.generate_report_page.setCurrentIndex(index)  # Switch to the next form (Test Results)

    def update_test_types(self): 
        self.test_type.clear()
        selected_test_name = self.test_name.currentText()
        for test in tests_list:
            if test["name"] == selected_test_name:
                self.test_type.addItems(test_type["name"] for test_type in test["types"])
                break
    
    def update_test_measurements(self):
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
                        
    def create_left_menu(self):
        # Create a dock widget for the menu
        self.left_menu = QDockWidget("Menu", self)
        self.left_menu.setAllowedAreas(Qt.LeftDockWidgetArea)  # Restrict to the left side

        # Create a widget for the dock content
        menu_widget = QWidget()
        menu_layout = QVBoxLayout(menu_widget)

        # Add a list of menu items
        menu_list = QListWidget()
        menu_list.addItem("Create Patient Record")
        menu_list.addItem("Search Patient Record")
        menu_list.addItem("View Test Results")
        menu_list.addItem("Generate Test Report")
        menu_list.addItem("Billing and Payments")
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
