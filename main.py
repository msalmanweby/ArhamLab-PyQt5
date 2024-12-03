import sys
import pytz
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QDockWidget, 
    QListWidget, 
    QVBoxLayout,  
    QWidget, 
    QStackedWidget, 
    QDesktopWidget,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from page_modules import PatientInfoPage, AddResultsPage
from app_config import cursor, connection, resource_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlArham Laboratory")
        self.setWindowIcon(QIcon(resource_path("assets\\icon.png")))
        self.time_zone = pytz.timezone('Asia/Karachi')
        screen_rect = QDesktopWidget().screenGeometry()
        self.resize(screen_rect.width(), screen_rect.height())
        # Maximize the window
        self.showMaximized()

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.patient_info_page = PatientInfoPage()
        self.add_results_page = AddResultsPage()
        # Set the initial page to "Create Patient Record"
        self.pages.addWidget(self.patient_info_page)
        self.pages.addWidget(self.add_results_page)
        self.pages.setCurrentIndex(0)

        # Create the left menu
        self.create_left_menu()

        # Initialize Database
        self.init_db()

    def init_db(self):
        """Initialize SQLite database and create tables if not exists."""

        # Create LabReport table if it doesn't exist
        cursor.execute(""" 
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
                test_results TEXT,
                phone_number TEXT
            )
        """)
        connection.commit()

    

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

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
