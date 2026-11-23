from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import database
import os
import random

app = Flask(__name__)
app.secret_key = 'courier_dbms_secret_key_ultra_secure'

# Ensure database exists
if not os.path.exists(database.DB_PATH):
    database.init_database()
    database.seed_database()

SHIPMENT_STATUSES = ['Booked', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Returned', 'Cancelled']
PACKAGE_TYPES = ['Document', 'Parcel', 'Fragile', 'Electronics', 'Perishable']

def get_dropdown_data():
    return {
        'branches': database.query_all("SELECT branch_id, branch_code, branch_name, city FROM branches ORDER BY city;"),
        'agents': database.query_all("SELECT e.employee_id, e.first_name || ' ' || e.last_name AS name, COALESCE(b.city, 'N/A') AS city FROM employees e LEFT JOIN branches b ON e.branch_id = b.branch_id WHERE e.role = 'Delivery Agent' ORDER BY e.first_name;"),
        'vehicles': database.query_all("SELECT vehicle_id, vehicle_number, vehicle_type, capacity_kg, status FROM vehicles ORDER BY vehicle_number;"),
        'customers': database.query_all("SELECT customer_id, name, phone, reward_points FROM customers ORDER BY name;"),
        'services': database.query_all("SELECT service_id, service_name, base_rate, rate_per_kg, delivery_days FROM service_types WHERE is_active = 1 ORDER BY service_name;"),
    }

# -------------------------------------------------------------------
# 1. Dashboard
# -------------------------------------------------------------------
@app.route('/')
def index():
    stats = {
        'total_revenue': database.query_one("SELECT COALESCE(SUM(total_charge), 0.0) AS rev FROM shipments WHERE payment_status = 'Paid';")['rev'],
        'total_shipments': database.query_one("SELECT COUNT(*) AS c FROM shipments;")['c'],
        'in_transit': database.query_one("SELECT COUNT(*) AS c FROM shipments WHERE status IN ('Picked Up', 'In Transit', 'Out for Delivery');")['c'],
        'delivered': database.query_one("SELECT COUNT(*) AS c FROM shipments WHERE status = 'Delivered';")['c'],
        'active_vehicles': database.query_one("SELECT COUNT(*) AS c FROM vehicles WHERE status = 'On Route';")['c'],
        'total_vehicles': database.query_one("SELECT COUNT(*) AS c FROM vehicles;")['c'],
        'total_branches': database.query_one("SELECT COUNT(*) AS c FROM branches;")['c'],
        'total_employees': database.query_one("SELECT COUNT(*) AS c FROM employees;")['c'],
        'total_customers': database.query_one("SELECT COUNT(*) AS c FROM customers;")['c'],
    }

    status_counts = database.query_all("""
        SELECT status, COUNT(*) AS total FROM shipments GROUP BY status ORDER BY total DESC;
    """)

    vehicles = database.query_all("""
        SELECT v.*, COALESCE(b.city, 'N/A') AS city FROM vehicles v
        LEFT JOIN branches b ON v.branch_id = b.branch_id ORDER BY v.vehicle_number;
    """)

    # Service plan revenue (view)
    service_sales = database.query_all("""
        SELECT service_name, total_shipments, total_weight_kg, total_revenue
        FROM v_service_analytics ORDER BY total_revenue DESC;
    """)

    # Busiest routes (GROUP BY on origin & destination)
    top_routes = database.query_all("""
        SELECT ob.city AS origin_city, db.city AS destination_city,
               COUNT(*) AS shipments_count, ROUND(SUM(sh.weight_kg), 2) AS total_weight
        FROM shipments sh
        JOIN branches ob ON sh.origin_branch_id = ob.branch_id
        JOIN branches db ON sh.destination_branch_id = db.branch_id
        GROUP BY ob.city, db.city
        ORDER BY shipments_count DESC, total_weight DESC
        LIMIT 5;
    """)

    recent_logs = database.query_all("SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT 6;")

    return render_template('index.html', stats=stats, status_counts=status_counts, vehicles=vehicles,
                           service_sales=service_sales, top_routes=top_routes, recent_logs=recent_logs)

# -------------------------------------------------------------------
# 2. Service Plans CRUD
# -------------------------------------------------------------------
@app.route('/services')
def services():
    search = request.args.get('search', '').strip()
    sql = """
        SELECT st.*, COUNT(sh.shipment_id) AS total_shipments
        FROM service_types st
        LEFT JOIN shipments sh ON st.service_id = sh.service_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (st.service_name LIKE ? OR st.description LIKE ?)"
        like_str = f"%{search}%"
        params.extend([like_str, like_str])
    sql += " GROUP BY st.service_id ORDER BY st.base_rate ASC;"
    return render_template('services.html', services=database.query_all(sql, params), search=search, sql_used=sql)

@app.route('/services/add', methods=['POST'])
def add_service():
    name = request.form['service_name'].strip()
    desc = request.form.get('description', '').strip()
    base_rate = float(request.form['base_rate'])
    rate_per_kg = float(request.form['rate_per_kg'])
    days = int(request.form.get('delivery_days', 3))
    active = 1 if request.form.get('is_active') == '1' else 0
    sql = """INSERT INTO service_types (service_name, description, base_rate, rate_per_kg, delivery_days, is_active)
             VALUES (?, ?, ?, ?, ?, ?);"""
    ok, res = database.execute_commit(sql, (name, desc, base_rate, rate_per_kg, days, active))
    flash(f"Service plan '{name}' added!" if ok else f"Error adding service: {res}", "success" if ok else "danger")
    return redirect(url_for('services'))

@app.route('/services/edit/<int:service_id>', methods=['POST'])
def edit_service(service_id):
    sql = """UPDATE service_types SET service_name = ?, description = ?, base_rate = ?, rate_per_kg = ?,
             delivery_days = ?, is_active = ? WHERE service_id = ?;"""
    try:
        params = (request.form['service_name'].strip(), request.form.get('description', '').strip(),
                  float(request.form['base_rate']), float(request.form['rate_per_kg']),
                  int(request.form.get('delivery_days', 3)), int(request.form.get('is_active', 1)), service_id)
    except ValueError:
        flash("Invalid numeric value supplied.", "danger")
        return redirect(url_for('services'))
    ok, res = database.execute_commit(sql, params)
    flash(f"Service plan #{service_id} updated!" if ok else f"Error updating service: {res}", "success" if ok else "danger")
    return redirect(url_for('services'))

@app.route('/services/delete/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    ok, res = database.execute_commit("DELETE FROM service_types WHERE service_id = ?;", (service_id,))
    if ok:
        flash(f"Service plan #{service_id} removed.", "info")
    else:
        flash(f"Cannot delete service: {res} (Shipments reference it - protected by ON DELETE RESTRICT).", "danger")
    return redirect(url_for('services'))

# -------------------------------------------------------------------
# 3. Shipments & Tracking (Core Transaction Module)
# -------------------------------------------------------------------
@app.route('/shipments')
def shipments():
    status_filter = request.args.get('status', '').strip()
    service_filter = request.args.get('service', '').strip()
    search = request.args.get('search', '').strip()

    sql = """
        SELECT sh.*,
               COALESCE(c.name, 'Walk-in Sender') AS sender_name,
               ob.city AS origin_city, db.city AS destination_city,
               st.service_name,
               COALESCE(e.first_name || ' ' || e.last_name, 'Unassigned') AS agent_name,
               v.vehicle_number,
               COUNT(te.event_id) AS scan_events
        FROM shipments sh
        LEFT JOIN customers c ON sh.sender_id = c.customer_id
        LEFT JOIN branches ob ON sh.origin_branch_id = ob.branch_id
        LEFT JOIN branches db ON sh.destination_branch_id = db.branch_id
        JOIN service_types st ON sh.service_id = st.service_id
        LEFT JOIN employees e ON sh.agent_id = e.employee_id
        LEFT JOIN vehicles v ON sh.vehicle_id = v.vehicle_id
        LEFT JOIN tracking_events te ON sh.shipment_id = te.shipment_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        sql += " AND sh.status = ?"
        params.append(status_filter)
    if service_filter:
        sql += " AND sh.service_id = ?"
        params.append(service_filter)
    if search:
        sql += " AND (sh.tracking_number LIKE ? OR sh.receiver_name LIKE ? OR c.name LIKE ?)"
        like_str = f"%{search}%"
        params.extend([like_str, like_str, like_str])
    sql += " GROUP BY sh.shipment_id ORDER BY sh.shipment_id DESC;"

    shipments_list = database.query_all(sql, params)
    dropdowns = get_dropdown_data()
    all_services = database.query_all("SELECT service_id, service_name FROM service_types ORDER BY service_name;")
    return render_template('shipments.html', shipments=shipments_list, dropdowns=dropdowns, all_services=all_services,
                           statuses=SHIPMENT_STATUSES, package_types=PACKAGE_TYPES, status_filter=status_filter,
                           service_filter=service_filter, search=search, sql_used=sql)

@app.route('/shipments/create', methods=['POST'])
def create_shipment():
    try:
        sender_id = int(request.form['sender_id']) if request.form.get('sender_id') else None
        origin_id = int(request.form['origin_branch_id'])
        dest_id = int(request.form['destination_branch_id'])
        service_id = int(request.form['service_id'])
        agent_id = int(request.form['agent_id']) if request.form.get('agent_id') else None
        vehicle_id = int(request.form['vehicle_id']) if request.form.get('vehicle_id') else None
        weight = float(request.form['weight_kg'])
    except (ValueError, KeyError):
        flash("Invalid form values supplied.", "danger")
        return redirect(url_for('shipments'))

    service = database.query_one("SELECT base_rate, rate_per_kg, is_active FROM service_types WHERE service_id = ?;", (service_id,))
    if not service or not service['is_active']:
        flash("Selected service plan is not available.", "danger")
        return redirect(url_for('shipments'))
    if vehicle_id:
        veh = database.query_one("SELECT status, capacity_kg FROM vehicles WHERE vehicle_id = ?;", (vehicle_id,))
        if not veh or veh['status'] != 'Available':
            flash("Selected vehicle is not available (already on route or under maintenance).", "danger")
            return redirect(url_for('shipments'))
        if weight > veh['capacity_kg']:
            flash("Shipment weight exceeds the selected vehicle capacity.", "danger")
            return redirect(url_for('shipments'))

    total_charge = round(service['base_rate'] + service['rate_per_kg'] * weight, 2)
    next_no = database.query_one("SELECT COUNT(*) + 1 AS c FROM shipments;")['c']
    tracking_number = f"PDB-2026-{next_no:04d}"
    while database.query_one("SELECT 1 AS x FROM shipments WHERE tracking_number = ?;", (tracking_number,)):
        next_no += random.randint(1, 9)
        tracking_number = f"PDB-2026-{next_no:04d}"

    sql = """
        INSERT INTO shipments (tracking_number, sender_id, receiver_name, receiver_phone, receiver_address,
            origin_branch_id, destination_branch_id, service_id, agent_id, vehicle_id, package_type,
            weight_kg, status, payment_status, payment_method, total_charge)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Booked', 'Unpaid', 'Pending', ?);
    """
    ok, res = database.execute_commit(sql, (
        tracking_number, sender_id, request.form['receiver_name'].strip(), request.form['receiver_phone'].strip(),
        request.form['receiver_address'].strip(), origin_id, dest_id, service_id, agent_id, vehicle_id,
        request.form.get('package_type', 'Parcel'), weight, total_charge))
    if ok:
        flash(f"Shipment {tracking_number} booked (Rs {total_charge:.2f})! Trigger created the first tracking scan.", "success")
    else:
        flash(f"Error booking shipment: {res}", "danger")
    return redirect(url_for('shipments'))

@app.route('/shipments/scan/<int:shipment_id>', methods=['POST'])
def add_scan(shipment_id):
    status = request.form['status']
    branch_id = int(request.form['branch_id']) if request.form.get('branch_id') else None
    remarks = request.form.get('remarks', '').strip() or f"Status updated to {status}."
    sql = "INSERT INTO tracking_events (shipment_id, branch_id, status, remarks) VALUES (?, ?, ?, ?);"
    ok, res = database.execute_commit(sql, (shipment_id, branch_id, status, remarks))
    if ok:
        if status == 'Delivered':
            flash("Delivered! Triggers synced the status, released the vehicle and credited sender reward points.", "success")
        else:
            flash(f"Scan recorded - trigger synchronised shipment status to '{status}'.", "info")
    else:
        flash(f"Error recording scan: {res}", "danger")
    return redirect(request.referrer or url_for('shipments'))

@app.route('/shipments/payment/<int:shipment_id>', methods=['POST'])
def update_payment(shipment_id):
    sql = "UPDATE shipments SET payment_status = ?, payment_method = ? WHERE shipment_id = ?;"
    ok, res = database.execute_commit(sql, (request.form['payment_status'], request.form.get('payment_method', 'Pending'), shipment_id))
    flash(f"Payment details for shipment #{shipment_id} updated." if ok else f"Error updating payment: {res}", "info" if ok else "danger")
    return redirect(url_for('shipments'))

@app.route('/shipments/assign/<int:shipment_id>', methods=['POST'])
def assign_agent(shipment_id):
    agent_id = int(request.form['agent_id']) if request.form.get('agent_id') else None
    ok, res = database.execute_commit("UPDATE shipments SET agent_id = ? WHERE shipment_id = ?;", (agent_id, shipment_id))
    flash(f"Delivery agent assigned to shipment #{shipment_id}." if ok else f"Error assigning agent: {res}", "info" if ok else "danger")
    return redirect(url_for('shipments'))

@app.route('/shipments/delete/<int:shipment_id>', methods=['POST'])
def delete_shipment(shipment_id):
    ok, res = database.execute_commit("DELETE FROM shipments WHERE shipment_id = ?;", (shipment_id,))
    flash(f"Shipment #{shipment_id} deleted. CASCADE removed its tracking scans." if ok else f"Error deleting shipment: {res}", "info" if ok else "danger")
    return redirect(url_for('shipments'))

@app.route('/track', methods=['GET'])
def track():
    number = request.args.get('tn', '').strip().upper()
    shipment, events = None, []
    if number:
        shipment = database.query_one("SELECT * FROM v_shipment_tracking_summary WHERE tracking_number = ?;", (number,))
        if shipment:
            events = database.query_all("""
                SELECT te.*, COALESCE(b.branch_name, 'In Network') AS branch_name, b.city
                FROM tracking_events te LEFT JOIN branches b ON te.branch_id = b.branch_id
                WHERE te.shipment_id = ? ORDER BY te.event_time ASC, te.event_id ASC;
            """, (shipment['shipment_id'],))
        else:
            flash(f"No shipment found with tracking number '{number}'.", "danger")
    return render_template('track.html', shipment=shipment, events=events, tn=number,
                           branches=get_dropdown_data()['branches'], statuses=SHIPMENT_STATUSES)

# -------------------------------------------------------------------
# 4. Branches & Fleet
# -------------------------------------------------------------------
@app.route('/branches')
def branches():
    branches_list = database.query_all("""
        SELECT b.*,
               (SELECT COUNT(*) FROM employees e WHERE e.branch_id = b.branch_id) AS staff_count,
               (SELECT COUNT(*) FROM vehicles v WHERE v.branch_id = b.branch_id) AS vehicle_count,
               (SELECT COUNT(*) FROM shipments s WHERE s.origin_branch_id = b.branch_id) AS outbound,
               (SELECT COUNT(*) FROM shipments s WHERE s.destination_branch_id = b.branch_id) AS inbound
        FROM branches b ORDER BY b.branch_type, b.city;
    """)
    return render_template('branches.html', branches=branches_list)

@app.route('/branches/add', methods=['POST'])
def add_branch():
    sql = """INSERT INTO branches (branch_code, branch_name, city, state, address, phone, branch_type)
             VALUES (?, ?, ?, ?, ?, ?, ?);"""
    f = request.form
    ok, res = database.execute_commit(sql, (f['branch_code'].strip().upper(), f['branch_name'].strip(), f['city'].strip(),
                                            f['state'].strip(), f.get('address', '').strip(), f['phone'].strip(),
                                            f.get('branch_type', 'Service Centre')))
    flash(f"Branch '{f['branch_name']}' added!" if ok else f"Error adding branch: {res}", "success" if ok else "danger")
    return redirect(url_for('branches'))

@app.route('/vehicles')
def vehicles():
    vehicles_list = database.query_all("""
        SELECT v.*, COALESCE(b.city, 'N/A') AS city, sh.tracking_number AS current_shipment
        FROM vehicles v
        LEFT JOIN branches b ON v.branch_id = b.branch_id
        LEFT JOIN shipments sh ON v.vehicle_id = sh.vehicle_id AND sh.status NOT IN ('Delivered', 'Returned', 'Cancelled')
        GROUP BY v.vehicle_id ORDER BY v.vehicle_type, v.vehicle_number;
    """)
    return render_template('vehicles.html', vehicles=vehicles_list, branches=get_dropdown_data()['branches'])

@app.route('/vehicles/add', methods=['POST'])
def add_vehicle():
    f = request.form
    sql = "INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, status, branch_id) VALUES (?, ?, ?, 'Available', ?);"
    try:
        params = (f['vehicle_number'].strip().upper(), f['vehicle_type'], float(f['capacity_kg']),
                  int(f['branch_id']) if f.get('branch_id') else None)
    except ValueError:
        flash("Invalid numeric value supplied.", "danger")
        return redirect(url_for('vehicles'))
    ok, res = database.execute_commit(sql, params)
    flash(f"Vehicle {params[0]} added to the fleet!" if ok else f"Error adding vehicle: {res}", "success" if ok else "danger")
    return redirect(url_for('vehicles'))

@app.route('/vehicles/status/<int:vehicle_id>', methods=['POST'])
def update_vehicle_status(vehicle_id):
    ok, res = database.execute_commit("UPDATE vehicles SET status = ? WHERE vehicle_id = ?;", (request.form['status'], vehicle_id))
    flash(f"Vehicle #{vehicle_id} status updated." if ok else f"Error updating vehicle: {res}", "info" if ok else "danger")
    return redirect(url_for('vehicles'))

# -------------------------------------------------------------------
# 5. Employees CRUD
# -------------------------------------------------------------------
@app.route('/employees')
def employees():
    employees_list = database.query_all("""
        SELECT e.*, COALESCE(b.city, 'N/A') AS branch_city,
               COUNT(sh.shipment_id) AS total_assigned,
               SUM(CASE WHEN sh.status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_count
        FROM employees e
        LEFT JOIN branches b ON e.branch_id = b.branch_id
        LEFT JOIN shipments sh ON e.employee_id = sh.agent_id
        GROUP BY e.employee_id ORDER BY e.role, e.first_name ASC;
    """)
    return render_template('employees.html', employees=employees_list, branches=get_dropdown_data()['branches'])

@app.route('/employees/add', methods=['POST'])
def add_employee():
    f = request.form
    sql = """INSERT INTO employees (first_name, last_name, role, phone, email, salary, shift, branch_id)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
    try:
        params = (f['first_name'].strip(), f['last_name'].strip(), f['role'], f['phone'].strip(), f['email'].strip(),
                  float(f['salary']), f.get('shift', 'Morning'), int(f['branch_id']) if f.get('branch_id') else None)
    except ValueError:
        flash("Invalid numeric value supplied.", "danger")
        return redirect(url_for('employees'))
    ok, res = database.execute_commit(sql, params)
    flash(f"Employee '{params[0]} {params[1]}' ({params[2]}) registered!" if ok else f"Error adding employee: {res}", "success" if ok else "danger")
    return redirect(url_for('employees'))

# -------------------------------------------------------------------
# 6. Customers & Rewards
# -------------------------------------------------------------------
@app.route('/customers')
def customers():
    customer_list = database.query_all("""
        SELECT c.*, COUNT(sh.shipment_id) AS total_shipments,
               COALESCE(SUM(sh.total_charge), 0.0) AS total_spend
        FROM customers c
        LEFT JOIN shipments sh ON c.customer_id = sh.sender_id AND sh.status != 'Cancelled'
        GROUP BY c.customer_id ORDER BY total_spend DESC;
    """)
    return render_template('customers.html', customers=customer_list)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    f = request.form
    sql = "INSERT INTO customers (name, phone, email, address, city, reward_points) VALUES (?, ?, ?, ?, ?, 0);"
    ok, res = database.execute_commit(sql, (f['name'].strip(), f['phone'].strip(), f.get('email', '').strip(),
                                            f.get('address', '').strip(), f.get('city', '').strip()))
    flash(f"Customer '{f['name']}' registered!" if ok else f"Error adding customer: {res}", "success" if ok else "danger")
    return redirect(url_for('customers'))

# -------------------------------------------------------------------
# 7. SQL Query Lab (DBMS Project Core Highlight!)
# -------------------------------------------------------------------
PRESET_COURIER_QUERIES = [
    {
        "id": 1,
        "category": "Multi-Table JOIN",
        "title": "Complete Shipment Manifest (6-Table INNER JOIN)",
        "desc": "Joins shipments, customers, origin & destination branches, service plans and employees into a full delivery manifest.",
        "sql": """SELECT
    sh.tracking_number,
    c.name AS sender,
    sh.receiver_name,
    ob.city AS origin,
    db.city AS destination,
    st.service_name,
    e.first_name || ' ' || e.last_name AS delivery_agent,
    sh.weight_kg,
    sh.total_charge,
    sh.status
FROM shipments sh
JOIN customers c ON sh.sender_id = c.customer_id
JOIN branches ob ON sh.origin_branch_id = ob.branch_id
JOIN branches db ON sh.destination_branch_id = db.branch_id
JOIN service_types st ON sh.service_id = st.service_id
JOIN employees e ON sh.agent_id = e.employee_id
ORDER BY sh.tracking_number;"""
    },
    {
        "id": 2,
        "category": "LEFT OUTER JOIN",
        "title": "Find Unused Service Plans & Idle Vehicles (Zero Shipments)",
        "desc": "Uses LEFT JOIN with IS NULL to list service plans that no customer has ever booked.",
        "sql": """SELECT
    st.service_id,
    st.service_name,
    st.base_rate,
    st.rate_per_kg,
    st.is_active
FROM service_types st
LEFT JOIN shipments sh ON st.service_id = sh.service_id
WHERE sh.shipment_id IS NULL;"""
    },
    {
        "id": 3,
        "category": "Aggregate with GROUP BY & HAVING",
        "title": "High-Revenue Routes (Revenue > Rs 500)",
        "desc": "Aggregates revenue per origin-destination city pair and keeps only the profitable routes with HAVING.",
        "sql": """SELECT
    ob.city AS origin_city,
    db.city AS destination_city,
    COUNT(*) AS total_shipments,
    SUM(sh.weight_kg) AS total_weight_kg,
    SUM(sh.total_charge) AS total_revenue,
    ROUND(AVG(sh.total_charge), 2) AS avg_charge
FROM shipments sh
JOIN branches ob ON sh.origin_branch_id = ob.branch_id
JOIN branches db ON sh.destination_branch_id = db.branch_id
WHERE sh.status != 'Cancelled'
GROUP BY ob.city, db.city
HAVING SUM(sh.total_charge) > 500.0
ORDER BY total_revenue DESC;"""
    },
    {
        "id": 4,
        "category": "Nested Subquery (NOT IN)",
        "title": "Customers Who Never Used Express Air",
        "desc": "Uses NOT IN (subquery) to find registered senders who have never booked the Express Air plan.",
        "sql": """SELECT
    c.customer_id,
    c.name,
    c.city,
    c.reward_points
FROM customers c
WHERE c.customer_id NOT IN (
    SELECT DISTINCT sh.sender_id
    FROM shipments sh
    JOIN service_types st ON sh.service_id = st.service_id
    WHERE st.service_name = 'Express Air' AND sh.sender_id IS NOT NULL
)
ORDER BY c.reward_points DESC;"""
    },
    {
        "id": 5,
        "category": "Correlated Subquery",
        "title": "Heavier-Than-Average Shipments per Service Plan",
        "desc": "Compares each shipment's weight against the average weight of its own service plan.",
        "sql": """SELECT
    s1.tracking_number,
    st.service_name,
    s1.weight_kg,
    ROUND((SELECT AVG(s2.weight_kg) FROM shipments s2 WHERE s2.service_id = s1.service_id), 2) AS plan_avg_weight,
    ROUND(s1.weight_kg - (SELECT AVG(s2.weight_kg) FROM shipments s2 WHERE s2.service_id = s1.service_id), 2) AS excess_weight
FROM shipments s1
JOIN service_types st ON s1.service_id = st.service_id
WHERE s1.weight_kg > (
    SELECT AVG(s2.weight_kg)
    FROM shipments s2
    WHERE s2.service_id = s1.service_id
)
ORDER BY excess_weight DESC;"""
    },
    {
        "id": 6,
        "category": "Delivery Agent Performance",
        "title": "Agent Leaderboard (Assigned vs Delivered, Success Rate)",
        "desc": "Computes assigned count, delivered count and success percentage for every delivery agent using conditional aggregation.",
        "sql": """SELECT
    e.employee_id,
    e.first_name || ' ' || e.last_name AS agent_name,
    b.city AS base_city,
    COUNT(sh.shipment_id) AS shipments_assigned,
    SUM(CASE WHEN sh.status = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
    ROUND(100.0 * SUM(CASE WHEN sh.status = 'Delivered' THEN 1 ELSE 0 END) / COUNT(sh.shipment_id), 1) AS success_rate_pct
FROM employees e
JOIN branches b ON e.branch_id = b.branch_id
JOIN shipments sh ON e.employee_id = sh.agent_id
WHERE e.role = 'Delivery Agent'
GROUP BY e.employee_id
ORDER BY delivered DESC;"""
    },
    {
        "id": 7,
        "category": "Database Views",
        "title": "Querying Stored Analytics View (v_service_analytics)",
        "desc": "Reads from the pre-defined database view that abstracts service-wise revenue and weight totals.",
        "sql": """SELECT
    service_name,
    delivery_days,
    total_shipments,
    total_weight_kg,
    total_revenue
FROM v_service_analytics
WHERE total_shipments > 0
ORDER BY total_revenue DESC;"""
    },
    {
        "id": 8,
        "category": "Set Operations (UNION)",
        "title": "Unified Contact Directory (Customers UNION Employees UNION Branches)",
        "desc": "Demonstrates relational UNION combining customer, employee and branch phone books.",
        "sql": """SELECT name AS contact_name, phone, 'Customer' AS entity_type FROM customers
UNION
SELECT first_name || ' ' || last_name, phone, 'Employee (' || role || ')' FROM employees
UNION
SELECT branch_name, phone, 'Branch (' || branch_type || ')' FROM branches
ORDER BY entity_type, contact_name;"""
    }
]

@app.route('/query-lab')
def query_lab():
    return render_template('query_lab.html', presets=PRESET_COURIER_QUERIES)

@app.route('/api/execute-sql', methods=['POST'])
def api_execute_sql():
    data = request.get_json() or {}
    return jsonify(database.run_custom_query(data.get('sql', '').strip()))

# -------------------------------------------------------------------
# 8. Schema & ER Diagram Viewer
# -------------------------------------------------------------------
@app.route('/schema')
def schema_viewer():
    return render_template('schema_viewer.html', metadata=database.get_db_metadata())

@app.route('/download/schema-sqlite')
def download_sqlite_schema():
    return send_file(database.SCHEMA_PATH, as_attachment=True, download_name='courier_schema_sqlite.sql')

@app.route('/download/schema-mysql')
def download_mysql_schema():
    return send_file(os.path.join(database.BASE_DIR, 'mysql_schema.sql'), as_attachment=True, download_name='courier_schema_mysql.sql')

# -------------------------------------------------------------------
# 9. Audit Logs (Triggers Feed)
# -------------------------------------------------------------------
@app.route('/audit-logs')
def audit_logs():
    action_filter = request.args.get('action', '').strip()
    table_filter = request.args.get('table', '').strip()
    sql = "SELECT * FROM audit_logs WHERE 1=1"
    params = []
    if action_filter:
        sql += " AND action_type = ?"
        params.append(action_filter)
    if table_filter:
        sql += " AND table_name = ?"
        params.append(table_filter)
    sql += " ORDER BY log_id DESC LIMIT 100;"
    return render_template('audit_logs.html', logs=database.query_all(sql, params),
                           action_filter=action_filter, table_filter=table_filter, sql_used=sql)

# -------------------------------------------------------------------
# 10. Database Reset
# -------------------------------------------------------------------
@app.route('/reset-db', methods=['POST'])
def reset_db():
    try:
        database.reset_database()
        database.seed_database()
        flash("Courier Database has been reset and reseeded with clean sample records!", "success")
    except Exception as e:
        flash(f"Reset failed: {e}", "danger")
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("=================================================================")
    print("Courier DBMS Portal running at: http://127.0.0.1:5000")
    print("All SQL queries, CRUD actions, views, and triggers active!")
    print("=================================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
