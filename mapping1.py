import streamlit as st
import pandas as pd

st.set_page_config(page_title="File Ingestion App", layout="wide")

st.sidebar.header("Upload Your Files")

# Upload main table
main_file = st.sidebar.file_uploader("Upload Main Table", type=["csv", "xlsx"], key="main")

# Upload supplementary tables
supp_files = st.sidebar.file_uploader(
    "Upload Supplementary Tables (up to 11)", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True, 
    key="supp"
)

# Ensure no more than 11 supplementary files
if supp_files and len(supp_files) > 11:
    st.sidebar.warning("You can only upload up to 11 supplementary tables.")
    supp_files = supp_files[:11]

# Function to read files (CSV or Excel)
def read_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    return None

# Store processed tables
tables = {}

if main_file:
    tables["Main"] = read_file(main_file)

for idx, file in enumerate(supp_files, 1):
    tables[f"Supplementary {idx}"] = read_file(file)

# Function to extract distinct values
def get_distinct_values(df):
    distinct_dict = {}
    for col in df.columns:
        distinct_dict[col] = df[col].dropna().unique().tolist()
    return pd.DataFrame({
        "Column Name": list(distinct_dict.keys()),
        "Distinct Values": list(distinct_dict.values())
    })

# Display distinct values for each file
st.title("Distinct Values per Table")

distinct_tables = {}
for name, df in tables.items():
    st.subheader(f"📂 {name} ({df.shape[0]} rows, {df.shape[1]} cols)")
    distinct_table = get_distinct_values(df)
    distinct_tables[name] = distinct_table
    st.dataframe(distinct_table, use_container_width=True)

# Build mapping table between main and supplementary tables
if "Main" in tables:
    mapping = []
    main_distinct = distinct_tables["Main"]

    for _, row in main_distinct.iterrows():
        main_col = row["Column Name"]
        main_vals = set(row["Distinct Values"])

        row_mapping = {"Main Table Column": main_col}

        for supp_name, supp_distinct in distinct_tables.items():
            if supp_name == "Main":
                continue
            matched_col = None
            for _, supp_row in supp_distinct.iterrows():
                supp_vals = set(supp_row["Distinct Values"])
                if main_vals & supp_vals:  # check for intersection
                    matched_col = supp_row["Column Name"]
                    break
            row_mapping[supp_name] = matched_col
        mapping.append(row_mapping)

    mapping_df = pd.DataFrame(mapping)
    st.subheader("🔗 Mapping between Main Table and Supplementary Tables")
    st.dataframe(mapping_df, use_container_width=True)
