-- ====================================================================
-- Academic DBMS Project: Courier Management System (CMS) - ParcelDB
-- Dialect: SQLite 3 (Standard SQL compatible with MySQL/MariaDB)
-- Normalization: 3rd Normal Form (3NF)
-- ====================================================================

PRAGMA foreign_keys = ON;

-- --------------------------------------------------------------------
-- 1. Branches Entity (Hubs / Service Centres)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS branches (
    branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_code VARCHAR(10) UNIQUE NOT NULL,
    branch_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    address TEXT,
    phone VARCHAR(20) UNIQUE NOT NULL,
    branch_type VARCHAR(20) CHECK(branch_type IN ('Hub', 'Service Centre', 'Pickup Point')) DEFAULT 'Service Centre'
);

-- --------------------------------------------------------------------
-- 2. Employees Entity
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(30) CHECK(role IN ('Branch Manager', 'Dispatcher', 'Delivery Agent', 'Sorting Staff', 'Customer Support')) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    salary DECIMAL(10, 2) CHECK(salary > 0) NOT NULL,
    hire_date DATE DEFAULT (DATE('now')),
    shift VARCHAR(20) CHECK(shift IN ('Morning', 'Evening', 'Night', 'Full Day')) DEFAULT 'Morning',
    branch_id INTEGER,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
);

-- --------------------------------------------------------------------
-- 3. Vehicles Entity (Fleet)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(15) CHECK(vehicle_type IN ('Bike', 'Van', 'Truck', 'Cargo Bike')) NOT NULL,
    capacity_kg DECIMAL(8, 2) CHECK(capacity_kg > 0) NOT NULL,
    status VARCHAR(20) CHECK(status IN ('Available', 'On Route', 'Maintenance')) DEFAULT 'Available',
    branch_id INTEGER,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
);

-- --------------------------------------------------------------------
-- 4. Customers Entity (Senders)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100),
    address TEXT,
    city VARCHAR(50),
    reward_points INTEGER CHECK(reward_points >= 0) DEFAULT 0,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------------------
-- 5. Service Types Entity (Pricing Plans)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS service_types (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    base_rate DECIMAL(8, 2) CHECK(base_rate > 0) NOT NULL,
    rate_per_kg DECIMAL(8, 2) CHECK(rate_per_kg >= 0) NOT NULL,
    delivery_days INTEGER CHECK(delivery_days >= 0) DEFAULT 3,
    is_active INTEGER CHECK(is_active IN (0, 1)) DEFAULT 1
);

