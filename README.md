
---

# 🛒 Retail ETL Project (v3.0)

**Version:** 3.0 (Jenkins Automation)
**Release Date:** January 2026
**Architecture:** Automated CI/CD Pipeline (Jenkins) + Decoupled ELT (Oracle)

## 🚀 Overview

This project demonstrates a fully automated **Data Engineering Pipeline**. It evolves the manual "Run Scripts" approach of v2.0 into a professional **CI/CD Workflow** using Jenkins.

**Version 3.0 Major Upgrade:**

* **Automation:** A **Jenkins Pipeline** now orchestrates the entire flow (Data Generation → ETL Triggering).
* **Infrastructure as Code:** Jenkins is containerized and pre-configured with Python and Oracle drivers.
* **Local Development Loop:** Unique "Local Mount" strategy allows testing code changes instantly without waiting for Git pushes.

---

## 🏗️ Architecture Flow (v3.0)

1. **Trigger:** User clicks "Build Now" in Jenkins (Manual Trigger for Dev/Test).
2. **Sync (Stage 1):** Jenkins pulls the latest Python/SQL code directly from your local project folder.
3. **Generate (Stage 2):** Jenkins executes `generate_data.py` to create a synthetic CSV file (e.g., `sales_data_13012026.csv`).
4. **Process (Stage 3):** Jenkins executes `trigger_etl.py` to call the Oracle PL/SQL package.
5. **Load:** Oracle validates the file, archives it to the **Raw Vault**, and loads the **Star Schema**.

---

## 📂 Project Structure

```text
retail-etl-jenkins/
├── data/                        # Shared Volume: CSV files land here
├── script/
│   ├── generate_data.py         # [Auto] Generates daily data
│   └── trigger_etl.py           # [New] Python bridge to trigger PL/SQL
├── sql/
│   ├── 00_archive_table_DDL.sql # [Run Once] Creates Raw Vault
│   ├── 01_setup_users.sql       # [Run Once] Creates RETAIL_DW user
│   ├── 02_directory_creation.sql# [Run Once] Maps /data volume
│   ├── 03_ddl_tables.sql        # [Run Once] Creates Fact/Dim tables
│   └── 04_plsql_pkg.sql         # [Logic] Main ETL Package
├── Jenkinsfile                  # [New] Defines the CI/CD Pipeline
├── docker-compose.yml           # [Updated] Services: Oracle + Jenkins
├── dockerfile                   # [New] Custom Jenkins Image (w/ Python & OracleDB)
└── README.md

```

---

## ⚙️ Setup Instructions

### 1. Infrastructure Setup

Start the containerized environment (Oracle Database + Jenkins Server).

```bash
docker-compose up -d --build

```

* **Oracle DB:** Port `1521` (Persistent Data in `oracle_data` volume)
* **Jenkins:** Port `8080` (Persistent Home in `jenkins_home` folder)

### 2. Database Initialization (Run Once)

Since this is a fresh setup, you must initialize the database objects.

**A. System Setup (Run as SYSTEM)**

```sql
@sql/01_setup_users.sql
@sql/02_directory_creation.sql

```

**B. Application Setup (Run as RETAIL_DW)**

```sql
@sql/00_archive_table_DDL.sql
@sql/03_ddl_tables.sql
@sql/04_plsql_pkg.sql

```

---

## 🤖 Jenkins Configuration (First Run)

### 1. Unlock Jenkins

1. Open `http://localhost:8080` in your browser.
2. Get the Admin Password from your terminal:
```bash
docker exec retail_jenkins cat /var/jenkins_home/secrets/initialAdminPassword

```


3. Paste the password and click **Continue**.
4. Select **"Install Suggested Plugins"**.

### 2. Create the Pipeline Job

1. **Dashboard** > **New Item**.
2. **Name:** `Retail-ETL-Pipeline`.
3. **Type:** Select **Pipeline** and click **OK**.
4. Scroll down to the **Pipeline** section.
5. **Definition:** Select `Pipeline script`.
6. **Script:** Copy the content of the `Jenkinsfile` from your project folder and paste it here.
* *Note: We paste it manually because we are using the "Local Mount" strategy for faster development.*


7. Click **Save**.

---

## ▶️ How to Run the Pipeline

1. Go to the **Retail-ETL-Pipeline** dashboard.
2. Click **Build Now** on the left menu.
3. Watch the **Stage View** progress bars:
* ✅ **0. Sync Local Code:** Copies your latest script edits.
* ✅ **1. Generate Data:** Creates today's sales CSV.
* ✅ **2. Run ETL:** Triggers the Oracle Stored Procedure.



---

## 📊 Validation

To confirm the pipeline worked, run these queries in your SQL Client (e.g., SQL Developer, DBeaver) connected to `localhost:1521` as `RETAIL_DW`.

### 1. Check the Job History (Raw Vault)

Confirm that a new batch was created and the file was archived.

```sql
SELECT batch_id, source_file, archived_at, count(*) as row_count 
FROM raw_sales_archive 
GROUP BY batch_id, source_file, archived_at 
ORDER BY batch_id DESC;

```

### 2. Check the Business Data (Star Schema)

Confirm the data landed in the analytics tables.

```sql
SELECT * FROM fact_sales ORDER BY sales_id DESC FETCH FIRST 10 ROWS ONLY;

```

---

## 🔮 Future

* [ ] **Airflow Orchestration:** Migrating the workflow to Apache Airflow to handle complex dependencies and retries as a different repository.
* [ ] **Advanced Logging:** Storing execution logs in a dedicated database table.
* [ ] **Efficient Filtering:** Currently we get 95% of the data to fact sales data, further improvement on filtering logic might be added as we progress on Airflow migration

---

**Author:** Pravin
**Mail:** pravin.puducherry@gmail.com