import streamlit as st
import pandas as pd
import os

def update_lms_schedule(lms_file, partner_file):
    # Read the uploaded Excel files
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Initialize the updated schedule and logs
    updated_schedule = []
    logs = []
    
    # Convert dates
    lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'])
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'])

    # Extract unique LANs from partner schedule
    unique_lans = partner_schedule['LAN'].unique()
    
    total_rows = len(unique_lans)
    
    # Progress tracking
    progress_bar = st.progress(0)

    for i, lan in enumerate(unique_lans):
        partner_rows = partner_schedule[partner_schedule['LAN'] == lan]
        lms_rows = lms_schedule[lms_schedule['LAN'] == lan]

        # Initialize variables for adjustment calculations
        total_satisfied_principal = 0
        total_satisfied_interest = 0

        # Calculate total satisfied amounts
        for _, row in lms_rows.iterrows():
            if row['status'] == 'Satisfied':
                total_satisfied_principal += row['Principal']
                total_satisfied_interest += row['Interest']
        
        # Adjust upcoming EMIs based on satisfied amounts
        for index, partner_row in partner_rows.iterrows():
            if index < len(lms_rows):
                lms_row = lms_rows.iloc[index]
                updated_row = lms_row.copy()

                # Update the Principal and Amount based on adjustment logic
                if lms_row['status'] != 'Satisfied':
                    principal_adjustment = total_satisfied_principal - total_satisfied_interest
                    updated_row['Principal'] += principal_adjustment
                    updated_row['Amount'] = updated_row['Principal'] + updated_row['Interest']
                    logs.append(f"Adjusted principal for LAN {lan}, instalment {updated_row['InstalmentNumber']}.")

                updated_schedule.append(updated_row)
            else:
                # If there are more demands in the partner schedule
                new_row = partner_row.copy()
                new_row['BalanceOutstanding'] = 0  # Default for new entries
                new_row['status'] = 'Due'  # Default to due for new entries
                updated_schedule.append(new_row)

        # Update progress bar
        progress_bar.progress((i + 1) / total_rows)

    # Create DataFrame for updated schedule
    updated_schedule_df = pd.DataFrame(updated_schedule)

    # Calculate Balance Outstanding based on previous logic
    updated_schedule_df['BalanceOutstanding'] = updated_schedule_df['Principal'].cumsum() - updated_schedule_df['Principal'].shift(fill_value=0).cumsum()

    # Save the updated schedule to a new Excel file
    updated_file_name = 'Updated_LMS_Schedule.xlsx'
    updated_schedule_df.to_excel(updated_file_name, index=False)

    return updated_schedule_df, updated_file_name, logs

# Streamlit UI
st.title("LMS Schedule Status Updater")

# Upload Files
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

# Process files only when both are uploaded
if lms_file and partner_file:
    with st.spinner("Processing..."):
        output, updated_file_name, logs = update_lms_schedule(lms_file, partner_file)

    # Display original schedules
    st.subheader("Original LMS Schedule")
    st.dataframe(pd.read_excel(lms_file))

    st.subheader("Partner Schedule")
    st.dataframe(pd.read_excel(partner_file))

    st.subheader("Updated LMS Schedule")
    st.dataframe(output)

    # Provide the download button for the updated Excel file
    with open(updated_file_name, "rb") as f:
        st.download_button("Download Updated Schedule", f, file_name=updated_file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Clean up by removing the updated file after download
    os.remove(updated_file_name)

    # Show logs for adjustments made
    st.subheader("Logs")
    for log in logs:
        st.write(log)
else:
    st.warning("Please upload both LMS and Partner schedule files.")
