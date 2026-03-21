-- =========================================
-- Insert 1000 sample industrial rows into documents
-- =========================================

INSERT INTO documents (title, content, embedding)
SELECT
    'Factory Process Log #' || gs,
    'Machine M-' || (gs % 50) || 
    ' reported abnormal vibration at station ' || (gs % 10) ||
    '. Temperature exceeded safe threshold during shift ' || (gs % 3) ||
    '. Operator ID OP-' || (gs % 25) ||
    '. Downtime recorded: ' || (gs % 120) || ' minutes.',
    ARRAY[
        random(), random(), random(), random(),
        random(), random(), random(), random()
    ]::vector
FROM generate_series(1, 1000) gs;


-- =========================================
-- Insert 1000 sample industrial rows into rag_documents
-- =========================================

INSERT INTO rag_documents (source_type, source_id, content, embedding)
SELECT
    CASE 
        WHEN gs % 4 = 0 THEN 'production_log'
        WHEN gs % 4 = 1 THEN 'maintenance_log'
        WHEN gs % 4 = 2 THEN 'quality_report'
        ELSE 'safety_report'
    END,
    'SRC-' || gs,
    'Industrial event #' || gs ||
    '. Production line L-' || (gs % 15) ||
    ' encountered issue: ' ||
    CASE 
        WHEN gs % 3 = 0 THEN 'Overheat'
        WHEN gs % 3 = 1 THEN 'Hydraulic Leak'
        ELSE 'Sensor Failure'
    END ||
    '. Shift: ' || (gs % 3) ||
    '. Batch: B-' || (gs % 200) ||
    '. Efficiency dropped to ' || (50 + (gs % 50)) || ' percent.',
    ARRAY[
        random(), random(), random(), random(),
        random(), random(), random(), random()
    ]::vector
FROM generate_series(1, 1000) gs;


-- =========================================
-- Refresh statistics
-- =========================================
ANALYZE documents;
ANALYZE rag_documents;
