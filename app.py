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

        # Display the column names for verification
        st.write("Columns in LMS Schedule File:", lms_schedule_df.columns.tolist())
        st.write("Columns in Satisfied Svasti File:", satisfied_svasti_df.columns.tolist())

        # Ensure column names are consistent and strip any leading/trailing whitespaces
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
            # Convert the 'InstalmentDate' columns to datetime to ensure consistency
            try:
                lms_schedule_df['InstalmentDate'] = pd.to_datetime(lms_schedule_df['InstalmentDate'], errors='coerce')
                satisfied_svasti_df['InstalmentDate'] = pd.to_datetime(satisfied_svasti_df['InstalmentDate'], errors='coerce')
            except Exception as e:
                st.error(f"Error converting InstalmentDate columns to datetime: {e}")
                st.stop()

            # Check for any NaT (Not-a-Time) entries in 'InstalmentDate'
            if lms_schedule_df['InstalmentDate'].isna().any():
                st.warning("There are invalid dates in the LMS Schedule 'InstalmentDate' column. Please review the file.")
            if satisfied_svasti_df['InstalmentDate'].isna().any():
                st.warning("There are invalid dates in the Satisfied Svasti 'InstalmentDate' column. Please review the file.")

            # Merge the dataframes based on 'LAN' and 'InstalmentDate'
            try:
                merged_df = pd.merge(lms_schedule_df, satisfied_svasti_df[['LAN', 'InstalmentDate', 'status']], 
                                     on=['LAN', 'InstalmentDate'], how='left')
            except Exception as e:
                st.error(f"Error during merging: {e}")
                st.stop()

            # Check if the merge added the 'status' column from the satisfied_svasti_df
            if 'status' in merged_df.columns:
                # Fill missing 'status' values from the original LMS data if available
                merged_df['status'] = merged_df['status'].combine_first(lms_schedule_df.get('status', ''))
            else:
                st.error("The 'status' column could not be found in the merged data. Please verify your files.")
                st.stop()

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
