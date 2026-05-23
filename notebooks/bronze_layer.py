#  Read the CSV and clean up the spaces in column names
import re

volume_path = "/Volumes/workspace/default/healthcare_landing/hospital_general_info.csv"

raw_hospital_info = (
    spark.read.format("csv")
    .option("header", "True")
    .option("inferSchema", "True")
    .load(volume_path)
)

# LOOP THROUGH COLUMNS AND REPLACE SPACES/SPECIAL CHARACTERS WITH UNDERSCORES
# This converts "Facility ID" to "Facility_ID" and removes parentheses ()
cleaned_columns = [
    re.sub(r"[ ,;{}()\n\t=]+", "_", col).strip("_") for col in raw_hospital_info.columns
]

# Apply the clean column names back to the DataFrame
raw_hospital_info = raw_hospital_info.toDF(*cleaned_columns)

# Display the first 5 rows to verify columns
display(raw_hospital_info.limit(5))
#  Add metadata columns for audit tracking
from pyspark.sql.functions import current_timestamp, lit

bronze_hospital_info = raw_hospital_info.withColumn(
    "ingestion_timestamp", current_timestamp()
).withColumn("source_file_name", lit("hospital_general_info.csv"))

# Verify the two new columns appear
display(bronze_hospital_info.limit(5))
# Create the Bronze schema inside the workspace catalog and save
spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.healthcare_bronze")

# Save the DataFrame as a Delta table inside workspace.healthcare_bronze
bronze_hospital_info.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_bronze.hospital_general_information"
)

print(
    "[SUCCESS] hospital_general_information table successfully written to workspace.healthcare_bronze!"
)
# Batch load the remaining 3 datasets with cleaned column names
from pyspark.sql.functions import current_timestamp, lit
import re


def clean_column_names(df):
    """Helper function to strip out spaces and invalid characters from DataFrame columns"""
    clean_cols = [re.sub(r"[ ,;{}()\n\t=]+", "_", col).strip("_") for col in df.columns]
    return df.toDF(*clean_cols)


# 1. Hospital Readmissions
print("[INFO] Processing readmissions data...")
df_readmissions = (
    spark.read.format("csv")
    .option("header", "True")
    .option("inferSchema", "True")
    .load(
        "/Volumes/workspace/default/healthcare_landing/hospital_hrrp_readmissions.csv"
    )
)
df_readmissions = clean_column_names(df_readmissions)  # Clean the columns!
df_readmissions = df_readmissions.withColumn(
    "ingestion_timestamp", current_timestamp()
).withColumn("source_file_name", lit("hospital_hrrp_readmissions.csv"))

df_readmissions.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_bronze.hospital_readmissions"
)


# 2. Effective Care
print("[INFO] Processing effective care data...")
df_care = (
    spark.read.format("csv")
    .option("header", "True")
    .option("inferSchema", "True")
    .load("/Volumes/workspace/default/healthcare_landing/hospital_effective_care.csv")
)
df_care = clean_column_names(df_care)  # Clean the columns!
df_care = df_care.withColumn("ingestion_timestamp", current_timestamp()).withColumn(
    "source_file_name", lit("hospital_effective_care.csv")
)

df_care.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_bronze.hospital_effective_care"
)


# 3. Medicare Spending
print("[INFO] Processing medicare spending data...")
df_spending = (
    spark.read.format("csv")
    .option("header", "True")
    .option("inferSchema", "True")
    .load(
        "/Volumes/workspace/default/healthcare_landing/hospital_medicare_spending.csv"
    )
)
df_spending = clean_column_names(df_spending)  # Clean the columns!
df_spending = df_spending.withColumn(
    "ingestion_timestamp", current_timestamp()
).withColumn("source_file_name", lit("hospital_medicare_spending.csv"))

df_spending.write.format("delta").mode("overwrite").saveAsTable(
    "workspace.healthcare_bronze.hospital_medicare_spending"
)

print(
    "[SUCCESS] All remaining tables successfully written to the Bronze layer with clean schemas!"
)
