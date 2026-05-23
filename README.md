# Automated Cloud Healthcare Data Pipeline & Analytics Platform

Data engineering solution that automates the ingestion, transformation, and visualization of public Centers for Medicare & Medicaid Services (CMS) data to track, profile, and isolate national hospital readmission risks.

## Executive Dashboard Preview

![dashboardPreview](/dashboard/dashboard_unfiltered.png)

> **BI Engineering Highlight:** This dashboard utilizes a geographic mapping layout and ownership distribution donut charts. To ensure seamless executive drill-downs across mismatched data grains, a **bidirectional data relationship ("Both")** was implemented in the semantic layer, resolving default single-direction filter propagation bottlenecks.

## Technical Architecture (Medallion Layout)

1. **Bronze Layer:** Raw data landing utilizing programmatic Python and standard file streaming, appending ingestion metadata.
2. **Silver Layer:** Schema enforcement, null value cleaning, string trimming, and duplicate isolation using scalable PySpark DataFrames.
3. **Gold Layer:** Business-ready dimensional modeling executing analytical aggregations optimized for production business intelligence.

## Tech Stack

- **Language:** Python, Spark SQL
- **Platform:** Databricks Community Edition
- **Storage:** Delta Lake (ACID Compliant)
- **Orchestration:** Databricks Workflows
- **Visualization:** Power BI Desktop

## Key Engineering Challenges Overcome

- **Databricks Community Edition Ingestion Constraints:** Due to environment security limitations and a lack of root cloud administrative privileges to mount external storage in the free community tier, standard Spark-based network downloads were restricted. I resolved this roadblock by writing a lightweight, pure Python script using `urllib` to stream the source files directly into the driver nodes' local filesystem, successfully decoupling ingestion from cluster state.
- **Cross-Filter Propagation Breakdown:** Identified a data grain mismatch where filtering the granular roster table caused summary KPI metric cards to default to blank spaces. Solved by shifting the cross-filter mapping to bidirectional ("Both") in the model properties, restoring fluid data flow across the canvas.
