import sqlite3

# Establish the connection to the database
connection = sqlite3.connect('your_database.db')

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

import pytz

time_zone = pytz.timezone('Asia/Karachi')