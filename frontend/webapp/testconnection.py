import pyodbc

server = r"202.140.137.225\STILDB,8181"
database = "Smart_Eye_Jute_STIL_Hastings_Live"
username = "ERP"
password = "ERP#SFactor"

conn_str = (
    f"DRIVER={{SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};PWD={password}"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Connected Successfully!")
except Exception as e:
    print("Error:", e)
