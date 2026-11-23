# Courier Management System (DBMS Project) - ParcelDB

An end-to-end relational database web application developed for Database Management System (DBMS) college coursework, lab practical examinations, and project viva presentations.

---

## 🌟 Key Database Highlights

Built strictly on **Relational Database Management System (RDBMS)** principles:

1. **3NF Normalized Relational Schema**:
   - `branches` (Hubs, service centres and pickup points)
   - `employees` (Staff, roles, shifts, salary, home branch)
   - `vehicles` (Fleet with capacity and live availability status)
   - `customers` (Registered senders with reward points tracking)
   - `service_types` (Pricing plans: base rate + rate per kg + delivery days)
   - `shipments` (Master booking linked to sender, two branches, service, agent and vehicle)
   - `tracking_events` (Many-to-Many junction between `shipments` and `branches`; one row per scan)
   - `audit_logs` (Automated audit trail populated by database triggers)

2. **Integrity & Constraints**:
   - **Primary Keys** (`AUTOINCREMENT`)
   - **Foreign Keys** with enforcement (`PRAGMA foreign_keys = ON;`)
   - **Referential Integrity Actions**: `ON DELETE CASCADE` (for `tracking_events`), `ON DELETE RESTRICT` (for `service_types`), `ON DELETE SET NULL` (for branches, staff, vehicles, customers)
   - **UNIQUE Constraints**: tracking numbers, phones, emails, vehicle numbers, branch codes
   - **CHECK Constraints**: `weight_kg > 0`, `capacity_kg > 0`, `salary > 0`, `total_charge >= 0`, and status lists such as `status IN ('Booked', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Returned', 'Cancelled')`.

3. **Database Views (`CREATE VIEW`)**:
   - `v_shipment_tracking_summary`: Joins shipments, customers, branches, service plans and agents with a scan count.
   - `v_service_analytics`: Shipments, total weight and revenue for every service plan.
   - `v_agent_performance`: Assigned vs delivered parcels and revenue handled by each delivery agent.

4. **Automated Database Triggers (`CREATE TRIGGER`)**:
   - `trg_after_shipment_insert_booked`: Creates the first "Booked" tracking scan and marks the assigned vehicle `On Route`.
   - `trg_after_tracking_event_insert_sync_status`: Every new scan automatically updates `shipments.status` (and `delivered_at`).
   - `trg_after_shipment_delivered`: On delivery, releases the vehicle and credits sender reward points (1 point per ₹100 charged).
   - `trg_after_shipment_delete`: Automatically logs deletions.

