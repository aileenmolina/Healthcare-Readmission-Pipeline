%sql
-- Build the Comprehensive Hospital Performance Business Mart
CREATE SCHEMA IF NOT EXISTS workspace.healthcare_gold;

CREATE OR REPLACE TABLE workspace.healthcare_gold.hospital_readmission_analysis AS
SELECT 
    inf.facility_id,
    inf.hospital_name,
    inf.city,
    inf.state,
    inf.hospital_type,
    inf.hospital_ownership,
    inf.overall_rating,
    readm.measure_name,
    readm.number_of_discharges,
    readm.readmission_ratio,
    -- Segment individual rows based on risk performance thresholds
    CASE 
        WHEN readm.readmission_ratio > 1.0 THEN 'High Readmission Risk'
        WHEN readm.readmission_ratio <= 1.0 THEN 'Low/Target Readmission Risk'
        ELSE 'Undetermined (Missing Data)'
    END as hospital_risk_segment
FROM workspace.healthcare_silver.hospital_general_information inf
INNER JOIN workspace.healthcare_silver.hospital_readmissions readm 
    ON inf.facility_id = readm.facility_id
-- Catches ALL 30-day readmission measures using a wildcard string match
WHERE readm.measure_name LIKE 'READM-30-%';

-- Preview  Gold Table
SELECT * FROM workspace.healthcare_gold.hospital_readmission_analysis LIMIT 10;
%sql
-- Rank States by Highest Overall Readmission Risk Across All Tracked Measures
WITH hospital_averages AS (
    -- Calculatesthe overall average readmission ratio for each individual hospital
    SELECT 
        facility_id,
        hospital_name,
        state,
        AVG(readmission_ratio) as avg_hospital_readmission_ratio
    FROM workspace.healthcare_gold.hospital_readmission_analysis
    WHERE readmission_ratio IS NOT NULL
    GROUP BY facility_id, hospital_name, state
)
SELECT 
    state,
    COUNT(facility_id) as total_unique_hospitals_monitored,
    -- Counts a hospital as High Risk if its overall average ratio across all measures is > 1.0
    SUM(CASE WHEN avg_hospital_readmission_ratio > 1.0 THEN 1 ELSE 0 END) as high_risk_hospital_count,
    ROUND((SUM(CASE WHEN avg_hospital_readmission_ratio > 1.0 THEN 1 ELSE 0 END) / COUNT(facility_id)) * 100, 2) as high_risk_percentage,
    ROUND(AVG(avg_hospital_readmission_ratio), 3) as average_regional_readmission_ratio
FROM hospital_averages
GROUP BY state
HAVING total_unique_hospitals_monitored >= 5
ORDER BY high_risk_percentage DESC;
%sql

-- Ensuring the target Gold Schema database exists in catalog
CREATE SCHEMA IF NOT EXISTS workspace.healthcare_gold;


-- =====================================================================
-- MASTER HEALTHCARE BUSINESS MART
-- =====================================================================
-- This creates a unified table joining demographics and clinical metrics.
-- It applies the wildcard filter to capture HIP-KNEE, CABG, AMI, COPD, and PN.
CREATE OR REPLACE TABLE workspace.healthcare_gold.hospital_readmission_analysis AS
SELECT 
    inf.facility_id,
    inf.hospital_name,
    inf.city,
    inf.state,
    inf.hospital_type,
    inf.hospital_ownership,
    inf.overall_rating,
    readm.measure_name,
    readm.number_of_discharges,
    readm.readmission_ratio,
    -- Label individual row metrics based on clinical performance thresholds
    CASE 
        WHEN readm.readmission_ratio > 1.0 THEN 'High Readmission Risk'
        WHEN readm.readmission_ratio <= 1.0 THEN 'Low/Target Readmission Risk'
        ELSE 'Undetermined (Missing Data)'
    END as hospital_risk_segment
FROM workspace.healthcare_silver.hospital_general_information inf
INNER JOIN workspace.healthcare_silver.hospital_readmissions readm 
    ON inf.facility_id = readm.facility_id
-- Captures ALL 30-day readmission measures for a comprehensive regional scope
WHERE readm.measure_name LIKE 'READM-30-%';


-- =====================================================================
-- REGIONAL SUMMARY TABLE
-- =====================================================================
-- Pre-aggregates data by State to feed geographic maps and regional KPIs.
CREATE OR REPLACE TABLE workspace.healthcare_gold.bi_regional_readmission_summary AS
WITH hospital_averages AS (
    -- Calculate a single, clean average readmission ratio per unique facility
    SELECT 
        facility_id,
        hospital_name,
        state,
        AVG(readmission_ratio) as avg_hospital_readmission_ratio
    FROM workspace.healthcare_gold.hospital_readmission_analysis
    WHERE readmission_ratio IS NOT NULL
    GROUP BY facility_id, hospital_name, state
)
SELECT 
    state,
    COUNT(facility_id) as total_unique_hospitals_monitored,
    -- A hospital is classified as High Risk if its overall average ratio across all measures is > 1.0
    SUM(CASE WHEN avg_hospital_readmission_ratio > 1.0 THEN 1 ELSE 0 END) as high_risk_hospital_count,
    ROUND((SUM(CASE WHEN avg_hospital_readmission_ratio > 1.0 THEN 1 ELSE 0 END) / COUNT(facility_id)) * 100, 2) as high_risk_percentage,
    ROUND(AVG(avg_hospital_readmission_ratio), 3) as average_regional_readmission_ratio
FROM hospital_averages
GROUP BY state
HAVING total_unique_hospitals_monitored >= 5;


-- =====================================================================
-- POWER BI DETAILED HOSPITAL ROSTER
-- =====================================================================
-- Collapses metrics so that 1 hospital = 1 row.
CREATE OR REPLACE TABLE workspace.healthcare_gold.bi_hospital_risk_roster AS
SELECT 
    facility_id,
    hospital_name,
    city,
    state,
    hospital_type,
    hospital_ownership,
    overall_rating,
    ROUND(AVG(readmission_ratio), 2) as overall_avg_readmission_ratio,
    CASE 
        WHEN AVG(readmission_ratio) > 1.0 THEN 'High Readmission Risk'
        ELSE 'Low/Target Readmission Risk'
    END as hospital_risk_segment
FROM workspace.healthcare_gold.hospital_readmission_analysis
GROUP BY facility_id, hospital_name, city, state, hospital_type, hospital_ownership, overall_rating;
%sql
-- Readmission Summary Table
SELECT 'REGIONAL SUMMARY PREVIEW (MAP DATA)' as table_check, * FROM workspace.healthcare_gold.bi_regional_readmission_summary 
LIMIT 5;

%sql
--  Detailed Hospital Roster Table
SELECT * FROM workspace.healthcare_gold.bi_hospital_risk_roster LIMIT 10;