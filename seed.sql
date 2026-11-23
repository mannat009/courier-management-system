-- ====================================================================
-- Academic DBMS Project: Courier Sample Seed Data
-- ====================================================================

DELETE FROM tracking_events;
DELETE FROM shipments;
DELETE FROM customers;
DELETE FROM service_types;
DELETE FROM vehicles;
DELETE FROM employees;
DELETE FROM branches;
DELETE FROM audit_logs;

DELETE FROM sqlite_sequence WHERE name IN ('branches', 'employees', 'vehicles', 'customers', 'service_types', 'shipments', 'tracking_events', 'audit_logs');

-- --------------------------------------------------------------------
-- 1. Branches
-- --------------------------------------------------------------------
INSERT INTO branches (branch_id, branch_code, branch_name, city, state, address, phone, branch_type) VALUES
(1, 'DEL-HUB', 'Delhi Central Hub', 'New Delhi', 'Delhi', 'Plot 12, Transport Nagar, Okhla Phase II', '+91-1140001001', 'Hub'),
(2, 'GGN-SC', 'Gurugram Service Centre', 'Gurugram', 'Haryana', 'Sector 29, Near Leisure Valley Park', '+91-1240002002', 'Service Centre'),
(3, 'BOM-HUB', 'Mumbai Gateway Hub', 'Mumbai', 'Maharashtra', 'Andheri East, MIDC Logistics Park', '+91-2240003003', 'Hub'),
(4, 'BLR-HUB', 'Bengaluru Tech Hub', 'Bengaluru', 'Karnataka', 'Whitefield, ITPL Main Road', '+91-8040004004', 'Hub'),
(5, 'CCU-SC', 'Kolkata Service Centre', 'Kolkata', 'West Bengal', 'Salt Lake Sector V', '+91-3340005005', 'Service Centre'),
(6, 'MAA-SC', 'Chennai Service Centre', 'Chennai', 'Tamil Nadu', 'Guindy Industrial Estate', '+91-4440006006', 'Service Centre'),
(7, 'JPR-PP', 'Jaipur Pickup Point', 'Jaipur', 'Rajasthan', 'MI Road, Near Raj Mandir', '+91-1410007007', 'Pickup Point');

-- --------------------------------------------------------------------
-- 2. Employees
-- --------------------------------------------------------------------
INSERT INTO employees (employee_id, first_name, last_name, role, phone, email, salary, hire_date, shift, branch_id) VALUES
(1, 'Rakesh', 'Malhotra', 'Branch Manager', '+91-9811100001', 'rakesh.m@parceldb.com', 62000.00, '2021-04-01', 'Full Day', 1),
(2, 'Anita', 'Deshmukh', 'Branch Manager', '+91-9811100002', 'anita.d@parceldb.com', 58000.00, '2022-01-10', 'Full Day', 3),
(3, 'Suresh', 'Yadav', 'Dispatcher', '+91-9811100003', 'suresh.y@parceldb.com', 34000.00, '2022-06-15', 'Morning', 1),
(4, 'Manoj', 'Tiwari', 'Delivery Agent', '+91-9811100004', 'manoj.t@parceldb.com', 24000.00, '2023-02-01', 'Morning', 1),
(5, 'Imran', 'Sheikh', 'Delivery Agent', '+91-9811100005', 'imran.s@parceldb.com', 24500.00, '2023-03-20', 'Evening', 3),
(6, 'Karthik', 'Raman', 'Delivery Agent', '+91-9811100006', 'karthik.r@parceldb.com', 23500.00, '2023-08-05', 'Morning', 4),
(7, 'Deepak', 'Chauhan', 'Delivery Agent', '+91-9811100007', 'deepak.c@parceldb.com', 22500.00, '2024-01-12', 'Evening', 2),
(8, 'Sourav', 'Ghosh', 'Delivery Agent', '+91-9811100008', 'sourav.g@parceldb.com', 23000.00, '2024-02-18', 'Morning', 5),
(9, 'Lakshmi', 'Iyer', 'Sorting Staff', '+91-9811100009', 'lakshmi.i@parceldb.com', 21000.00, '2023-09-09', 'Night', 6),
(10, 'Nikhil', 'Bansal', 'Customer Support', '+91-9811100010', 'nikhil.b@parceldb.com', 28000.00, '2022-11-25', 'Full Day', 1);

-- --------------------------------------------------------------------
-- 3. Vehicles
-- --------------------------------------------------------------------
INSERT INTO vehicles (vehicle_id, vehicle_number, vehicle_type, capacity_kg, status, branch_id) VALUES
(1, 'DL-01-AB-1234', 'Van', 800.00, 'Available', 1),
(2, 'DL-04-CD-5678', 'Bike', 25.00, 'Available', 1),
(3, 'MH-02-EF-9012', 'Truck', 5000.00, 'Available', 3),
(4, 'MH-01-GH-3456', 'Cargo Bike', 40.00, 'Available', 3),
(5, 'KA-03-JK-7890', 'Van', 750.00, 'Available', 4),
(6, 'HR-26-LM-2468', 'Bike', 25.00, 'Available', 2),
(7, 'WB-06-NP-1357', 'Van', 700.00, 'Maintenance', 5),
(8, 'TN-09-QR-8642', 'Truck', 4500.00, 'Available', 6);

