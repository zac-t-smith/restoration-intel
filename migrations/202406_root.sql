-- Migration script for Restoration-Intel Next.js + Supabase rewrite
-- June 2024

-- Create core business tables
-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    lead_source TEXT,
    lead_cost FLOAT DEFAULT 0,
    status TEXT DEFAULT 'new',
    notes TEXT,
    created_at TIMESTAMP DEFAULT now(),
    converted_at TIMESTAMP,
    lead_source_type TEXT
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    lead_id INTEGER REFERENCES leads(id),
    name TEXT NOT NULL,
    description TEXT,
    job_type TEXT,
    num_pods INTEGER DEFAULT 1,
    status TEXT DEFAULT 'new',
    start_date TIMESTAMP,
    estimated_completion TIMESTAMP,
    total_revenue FLOAT DEFAULT 0,
    total_expenses FLOAT DEFAULT 0,
    allocated_lead_cost FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT now(),
    contract_filename TEXT,
    contract_path TEXT,
    contract_uploaded_at TIMESTAMP,
    contract_uploaded_by TEXT
);

-- Collections table
CREATE TABLE IF NOT EXISTS collections (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    description TEXT,
    amount FLOAT NOT NULL,
    expected_date TIMESTAMP,
    status TEXT DEFAULT 'pending',
    actual_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    vendor TEXT,
    description TEXT,
    amount FLOAT NOT NULL,
    due_date TIMESTAMP,
    urgency TEXT DEFAULT 'medium',
    category TEXT,
    status TEXT DEFAULT 'pending',
    is_recurring BOOLEAN DEFAULT false,
    recurring_frequency TEXT,
    paid_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Cash balances table
CREATE TABLE IF NOT EXISTS cash_balances (
    id SERIAL PRIMARY KEY,
    balance FLOAT NOT NULL,
    as_of_date TIMESTAMP NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Create indexes for core tables
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(lead_source);
CREATE INDEX IF NOT EXISTS idx_customers_lead_id ON customers(lead_id);
CREATE INDEX IF NOT EXISTS idx_projects_customer_id ON projects(customer_id);
CREATE INDEX IF NOT EXISTS idx_projects_lead_id ON projects(lead_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_collections_project_id ON collections(project_id);
CREATE INDEX IF NOT EXISTS idx_collections_status ON collections(status);
CREATE INDEX IF NOT EXISTS idx_expenses_project_id ON expenses(project_id);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
CREATE INDEX IF NOT EXISTS idx_cash_balances_date ON cash_balances(as_of_date);

-- Add updated_at to projects table with trigger
ALTER TABLE projects ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT now();

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_project_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update timestamp on projects
DROP TRIGGER IF EXISTS update_project_updated_at ON projects;
CREATE TRIGGER update_project_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW
EXECUTE FUNCTION update_project_timestamp();

-- Add confidence_percentage to collections
ALTER TABLE collections ADD COLUMN IF NOT EXISTS confidence_percentage FLOAT DEFAULT 85;

-- Create leading_indicators table
CREATE TABLE IF NOT EXISTS leading_indicators (
    id SERIAL PRIMARY KEY,
    kpi_code TEXT NOT NULL,
    kpi_date DATE NOT NULL,
    value FLOAT NOT NULL,
    breach BOOLEAN DEFAULT false,
    playbook_json JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- Create indexes for leading_indicators
CREATE INDEX IF NOT EXISTS idx_leading_indicators_kpi_code ON leading_indicators(kpi_code);
CREATE INDEX IF NOT EXISTS idx_leading_indicators_kpi_date ON leading_indicators(kpi_date);
CREATE INDEX IF NOT EXISTS idx_leading_indicators_breach ON leading_indicators(breach);

-- Create vendors table
CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    sla_days INTEGER DEFAULT 30,
    notes TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Create index for vendor name
CREATE INDEX IF NOT EXISTS idx_vendors_name ON vendors(name);

-- Add vendor_id to expenses table
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS vendor_id INTEGER REFERENCES vendors(id);
CREATE INDEX IF NOT EXISTS idx_expenses_vendor_id ON expenses(vendor_id);

-- Create Supabase RPC functions
CREATE OR REPLACE FUNCTION get_cash_position()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'current_balance', (
            SELECT balance 
            FROM cash_balances 
            ORDER BY as_of_date DESC, id DESC 
            LIMIT 1
        ),
        'pending_collections', (
            SELECT COALESCE(SUM(amount), 0) 
            FROM collections 
            WHERE status = 'pending'
        ),
        'pending_expenses', (
            SELECT COALESCE(SUM(amount), 0) 
            FROM expenses 
            WHERE status = 'pending'
        ),
        'projected_balance', (
            SELECT (
                (SELECT balance FROM cash_balances ORDER BY as_of_date DESC, id DESC LIMIT 1) +
                (SELECT COALESCE(SUM(amount), 0) FROM collections WHERE status = 'pending') -
                (SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE status = 'pending')
            )
        ),
        'updated_at', now()
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- AP Timeline function
CREATE OR REPLACE FUNCTION get_ap_timeline()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    WITH timeline_data AS (
        SELECT 
            e.id,
            e.description,
            e.amount,
            e.due_date,
            e.urgency,
            e.category,
            v.name as vendor_name,
            v.sla_days,
            p.name as project_name,
            e.due_date - NOW()::date as days_until_due,
            CASE 
                WHEN e.urgency = 'high' THEN 3
                WHEN e.urgency = 'medium' THEN 2
                ELSE 1
            END as urgency_factor,
            CASE
                WHEN e.due_date <= NOW()::date THEN 'overdue'
                WHEN e.due_date <= (NOW()::date + INTERVAL '7 days') THEN 'due_soon'
                ELSE 'upcoming'
            END as status
        FROM 
            expenses e
            LEFT JOIN vendors v ON e.vendor_id = v.id
            LEFT JOIN projects p ON e.project_id = p.id
        WHERE 
            e.status = 'pending'
        ORDER BY 
            status, days_until_due
    )
    
    SELECT json_agg(
        json_build_object(
            'id', t.id,
            'description', t.description,
            'amount', t.amount,
            'due_date', t.due_date,
            'days_until_due', t.days_until_due,
            'urgency', t.urgency,
            'urgency_factor', t.urgency_factor,
            'category', t.category,
            'vendor_name', t.vendor_name,
            'project_name', t.project_name,
            'status', t.status,
            'payment_priority', CASE
                WHEN t.status = 'overdue' THEN 'high'
                WHEN t.status = 'due_soon' AND t.urgency_factor >= 2 THEN 'high'
                WHEN t.status = 'due_soon' THEN 'medium'
                ELSE 'low'
            END,
            'rationale', CASE
                WHEN t.status = 'overdue' THEN 'Payment is past due'
                WHEN t.status = 'due_soon' AND t.urgency_factor >= 2 THEN 'High urgency payment due soon'
                WHEN t.status = 'due_soon' THEN 'Payment coming due soon'
                ELSE 'Payment can be scheduled later'
            END
        )
    ) INTO result
    FROM timeline_data t;
    
    RETURN COALESCE(result, '[]'::json);
END;
$$ LANGUAGE plpgsql;

-- Leading indicator insertion function
CREATE OR REPLACE FUNCTION insert_leading_indicator(payload JSON)
RETURNS JSON AS $$
DECLARE
    result JSON;
    new_id INTEGER;
BEGIN
    INSERT INTO leading_indicators (
        kpi_code,
        kpi_date,
        value,
        breach,
        playbook_json
    ) VALUES (
        payload->>'kpi_code',
        (payload->>'kpi_date')::DATE,
        (payload->>'value')::FLOAT,
        (payload->>'breach')::BOOLEAN,
        payload->'playbook_json'
    )
    RETURNING id INTO new_id;
    
    SELECT json_build_object(
        'id', new_id,
        'status', 'success',
        'message', 'Leading indicator inserted successfully',
        'timestamp', now()
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;