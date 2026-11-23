import base64
import html as htmllib
import os
import shutil
import sqlite3
import subprocess
import sys

# ---- Fill these in after you deploy / push to GitHub (leave empty to omit) ----
LIVE_URL = ""      # e.g. "https://courier-dbms.onrender.com"
GITHUB_URL = ""    # e.g. "https://github.com/<user>/courier-dbms-project"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'report_assets')
HTML_OUTPUT = os.path.join(BASE_DIR, 'Project_Report.html')
PDF_OUTPUT = os.path.join(BASE_DIR, 'Project_Report.pdf')

with open(os.path.join(ASSETS_DIR, 'extracted_0_Image18.png'), 'rb') as f:
    b64_header = base64.b64encode(f.read()).decode('utf-8')

with open(os.path.join(ASSETS_DIR, 'extracted_1_Image20.png'), 'rb') as f:
    b64_logo = base64.b64encode(f.read()).decode('utf-8')

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DBMS Project Report - Courier Management System</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 18mm 20mm 18mm;
            @bottom-right {{
                content: counter(page);
                font-family: 'Times New Roman', Times, serif;
                font-size: 10pt;
            }}
        }}
        @page:first {{
            margin: 0;
            @bottom-right {{
                content: normal;
            }}
        }}
        
        * {{
            box-sizing: border-box;
            color: #000000 !important;
        }}

        body {{
            font-family: 'Times New Roman', Times, serif;
            color: #000000;
            line-height: 1.5;
            margin: 0;
            padding: 0;
            background-color: #ffffff;
            font-size: 12pt;
        }}
        
        .page-break {{
            page-break-before: always;
            break-before: page;
        }}

        /* B&W Logo Styling */
        .bw-logo {{
            filter: grayscale(100%) contrast(120%);
            -webkit-filter: grayscale(100%) contrast(120%);
        }}

        /* Cover Page Styling */
        .cover-page {{
            width: 100%;
            height: 100vh;
            min-height: 297mm;
            box-sizing: border-box;
            padding: 24mm 24mm 20mm 24mm;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            text-align: center;
            background: #ffffff;
        }}
        
        .top-banner img {{
            max-width: 95%;
            height: auto;
            max-height: 60px;
            object-fit: contain;
        }}
        
        .prog-title {{
            margin-top: 16px;
            font-size: 14pt;
            font-weight: bold;
            color: #000000;
            letter-spacing: 0.5px;
        }}
        .dept-title {{
            font-size: 14pt;
            font-weight: bold;
            color: #000000;
            margin-top: 2px;
        }}
        
        .file-title {{
            font-size: 14pt;
            font-weight: bold;
            color: #000000;
            margin-top: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .file-on {{
            font-size: 12pt;
            font-style: italic;
            color: #000000;
            margin: 3px 0;
        }}
        .course-title {{
            font-size: 14pt;
            font-weight: bold;
            color: #000000;
        }}
        .course-code {{
            font-size: 12pt;
            font-weight: bold;
            color: #000000;
            margin-top: 3px;
        }}
        .batch-text {{
            font-size: 12pt;
            font-weight: bold;
            color: #000000;
            margin-top: 3px;
        }}

        .award-subtext {{
            font-size: 11pt;
            color: #000000;
            max-width: 520px;
            margin: 14px auto 8px auto;
            line-height: 1.4;
        }}
        
        .center-logo img {{
            width: 175px;
            height: 155px;
            object-fit: contain;
            margin: 8px 0;
        }}
        
        .submission-grid {{
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-top: 14px;
            text-align: left;
            font-size: 12pt;
        }}
        .submit-to {{
            text-align: left;
        }}
        .submit-by {{
            text-align: right;
        }}
        .sub-header {{
            font-weight: bold;
            font-size: 13pt;
            color: #000000;
            margin-bottom: 4px;
            text-decoration: underline;
        }}
        .sub-name {{
            font-size: 12pt;
            font-weight: bold;
            color: #000000;
        }}
        .sub-roll {{
            font-size: 11pt;
            color: #000000;
        }}

        .cover-footer {{
            margin-top: 14px;
            border-top: 1px solid #000000;
            padding-top: 8px;
            width: 100%;
            text-align: center;
            font-size: 11pt;
            font-weight: bold;
            color: #000000;
            line-height: 1.4;
        }}

        /* Document Body Styling */
        .report-content {{
            padding: 8mm 10mm;
        }}
        
        /* All Headings kept at 14pt */
        h1.chap-heading {{
            font-size: 14pt;
            font-weight: bold;
            color: #000000;
            margin-top: 24px;
            margin-bottom: 12px;
            text-transform: uppercase;
            page-break-after: avoid;
        }}
        
        h2.sec-heading {{
            font-size: 14pt;
            font-weight: bold;
            color: #000000;
            margin-top: 18px;
            margin-bottom: 8px;
            text-decoration: underline;
            page-break-after: avoid;
        }}

        h3.subsec-heading {{
            font-size: 14pt;
            font-weight: bold;
            color: #000000;
            margin-top: 14px;
            margin-bottom: 4px;
            page-break-after: avoid;
        }}

        p, li {{
            font-size: 12pt;
            text-align: justify;
            margin: 6px 0 10px 0;
            line-height: 1.55;
            color: #000000;
        }}

        ul {{
            margin: 6px 0 12px 20px;
        }}

        /* Tables ONLY retain borders/boxes as requested */
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0 16px 0;
            font-size: 11pt;
            page-break-inside: avoid;
        }}
        table.data-table th, table.data-table td {{
            border: 1px solid #000000;
            padding: 6px 8px;
            text-align: left;
            color: #000000;
        }}
        table.data-table th {{
            background-color: #f2f2f2;
            font-weight: bold;
            border-bottom: 2px solid #000000;
        }}
        table.data-table tr:nth-child(even) {{
            background-color: #fafafa;
        }}

        /* Code block box removed - clean indented monospace text */
        pre.sql-code {{
            background-color: transparent;
            color: #000000;
            padding: 4px 0 4px 14px;
            border: none;
            border-left: 2px solid #000000;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10.5pt;
            overflow-x: auto;
            white-space: pre-wrap;
            line-height: 1.45;
            margin: 8px 0 14px 0;
            page-break-inside: avoid;
        }}

        /* Callout box removed - clean indented text */
        .callout-box {{
            background-color: transparent;
            border: none;
            padding: 4px 0;
            font-size: 12pt;
            color: #000000;
            margin: 10px 0;
        }}

        /* Certificate card box removed - clean formal page layout */
        .cert-card {{
            border: none;
            padding: 10px 0;
            margin: 15px 0;
            background: transparent;
        }}
    </style>