-- --------------------------------------------------------------------
-- 4. Customers
-- --------------------------------------------------------------------
INSERT INTO customers (customer_id, name, phone, email, address, city, reward_points) VALUES
(1, 'Aditya Malhotra', '+91-9988776601', 'aditya.m@gmail.com', 'B-45, Defence Colony', 'New Delhi', 40),
(2, 'Neha Sen', '+91-9988776602', 'neha.sen@yahoo.com', '22, Park Street', 'Kolkata', 15),
(3, 'Kunal Kapoor', '+91-9988776603', 'kunal.k@outlook.com', 'Flat 7, Powai Heights', 'Mumbai', 0),
(4, 'Simran Kaur', '+91-9988776604', 'simran.kaur@gmail.com', 'Sector 56, Golf Course Road', 'Gurugram', 62),
(5, 'Gaurav Jain', '+91-9988776605', 'gaurav.jain@gmail.com', 'C-Scheme, Ashok Nagar', 'Jaipur', 8),
(6, 'Priya Nair', '+91-9988776606', 'priya.nair@corp.com', 'HSR Layout, Sector 2', 'Bengaluru', 0),
(7, 'TechNova Pvt Ltd', '+91-9988776607', 'dispatch@technova.in', 'Electronic City Phase 1', 'Bengaluru', 120);

-- --------------------------------------------------------------------
-- 5. Service Types
-- --------------------------------------------------------------------
INSERT INTO service_types (service_id, service_name, description, base_rate, rate_per_kg, delivery_days, is_active) VALUES
(1, 'Standard Surface', 'Economical road delivery for non-urgent parcels', 40.00, 18.00, 5, 1),
(2, 'Express Air', 'Priority air-linked delivery between metro cities', 90.00, 45.00, 2, 1),
(3, 'Same Day Local', 'Within-city delivery completed the same day', 60.00, 25.00, 0, 1),
(4, 'Heavy Freight', 'Truck-based cargo for bulk and heavy consignments', 250.00, 12.00, 7, 1),
(5, 'International Priority', 'Cross-border express service (currently suspended)', 900.00, 350.00, 6, 0);

-- --------------------------------------------------------------------
-- 6. Shipments (inserted as Booked; triggers create the first scan)
-- --------------------------------------------------------------------
INSERT INTO shipments (shipment_id, tracking_number, sender_id, receiver_name, receiver_phone, receiver_address, origin_branch_id, destination_branch_id, service_id, agent_id, vehicle_id, package_type, weight_kg, payment_status, payment_method, total_charge, booked_at) VALUES
(1, 'PDB-2026-0001', 1, 'Rohit Sharma', '+91-9700000001', '14, Marine Drive, Mumbai', 1, 3, 2, 5, NULL, 'Electronics', 2.50, 'Paid', 'UPI', 202.50, '2026-11-10 10:15:00'),
(2, 'PDB-2026-0002', 2, 'Ankita Das', '+91-9700000002', 'Anna Nagar, Chennai', 5, 6, 1, NULL, NULL, 'Parcel', 6.00, 'Paid', 'Card', 148.00, '2026-11-11 12:00:00'),
(3, 'PDB-2026-0003', 3, 'Mehul Shah', '+91-9700000003', 'Bandra West, Mumbai', 3, 3, 3, 5, NULL, 'Document', 0.50, 'Paid', 'Cash', 72.50, '2026-11-12 09:30:00'),
(4, 'PDB-2026-0004', 4, 'Vivek Arora', '+91-9700000004', 'Koramangala, Bengaluru', 2, 4, 2, 6, NULL, 'Fragile', 4.00, 'Paid', 'UPI', 270.00, '2026-11-13 16:40:00'),
(5, 'PDB-2026-0005', 7, 'Infinity Retail Ltd', '+91-9700000005', 'Sector 18, Noida', 4, 1, 4, 4, 1, 'Parcel', 350.00, 'Unpaid', 'Pending', 4450.00, '2026-11-18 08:20:00'),
(6, 'PDB-2026-0006', 5, 'Sunita Rathore', '+91-9700000006', 'Vaishali Nagar, Jaipur', 7, 1, 1, 4, NULL, 'Parcel', 3.20, 'Unpaid', 'Pending', 97.60, '2026-11-19 11:10:00'),
(7, 'PDB-2026-0007', 6, 'Arjun Reddy', '+91-9700000007', 'Banjara Hills, Hyderabad', 4, 6, 2, 6, 5, 'Electronics', 1.80, 'Paid', 'Card', 171.00, '2026-11-20 14:05:00'),
(8, 'PDB-2026-0008', 1, 'Pallavi Joshi', '+91-9700000008', 'Koregaon Park, Pune', 1, 3, 1, NULL, NULL, 'Perishable', 5.50, 'Unpaid', 'Pending', 139.00, '2026-11-22 17:45:00'),
(9, 'PDB-2026-0009', 4, 'Rahul Bose', '+91-9700000009', 'Salt Lake, Kolkata', 2, 5, 2, 7, 6, 'Document', 0.80, 'Paid', 'UPI', 126.00, '2026-11-21 09:00:00'),
(10, 'PDB-2026-0010', 7, 'Greenleaf Exports', '+91-9700000010', 'Fort, Mumbai', 4, 3, 4, 6, NULL, 'Parcel', 120.00, 'Paid', 'Card', 1690.00, '2026-11-15 10:00:00');

