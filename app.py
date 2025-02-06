import streamlit as st
import pandas as pd
import plotly.express as px

# Load the merged dataset
@st.cache_data
def load_data():
    file_path = "merged_metadata.csv"  # Save the merged data as CSV and load it here
    return pd.read_csv(file_path)

df = load_data()

# Assign numerical order to updates based on source file
update_mapping = {
    "task_2_metadata_1st_dedup.json": "1st",
    "task_2_metadata_2nd_filtered.json": "2nd",
    "task_2_metadata_3rd_filtered.json": "3rd"
}
df["update"] = df["source_file"].map(update_mapping)

# Aggregate document counts per country per update
update_agg_df = df.groupby(["country", "update"]).size().reset_index(name="document_count")
update_pivot = update_agg_df.pivot(index="country", columns="update", values="document_count").fillna(0)
update_pivot["Total"] = update_pivot.sum(axis=1)
update_pivot.loc["Total"] = update_pivot.sum()

# Sidebar filters
st.sidebar.header("Filters")
selected_countries = st.sidebar.multiselect("Select Countries", df["country"].unique(), default=df["country"].unique())

# Year selection slider
min_year, max_year = int(df["year"].min()), int(df["year"].max())
selected_year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

# Tab layout
st.title("CABRI Document Collection Overview")
tabs = st.tabs(["Overview Table", "Detailed View"])

# First tab: Document count per country per update
with tabs[0]:
    st.subheader("Document Count per Country per Update")
    st.dataframe(update_pivot)

# Second tab: Detailed document exploration
with tabs[1]:
    # Dynamic document type filters
    document_type_1_options = ["All"] + list(df["document_type_1"].dropna().unique())
    selected_document_type_1 = st.sidebar.selectbox("Select Document Type 1", document_type_1_options)

    # Filter by Document Type 1
    if selected_document_type_1 != "All":
        filtered_df = df[df["document_type_1"] == selected_document_type_1]
    else:
        filtered_df = df.copy()

    # Update options for Document Type 2
    document_type_2_options = ["All"] + list(filtered_df["document_type_2"].dropna().unique())
    selected_document_type_2 = st.sidebar.selectbox("Select Document Type 2", document_type_2_options)

    # Filter by Document Type 2
    if selected_document_type_2 != "All":
        filtered_df = filtered_df[filtered_df["document_type_2"] == selected_document_type_2]

    # Update options for Document Type 3
    document_type_3_options = ["All"] + list(filtered_df["document_type_3"].dropna().unique())
    selected_document_type_3 = st.sidebar.selectbox("Select Document Type 3", document_type_3_options)

    # Filter by Document Type 3
    if selected_document_type_3 != "All":
        filtered_df = filtered_df[filtered_df["document_type_3"] == selected_document_type_3]

    # Further filter data based on selections
    filtered_df = filtered_df[(filtered_df["country"].isin(selected_countries)) &
                              (filtered_df["year"] >= selected_year_range[0]) &
                              (filtered_df["year"] <= selected_year_range[1])]

    # Aggregate data by country and year
    agg_df = filtered_df.groupby(["country", "year"]).size().reset_index(name="document_count")

    st.subheader("Detailed View: Number of Documents Collected per Country per Year")
    fig = px.bar(agg_df, x="year", y="document_count", color="country", barmode="group",
                 title="Number of Documents Collected per Country per Year",
                 labels={"document_count": "Document Count", "year": "Year", "country": "Country"})
    st.plotly_chart(fig)

    st.subheader("Filtered Data")
    st.dataframe(filtered_df)