</head>
<body>

    <!-- ==================== COVER PAGE ==================== -->
    <div class="cover-page">
        <!-- Top SGT University Header Banner with NAAC A+ in Grayscale -->
        <div class="top-banner">
            <img class="bw-logo" src="data:image/png;base64,{b64_header}" alt="SGT University Logo">
        </div>

        <div>
            <div class="prog-title">Bachelor of Technology</div>
            <div class="dept-title">Computer Science &amp; Engineering</div>

            <div class="file-title">Project Report</div>
            <div class="file-on">on</div>
            <div class="course-title">Course :- Database Management System</div>
            <div class="course-code">Course Code: – 130203144</div>
            <div class="batch-text">Batch :– 2025-29</div>

            <div class="award-subtext">
                Submitted in partial fulfillment of requirements<br>
                for the award of the degree of Bachelor of Technology in Computer Science &amp; Engineering
            </div>
        </div>

        <!-- Center SGT Crest Logo in Grayscale -->
        <div class="center-logo">
            <img class="bw-logo" src="data:image/png;base64,{b64_logo}" alt="SGT University Crest">
        </div>

        <!-- Submission Block -->
        <div class="submission-grid">
            <div class="submit-to">
                <div class="sub-header">Submitted To:</div>
                <div class="sub-name">Dr. Satnam Kaur</div>
                <div style="font-size: 11pt;">Assistant Professor / Faculty</div>
                <div style="font-size: 11pt;">Department of CSE</div>
            </div>
            <div class="submit-by">
                <div class="sub-header">Submitted By:</div>
                <div class="sub-name">Krish Dahiya</div>
                <div class="sub-roll">Roll No: 251302308</div>
                <div class="sub-name" style="margin-top: 6px;">Mannat</div>
                <div class="sub-roll">Roll No: 251302109</div>
                <div class="sub-name" style="margin-top: 6px;">Riya</div>
                <div class="sub-roll">Roll No: 251302200</div>
            </div>
        </div>

        <!-- Bottom Department / University Footnote -->
        <div class="cover-footer">
            School of Engineering &amp; Technology Department of<br>
            Computer Science &amp; Engineering<br>
            Sgt University Gurugram<br>
            July-Dec 2026
        </div>
    </div>

    <!-- ==================== BODY CONTENT ==================== -->
    <div class="report-content">

        <!-- Page 2: Certificate of Authenticity (Box removed) -->
        <div class="page-break"></div>
        <h1 class="chap-heading">Certificate of Authenticity</h1>
        <div class="cert-card">
            <p style="font-size: 12pt; line-height: 1.8;">
                This is to certify that the project entitled <strong>"Courier Management System (ParcelDB)"</strong> has been successfully carried out and submitted by <strong>Krish Dahiya (Roll No. 251302308)</strong>, <strong>Mannat (Roll No. 251302109)</strong> and <strong>Riya (Roll No. 251302200)</strong>, students of <strong>Bachelor of Technology in Computer Science &amp; Engineering</strong>, Batch <strong>2025-29</strong>, SGT University Gurugram, in partial fulfillment of the academic requirements for the course <strong>Database Management System (Course Code: 130203144)</strong> during the session <strong>July-Dec 2026</strong>.
            </p>
            <p style="font-size: 12pt; line-height: 1.8;">
                The project embodies an original work focusing on 3NF Relational Database Design, Automated Engine Triggers, Stored Database Views, Comprehensive CRUD Operations, and Cloud-Ready Deployment under my supervision and guidance.
            </p>
            
            <div style="margin-top: 60px; display: flex; justify-content: space-between; align-items: flex-end;">
                <div>
                    <p style="font-weight: bold; margin-bottom: 2px;">Date: ________________</p>
                    <p style="font-weight: bold; margin-top: 0;">Place: Gurugram, Haryana</p>
                </div>
                <div style="text-align: right;">
                    <p style="font-weight: bold; margin-bottom: 2px;">______________________________</p>
                    <p style="font-weight: bold; margin-top: 0; font-size: 12pt;">Dr. Satnam Kaur</p>
                    <p style="font-size: 11pt; margin: 0;">Department of Computer Science &amp; Engineering</p>
                    <p style="font-size: 11pt; margin: 0;">School of Engineering &amp; Technology, SGT University</p>
                </div>
            </div>
        </div>

        <!-- Page 3: Acknowledgement (Dedicated Page) -->
        <div class="page-break"></div>
        <h1 class="chap-heading">Acknowledgement</h1>
        <div style="margin-top: 20px; font-size: 12pt; line-height: 1.85;">
            <p>
                We express our deepest sense of gratitude and sincere thanks to our respected project mentor, <strong>Dr. Satnam Kaur</strong>, Assistant Professor, Department of Computer Science &amp; Engineering, for her invaluable guidance, visionary suggestions, constructive critiques, and continuous encouragement throughout the development of the <strong>Courier Management System (ParcelDB)</strong>.
            </p>
            <p>
                Her intellectual support and insightful advice provided us with immense clarity regarding complex relational database concepts, including 3NF normalization, constraint design, and automated trigger logic.
            </p>
            <p>
                We would also like to express our heartfelt gratitude to the <strong>Head of the Department</strong> and the faculty members of the <strong>Department of Computer Science &amp; Engineering</strong>, as well as the <strong>School of Engineering &amp; Technology, SGT University Gurugram</strong>, for their constant support and for providing state-of-the-art laboratory infrastructure and computing resources.
            </p>
            <p>
                Finally, we thank our parents, classmates, and peers whose encouragement and moral support enabled us to successfully conclude this project within the stipulated academic timeline.
            </p>
        </div>
        
        <div style="margin-top: 65px; display: flex; justify-content: flex-end;">
            <div style="text-align: right; font-size: 12pt; line-height: 1.6;">
                <p style="font-weight: bold; margin-top: 0px; margin-bottom: 3px;">Krish Dahiya</p>
                <p style="margin: 0; font-size: 11pt;">Roll No: 251302308</p>
                <p style="font-weight: bold; margin-top: 14px; margin-bottom: 3px;">Mannat</p>
                <p style="margin: 0; font-size: 11pt;">Roll No: 251302109</p>
                <p style="font-weight: bold; margin-top: 14px; margin-bottom: 3px;">Riya</p>
                <p style="margin: 0; font-size: 11pt;">Roll No: 251302200</p>
                <p style="font-size: 11pt; margin-top: 10px;">B.Tech Computer Science &amp; Engineering<br>Batch 2025-29, SGT University</p>
            </div>
        </div>

        """

# ======================================================================
# Dynamic content: run the real SQL against a fresh in-memory database
# built from schema.sql + seed.sql so every output below is genuine.
# ======================================================================
def build_memory_db():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    for fname in ('schema.sql', 'seed.sql'):
        with open(os.path.join(BASE_DIR, fname), 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
    return conn

MEM = build_memory_db()

def esc(x):
    return htmllib.escape(str(x))

def result_table(sql, limit=8):
    cur = MEM.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()[:limit]
    h = '<table class="data-table"><thead><tr>' + ''.join('<th>%s</th>' % esc(c) for c in cols) + '</tr></thead><tbody>'
    for r in rows:
        h += '<tr>' + ''.join('<td>%s</td>' % esc('' if v is None else v) for v in r) + '</tr>'
    return h + '</tbody></table>'

def sql_block(sql):
    return '<pre class="sql-code">%s</pre>' % esc(sql.strip())

def read_text(name):
    with open(os.path.join(BASE_DIR, name), 'r', encoding='utf-8') as f:
        return f.read()

def table(headers, rows, widths=None):
    h = '<table class="data-table"><thead><tr>'
    for i, c in enumerate(headers):
        w = ' style="width:%s%%;"' % widths[i] if widths else ''
        h += '<th%s>%s</th>' % (w, c)
    h += '</tr></thead><tbody>'
    for r in rows:
        h += '<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>'
    return h + '</tbody></table>'

# Presets (queries shown in Chapter 6) come from the application itself
sys.path.insert(0, BASE_DIR)
import app as courier_app
PRESETS = {p['id']: p for p in courier_app.PRESET_COURIER_QUERIES}

# Page numbers shown in the Table of Contents (A4, printed PDF)
PAGE_REFS = {'c1': 5, 'c2': 5, 'c3': 7, 'c4': 7, 'c5': 10, 'c6': 13, 'c7': 16, 'c8': 16, 'c9': 17, 'app': 19}

def pg(key):
    return PAGE_REFS.get(key, '')

url_line = ('<br><strong>Live Production URL:</strong> %s' % esc(LIVE_URL)) if LIVE_URL else ''
git_line = ('<br><strong>GitHub Repository:</strong> %s' % esc(GITHUB_URL)) if GITHUB_URL else ''

# ----------------------------------------------------------------------
# Triggers & views (read straight from schema.sql so they never drift)
# ----------------------------------------------------------------------
def extract_block(text, start_marker, end_marker):
    s = text.index(start_marker)
    e = text.index(end_marker, s)
    return text[s:e].strip()

SCHEMA = read_text('schema.sql')
TRG1 = extract_block(SCHEMA, 'CREATE TRIGGER IF NOT EXISTS trg_after_shipment_insert_booked', '-- Trigger 2')
TRG2 = extract_block(SCHEMA, 'CREATE TRIGGER IF NOT EXISTS trg_after_tracking_event_insert_sync_status', '-- Trigger 3')
TRG3 = extract_block(SCHEMA, 'CREATE TRIGGER IF NOT EXISTS trg_after_shipment_delivered', '-- Trigger 4')
TRG4 = SCHEMA[SCHEMA.index('CREATE TRIGGER IF NOT EXISTS trg_after_shipment_delete'):].strip()
VIEW2 = extract_block(SCHEMA, 'CREATE VIEW IF NOT EXISTS v_service_analytics', '-- View 3')

B = []   # body parts
add = B.append

# ======================= EXECUTIVE SUMMARY + TOC =======================
add('<div class="page-break"></div>')
add('<h1 class="chap-heading">Executive Summary / Abstract</h1>')
add("""<p>The <strong>Courier Management System (ParcelDB)</strong> is a full-stack relational database web portal created to demonstrate the core theoretical and practical principles of Database Management Systems (DBMS). The system manages the complete life-cycle of a courier business: branch network, employees and delivery agents, fleet vehicles, customer registration, service-plan pricing, shipment booking, scan-by-scan parcel tracking, payments, reward points and historical auditing.</p>""")
add("""<div class="callout-box"><p><strong>Key Architecture:</strong> The relational design is normalized to the <strong>3rd Normal Form (3NF)</strong>, enforces referential integrity actions (<code>CASCADE</code>, <code>RESTRICT</code>, <code>SET NULL</code>), and contains 7 entity tables plus 1 audit table, 4 autonomous database triggers and 3 stored views. An interactive SQL Query Lab lets examiners run live SQL against the database.%s%s</p></div>""" % (url_line, git_line))

add('<h2 class="sec-heading">Table of Contents</h2>')
add(table(['Chapter', 'Title', 'Page Ref'], [
    ['Chapter 1', 'Introduction, Problem Statement &amp; Objectives', pg('c1')],
    ['Chapter 2', 'Technology Stack &amp; System Architecture', pg('c2')],
    ['Chapter 3', 'Relational Database Schema &amp; 3NF Normalization', pg('c3')],
    ['Chapter 4', 'Entity-Relationship (ER) Architecture &amp; Data Dictionary', pg('c4')],
    ['Chapter 5', 'Automated Database Triggers &amp; Stored Views', pg('c5')],
    ['Chapter 6', 'Academic SQL Query Showcase (Joins, Aggregates, Subqueries)', pg('c6')],
    ['Chapter 7', 'System Modules &amp; User Interface Walkthrough', pg('c7')],
    ['Chapter 8', 'Testing, Verification &amp; Deployment', pg('c8')],
    ['Chapter 9', 'Conclusion &amp; Future Scope', pg('c9')],
    ['Appendix', 'Complete SQL DDL Schema Script (SQLite)', pg('app')],
], widths=[15, 70, 15]))

# ======================= CHAPTER 1 =======================
add('<div class="page-break"></div>')
add('<h1 class="chap-heading">Chapter 1: Introduction &amp; Problem Statement</h1>')
add('<h2 class="sec-heading">1.1 Background</h2>')
add("""<p>Courier and logistics companies handle thousands of parcels every day. Each parcel passes through several branches, is carried by different vehicles and delivery agents, is priced according to weight and service level, and must be traceable by the customer at any moment. Traditional paper registers or flat spreadsheets suffer from data redundancy, mismatched tracking information, billing errors, no referential integrity and no audit trail.</p>""")
add('<h2 class="sec-heading">1.2 Problem Statement</h2>')
add("""<p>To design and implement a normalized relational database and a web-based Courier Management System that (a) stores branches, staff, fleet, customers and service plans without redundancy, (b) books shipments with automatic charge calculation, (c) records every scan of a parcel and keeps shipment status consistent, and (d) automatically maintains vehicle availability and customer reward points using database-level logic.</p>""")
add('<h2 class="sec-heading">1.3 Objectives of the Project</h2>')
add("""<ul>
<li><strong>Strict Relational Integrity:</strong> Eliminate insertion, update and deletion anomalies through 3rd Normal Form (3NF) design with primary keys, foreign keys and CHECK constraints.</li>
<li><strong>Automated Business Logic:</strong> Use triggers to create the first tracking scan on booking, synchronise shipment status with every scan, release vehicles and credit reward points on delivery, and log deletions.</li>
<li><strong>Reporting Abstraction:</strong> Provide stored views (<code>CREATE VIEW</code>) for shipment tracking, service-plan revenue and agent performance.</li>
<li><strong>Transparent SQL Interface:</strong> Provide an interactive SQL Query Lab with eight ready-made academic queries and a live result timer.</li>
<li><strong>Customer Tracking:</strong> Allow any tracking number to be searched and displayed as a scan-by-scan timeline.</li>
<li><strong>Cloud Readiness:</strong> Ship deployment files (Procfile, render.yaml, requirements.txt) so the portal can be hosted on Render via GitHub.</li>
</ul>""")
add('<h2 class="sec-heading">1.4 Scope</h2>')
add("""<p>The system covers seven business entities: branches, employees, vehicles, customers, service types, shipments and tracking events. Online payment gateways, GPS telemetry and mobile applications are outside the scope of this academic project and are listed under Future Scope.</p>""")

# ======================= CHAPTER 2 =======================
add('<h1 class="chap-heading">Chapter 2: Technology Stack &amp; System Architecture</h1>')
add('<h2 class="sec-heading">2.1 Technology Stack</h2>')
add(table(['Layer', 'Technology', 'Purpose'], [
    ['Backend', 'Python 3, Flask, Gunicorn', 'Routing, raw parameterised SQL execution, form handling'],
    ['Database', 'SQLite 3 (MySQL script provided)', 'Relational storage, triggers, views, constraints'],
    ['Frontend', 'HTML5, Tailwind CSS, JavaScript, Font Awesome', 'Responsive dashboards, modals, live SQL console'],
    ['Hosting', 'Render (auto-deploy from GitHub)', 'Public web hosting using the supplied render.yaml'],
    ['Tools', 'DB Browser / phpMyAdmin, VS Code, Git', 'Inspection, development and version control'],
], widths=[18, 37, 45]))
add('<h2 class="sec-heading">2.2 Architecture</h2>')
add("""<p>The application follows a simple three-tier architecture. The <strong>presentation tier</strong> consists of Jinja2 templates rendered by Flask. The <strong>application tier</strong> (<code>app.py</code>) contains one route per use-case and executes raw SQL through the helper functions in <code>database.py</code>, deliberately avoiding an ORM so that every query is visible for evaluation. The <strong>data tier</strong> is the SQLite database <code>courier.db</code> created from <code>schema.sql</code> and populated from <code>seed.sql</code>. Foreign-key enforcement is switched on for every connection using <code>PRAGMA foreign_keys = ON</code>.</p>""")
add('<h2 class="sec-heading">2.3 Project File Structure</h2>')
add(table(['File', 'Description'], [
    ['app.py', 'Flask routes, shipment booking logic and the eight preset SQL queries'],
    ['database.py', 'Connection manager, query helpers, schema metadata reader and reset routine'],
    ['schema.sql / seed.sql', 'SQLite DDL (tables, indexes, views, triggers) and sample data'],
    ['mysql_schema.sql', 'MySQL / MariaDB compatible DDL including views and triggers'],
    ['templates/', 'Twelve HTML pages (dashboard, shipments, tracking, services, branches, fleet, employees, customers, SQL lab, schema viewer, audit log, base layout)'],
    ['Procfile, render.yaml, requirements.txt, run.bat', 'Deployment and one-click startup files'],
], widths=[32, 68]))

# ======================= CHAPTER 3 =======================
add('<div class="page-break"></div>')
add('<h1 class="chap-heading">Chapter 3: Database Design &amp; 3NF Normalization</h1>')
add("""<p>The design started from a single flat register of parcels: <code>(tracking_no, sender_name, sender_phone, sender_city, receiver_name, receiver_address, origin_city, origin_branch_phone, destination_city, service_name, base_rate, rate_per_kg, agent_name, agent_phone, vehicle_no, vehicle_type, weight, status, scan_1, scan_2, ...)</code>. This relation suffers from update, insertion and deletion anomalies and was normalized step by step.</p>""")
add('<h2 class="sec-heading">3.1 First Normal Form (1NF)</h2>')
add("""<p>Repeating groups such as <code>scan_1, scan_2, scan_3</code> were removed and every attribute was made atomic. Each scan became one row in a separate <code>tracking_events</code> relation identified by <code>event_id</code>, so a parcel may have any number of scans without adding columns.</p>""")
add('<h2 class="sec-heading">3.2 Second Normal Form (2NF)</h2>')
add("""<p>Partial dependencies were eliminated. In <code>tracking_events</code>, the branch city and phone depend only on <code>branch_id</code>, not on the whole scan record, so they were moved into <code>branches</code>. Likewise service rates depend only on the service plan and were moved to <code>service_types</code>, and vehicle details to <code>vehicles</code>.</p>""")
add('<h2 class="sec-heading">3.3 Third Normal Form (3NF)</h2>')
add("""<p>Transitive dependencies were removed: <code>sender_phone</code> and <code>sender_city</code> depend on the sender, not on the shipment, so a <code>customers</code> relation was created; <code>agent_phone</code> and salary depend on the employee, so an <code>employees</code> relation was created. After this step every non-key attribute in every relation depends on the key, the whole key and nothing but the key. The result is eight relations: <code>branches, employees, vehicles, customers, service_types, shipments, tracking_events, audit_logs</code>.</p>""")

# ======================= CHAPTER 4 =======================
add('<h1 class="chap-heading">Chapter 4: Entity-Relationship (ER) Architecture &amp; Data Dictionary</h1>')
add('<h2 class="sec-heading">4.1 Relational Entities &amp; Cardinality Map</h2>')
add(table(['Relationship', 'Cardinality', 'Foreign Key / Rule'], [
    ['branches &mdash; employees', '1 : N', 'employees.branch_id (ON DELETE SET NULL)'],
    ['branches &mdash; vehicles', '1 : N', 'vehicles.branch_id (ON DELETE SET NULL)'],
    ['customers &mdash; shipments', '1 : N', 'shipments.sender_id (ON DELETE SET NULL)'],
    ['service_types &mdash; shipments', '1 : N', 'shipments.service_id (ON DELETE RESTRICT)'],
    ['employees &mdash; shipments', '1 : N', 'shipments.agent_id (ON DELETE SET NULL)'],
    ['vehicles &mdash; shipments', '1 : N', 'shipments.vehicle_id (ON DELETE SET NULL)'],
    ['branches &mdash; shipments', '1 : N (twice)', 'origin_branch_id and destination_branch_id'],
    ['shipments &mdash; branches', 'M : N', 'resolved by tracking_events (shipment_id CASCADE, branch_id SET NULL)'],
], widths=[32, 16, 52]))
add('<h2 class="sec-heading">4.2 Data Dictionary (Relational Schema Specifications)</h2>')
add('<h3 class="subsec-heading">Table 1: branches</h3>')
add(table(['Column', 'Type', 'Constraint'], [
    ['branch_id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT'],
    ['branch_code', 'VARCHAR(10)', 'UNIQUE, NOT NULL'],
    ['branch_name, city, state', 'VARCHAR', 'NOT NULL'],
    ['address', 'TEXT', 'Optional'],
    ['phone', 'VARCHAR(20)', 'UNIQUE, NOT NULL'],
    ['branch_type', 'VARCHAR(20)', "CHECK IN ('Hub','Service Centre','Pickup Point')"],
], widths=[28, 22, 50]))
add('<h3 class="subsec-heading">Table 2: employees</h3>')
add(table(['Column', 'Type', 'Constraint'], [
    ['employee_id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT'],
    ['first_name, last_name', 'VARCHAR(50)', 'NOT NULL'],
    ['role', 'VARCHAR(30)', "CHECK IN ('Branch Manager','Dispatcher','Delivery Agent','Sorting Staff','Customer Support')"],
    ['phone, email', 'VARCHAR', 'UNIQUE, NOT NULL'],
    ['salary', 'DECIMAL(10,2)', 'CHECK (salary &gt; 0)'],
    ['shift', 'VARCHAR(20)', "CHECK IN ('Morning','Evening','Night','Full Day')"],
    ['branch_id', 'INTEGER', 'FOREIGN KEY &rarr; branches (SET NULL)'],
], widths=[28, 22, 50]))
add('<h3 class="subsec-heading">Table 3: vehicles</h3>')
add(table(['Column', 'Type', 'Constraint'], [
    ['vehicle_id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT'],
    ['vehicle_number', 'VARCHAR(20)', 'UNIQUE, NOT NULL'],
    ['vehicle_type', 'VARCHAR(15)', "CHECK IN ('Bike','Van','Truck','Cargo Bike')"],
    ['capacity_kg', 'DECIMAL(8,2)', 'CHECK (capacity_kg &gt; 0)'],
    ['status', 'VARCHAR(20)', "CHECK IN ('Available','On Route','Maintenance')"],
    ['branch_id', 'INTEGER', 'FOREIGN KEY &rarr; branches (SET NULL)'],
], widths=[28, 22, 50]))
add('<h3 class="subsec-heading">Table 4: customers &amp; Table 5: service_types</h3>')
add(table(['Column', 'Type', 'Constraint'], [
    ['customers.customer_id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT'],
    ['customers.phone', 'VARCHAR(20)', 'UNIQUE, NOT NULL'],
    ['customers.reward_points', 'INTEGER', 'CHECK (reward_points &gt;= 0), default 0'],
    ['service_types.service_id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT'],
    ['service_types.service_name', 'VARCHAR(50)', 'UNIQUE, NOT NULL'],
    ['service_types.base_rate', 'DECIMAL(8,2)', 'CHECK (base_rate &gt; 0)'],
    ['service_types.rate_per_kg', 'DECIMAL(8,2)', 'CHECK (rate_per_kg &gt;= 0)'],
    ['service_types.is_active', 'INTEGER', 'CHECK IN (0, 1)'],
], widths=[32, 20, 48]))
add('<h3 class="subsec-heading">Table 6: shipments &amp; Table 7: tracking_events (Master-Detail)</h3>')
add(table(['Column', 'Type', 'Constraint'], [
    ['shipments.shipment_id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT'],
    ['shipments.tracking_number', 'VARCHAR(25)', 'UNIQUE, NOT NULL'],
    ['shipments.sender_id / agent_id / vehicle_id', 'INTEGER', 'FOREIGN KEYS (SET NULL)'],
    ['shipments.origin_branch_id / destination_branch_id', 'INTEGER', 'FOREIGN KEYS &rarr; branches (SET NULL)'],
    ['shipments.service_id', 'INTEGER', 'FOREIGN KEY &rarr; service_types (RESTRICT), NOT NULL'],
    ['shipments.weight_kg', 'DECIMAL(8,2)', 'CHECK (weight_kg &gt; 0)'],
    ['shipments.status', 'VARCHAR(20)', 'CHECK IN (Booked, Picked Up, In Transit, Out for Delivery, Delivered, Returned, Cancelled)'],
    ['shipments.total_charge', 'DECIMAL(10,2)', 'CHECK (total_charge &gt;= 0)'],
    ['tracking_events.event_id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT'],
    ['tracking_events.shipment_id', 'INTEGER', 'FOREIGN KEY &rarr; shipments (CASCADE), NOT NULL'],
    ['tracking_events.branch_id', 'INTEGER', 'FOREIGN KEY &rarr; branches (SET NULL)'],
    ['tracking_events.status', 'VARCHAR(20)', 'CHECK (same status list), NOT NULL'],
], widths=[38, 18, 44]))

# ======================= CHAPTER 5 =======================
add('<div class="page-break"></div>')
add('<h1 class="chap-heading">Chapter 5: Automated Database Triggers &amp; Stored Views</h1>')
add('<h2 class="sec-heading">5.1 Database Engine Triggers (Autonomous Business Logic)</h2>')
add("""<p>Triggers execute inside the database engine, so the business rules hold no matter which application or SQL console modifies the data.</p>""")
add('<h3 class="subsec-heading">Trigger 1: First Scan &amp; Vehicle Allocation (trg_after_shipment_insert_booked)</h3>')
add("""<p>When a shipment is booked, the trigger inserts the first <em>Booked</em> scan at the origin branch, marks the assigned vehicle <em>On Route</em> and writes an audit entry.</p>""")
add(sql_block(TRG1))
add('<h3 class="subsec-heading">Trigger 2: Status Synchronisation (trg_after_tracking_event_insert_sync_status)</h3>')
add("""<p>Every new tracking scan updates <code>shipments.status</code> and stamps <code>delivered_at</code> when the parcel is delivered. Staff therefore only record scans; the master record can never disagree with its latest scan.</p>""")
add(sql_block(TRG2))
add('<h3 class="subsec-heading">Trigger 3: Vehicle Release &amp; Reward Points (trg_after_shipment_delivered)</h3>')
add("""<p>When the status changes to <em>Delivered</em>, the vehicle is released (only if it carries no other active shipment) and the registered sender earns one reward point per Rs 100 charged.</p>""")
add(sql_block(TRG3))
add('<h3 class="subsec-heading">Trigger 4: Deletion Audit (trg_after_shipment_delete)</h3>')
add(sql_block(TRG4))
add('<h2 class="sec-heading">5.2 Stored Database Views (CREATE VIEW)</h2>')
add("""<p>Three views hide complex JOINs and aggregates behind simple virtual tables: <code>v_shipment_tracking_summary</code> (shipment, sender, route, service, agent and scan count), <code>v_service_analytics</code> (shipments, weight and revenue per service plan) and <code>v_agent_performance</code> (assigned versus delivered parcels for each delivery agent).</p>""")
add(sql_block(VIEW2))
add('<p>Output of <code>SELECT * FROM v_agent_performance;</code> on the seed data:</p>')
add(result_table('SELECT * FROM v_agent_performance;'))

# ======================= CHAPTER 6 =======================
add('<div class="page-break"></div>')
add('<h1 class="chap-heading">Chapter 6: Academic SQL Query Showcase</h1>')
add("""<p>The following queries are available as one-click presets in the SQL Query Lab of the application. Each output below was produced by running the query on the seeded database.</p>""")
for num, pid, title in [(1, 1, 'Multi-Table INNER JOIN (6-Table Shipment Manifest)'),
                        (2, 2, 'LEFT OUTER JOIN (Service Plans With No Shipments)'),
                        (3, 3, 'Aggregate Functions with GROUP BY &amp; HAVING'),
                        (4, 5, 'Correlated Subquery (Shipments Heavier Than Their Plan Average)'),
                        (5, 8, 'Set Operation (UNION of Customers, Employees and Branches)')]:
    add('<h2 class="sec-heading">6.%d %s</h2>' % (num, title))
    add('<p>%s</p>' % esc(PRESETS[pid]['desc']))
    add(sql_block(PRESETS[pid]['sql']))
    add(result_table(PRESETS[pid]['sql'].rstrip().rstrip(';'), limit=6))
add('<h2 class="sec-heading">6.6 Nested Subquery (NOT IN)</h2>')
add('<p>%s</p>' % esc(PRESETS[4]['desc']))
add(sql_block(PRESETS[4]['sql']))
add(result_table(PRESETS[4]['sql'].rstrip().rstrip(';')))

# ======================= CHAPTER 7 =======================
add('<div class="page-break"></div>')
add('<h1 class="chap-heading">Chapter 7: System Modules &amp; User Interface</h1>')
add(table(['Module', 'Page', 'Database Concepts Demonstrated'], [
    ['Dashboard', '/', 'Aggregates, GROUP BY, view usage, JOIN-based route statistics, trigger log feed'],
    ['Shipments &amp; Billing', '/shipments', 'Booking (INSERT), filters (WHERE/LIKE), 6-table JOIN, payment UPDATE, cascade DELETE, live SQL preview'],
    ['Track Shipment', '/track', 'Parameterised SELECT on a view, ordered tracking timeline, scan INSERT firing triggers'],
    ['Service Plans', '/services', 'Full CRUD, LIKE search, ON DELETE RESTRICT protection'],
    ['Branches', '/branches', 'Correlated scalar subqueries for staff, vehicle and traffic counts'],
    ['Fleet', '/vehicles', 'LEFT JOIN with current shipment, status updates, trigger-driven availability'],
    ['Employees', '/employees', 'LEFT JOIN with conditional aggregation (SUM CASE)'],
    ['Customers', '/customers', 'Lifetime spend aggregation, reward points updated by trigger'],
    ['SQL Query Lab', '/query-lab', 'Eight preset queries, free-form SQL, execution timer, CSV export'],
    ['Schema &amp; ER', '/schema', 'Runtime metadata via PRAGMA table_info / foreign_key_list, DDL download'],
    ['Trigger Audit Log', '/audit-logs', 'Audit table populated automatically by the four triggers'],
], widths=[20, 14, 66]))
add('<h2 class="sec-heading">7.1 Shipment Booking Workflow</h2>')
add("""<p>The booking form calculates the charge as <code>base_rate + rate_per_kg &times; weight</code> using the chosen service plan. The server re-computes the amount (the browser value is only a preview), verifies that the plan is active, that the selected vehicle is <em>Available</em> and that the weight does not exceed its capacity, then inserts the shipment. Triggers create the first scan and mark the vehicle On Route. Each later scan recorded from the Shipments or Track page moves the shipment through Picked Up, In Transit and Out for Delivery up to Delivered, at which point the vehicle is released and reward points are credited.</p>""")

# ======================= CHAPTER 8 =======================
add('<h1 class="chap-heading">Chapter 8: Testing, Verification &amp; Deployment</h1>')
add('<h2 class="sec-heading">8.1 Functional Test Cases</h2>')
add(table(['#', 'Test Case', 'Expected Result', 'Result'], [
    ['1', 'Book a shipment with an available vehicle', 'Charge = base + rate x weight; first scan created; vehicle On Route', 'Pass'],
    ['2', 'Book a shipment with a vehicle already On Route', 'Booking rejected with a clear message', 'Pass'],
    ['3', 'Book a shipment on a suspended service plan', 'Booking rejected', 'Pass'],
    ['4', 'Record Picked Up, In Transit, Delivered scans', 'Shipment status follows each scan; delivered_at stamped', 'Pass'],
    ['5', 'Deliver the shipment', 'Vehicle becomes Available; sender reward points increase', 'Pass'],
    ['6', 'Delete a service plan used by shipments', 'Blocked by ON DELETE RESTRICT', 'Pass'],
    ['7', 'Delete a shipment', 'Tracking events removed by CASCADE; audit row created', 'Pass'],
    ['8', 'Run all eight preset queries in the SQL Lab', 'Every query executes without error', 'Pass'],
    ['9', 'Reset database', 'Schema rebuilt and seed data restored', 'Pass'],
], widths=[5, 35, 48, 12]))
add('<h2 class="sec-heading">8.2 Running Locally</h2>')
add("""<p>Install Python 3.8+ and Flask (<code>pip install -r requirements.txt</code>), then run <code>python app.py</code> (or double-click <code>run.bat</code> on Windows) and open <code>http://127.0.0.1:5000</code>. If <code>courier.db</code> is missing it is created and seeded automatically.</p>""")
add('<h2 class="sec-heading">8.3 Cloud Deployment</h2>')
dep = """<p>The project includes a <code>Procfile</code> (<code>web: gunicorn app:app</code>), <code>requirements.txt</code> and a <code>render.yaml</code> blueprint. To deploy, push the project to a GitHub repository, create a new Web Service on Render from that repository and use <code>pip install -r requirements.txt</code> as the build command and <code>gunicorn app:app</code> as the start command. Render then redeploys automatically on every push.</p>"""
if LIVE_URL:
    dep += '<p><strong>Live Production URL:</strong> %s</p>' % esc(LIVE_URL)