-- --------------------------------------------------------------------
-- 7. Tracking Events (Triggers sync shipment status & reward points)
-- --------------------------------------------------------------------
INSERT INTO tracking_events (shipment_id, branch_id, status, remarks, event_time) VALUES
-- Shipment 1: Delivered (Delhi -> Mumbai)
(1, 1, 'Picked Up', 'Picked up from sender by Delhi hub.', '2026-11-10 11:30:00'),
(1, 1, 'In Transit', 'Dispatched on air-linked Delhi-Mumbai line.', '2026-11-10 18:00:00'),
(1, 3, 'Out for Delivery', 'Arrived Mumbai hub; assigned to delivery agent.', '2026-11-11 09:00:00'),
(1, 3, 'Delivered', 'Delivered and signed by receiver.', '2026-11-11 13:20:00'),
-- Shipment 2: Delivered (Kolkata -> Chennai)
(2, 5, 'Picked Up', 'Collected from sender address.', '2026-11-11 15:00:00'),
(2, 5, 'In Transit', 'Left Kolkata on surface line.', '2026-11-12 06:00:00'),
(2, 6, 'Out for Delivery', 'Reached Chennai service centre.', '2026-11-16 08:30:00'),
(2, 6, 'Delivered', 'Delivered to receiver.', '2026-11-16 12:45:00'),
-- Shipment 3: Delivered (same-day, Mumbai)
(3, 3, 'Picked Up', 'Picked up by local rider.', '2026-11-12 10:00:00'),
(3, 3, 'Out for Delivery', 'Out for same-day delivery.', '2026-11-12 11:30:00'),
(3, 3, 'Delivered', 'Delivered within 3 hours.', '2026-11-12 13:00:00'),
-- Shipment 4: Out for Delivery (Gurugram -> Bengaluru)
(4, 2, 'Picked Up', 'Fragile parcel picked up and bubble-packed.', '2026-11-13 17:30:00'),
(4, 1, 'In Transit', 'Routed via Delhi hub to air line.', '2026-11-14 02:00:00'),
(4, 4, 'Out for Delivery', 'At Bengaluru hub; out with delivery agent.', '2026-11-23 08:15:00'),
-- Shipment 5: In Transit with vehicle (Bengaluru -> Delhi, freight)
(5, 4, 'Picked Up', 'Freight loaded at Bengaluru hub.', '2026-11-18 12:00:00'),
(5, 4, 'In Transit', 'Truck departed for Delhi.', '2026-11-18 20:00:00'),
-- Shipment 6: Picked Up (Jaipur -> Delhi)
(6, 7, 'Picked Up', 'Collected at Jaipur pickup point.', '2026-11-19 15:00:00'),
-- Shipment 7: In Transit (Bengaluru -> Chennai)
(7, 4, 'Picked Up', 'Picked up from sender.', '2026-11-20 15:00:00'),
(7, 4, 'In Transit', 'On the way to Chennai.', '2026-11-21 05:30:00'),
-- Shipment 9: Out for Delivery (Gurugram -> Kolkata)
(9, 2, 'Picked Up', 'Document pouch collected.', '2026-11-21 10:00:00'),
(9, 5, 'Out for Delivery', 'At Kolkata service centre; out for delivery.', '2026-11-23 09:30:00'),
-- Shipment 10: Delivered (Bengaluru -> Mumbai, freight)
(10, 4, 'Picked Up', 'Bulk consignment loaded.', '2026-11-15 12:00:00'),
(10, 4, 'In Transit', 'Truck departed.', '2026-11-15 22:00:00'),
(10, 3, 'Out for Delivery', 'Arrived at Mumbai hub.', '2026-11-20 08:00:00'),
(10, 3, 'Delivered', 'Delivered to consignee warehouse.', '2026-11-20 15:30:00');

-- Initial System Audit entry
INSERT INTO audit_logs (table_name, action_type, record_id, action_details)
VALUES ('SYSTEM', 'INITIALIZE', 0, 'Courier Database initialized with 3NF Schema, branches, employees, fleet, service plans, and seed shipments.');
