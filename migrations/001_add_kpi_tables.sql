-- Add KPI tracking tables
CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    kpi_code VARCHAR(50) NOT NULL,
    value DECIMAL(15,2) NOT NULL,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    rule_breached JSONB
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details TEXT,
    link VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trends (
    id SERIAL PRIMARY KEY,
    direction VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details TEXT,
    link VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_kpi_metrics_code ON kpi_metrics(kpi_code);
CREATE INDEX IF NOT EXISTS idx_kpi_metrics_captured_at ON kpi_metrics(captured_at);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(type);
CREATE INDEX IF NOT EXISTS idx_trends_direction ON trends(direction); 