add(dep)

# ======================= CHAPTER 9 =======================
add('<h1 class="chap-heading">Chapter 9: Conclusion &amp; Future Scope</h1>')
add("""<p>The <strong>Courier Management System (ParcelDB)</strong> provides a complete, normalized and transaction-safe DBMS implementation. Through this project we gained hands-on proficiency in 3NF normalization, primary, foreign and unique keys, referential actions, CHECK constraints, engine-level triggers, stored views, advanced joins, subqueries and deployment of a database-driven web application.</p>""")
add("""<p><strong>Future Scope:</strong> Enhancements can include SMS/e-mail notifications on every scan, QR-code or barcode label printing, GPS-based live vehicle tracking, route optimisation for delivery agents, integration with an online payment gateway, and migration from SQLite to MySQL or PostgreSQL for multi-user production workloads.</p>""")

# ======================= APPENDIX =======================
add('<div class="page-break"></div>')
add('<h1 class="chap-heading">Appendix: Complete SQL DDL Schema Script (SQLite)</h1>')
add(sql_block(SCHEMA))

add("""<div style="margin-top: 40px; border-top: 1px solid #000000; padding-top: 15px; text-align: center; font-size: 11pt; font-weight: bold;">
Department of Computer Science &amp; Engineering | SGT University Gurugram | Academic Session July-Dec 2026
</div>""")

full_html = html_content + '\n'.join(B) + '\n    </div>\n</body>\n</html>\n'

with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
    f.write(full_html)
print("Generated HTML report at: %s" % HTML_OUTPUT)

# ----------------------------------------------------------------------
# HTML -> PDF using whichever browser / tool is available
# ----------------------------------------------------------------------
def find_browser():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for name in ('google-chrome', 'chromium', 'chromium-browser', 'microsoft-edge', 'msedge'):
        p = shutil.which(name)
        if p:
            return p
    return None

browser = find_browser()
if browser:
    print("Converting HTML to PDF via headless browser: %s" % browser)
    cmd = [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           "--run-all-compositor-stages-before-draw", "--print-to-pdf=%s" % PDF_OUTPUT, HTML_OUTPUT]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(PDF_OUTPUT):
        print("SUCCESS: PDF report generated at: %s (%d bytes)" % (PDF_OUTPUT, os.path.getsize(PDF_OUTPUT)))
    else:
        print("Browser failed to generate PDF. Returncode:", res.returncode, "Stderr:", res.stderr)
else:
    print("No Chrome/Edge found. Open Project_Report.html in a browser and use Print > Save as PDF.")
