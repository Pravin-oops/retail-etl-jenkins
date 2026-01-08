import oracledb
import os

# Database Configuration (From your Docker Compose service names)
# NOTE: Inside Docker, we use the service name 'oracle-db', not 'localhost'
DB_USER = 'RETAIL_DW'
DB_PASS = 'RetailPass123'
DB_DSN = 'oracle-db:1521/xepdb1' 

print("--- Connecting to Oracle Database ---")

try:
    # Connect in "Thin" mode (No Oracle Client required)
    connection = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cursor = connection.cursor()

    print("--- Executing Stored Procedure: pkg_etl_retail.load_daily_sales ---")
    
    # Call the stored procedure
    cursor.callproc("pkg_etl_retail.load_daily_sales")

    print("✅ Success! ETL Job Completed.")

except oracledb.Error as e:
    print(f"❌ Error connecting to Oracle: {e}")
    # Force Jenkins to fail if this script fails
    exit(1)

finally:
    if 'connection' in locals():
        connection.close()