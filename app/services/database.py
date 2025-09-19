import pyodbc

conn = pyodbc.connect("DSN=NetSuite;UID=mnetsuite.webservice@biobridgeglobal.org;PWD=BBGNetsuite@2025")

cursor = conn.cursor()
cursor.execute("SELECT tranid from transactions where id = 3804715")

for row in cursor.fetchall():
    print(row)
