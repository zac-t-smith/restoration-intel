-- Seed data for Restoration-Intel Next.js + Supabase rewrite
-- June 2024

-- Seed vendors
INSERT INTO vendors (name, sla_days, notes) VALUES
('Premier Contractors', 30, 'Preferred vendor for major structural work'),
('Quality Materials Inc', 45, 'Bulk supplier with competitive pricing'),
('Rapid Response Services', 15, 'Emergency services provider');

-- Seed leads
INSERT INTO leads (name, email, phone, address, lead_source, lead_cost, status, notes, created_at, lead_source_type) VALUES
('John Smith', 'john.smith@example.com', '555-123-4567', '123 Main St, Springfield, IL', 'Google Ads', 350.00, 'converted', 'Contacted about water damage restoration', NOW() - INTERVAL '60 days', 'paid'),
('Jane Doe', 'jane.doe@example.com', '555-987-6543', '456 Oak Ave, Springfield, IL', 'Referral', 100.00, 'converted', 'Referred by previous client for fire damage', NOW() - INTERVAL '45 days', 'referral'),
('Bob Johnson', 'bob.johnson@example.com', '555-555-5555', '789 Pine Rd, Springfield, IL', 'Direct Mail', 250.00, 'contacted', 'Interested in mold remediation services', NOW() - INTERVAL '15 days', 'marketing');

-- Seed customers (converted from leads)
INSERT INTO customers (lead_id, name, email, phone, address, created_at) VALUES
(1, 'John Smith', 'john.smith@example.com', '555-123-4567', '123 Main St, Springfield, IL', NOW() - INTERVAL '58 days'),
(2, 'Jane Doe', 'jane.doe@example.com', '555-987-6543', '456 Oak Ave, Springfield, IL', NOW() - INTERVAL '43 days');

-- Seed projects
INSERT INTO projects (customer_id, lead_id, name, description, job_type, num_pods, status, 
                     start_date, estimated_completion, total_revenue, total_expenses, allocated_lead_cost,
                     created_at, updated_at, contract_filename, contract_path, contract_uploaded_at) VALUES
(1, 1, 'Smith Water Damage Restoration', 'Water damage restoration for basement flooding', 'water', 2, 'in_progress',
 NOW() - INTERVAL '55 days', NOW() + INTERVAL '5 days', 12500.00, 7800.00, 350.00,
 NOW() - INTERVAL '57 days', NOW() - INTERVAL '2 days', 'smith_contract.pdf', '/uploads/contracts/smith_contract.pdf', NOW() - INTERVAL '57 days'),
 
(2, 2, 'Doe Fire Damage Repair', 'Kitchen fire damage restoration and repair', 'fire', 3, 'in_progress',
 NOW() - INTERVAL '40 days', NOW() + INTERVAL '20 days', 28750.00, 18200.00, 100.00,
 NOW() - INTERVAL '42 days', NOW() - INTERVAL '1 day', 'doe_contract.pdf', '/uploads/contracts/doe_contract.pdf', NOW() - INTERVAL '42 days');

-- Seed collections
INSERT INTO collections (project_id, description, amount, expected_date, status, actual_date, confidence_percentage, notes, created_at) VALUES
(1, 'Smith Initial Payment', 6250.00, NOW() - INTERVAL '50 days', 'received', NOW() - INTERVAL '50 days', 100, 'Initial 50% payment received', NOW() - INTERVAL '55 days'),
(1, 'Smith Final Payment', 6250.00, NOW() + INTERVAL '7 days', 'pending', NULL, 90, 'Final payment upon completion', NOW() - INTERVAL '55 days'),
(2, 'Doe Initial Payment', 9583.33, NOW() - INTERVAL '38 days', 'received', NOW() - INTERVAL '38 days', 100, 'Initial 33% payment received', NOW() - INTERVAL '40 days'),
(2, 'Doe Progress Payment', 9583.33, NOW() - INTERVAL '10 days', 'received', NOW() - INTERVAL '9 days', 100, 'Progress payment at 50% completion', NOW() - INTERVAL '40 days'),
(2, 'Doe Final Payment', 9583.34, NOW() + INTERVAL '22 days', 'pending', NULL, 75, 'Final payment upon completion', NOW() - INTERVAL '40 days');

