from sql_guard import validate_sql

# Valid SQL
sql_ok = "SELECT TOP (200) * FROM AttendanceReport WHERE ECode = ?"
print(validate_sql(sql_ok))

# Invalid SQL (should fail)
sql_bad = "DELETE FROM AttendanceReport"
print(validate_sql(sql_bad))
