
---

# 🛒 Retail ETL Project (v3.0)

**Version:** 3.0 (Jenkins CI/CD + Zero Data Loss)
**Release Date:** January 2026
**Architecture:** Automated Pipeline (Jenkins) + Oracle ELT + Persistent Error Logging

## 🚀 Overview

This project represents the final evolution of the Retail ETL Pipeline. It implements a production-grade **CI/CD Workflow** that guarantees **Zero Data Loss**.

**Version 3.0 Key Features:**

* **Automated Orchestration:** A containerized Jenkins pipeline manages the entire lifecycle (Code Sync → Data Generation → ETL Execution).
* **Zero Data Loss Architecture:** * **Raw Vault:** 100% of incoming data is archived immediately before processing.
* **Error Trapping:** Invalid rows (e.g., Missing Categories, System Errors) are captured in a persistent `ERR_SALES_REJECTS` table instead of being lost.


* **Idempotency:** A smart schema reset utility (`data_truncate.py`) ensures the pipeline can be re-run safely without creating duplicate data in the analysis layer.

---

## 🏗️ Architecture Flow

1. **Trigger:** Manual Build in Jenkins (One-Click Deployment).
2. **Sync (Stage 0):** Jenkins pulls the latest Python & SQL code from the local development environment.
3. **Reset (Stage 1):** Executes `data_truncate.py` to wipe the Analysis Layer (`fact_sales`, dimensions) while strictly preserving the **Raw Vault** and **Error History**.
4. **Generate (Stage 2):** Python script generates synthetic retail data (including 5% "Bad Data" to test error handling).
5. **Process (Stage 3):** Oracle PL/SQL Package (`pkg_etl_retail`):
* **Archive:** Copies every row to `RAW_SALES_ARCHIVE` (The Time Machine).
* **Validate:** Filters out rows with missing categories or data quality issues.
* **Load:** Inserts valid rows into the Star Schema (`FACT_SALES`).
* **Reject:** Inserts invalid rows into `ERR_SALES_REJECTS` for auditing.



---

## 📂 Project Structure

```text
retail-etl-jenkins/
├── data/                        # Shared Volume: CSV files land here
├── script/
│   ├── generate_data.py         # [Auto] Generates data (95% Valid / 5% Invalid)
│   ├── trigger_etl.py           # [Auto] Python bridge to trigger PL/SQL
│   └── data_truncate.py         # [Util] Smart SQL Runner to reset schema safely
├── sql/
│   ├── 00_archive_table_DDL.sql # [Run Once] Creates PERMANENT Vault & Error Tables
│   ├── 01_setup_users.sql       # [Run Once] Creates RETAIL_DW user
│   ├── 02_directory_creation.sql# [Run Once] Maps /data volume
│   ├── 03_ddl_tables.sql        # [Daily] Resets Fact/Dim tables (Analysis Layer)
│   └── 04_plsql_pkg.sql         # [Logic] Main ETL with Error Handling logic
├── Jenkinsfile                  # [Pipeline] Defines the 4-Stage CI/CD Flow
├── docker-compose.yml           # [Infra] Services: Oracle XE + Jenkins
├── dockerfile                   # [Infra] Custom Jenkins Image (w/ Python & OracleDB)
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

You must initialize the system and permanent storage tables.

**A. System Setup (Run as SYSTEM)**

```sql
@sql/01_setup_users.sql
@sql/02_directory_creation.sql
```

**B. Permanent Storage Setup (Run as RETAIL_DW)**
*Crucial: This creates the tables that must never be dropped (Vault & Errors).*

```sql
@sql/00_archive_table_DDL.sql
```

**C. Application Setup (Run as RETAIL_DW)**

```sql
@sql/03_ddl_tables.sql
@sql/04_plsql_pkg.sql
```

---

## 🤖 Jenkins Configuration

1. **Unlock Jenkins:** Retrieve the initial password:
```bash
docker exec retail_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```


2. **Create Job:** New Item -> Pipeline -> Name: `Retail-ETL-Pipeline`.
3. **Pipeline Script:** Copy content from `Jenkinsfile` in your project folder.
4. **Run:** Click **Build Now**.

---

## 📊 Validation & Auditing

Run these queries in your SQL Client to verify the pipeline's logic.

### 1. Verify "Zero Data Loss" Split

Confirm that the total rows generated match the sum of Valid + Rejected rows.

```sql
SELECT 
    (SELECT count(*) FROM fact_sales) AS "Valid Rows (Analysis)",
    (SELECT count(*) FROM err_sales_rejects) AS "Rejected Rows (Audit)",
    (SELECT count(*) FROM raw_sales_archive WHERE batch_id = (SELECT max(batch_id) FROM raw_sales_archive)) AS "Total Vault Rows"
FROM dual;
```

### 2. Analyze Rejections

Check the `ERR_SALES_REJECTS` table to understand why data was excluded from the report.

```sql
SELECT reason, count(*) 
FROM err_sales_rejects 
GROUP BY reason;
```

*Expected Output:* `Data Quality: Missing Category` (approx 50 rows).

---

## 🔮 Roadmap (Next Phase)

* [ ] **Apache Airflow:** Migrate orchestration to Airflow DAGs for complex dependency management (New repository).
* [ ] **Email Alerts:** Configure notification triggers for high rejection rates.

---

**Author:** Pravin
**Contact:** pravin.puducherry@gmail.com