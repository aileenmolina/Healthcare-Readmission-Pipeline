# 📋 Project Charter: Healthcare Readmission Analytics & Risk Profiling

## 🎯 1. Business Problem & Project Scoping
Healthcare payer networks and clinical analytics teams lack an automated, unified data platform to combine baseline hospital infrastructure characteristics with localized 30-day readmission performance scores. Currently, clinical analysts waste critical operational cycles manually consolidating disjointed spreadsheets and tracking multi-condition metrics (such as COPD, Heart Failure, and Hip/Knee revisions). 

This manual process delays administrative decisions on regional cost containment, regional risk profiling, and the deployment of targeted quality improvement initiatives. 

---

## 🚀 2. Technical Solution Summary
To resolve this data bottleneck, this project delivers an automated Medallion data pipeline built natively on Databricks. The final analytical tier transforms raw public Centers for Medicare & Medicaid Services (CMS) source files into a conformed, highly responsive Star-Schema reporting layer within the production catalog. 

The pipeline bridges the operational gap by delivering three highly optimized target layers for end-user business intelligence:
1. **`hospital_readmission_analysis`**: A comprehensive query base mapping granular condition-specific metrics via explicit `READM-30-%` wildcard filters.
2. **`bi_regional_readmission_summary`**: A pre-aggregated regional metric table designed to feed geographic choropleth map layers and high-level executive KPIs.
3. **`bi_hospital_risk_roster`**: A flattened, high-performance operational directory collapsing multi-measure variations into a clean, 1-row-per-facility format optimized for fast front-end cross-filtering.

---

## 📊 3. Target KPIs & Analytical Deliverables
* **Isolate Elevated Return Margins**: Quantify and segment facility performance using the clinical readmission ratio threshold ($> 1.0$).
* **Automate Regional Risk Mapping**: Group hospital metrics at the state boundary level to track the percentage of high-risk hospitals and rank regional risk profiles.
* **Streamline BI Semantic Connections**: Serve pre-structured, conformed tables to Power BI, mitigating performance bottlenecks and ensuring fluid cross-filtering behavior across complex data grains. 