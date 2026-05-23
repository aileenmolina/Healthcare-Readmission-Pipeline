# 📊 Gold Layer:Analytical Queries for Data Analysts

These production-ready Spark SQL queries are designed for Data Analysts and Business Intelligence teams to query the `workspace.healthcare_gold` schema. They extract high-level strategic insights regarding hospital quality performance and 30-day readmission risks.

---

### 📈 Part 1: Hospital Quality & Ownership Benchmarking

#### 1. Executive Performance Overview
**Business Question:** What is the overall distribution of hospital star ratings across the network, and what is the average readmission ratio for each tier?

```sql
SELECT 
    overall_rating,
    COUNT(DISTINCT facility_id) as total_hospitals,
    ROUND(AVG(overall_avg_readmission_ratio), 3) as aggregate_readmission_ratio
FROM workspace.healthcare_gold.bi_hospital_risk_roster
WHERE overall_rating IS NOT NULL
GROUP BY overall_rating
ORDER BY overall_rating DESC;
```

#### 2. Risk Segmentation by Hospital Ownership

**Business Question:** Do public, proprietary, or non-profit hospitals exhibit higher rates of "High Readmission Risk" facilities?

```sql
SELECT 
    hospital_ownership,
    COUNT(facility_id) as total_hospitals,
    SUM(CASE WHEN hospital_risk_segment = 'High Readmission Risk' THEN 1 ELSE 0 END) as high_risk_count,
    ROUND((SUM(CASE WHEN hospital_risk_segment = 'High Readmission Risk' THEN 1 ELSE 0 END) / COUNT(facility_id)) * 100, 2) as high_risk_percentage
FROM workspace.healthcare_gold.bi_hospital_risk_roster
GROUP BY hospital_ownership
ORDER BY high_risk_percentage DESC;
```
### 3. High-Risk Facility Operational Directory

**Business Question:** Which Acute Care Hospitals are classified as high risk despite maintaining a high (4 or 5-star) CMS rating? (Identifying anomalies for deeper clinical audit).

```sql

SELECT 
    facility_id,
    hospital_name,
    state,
    overall_rating,
    overall_avg_readmission_ratio
FROM workspace.healthcare_gold.bi_hospital_risk_roster
WHERE hospital_type = 'Acute Care Hospitals'
  AND overall_rating >= 4
  AND hospital_risk_segment = 'High Readmission Risk'
ORDER BY overall_avg_readmission_ratio DESC;
```
### 🗺️ Part 2: Regional & Geographic Risk Profiling
### 4. Top 5 Most Critical States by Risk Percentage

**Business Question:** Which states have the highest percentage of monitored hospitals falling into the "High Risk" tier?

```sql

SELECT 
    state,
    total_unique_hospitals_monitored,
    high_risk_hospital_count,
    high_risk_percentage
FROM workspace.healthcare_gold.bi_regional_readmission_summary
ORDER BY high_risk_percentage DESC
LIMIT 5;
```
### 5. Most Prevalent High-Risk Medical Conditions

**Business Question:** Which specific 30-day readmission measures (e.g., COPD, Heart Failure, Hip/Knee) are driving the most high-risk row segments across the country?

```sql

SELECT 
    measure_name,
    COUNT(*) as total_cases_tracked,
    SUM(CASE WHEN hospital_risk_segment = 'High Readmission Risk' THEN 1 ELSE 0 END) as high_risk_case_count,
    ROUND(AVG(readmission_ratio), 3) as average_measure_readmission_ratio
FROM workspace.healthcare_gold.hospital_readmission_analysis
GROUP BY measure_name
ORDER BY high_risk_case_count DESC;
```