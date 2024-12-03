from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import sys

def resource_path(relative_path):
    try:
        # PyInstaller's temporary folder during runtime
        base_path = sys._MEIPASS
    except Exception:
        # Base path for a regular Python script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

db_path = resource_path("data\\lab_reports.db")
# Establish the connection to the database
connection = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

import pytz

time_zone = pytz.timezone('Asia/Karachi')