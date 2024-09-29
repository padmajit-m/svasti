import pandas as pd
import streamlit as st

def update_lms_schedule(lms_file, partner_file):
    # Read the files
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Ensure the 'InstalmentDate' columns are datetime
    lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'], errors='coerce')
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], errors='coerce')

    # Prepare a list for the updated schedule
    updated_schedule = []

    # Iterate over partner schedule to adjust LMS
    for _, partner_row in partner_schedule.iterrows():
        lan = partner_row['LAN']
        partner_date = partner_row['InstalmentDate']
        partner_amount = partner_row['Amount']
        partner_principal = partner_row['Principal']
        partner_interest = partner_row['Interest']

        # Find corresponding rows in LMS schedule
        lms_rows = lms_schedule[lms_schedule['LAN'] == lan]

        for idx, lms_row in lms_rows.iterrows():
            if lms_row['status'] == 'Satisfied':
                # Skip satisfied rows
                updated_schedule.append({
                    **lms_row,
                    'Remarks': 'No changes made, status is Satisfied'
                })
                continue

            # Update values if the instalment date is greater than 31st March 2024
            if lms_row['InstalmentDate'] > pd.Timestamp('2024-03-31'):
                # Calculate the new principal and interest if applicable
                new_principal = lms_row['Principal'] + partner_principal
                new_interest = lms_row['Interest'] + partner_interest

                # Append updated row
                updated_schedule.append({
                    **lms_row,
                    'Principal': new_principal,
                    'Interest': new_interest,
                    'Remarks': f'Adjusted Principal by {partner_principal}, Interest by {partner_interest}'
                })
            else:
                # Keep the original row if the date is before or on 31st March 2024
                updated_schedule.append({
                    **lms_row,
                    'Remarks': 'No changes made, date is before 31 March 2024'
                })

            # Update Balance Outstanding
            previous_month_outstanding = lms_row['BalanceOutstanding']
            current_month_principal = lms_row['Principal']
            current_outstanding = previous_month_outstanding - current_month_principal

            # Update the Balance Outstanding
            updated_schedule[-1]['BalanceOutstanding'] = current_outstanding

    # Create DataFrame for updated schedule
    updated_schedule_df = pd.DataFrame(updated_schedule)

    # Save to Excel
    updated_file_name = "Updated_LMS_Schedule.xlsx"
    updated_schedule_df.to_excel(updated_file_name, index=False)

    return updated_schedule_df

# Streamlit UI
st.title("LMS Schedule Status Updater")

# Upload Files
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

if lms_file and partner_file:
    st.write("Processing...")
    output = update_lms_schedule(lms_file, partner_file)
    
    # Display original and updated schedules side by side
    st.subheader("Original LMS Schedule")
    st.dataframe(pd.read_excel(lms_file))

    st.subheader("Partner Schedule")
    st.dataframe(pd.read_excel(partner_file))

    st.subheader("Updated LMS Schedule")
    st.dataframe(output)

    st.success(f"Updated LMS Schedule saved to {updated_file_name}")
    st.download_button("Download Updated Schedule", updated_file_name)
else:
    st.warning("Please upload both LMS and Partner schedule files.")
