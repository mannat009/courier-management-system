-- ====================================================================
-- Academic DBMS Project: Courier Management System (MySQL Dialect)
-- Compatible with MySQL 8.0.16+ / MariaDB 10.5+ / phpMyAdmin / XAMPP
-- Run the whole script, then insert your own sample rows (or adapt seed.sql).
-- ====================================================================

CREATE DATABASE IF NOT EXISTS courier_db;
USE courier_db;

-- 1. Branches
CREATE TABLE IF NOT EXISTS branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_code VARCHAR(10) NOT NULL UNIQUE,
    branch_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    address TEXT,
    phone VARCHAR(20) NOT NULL UNIQUE,
    branch_type ENUM('Hub', 'Service Centre', 'Pickup Point') DEFAULT 'Service Centre'
) ENGINE=InnoDB;

-- 2. Employees
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role ENUM('Branch Manager', 'Dispatcher', 'Delivery Agent', 'Sorting Staff', 'Customer Support') NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    salary DECIMAL(10, 2) NOT NULL CHECK(salary > 0),
    hire_date DATE DEFAULT (CURRENT_DATE),
    shift ENUM('Morning', 'Evening', 'Night', 'Full Day') DEFAULT 'Morning',
    branch_id INT,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. Vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type ENUM('Bike', 'Van', 'Truck', 'Cargo Bike') NOT NULL,
    capacity_kg DECIMAL(8, 2) NOT NULL CHECK(capacity_kg > 0),
    status ENUM('Available', 'On Route', 'Maintenance') DEFAULT 'Available',
    branch_id INT,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 4. Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    address TEXT,
    city VARCHAR(50),
    reward_points INT DEFAULT 0 CHECK(reward_points >= 0),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 5. Service Types
