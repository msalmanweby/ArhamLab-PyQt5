from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3

# Establish the connection to the database
connection = sqlite3.connect(os.environ["DATABASE_NAME"])

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

import pytz

time_zone = pytz.timezone('Asia/Karachi')