import streamlit as st
import pandas as pd

# Streamlit app title
st.title("LMS Schedule Status Updater")

# File upload section
st.header("Upload Files")
lms_schedule_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])
satisfied_svasti_file = st.file_uploader("Upload Satisfied Svasti File", type=["xlsx"])

# When both files are uploaded
if lms_schedule_file and satisfied_svasti_file:
    try:
        # Load the Excel files
        lms_schedule_df = pd.read_excel(lms_schedule_file)
        satisfied_svasti_df = pd.read_excel(satisfied_svasti_file)

        # Ensure column names are consistent
        lms_schedule_df.columns = lms_schedule_df.columns.str.strip()
        satisfied_svasti_df.columns = satisfied_svasti_df.columns.str.strip()

        # Check if the key columns exist
        required_columns_lms = ['LAN', 'InstalmentDate']
        required_columns_svasti = ['LAN', 'InstalmentDate', 'status']

        if not all(col in lms_schedule_df.columns for col in required_columns_lms):
            st.error(f"LMS schedule file must contain columns: {required_columns_lms}")
        elif not all(col in satisfied_svasti_df.columns for col in required_columns_svasti):
            st.error(f"Satisfied Svasti file must contain columns: {required_columns_svasti}")
        else:
            # Merge the dataframes based on 'LAN' and 'InstalmentDate'
            merged_df = pd.merge(lms_schedule_df, satisfied_svasti_df[['LAN', 'InstalmentDate', 'status']], 
                                 on=['LAN', 'InstalmentDate'], how='left', suffixes=('', '_svasti'))

            # Update the 'status' in the LMS schedule based on the matched data
            merged_df['status'] = merged_df['status_svasti'].combine_first(merged_df['status'])

            # Drop the 'status_svasti' column as it's no longer needed
            merged_df.drop(columns=['status_svasti'], inplace=True)

            # Display the merged dataframe
            st.subheader("Updated LMS Schedule")
            st.write(merged_df)

            # Provide a download link for the updated LMS schedule
            @st.cache_data
            def convert_df_to_excel(df):
                return df.to_excel(index=False, engine='openpyxl')

            updated_file = convert_df_to_excel(merged_df)
            st.download_button(
                label="Download Updated LMS Schedule",
                data=updated_file,
                file_name="Updated_LMS_Schedule.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload both the LMS Schedule and Satisfied Svasti files to proceed.")