-- --------------------------------------------------------------------
-- 6. Shipments Master Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_number VARCHAR(25) UNIQUE NOT NULL,
    sender_id INTEGER,
    receiver_name VARCHAR(100) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    receiver_address TEXT NOT NULL,
    origin_branch_id INTEGER,
    destination_branch_id INTEGER,
    service_id INTEGER NOT NULL,
    agent_id INTEGER,
    vehicle_id INTEGER,
    package_type VARCHAR(20) CHECK(package_type IN ('Document', 'Parcel', 'Fragile', 'Electronics', 'Perishable')) DEFAULT 'Parcel',
    weight_kg DECIMAL(8, 2) CHECK(weight_kg > 0) NOT NULL,
    status VARCHAR(20) CHECK(status IN ('Booked', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Returned', 'Cancelled')) DEFAULT 'Booked',
    payment_status VARCHAR(20) CHECK(payment_status IN ('Unpaid', 'Paid', 'Refunded')) DEFAULT 'Unpaid',
    payment_method VARCHAR(20) CHECK(payment_method IN ('Cash', 'Card', 'UPI', 'Pending')) DEFAULT 'Pending',
    total_charge DECIMAL(10, 2) CHECK(total_charge >= 0) DEFAULT 0.0,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (origin_branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL,
    FOREIGN KEY (destination_branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES service_types(service_id) ON DELETE RESTRICT,
    FOREIGN KEY (agent_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
);

-- --------------------------------------------------------------------
-- 7. Tracking Events Table (M:N between Shipments & Branches)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tracking_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id INTEGER NOT NULL,
    branch_id INTEGER,
    status VARCHAR(20) CHECK(status IN ('Booked', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Returned', 'Cancelled')) NOT NULL,
    remarks TEXT,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
);

-- --------------------------------------------------------------------
-- 8. Audit Logs Table (Automated Trigger Event Capture)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    record_id INTEGER,
    action_details TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------------------
-- Performance Indexes
-- --------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_emp_branch ON employees(branch_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_branch ON vehicles(branch_id);
CREATE INDEX IF NOT EXISTS idx_ship_sender ON shipments(sender_id);
CREATE INDEX IF NOT EXISTS idx_ship_service ON shipments(service_id);
CREATE INDEX IF NOT EXISTS idx_ship_agent ON shipments(agent_id);
CREATE INDEX IF NOT EXISTS idx_ship_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_event_shipment ON tracking_events(shipment_id);
CREATE INDEX IF NOT EXISTS idx_event_branch ON tracking_events(branch_id);

-- --------------------------------------------------------------------
-- SQL Stored Views
-- --------------------------------------------------------------------

-- View 1: Complete Shipment Tracking & Billing Summary View
CREATE VIEW IF NOT EXISTS v_shipment_tracking_summary AS
SELECT
    sh.shipment_id,
    sh.tracking_number,
    sh.status,
    sh.package_type,
    sh.weight_kg,
    sh.total_charge,
    sh.payment_status,
    sh.booked_at,
    sh.delivered_at,
    COALESCE(c.name, 'Walk-in Sender') AS sender_name,
    sh.receiver_name,
    ob.city AS origin_city,
    db.city AS destination_city,
    st.service_name,
    COALESCE(e.first_name || ' ' || e.last_name, 'Unassigned') AS agent_name,
    COUNT(te.event_id) AS scan_events
FROM shipments sh
LEFT JOIN customers c ON sh.sender_id = c.customer_id
LEFT JOIN branches ob ON sh.origin_branch_id = ob.branch_id
LEFT JOIN branches db ON sh.destination_branch_id = db.branch_id
JOIN service_types st ON sh.service_id = st.service_id
LEFT JOIN employees e ON sh.agent_id = e.employee_id
LEFT JOIN tracking_events te ON sh.shipment_id = te.shipment_id
GROUP BY sh.shipment_id;

-- View 2: Service Plan Revenue Analytics View
CREATE VIEW IF NOT EXISTS v_service_analytics AS
SELECT
    st.service_id,
    st.service_name,
    st.base_rate,
    st.rate_per_kg,
    st.delivery_days,
    COUNT(sh.shipment_id) AS total_shipments,
    COALESCE(SUM(sh.weight_kg), 0.0) AS total_weight_kg,
    COALESCE(SUM(sh.total_charge), 0.0) AS total_revenue
FROM service_types st
LEFT JOIN shipments sh ON st.service_id = sh.service_id AND sh.status != 'Cancelled'
GROUP BY st.service_id;

-- View 3: Delivery Agent Performance Analytics View
CREATE VIEW IF NOT EXISTS v_agent_performance AS
SELECT
    e.employee_id,
    e.first_name || ' ' || e.last_name AS agent_name,
    e.shift,
    COALESCE(b.city, 'N/A') AS base_city,
    COUNT(sh.shipment_id) AS total_assigned,
    SUM(CASE WHEN sh.status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_count,
    COALESCE(SUM(sh.total_charge), 0.0) AS revenue_handled
FROM employees e
LEFT JOIN branches b ON e.branch_id = b.branch_id
LEFT JOIN shipments sh ON e.employee_id = sh.agent_id
WHERE e.role = 'Delivery Agent'
GROUP BY e.employee_id;

-- --------------------------------------------------------------------
-- Database Triggers (Automated Business Logic Enforcement)
-- --------------------------------------------------------------------

-- Trigger 1: When a shipment is booked, create the first tracking scan,
--            mark the assigned vehicle 'On Route' and write an audit entry
CREATE TRIGGER IF NOT EXISTS trg_after_shipment_insert_booked
AFTER INSERT ON shipments
BEGIN
    INSERT INTO tracking_events (shipment_id, branch_id, status, remarks, event_time)
    VALUES (NEW.shipment_id, NEW.origin_branch_id, 'Booked', 'Shipment booked at origin branch.', NEW.booked_at);

    UPDATE vehicles
    SET status = 'On Route'
    WHERE vehicle_id = NEW.vehicle_id AND status = 'Available';

    INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
    VALUES (
        'shipments',
        'INSERT',
        NEW.shipment_id,
        'Shipment ' || NEW.tracking_number || ' booked (' || NEW.weight_kg || ' kg, Rs ' || NEW.total_charge || '). First tracking scan created.'
    );
END;

-- Trigger 2: Every new tracking scan automatically updates the shipment status
--            (and stamps delivered_at when the parcel is delivered)
CREATE TRIGGER IF NOT EXISTS trg_after_tracking_event_insert_sync_status
AFTER INSERT ON tracking_events
BEGIN
    UPDATE shipments
    SET status = NEW.status,
        delivered_at = CASE WHEN NEW.status = 'Delivered' THEN NEW.event_time ELSE delivered_at END
    WHERE shipment_id = NEW.shipment_id;

    INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
    VALUES (
        'tracking_events',
        'INSERT',
        NEW.event_id,
        'Scan "' || NEW.status || '" recorded for Shipment ID #' || NEW.shipment_id || '. Shipment status synchronised.'
    );
END;

-- Trigger 3: When a shipment is Delivered, free the vehicle and credit reward points
CREATE TRIGGER IF NOT EXISTS trg_after_shipment_delivered
AFTER UPDATE ON shipments
WHEN OLD.status != 'Delivered' AND NEW.status = 'Delivered'
BEGIN
    -- Free the vehicle if it has no other active shipment
    UPDATE vehicles
    SET status = 'Available'
    WHERE vehicle_id = NEW.vehicle_id
      AND status = 'On Route'
      AND NOT EXISTS (
          SELECT 1 FROM shipments
          WHERE vehicle_id = NEW.vehicle_id
            AND shipment_id != NEW.shipment_id
            AND status NOT IN ('Delivered', 'Returned', 'Cancelled')
      );

    -- Award 1 reward point per Rs 100 charged to a registered sender
    UPDATE customers
    SET reward_points = reward_points + CAST(NEW.total_charge / 100 AS INTEGER)
    WHERE customer_id = NEW.sender_id;

    INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
    VALUES (
        'shipments',
        'UPDATE',
        NEW.shipment_id,
        'Shipment ' || NEW.tracking_number || ' delivered. Vehicle released & sender reward points credited.'
    );
END;

-- Trigger 4: Log Shipment Deletion
CREATE TRIGGER IF NOT EXISTS trg_after_shipment_delete
AFTER DELETE ON shipments
BEGIN
    INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
    VALUES (
        'shipments',
        'DELETE',
        OLD.shipment_id,
        'Shipment ' || OLD.tracking_number || ' deleted. Associated tracking_events removed via CASCADE.'
    );
END;