-- Seed expenses
INSERT INTO expenses (project_id, vendor_id, vendor, description, amount, due_date, urgency, category, status, is_recurring, notes, created_at) VALUES
(1, 1, 'Premier Contractors', 'Smith project materials', 3200.00, NOW() - INTERVAL '45 days', 'high', 'materials', 'paid', false, 'Initial materials for water damage restoration', NOW() - INTERVAL '54 days'),
(1, 3, 'Rapid Response Services', 'Smith water extraction services', 1200.00, NOW() - INTERVAL '48 days', 'high', 'services', 'paid', false, 'Emergency water extraction', NOW() - INTERVAL '54 days'),
(1, 1, 'Premier Contractors', 'Smith additional labor', 1500.00, NOW() + INTERVAL '2 days', 'medium', 'labor', 'pending', false, 'Additional labor for unexpected damage', NOW() - INTERVAL '10 days'),
(2, 2, 'Quality Materials Inc', 'Doe project materials', 7500.00, NOW() - INTERVAL '35 days', 'high', 'materials', 'paid', false, 'Initial materials for fire damage repair', NOW() - INTERVAL '39 days'),
(2, 1, 'Premier Contractors', 'Doe specialized restoration', 5800.00, NOW() - INTERVAL '25 days', 'medium', 'services', 'paid', false, 'Specialized restoration services', NOW() - INTERVAL '30 days'),
(2, 2, 'Quality Materials Inc', 'Doe finishing materials', 2500.00, NOW() + INTERVAL '5 days', 'medium', 'materials', 'pending', false, 'Finishing materials for project completion', NOW() - INTERVAL '5 days'),
(NULL, 3, 'Rapid Response Services', 'Monthly equipment rental', 800.00, NOW() + INTERVAL '15 days', 'low', 'overhead', 'pending', true, 'Monthly equipment rental fee', NOW() - INTERVAL '15 days');

-- Seed cash balances
INSERT INTO cash_balances (balance, as_of_date, notes, created_at) VALUES
(25000.00, NOW() - INTERVAL '90 days', 'Starting balance', NOW() - INTERVAL '90 days'),
(30000.00, NOW() - INTERVAL '60 days', 'After new investment', NOW() - INTERVAL '60 days'),
(42000.00, NOW() - INTERVAL '30 days', 'After collections', NOW() - INTERVAL '30 days'),
(38500.00, NOW() - INTERVAL '15 days', 'After vendor payments', NOW() - INTERVAL '15 days'),
(45000.00, NOW() - INTERVAL '1 day', 'Current balance', NOW() - INTERVAL '1 day');

-- Seed leading indicators
INSERT INTO leading_indicators (kpi_code, kpi_date, value, breach, playbook_json, created_at) VALUES
('pipeline_velocity_days', NOW() - INTERVAL '7 days', 18.5, false, '{"action": "No action needed", "rationale": "Pipeline velocity within acceptable range", "expected_impact": "Maintain current sales process"}', NOW() - INTERVAL '7 days'),
('backlog_coverage_ratio', NOW() - INTERVAL '7 days', 3.2, false, '{"action": "No action needed", "rationale": "Healthy backlog coverage", "expected_impact": "Stable revenue projection"}', NOW() - INTERVAL '7 days'),
('ar_30d_new', NOW() - INTERVAL '7 days', 6250.00, true, '{"action": "Contact clients about upcoming payments", "rationale": "New receivables entering 30-day window", "expected_impact": "Avoid aging receivables"}', NOW() - INTERVAL '7 days'),
('ap_30-45_ratio', NOW() - INTERVAL '7 days', 0.4, false, '{"action": "No action needed", "rationale": "AP schedule balanced", "expected_impact": "Maintain vendor relationships"}', NOW() - INTERVAL '7 days'),
('real_time_CAC', NOW() - INTERVAL '7 days', 233.33, false, '{"action": "No action needed", "rationale": "CAC within target range", "expected_impact": "Maintain current marketing spend"}', NOW() - INTERVAL '7 days'),
('runway_p5_weeks', NOW() - INTERVAL '7 days', 16.0, false, '{"action": "No action needed", "rationale": "Cash runway sufficient", "expected_impact": "Maintain operations without cash constraints"}', NOW() - INTERVAL '7 days'),
('gp_per_job_drift', NOW() - INTERVAL '7 days', -2.8, true, '{"action": "Review recent job costing", "rationale": "Gross profit per job trending down", "expected_impact": "Identify cost overruns and correct pricing"}', NOW() - INTERVAL '7 days'),
('price_cost_delta', NOW() - INTERVAL '7 days', -1.5, true, '{"action": "Update pricing model", "rationale": "Supplier costs rising faster than prices", "expected_impact": "Restore margin structure"}', NOW() - INTERVAL '7 days');