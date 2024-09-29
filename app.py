import streamlit as st
import pandas as pd
import numpy as np
import os

def update_lms_schedule(lms_file, partner_file):
    # Read the uploaded Excel files
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Initialize the list for the updated schedule
    updated_schedule = []
    remarks = []
    
    # Convert dates
    lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'])
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'])

    # Extract unique LANs from partner schedule
    unique_lans = partner_schedule['LAN'].unique()
    
    for lan in unique_lans:
        partner_rows = partner_schedule[partner_schedule['LAN'] == lan]
        lms_rows = lms_schedule[lms_schedule['LAN'] == lan]

        # Track the number of satisfied rows
        satisfied_principal = 0
        satisfied_interest = 0
        total_satisfied = 0

        # Calculate satisfied amounts
        for _, row in lms_rows.iterrows():
            if row['status'] == 'Satisfied':
                satisfied_principal += row['Principal']
                satisfied_interest += row['Interest']
                total_satisfied += 1

        # Process upcoming demands for both satisfied and not satisfied cases
        for index, partner_row in partner_rows.iterrows():
            if index < len(lms_rows):
                lms_row = lms_rows.iloc[index]
                updated_row = {
                    'LAN': lms_row['LAN'],
                    'InstalmentNumber': lms_row['InstalmentNumber'],
                    'InstalmentDate': lms_row['InstalmentDate'],
                    'Amount': lms_row['Amount'],
                    'Principal': lms_row['Principal'],
                    'Interest': lms_row['Interest'],
                    'BalanceOutstanding': lms_row['BalanceOutstanding'],
                    'status': lms_row['status'],
                }

                if lms_row['status'] != 'Satisfied':
                    # Adjust based on satisfied amounts
                    adjusted_principal = updated_row['Principal'] + (satisfied_principal - satisfied_interest)
                    updated_row['Principal'] = adjusted_principal
                    updated_row['Amount'] = updated_row['Principal'] + updated_row['Interest']
                    remarks.append(f"Adjusted principal for LAN {lan}, instalment {updated_row['InstalmentNumber']}.")

                updated_schedule.append(updated_row)
            else:
                # If there are more demands in the partner schedule
                new_row = {
                    'LAN': partner_row['LAN'],
                    'InstalmentNumber': partner_row['InstalmentNumber'],
                    'InstalmentDate': partner_row['InstalmentDate'],
                    'Amount': partner_row['Amount'],
                    'Principal': partner_row['Principal'],
                    'Interest': partner_row['Interest'],
                    'BalanceOutstanding': 0,  # Set to default for new entries
                    'status': 'Due'  # Default to due for new entries
                }
                updated_schedule.append(new_row)

    # Create DataFrame for updated schedule
    updated_schedule_df = pd.DataFrame(updated_schedule)

    # Calculate Balance Outstanding logic
    updated_schedule_df['BalanceOutstanding'] = updated_schedule_df['Principal'].cumsum() - updated_schedule_df['Principal'].shift(fill_value=0).cumsum()

    # Save the updated schedule to a new Excel file
    updated_file_name = 'Updated_LMS_Schedule.xlsx'
    updated_schedule_df.to_excel(updated_file_name, index=False)

    return updated_schedule_df, updated_file_name

# Streamlit UI
st.title("LMS Schedule Status Updater")

# Upload Files
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

# Process files only when both are uploaded
if lms_file and partner_file:
    with st.spinner("Processing..."):
        # Call the function to update the LMS schedule
        output, updated_file_name = update_lms_schedule(lms_file, partner_file)
    
    # Display original and updated schedules side by side
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
else:
    st.warning("Please upload both LMS and Partner schedule files.")