5. **Interactive Live SQL Query Lab**:
   - Web SQL console to type any SQL command (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`).
   - 8 Academic preset queries covering:
     - 6-table `INNER JOIN` (shipment manifest)
     - `LEFT OUTER JOIN` (service plans with zero shipments)
     - `GROUP BY` with `HAVING` (high-revenue routes)
     - Nested subquery with `NOT IN` (customers who never used Express Air)
     - Correlated subquery (shipments heavier than their plan average)
     - Conditional aggregation (agent success rate)
     - Views and set operations (`UNION`)
     - Real-time execution benchmark timer in milliseconds
     - One-click CSV export of query results

6. **Shipment Tracking**: search any tracking number (e.g. `PDB-2026-0004`) to see the full scan timeline.

---

## 🚀 How to Run the Project

### Prerequisites:
- Python 3.8+
- Flask (`pip install -r requirements.txt`)

### Steps:
1. Open terminal / command prompt in this directory.
2. Run the application:
   ```powershell
   python app.py
   ```
   *(Or simply double click `run.bat` on Windows)*

3. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

`courier.db` is created and seeded automatically if it is missing. Use **Reset DB** in the top bar to restore the sample data at any time.

### Regenerating the report
```powershell
python generate_report.py
```
This rebuilds `Project_Report.html` (all SQL outputs are executed live on a fresh in-memory copy of the database) and converts it to `Project_Report.pdf` using Edge/Chrome if installed. Set `LIVE_URL` / `GITHUB_URL` at the top of the script after you deploy.

### Deploying on Render
Push the project to GitHub, create a **Web Service** on Render from the repository (it will pick up `render.yaml`), build command `pip install -r requirements.txt`, start command `gunicorn app:app`.

---

## 📁 Project Structure

```text
courier_dbms_project/
│── app.py                 # Flask server & route handlers with raw SQL
│── database.py            # SQLite connection manager & query execution engine
│── schema.sql             # SQLite DDL script (tables, views, triggers, indexes)
│── seed.sql               # Clean sample courier data for demo
│── mysql_schema.sql       # MySQL / MariaDB compatible DDL script for XAMPP
│── courier.db             # Pre-built SQLite database (seeded)
│── generate_report.py     # Builds Project_Report.html / .pdf
│── run.bat                # Windows 1-click startup batch script
│── Procfile, render.yaml, requirements.txt   # Cloud deployment files
│── README.md              # Project documentation
└── templates/
    ├── base.html          # Main layout, Tailwind CSS, FontAwesome, navbar
    ├── index.html         # Dashboard with KPIs, fleet board, routes, revenue
    ├── shipments.html     # Booking, scans, payment, agent assignment
    ├── track.html         # Tracking search & scan timeline
    ├── services.html      # Service plan CRUD
    ├── branches.html      # Branch network
    ├── vehicles.html      # Fleet management
    ├── employees.html     # Employees & delivery agents
    ├── customers.html     # Customers & reward points
    ├── query_lab.html     # Interactive SQL terminal & 8 academic query presets
    ├── schema_viewer.html # ER overview, table columns, PK/FK viewer, SQL downloads
    └── audit_logs.html    # Automated trigger logs viewer
```

---

## 🎯 Academic SQL Queries Showcase

| Query Type | Concept Demonstrated | Example Target |
|---|---|---|
| **DQL (Select)** | Filter & Sort | `SELECT * FROM shipments WHERE weight_kg > 5 ORDER BY weight_kg DESC;` |
| **Multi-Table JOIN** | 6-table `INNER JOIN` | Shipments + Customers + 2 Branches + Service + Employee |
| **Outer Join** | `LEFT JOIN` with `IS NULL` | Service plans that have never been booked |
| **Aggregates** | `COUNT`, `SUM`, `AVG`, `MAX`, `MIN` | Revenue and weight per route / service plan |
| **Grouping & Filter** | `GROUP BY` with `HAVING` | Routes with total revenue > ₹500 |
| **Subqueries** | `NOT IN (SELECT ...)` | Customers who never booked Express Air |
| **Correlated Query** | Scalar subquery comparison | Shipments heavier than their service-plan average |
| **Set Operations** | `UNION` | Unified phone directory of customers, employees and branches |
| **Stored Views** | `CREATE VIEW` abstraction | Read from `v_service_analytics` |
| **Triggers** | `AFTER INSERT ON tracking_events` | Automatically syncs shipment status; releases vehicle & credits points on delivery |

---

## 🎓 Viva Questions & Answers (For Evaluation)

**Q1: Why is a `tracking_events` table needed in addition to the `shipments` table?**
> **Answer:** A shipment passes through many branches and a branch scans many shipments, which is a Many-to-Many (M:N) relationship. `tracking_events` resolves it into two 1:N relationships and stores scan-specific data such as `status`, `remarks` and `event_time`. It also removes the repeating group (`scan_1`, `scan_2`, ...) that would violate 1NF.

**Q2: What is the benefit of the trigger on `tracking_events`?**
> **Answer:** `trg_after_tracking_event_insert_sync_status` updates `shipments.status` whenever a scan is inserted, so the master record can never disagree with the latest scan, regardless of which application inserts the row. On `Delivered`, `trg_after_shipment_delivered` also frees the vehicle and credits reward points inside the database engine.

**Q3: How is referential integrity enforced on service plan deletion?**
> **Answer:** `shipments.service_id` references `service_types` with `ON DELETE RESTRICT`. A plan that has been used for any shipment cannot be deleted, protecting billing history, while deleting a shipment cascades to its tracking events.

**Q4: Why is the charge calculated on the server and not trusted from the browser?**
> **Answer:** The form shows a live estimate for convenience, but `app.py` recomputes `base_rate + rate_per_kg × weight_kg` from the database before the INSERT, so a tampered form value cannot change the price.
