from pyspark.sql.functions import col, expr, trim

spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.healthcare_silver")

print("==================================================")
print("STARTING SILVER LAYER PIPELINE RUN...")
print("==================================================")


# HOSPITAL GENERAL INFORMATION (Hospital Grain)
print("[INFO] Processing Table 1: Hospital General Information...")
bronze_info_df = spark.read.table(
    "workspace.healthcare_bronze.hospital_general_information"
)

# Select and conform core columns to lowercase aliases
selected_info_df = bronze_info_df.select(
    col("Facility_ID").alias("facility_id"),
    col("Facility_Name").alias("hospital_name"),
    col("City/Town").alias("city"),  # Matches exact Bronze column name 'City/Town'
    col("State").alias("state"),
    col("ZIP_Code").alias("zip_code"),
    col("Hospital_Type").alias("hospital_type"),
    col("Hospital_Ownership").alias("hospital_ownership"),
    col("Hospital_overall_rating").alias("overall_rating"),
)

# Protect against blanks, 'Not Available', and 'N/A' strings safely using SQL evaluation
transformed_info_df = selected_info_df.withColumn(
    "overall_rating",
    expr(
        "CASE WHEN TRIM(overall_rating) IN ('', 'Not Available', 'N/A') THEN NULL ELSE CAST(overall_rating AS INT) END"
    ),
)

# Data Quality Checks
cleaned_info_df = transformed_info_df.filter(
    (col("facility_id").isNotNull()) & (trim(col("facility_id")) != "")
)

# Write out the clean Delta Table
cleaned_info_df.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_silver.hospital_general_information"
)
print("[SUCCESS] Table 1: hospital_general_information successfully written to Silver!")


# HOSPITAL READMISSIONS (Hospital Grain)
print("\n[INFO] Processing Table 2: Hospital Readmissions...")
bronze_readmissions = spark.read.table(
    "workspace.healthcare_bronze.hospital_readmissions"
)

silver_readmissions = bronze_readmissions.select(
    col("Facility_ID").alias("facility_id"),
    col("State").alias("state"),
    col("Measure_Name").alias("measure_name"),
    col("Number_of_Discharges").alias("number_of_discharges"),
    col("Excess_Readmission_Ratio").alias("readmission_ratio"),
).filter((col("facility_id").isNotNull()) & (trim(col("facility_id")) != ""))

# Safe conditional casting updated to catch empty strings, 'Not Available', and 'N/A'
cleaned_readmissions = silver_readmissions.withColumn(
    "number_of_discharges",
    expr(
        "CASE WHEN TRIM(number_of_discharges) IN ('', 'Not Available', 'N/A') THEN NULL ELSE CAST(number_of_discharges AS INT) END"
    ),
).withColumn(
    "readmission_ratio",
    expr(
        "CASE WHEN TRIM(readmission_ratio) IN ('', 'Not Available', 'N/A') THEN NULL ELSE CAST(readmission_ratio AS FLOAT) END"
    ),
)

cleaned_readmissions.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_silver.hospital_readmissions"
)
print("[SUCCESS] Table 2: hospital_readmissions successfully written to Silver!")


# HOSPITAL EFFECTIVE CARE (Measure Grain)
print("\n[INFO] Processing Table 3: Hospital Effective Care...")
bronze_care = spark.read.table("workspace.healthcare_bronze.hospital_effective_care")

# Conformed by Measure Grain as it naturally lacks facility_id/hospital scopes
silver_care = bronze_care.select(
    col("Measure_ID").alias("measure_id"),
    col("Measure_Name").alias("measure_name"),
    col("Condition").alias("condition"),
    col("Category").alias("category"),
    col("Score").alias("care_score"),
).filter((col("measure_id").isNotNull()) & (trim(col("measure_id")) != ""))

# Clean and cast scores safely while dropping non-numeric text values
cleaned_care = silver_care.withColumn(
    "care_score",
    expr(
        "CASE WHEN TRIM(care_score) IN ('', 'Not Available', 'N/A', 'High', 'Low') THEN NULL ELSE CAST(care_score AS INT) END"
    ),
)

cleaned_care.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_silver.hospital_effective_care"
)
print("[SUCCESS] Table 3: hospital_effective_care successfully written to Silver!")


# MEDICARE SPENDING (Measure Grain)
print("\n[INFO] Processing Table 4: Hospital Medicare Spending...")
bronze_spending = spark.read.table(
    "workspace.healthcare_bronze.hospital_medicare_spending"
)

silver_spending = bronze_spending.select(
    col("Measure_ID").alias("measure_id"),
    col("Measure_Name").alias("measure_name"),
    col("Score").alias("spending_ratio"),
    col("National_Median").alias("national_median"),
).filter((col("measure_id").isNotNull()) & (trim(col("measure_id")) != ""))

# Clean spending ratio safely using SQL expression syntax
cleaned_spending = silver_spending.withColumn(
    "spending_ratio",
    expr(
        "CASE WHEN TRIM(spending_ratio) IN ('', 'Not Available', 'N/A') THEN NULL ELSE CAST(spending_ratio AS FLOAT) END"
    ),
)

cleaned_spending.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_silver.hospital_medicare_spending"
)
print("[SUCCESS] Table 4: hospital_medicare_spending successfully written to Silver!")


print("\n==================================================")
print("[FINISHED] All 4 tables are fully conformed and securely written to Silver!")
print("==================================================")
