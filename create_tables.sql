CREATE TABLE IF NOT EXISTS triage_results (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(100) UNIQUE NOT NULL,
    resumen TEXT,
    notas TEXT,
    fecha_creacion TIMESTAMP,
    causa_raiz_predicha VARCHAR(200),
    confianza DECIMAL(3,2),
    razonamiento TEXT,
    keywords_detectadas JSONB,
    causas_alternativas JSONB,
    incidencias_similares JSONB,
    modelo_version VARCHAR(50),
    tiempo_procesamiento_ms INTEGER,
    timestamp_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_incident_id ON triage_results(incident_id);
CREATE INDEX IF NOT EXISTS idx_batch_id ON triage_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_causa_raiz ON triage_results(causa_raiz_predicha);
CREATE INDEX IF NOT EXISTS idx_timestamp ON triage_results(timestamp_procesamiento);

CREATE TABLE IF NOT EXISTS triage_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value DECIMAL(10,2),
    metric_metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
