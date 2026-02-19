-- Sample data for Asset Inventory Tracker
-- Run after initial migrations

-- Sample Users (passwords are hashed 'password123')
INSERT INTO users (email, username, hashed_password, full_name, department, role, is_active, created_at, updated_at)
VALUES 
  ('admin@company.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.3cW6jL8s8m0oy.a', 'System Admin', 'IT', 'admin', 1, datetime('now'), datetime('now')),
  ('john.smith@company.com', 'jsmith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.3cW6jL8s8m0oy.a', 'John Smith', 'Engineering', 'user', 1, datetime('now'), datetime('now')),
  ('jane.doe@company.com', 'jdoe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.3cW6jL8s8m0oy.a', 'Jane Doe', 'Marketing', 'user', 1, datetime('now'), datetime('now')),
  ('auditor@company.com', 'auditor', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.3cW6jL8s8m0oy.a', 'Bob Auditor', 'Finance', 'auditor', 1, datetime('now'), datetime('now'));

-- Sample Assets
INSERT INTO assets (asset_tag, name, category, description, serial_number, manufacturer, model, purchase_date, status, location, created_at, updated_at)
VALUES
  ('AST-001', 'MacBook Pro 16"', 'laptop', '16-inch MacBook Pro with M3 Max chip', 'FVFXC2ABCD01', 'Apple', 'MacBook Pro 16" M3 Max', '2024-01-15', 'available', 'IT Storage Room A', datetime('now'), datetime('now')),
  ('AST-002', 'MacBook Pro 14"', 'laptop', '14-inch MacBook Pro with M3 Pro chip', 'FVFXC2ABCD02', 'Apple', 'MacBook Pro 14" M3 Pro', '2024-01-15', 'checked_out', 'Engineering Floor 3', datetime('now'), datetime('now')),
  ('AST-003', 'Dell XPS 15', 'laptop', 'Dell XPS 15 with Intel i9', 'DELLXPS15001', 'Dell', 'XPS 15 9530', '2023-11-20', 'available', 'IT Storage Room A', datetime('now'), datetime('now')),
  ('AST-004', 'ThinkPad X1 Carbon', 'laptop', 'Lenovo ThinkPad X1 Carbon Gen 11', 'TPXC11G00001', 'Lenovo', 'ThinkPad X1 Carbon Gen 11', '2023-10-05', 'maintenance', 'IT Workshop', datetime('now'), datetime('now')),
  ('AST-005', 'Dell UltraSharp 27"', 'monitor', '27-inch 4K USB-C Hub Monitor', 'DELLMON27001', 'Dell', 'U2723QE', '2024-02-01', 'available', 'IT Storage Room B', datetime('now'), datetime('now')),
  ('AST-006', 'Dell UltraSharp 27"', 'monitor', '27-inch 4K USB-C Hub Monitor', 'DELLMON27002', 'Dell', 'U2723QE', '2024-02-01', 'checked_out', 'Engineering Floor 3', datetime('now'), datetime('now')),
  ('AST-007', 'LG UltraFine 32"', 'monitor', '32-inch 4K Thunderbolt Display', 'LGUF32001', 'LG', 'UltraFine 32UN880', '2023-09-15', 'available', 'IT Storage Room B', datetime('now'), datetime('now')),
  ('AST-008', 'Magic Keyboard', 'keyboard', 'Apple Magic Keyboard with Touch ID', 'APKB001', 'Apple', 'Magic Keyboard', '2024-01-15', 'available', 'IT Storage Room C', datetime('now'), datetime('now')),
  ('AST-009', 'Magic Mouse', 'mouse', 'Apple Magic Mouse', 'APMM001', 'Apple', 'Magic Mouse', '2024-01-15', 'checked_out', 'Marketing Floor 2', datetime('now'), datetime('now')),
  ('AST-010', 'Logitech MX Master 3S', 'mouse', 'Wireless mouse with MagSpeed wheel', 'LGMXM3S001', 'Logitech', 'MX Master 3S', '2023-12-10', 'available', 'IT Storage Room C', datetime('now'), datetime('now')),
  ('AST-011', 'AirPods Pro', 'headset', 'Apple AirPods Pro 2nd Gen with USB-C', 'APAPRO001', 'Apple', 'AirPods Pro 2', '2024-01-20', 'checked_out', 'Engineering Floor 3', datetime('now'), datetime('now')),
  ('AST-012', 'Sony WH-1000XM5', 'headset', 'Wireless noise-canceling headphones', 'SNYWH1000XM5001', 'Sony', 'WH-1000XM5', '2023-11-01', 'available', 'IT Storage Room C', datetime('now'), datetime('now')),
  ('AST-013', 'iPhone 15 Pro', 'phone', 'Company iPhone 15 Pro 256GB', 'IP15PRO001', 'Apple', 'iPhone 15 Pro', '2024-01-10', 'checked_out', 'Executive Suite', datetime('now'), datetime('now')),
  ('AST-014', 'Server Room Key', 'key', 'Physical key to Server Room A', 'KEY-SRA-001', 'N/A', 'Physical Key', '2020-01-01', 'available', 'Security Desk', datetime('now'), datetime('now')),
  ('AST-015', 'Office Master Key', 'key', 'Master key for all office doors', 'KEY-MASTER-001', 'N/A', 'Physical Key', '2020-01-01', 'checked_out', 'Facilities', datetime('now'), datetime('now'));

-- Assign some assets
UPDATE assets SET assigned_to = 2 WHERE asset_tag = 'AST-002';
UPDATE assets SET assigned_to = 2 WHERE asset_tag = 'AST-006';
UPDATE assets SET assigned_to = 2 WHERE asset_tag = 'AST-011';
UPDATE assets SET assigned_to = 3 WHERE asset_tag = 'AST-009';
UPDATE assets SET assigned_to = 1 WHERE asset_tag = 'AST-013';
UPDATE assets SET assigned_to = 1 WHERE asset_tag = 'AST-015';

-- Sample Software Licenses
INSERT INTO software_licenses (name, vendor, license_key, license_type, seats_total, seats_used, expires_at, cost, notes, created_at, updated_at)
VALUES
  ('Microsoft 365 Business', 'Microsoft', 'XXXXX-XXXXX-XXXXX-XXXXX', 'subscription', 50, 35, '2025-01-15', '$12/user/month', 'Annual subscription', datetime('now'), datetime('now')),
  ('Adobe Creative Cloud', 'Adobe', 'ADOBE-CC-ENTERPRISE-001', 'subscription', 20, 12, '2025-03-01', '$54.99/user/month', 'Creative Cloud All Apps', datetime('now'), datetime('now')),
  ('Slack Business+', 'Slack', 'SLACK-BIZ-001', 'subscription', 100, 78, '2025-02-28', '$12.50/user/month', 'Annual billing', datetime('now'), datetime('now')),
  ('JetBrains All Products', 'JetBrains', 'JETBRAINS-ALL-001', 'subscription', 15, 10, '2024-12-31', '$649/user/year', 'All Products Pack', datetime('now'), datetime('now')),
  ('Figma Organization', 'Figma', 'FIGMA-ORG-001', 'subscription', 25, 18, '2025-06-30', '$45/editor/month', 'Organization plan', datetime('now'), datetime('now'));

-- Sample Checkout History
INSERT INTO checkout_history (asset_id, user_id, checkout_date, checked_out_by, notes)
SELECT id, 2, datetime('now', '-30 days'), 1, 'Initial assignment for new hire'
FROM assets WHERE asset_tag = 'AST-002';

INSERT INTO checkout_history (asset_id, user_id, checkout_date, checked_out_by, notes)
SELECT id, 2, datetime('now', '-30 days'), 1, 'Paired with laptop AST-002'
FROM assets WHERE asset_tag = 'AST-006';

-- Sample Audit Logs
INSERT INTO audit_logs (action, entity_type, entity_id, user_id, changes, timestamp)
VALUES
  ('create', 'asset', 1, 1, '{"asset_tag": "AST-001", "name": "MacBook Pro 16\""}', datetime('now', '-60 days')),
  ('checkout', 'asset', 2, 1, '{"user_id": 2, "notes": "Initial assignment"}', datetime('now', '-30 days')),
  ('update', 'asset', 4, 1, '{"old": {"status": "available"}, "new": {"status": "maintenance"}}', datetime('now', '-7 days'));
