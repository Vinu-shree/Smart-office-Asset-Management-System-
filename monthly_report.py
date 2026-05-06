import pandas as pd

# Load CSV file
df = pd.read_csv("attendance_log.csv")

print("\n===================================")
print("       MONTHLY ATTENDANCE REPORT")
print("===================================\n")

# Total records
print("Total Records :", len(df))

# -----------------------------
# Entries by person
# -----------------------------
print("\nEntries By Person:")
person_count = df["Name"].value_counts()

for name, total in person_count.items():
    print(name, ":", total)

# -----------------------------
# Status count
# -----------------------------
print("\nStatus Count:")
status_count = df["Status"].value_counts()

for status, total in status_count.items():
    print(status, ":", total)

# -----------------------------
# Peak occupied count
# -----------------------------
print("\nPeak Occupied Count :", df["Count"].max())

print("\n===================================")
print("         REPORT COMPLETED")
print("===================================")