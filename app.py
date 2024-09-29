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
    
    # Progress bar
    total_rows = len(partner_schedule)
    progress_bar = st.progress(0)

    # Iterate over partner schedule to adjust LMS
    for idx, partner_row in partner_schedule.iterrows():
        lan = partner_row['LAN']
        partner_amount = partner_row['Amount']
        partner_principal = partner_row['Principal']
        partner_interest = partner_row['Interest']
        partner_due_date = partner_row['InstalmentDate']

        # Find corresponding rows in LMS schedule
        lms_rows = lms_schedule[lms_schedule['LAN'] == lan]

        # Initialize excess adjustment for this LAN
        excess_adjustment = 0
        is_first_due_adjusted = False

        for lms_idx, lms_row in lms_rows.iterrows():
            if lms_row['status'] == 'Satisfied':
                # Calculate the total amount for satisfied cases
                satisfied_total = lms_row['Principal'] + lms_row['Interest']
                # Check if there is excess or less payment
                if satisfied_total < partner_amount:
                    excess_adjustment += (partner_amount - satisfied_total)  # Track excess

            else:
                # Adjust the first upcoming due if not yet adjusted
                if not is_first_due_adjusted and lms_row['InstalmentDate'] > pd.Timestamp('2024-07-31'):
                    # Update the first due based on any excess
                    adjusted_principal = lms_row['Principal'] + excess_adjustment
                    adjusted_amount = adjusted_principal + lms_row['Interest']

                    # Update the row for first due
                    updated_schedule.append({
                        **lms_row,
                        'Principal': adjusted_principal,
                        'Amount': adjusted_amount,
                        'Remarks': f'Adjusted by excess of {excess_adjustment}'
                    })

                    # Set flag that the first due has been adjusted
                    is_first_due_adjusted = True

                else:
                    # Keep the original row for other dues
                    updated_schedule.append({
                        **lms_row,
                        'Remarks': 'No changes made, already satisfied or before adjustment'
                    })

        # Update Balance Outstanding
        if updated_schedule:  # Check if there's any entry
            previous_month_outstanding = updated_schedule[-1].get('BalanceOutstanding', lms_row['BalanceOutstanding'])
            current_month_principal = updated_schedule[-1].get('Principal', lms_row['Principal'])
            current_outstanding = previous_month_outstanding - current_month_principal

            # Update the Balance Outstanding
            updated_schedule[-1]['BalanceOutstanding'] = current_outstanding

        # Update the progress bar
        progress_percentage = (idx + 1) / total_rows
        progress_bar.progress(progress_percentage)

    # Create DataFrame for updated schedule
    updated_schedule_df = pd.DataFrame(updated_schedule)

    # Save to Excel
    updated_file_name = "Updated_LMS_Schedule.xlsx"
    updated_schedule_df.to_excel(updated_file_name, index=False)

    return updated_schedule_df, updated_file_name

# Streamlit UI
st.title("LMS Schedule Status Updater")

# Upload Files
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

if lms_file and partner_file:
    st.write("Processing...")
    output, updated_file_name = update_lms_schedule(lms_file, partner_file)
    
    # Display original and updated schedules side by side
    st.subheader("Original LMS Schedule")
    st.dataframe(pd.read_excel(lms_file))

    st.subheader("Partner Schedule")
    st.dataframe(pd.read_excel(partner_file))

    st.subheader("Updated LMS Schedule")
    st.dataframe(output)

    # Provide the download button for the updated Excel file
    st.download_button("Download Updated Schedule", updated_file_name, file_name=updated_file_name)
else:
    st.warning("Please upload both LMS and Partner schedule files.")
