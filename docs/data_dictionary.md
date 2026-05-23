
# 🥇 Gold Layer Data Dictionary: Healthcare Business Marts

This data dictionary reflects the production tables in the `workspace.healthcare_gold` schema, optimized as a star-schema analytical tier for Power BI semantic consumption.

---

### 📊 1. Master Analytical Table
#### Table Name: `workspace.healthcare_gold.hospital_readmission_analysis`
* **Grain:** One row per unique hospital (`facility_id`) per clinical measure name (`measure_name`).
* **Description:** The master analytical dataset combining conformed facility traits with row-level metrics. It uses a wildcard filter (`LIKE 'READM-30-%'`) to isolate 30-day return rates across major conditions (CABG, AMI, COPD, etc.).

| Column Name | Data Type | Key Type | Business Definition & Derived Transformation Logic | Sample Value |
| :--- | :--- | :--- | :--- | :--- |
| `facility_id` | STRING | FK | Unique Centers for Medicare & Medicaid Services (CMS) identification code. | `"010001"` |
| `hospital_name` | STRING | — | Standardized official name of the medical provider. | `"SOUTHEAST ALABAMA MEDICAL CENTER"` |
| `city` | STRING | — | Clean city location descriptor text. | `"DOTHAN"` |
| `state` | STRING | FK | Clean 2-letter geographical state boundary code. | `"AL"` |
| `hospital_type` | STRING | — | Facility structural categorization (e.g., Acute Care Hospitals). | `"Acute Care Hospitals"` |
| `hospital_ownership` | STRING | — | Institutional alignment grouping structure. | `"Government - Hospital District"` |
| `overall_rating` | INT | — | Official national CMS star quality score (1 to 5). | `3` |
| `measure_name` | STRING | — | The specific clinical diagnosis category captured (e.g., `READM-30-COPD-HRRP`). | `"READM-30-COPD-HRRP"` |
| `number_of_discharges` | INT | — | Total patient discharge records associated with the specific condition. | `432` |
| `readmission_ratio` | DECIMAL | — | Raw performance calculation; values $> 1.0$ denote elevated readmission margins. | `1.043` |
| `hospital_risk_segment` | STRING | — | **Derived Row-Level Status Logic:**<br>• `readmission_ratio > 1.0` $\rightarrow$ `"High Readmission Risk"`<br>• `readmission_ratio <= 1.0` $\rightarrow$ `"Low/Target Readmission Risk"`<br>• Otherwise $\rightarrow$ `"Undetermined (Missing Data)"` | `"High Readmission Risk"` |

---

### 🗺️ 2. Regional Summary Table (Map Feeder)
#### Table Name: `workspace.healthcare_gold.bi_regional_readmission_summary`
* **Grain:** One row per unique `state`.
* **Description:** Aggregated lookup summary table designed to serve geographic choropleth map layers and state-level benchmark KPIs.

| Column Name | Data Type | Key Type | Business Definition & Derived Transformation Logic | Sample Value |
| :--- | :--- | :--- | :--- | :--- |
| `state` | STRING | PK | Unique 2-letter uppercase state code used as the primary map join vector. | `"FL"` |
| `total_unique_hospitals_monitored` | BIGINT | — | Total unique count of distinct facilities located within the target state boundary. | `124` |
| `high_risk_hospital_count` | BIGINT | — | Conditional count of hospitals where the facility's average ratio across all measures is $> 1.0$. | `42` |
| `high_risk_percentage` | DECIMAL | — | Percentage computation: `(high_risk_hospital_count / total_unique_hospitals_monitored) * 100` | `33.87` |
| `average_regional_readmission_ratio` | DECIMAL | — | `AVG(readmission_ratio)` representing the entire state boundary average baseline. | `1.012` |

---

### 📋 3. Detailed Hospital Operational Roster
#### Table Name: `workspace.healthcare_gold.bi_hospital_risk_roster`
* **Grain:** One row per unique hospital (`1 facility_id = 1 row`).
* **Description:** Flattened master roster view that collapses specific condition measures, providing an executive operational directory.

| Column Name | Data Type | Key Type | Business Definition & Derived Transformation Logic | Sample Value |
| :--- | :--- | :--- | :--- | :--- |
| `facility_id` | STRING | PK | Unique CMS identification key ensuring exact entity tracking limits. | `"010001"` |
| `hospital_name` | STRING | — | Standardized official name of the medical provider. | `"SOUTHEAST ALABAMA MEDICAL CENTER"` |
| `city` | STRING | — | Clean city location descriptor text. | `"DOTHAN"` |
| `state` | STRING | — | Clean 2-letter geographical state boundary code. | `"AL"` |
| `hospital_type` | STRING | — | Facility structural categorization. | `"Acute Care Hospitals"` |
| `hospital_ownership` | STRING | — | Institutional alignment grouping structure. | `"Government - Hospital District"` |
| `overall_rating` | INT | — | Official national CMS star quality score (1 to 5). | `3` |
| `overall_avg_readmission_ratio` | DECIMAL | — | `ROUND(AVG(readmission_ratio), 2)` representing a hospital's aggregate performance. | `1.03` |
| `hospital_risk_segment` | STRING | — | **Derived Aggregate Status Logic:** Evaluates facility-level tracking mean:<br>• `AVG(readmission_ratio) > 1.0` $\rightarrow$ `"High Readmission Risk"`<br>• Otherwise $\rightarrow$ `"Low/Target Readmission Risk"` | `"High Readmission Risk"` |

```