CREATE TABLE IF NOT EXISTS service_types (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    base_rate DECIMAL(8, 2) NOT NULL CHECK(base_rate > 0),
    rate_per_kg DECIMAL(8, 2) NOT NULL CHECK(rate_per_kg >= 0),
    delivery_days INT DEFAULT 3 CHECK(delivery_days >= 0),
    is_active TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- 6. Shipments Master
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(25) NOT NULL UNIQUE,
    sender_id INT,
    receiver_name VARCHAR(100) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    receiver_address TEXT NOT NULL,
    origin_branch_id INT,
    destination_branch_id INT,
    service_id INT NOT NULL,
    agent_id INT,
    vehicle_id INT,
    package_type ENUM('Document', 'Parcel', 'Fragile', 'Electronics', 'Perishable') DEFAULT 'Parcel',
    weight_kg DECIMAL(8, 2) NOT NULL CHECK(weight_kg > 0),
    status ENUM('Booked', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Returned', 'Cancelled') DEFAULT 'Booked',
    payment_status ENUM('Unpaid', 'Paid', 'Refunded') DEFAULT 'Unpaid',
    payment_method ENUM('Cash', 'Card', 'UPI', 'Pending') DEFAULT 'Pending',
    total_charge DECIMAL(10, 2) DEFAULT 0.0 CHECK(total_charge >= 0),
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP NULL,
    FOREIGN KEY (sender_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (origin_branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL,
    FOREIGN KEY (destination_branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES service_types(service_id) ON DELETE RESTRICT,
    FOREIGN KEY (agent_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 7. Tracking Events (M:N between shipments and branches)
CREATE TABLE IF NOT EXISTS tracking_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id INT NOT NULL,
    branch_id INT,
    status ENUM('Booked', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Returned', 'Cancelled') NOT NULL,
    remarks TEXT,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    record_id INT,
    action_details TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Indexes
CREATE INDEX idx_ship_status ON shipments(status);
CREATE INDEX idx_ship_sender ON shipments(sender_id);
CREATE INDEX idx_event_shipment ON tracking_events(shipment_id);

-- Views
CREATE OR REPLACE VIEW v_shipment_tracking_summary AS
SELECT
    sh.shipment_id, sh.tracking_number, sh.status, sh.package_type, sh.weight_kg, sh.total_charge,
    sh.payment_status, sh.booked_at, sh.delivered_at,
    COALESCE(c.name, 'Walk-in Sender') AS sender_name,
    sh.receiver_name,
    ob.city AS origin_city,
    db.city AS destination_city,
    st.service_name,
    COALESCE(CONCAT(e.first_name, ' ', e.last_name), 'Unassigned') AS agent_name,
    COUNT(te.event_id) AS scan_events
FROM shipments sh
LEFT JOIN customers c ON sh.sender_id = c.customer_id
LEFT JOIN branches ob ON sh.origin_branch_id = ob.branch_id
LEFT JOIN branches db ON sh.destination_branch_id = db.branch_id
JOIN service_types st ON sh.service_id = st.service_id
LEFT JOIN employees e ON sh.agent_id = e.employee_id
LEFT JOIN tracking_events te ON sh.shipment_id = te.shipment_id
GROUP BY sh.shipment_id, sh.tracking_number, sh.status, sh.package_type, sh.weight_kg, sh.total_charge,
         sh.payment_status, sh.booked_at, sh.delivered_at, c.name, sh.receiver_name, ob.city, db.city,
         st.service_name, e.first_name, e.last_name;

CREATE OR REPLACE VIEW v_service_analytics AS
SELECT
    st.service_id, st.service_name, st.base_rate, st.rate_per_kg, st.delivery_days,
    COUNT(sh.shipment_id) AS total_shipments,
    COALESCE(SUM(sh.weight_kg), 0.0) AS total_weight_kg,
    COALESCE(SUM(sh.total_charge), 0.0) AS total_revenue
FROM service_types st
LEFT JOIN shipments sh ON st.service_id = sh.service_id AND sh.status <> 'Cancelled'
GROUP BY st.service_id, st.service_name, st.base_rate, st.rate_per_kg, st.delivery_days;

CREATE OR REPLACE VIEW v_agent_performance AS
SELECT
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS agent_name,
    e.shift,
    COALESCE(b.city, 'N/A') AS base_city,
    COUNT(sh.shipment_id) AS total_assigned,
    SUM(CASE WHEN sh.status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_count,
    COALESCE(SUM(sh.total_charge), 0.0) AS revenue_handled
FROM employees e
LEFT JOIN branches b ON e.branch_id = b.branch_id
LEFT JOIN shipments sh ON e.employee_id = sh.agent_id
WHERE e.role = 'Delivery Agent'
GROUP BY e.employee_id, e.first_name, e.last_name, e.shift, b.city;

-- ====================================================================
-- Triggers (MySQL syntax)
-- Note: MySQL forbids a trigger from updating the table that fired it
-- (Error 1442), so the status-sync trigger skips the 'Booked' scan that
-- trigger 1 inserts while a shipment is being created.
-- ====================================================================
DELIMITER $$

CREATE TRIGGER trg_after_shipment_insert_booked
AFTER INSERT ON shipments
FOR EACH ROW
BEGIN
    INSERT INTO tracking_events (shipment_id, branch_id, status, remarks, event_time)
    VALUES (NEW.shipment_id, NEW.origin_branch_id, 'Booked', 'Shipment booked at origin branch.', NEW.booked_at);

    UPDATE vehicles SET status = 'On Route'
    WHERE vehicle_id = NEW.vehicle_id AND status = 'Available';

    INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
    VALUES ('shipments', 'INSERT', NEW.shipment_id,
            CONCAT('Shipment ', NEW.tracking_number, ' booked (', NEW.weight_kg, ' kg, Rs ', NEW.total_charge, '). First tracking scan created.'));
END$$

CREATE TRIGGER trg_after_tracking_event_insert_sync_status
AFTER INSERT ON tracking_events
FOR EACH ROW
BEGIN
    IF NEW.status <> 'Booked' THEN
        UPDATE shipments
        SET status = NEW.status,
            delivered_at = CASE WHEN NEW.status = 'Delivered' THEN NEW.event_time ELSE delivered_at END
        WHERE shipment_id = NEW.shipment_id;
    END IF;

    INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
    VALUES ('tracking_events', 'INSERT', NEW.event_id,
            CONCAT('Scan "', NEW.status, '" recorded for Shipment ID #', NEW.shipment_id, '. Shipment status synchronised.'));
END$$

CREATE TRIGGER trg_after_shipment_delivered
AFTER UPDATE ON shipments
FOR EACH ROW
BEGIN
    IF OLD.status <> 'Delivered' AND NEW.status = 'Delivered' THEN
        UPDATE vehicles SET status = 'Available'
        WHERE vehicle_id = NEW.vehicle_id AND status = 'On Route'
          AND NOT EXISTS (
              SELECT 1 FROM shipments s
              WHERE s.vehicle_id = NEW.vehicle_id AND s.shipment_id <> NEW.shipment_id
                AND s.status NOT IN ('Delivered', 'Returned', 'Cancelled')
          );

        UPDATE customers SET reward_points = reward_points + FLOOR(NEW.total_charge / 100)
        WHERE customer_id = NEW.sender_id;

        INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
        VALUES ('shipments', 'UPDATE', NEW.shipment_id,
                CONCAT('Shipment ', NEW.tracking_number, ' delivered. Vehicle released & sender reward points credited.'));
    END IF;
END$$

CREATE TRIGGER trg_after_shipment_delete
AFTER DELETE ON shipments
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
    VALUES ('shipments', 'DELETE', OLD.shipment_id,
            CONCAT('Shipment ', OLD.tracking_number, ' deleted. Associated tracking_events removed via CASCADE.'));
END$$

DELIMITER ;
