import pandas as pd
import streamlit as st

def update_lms_schedule(lms_file, partner_file):
    # Read the files
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Ensure the 'InstalmentDate' columns are datetime
    lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'], errors='coerce')
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], errors='coerce')

    # Check for duplicates in LMS schedule and handle them
    if lms_schedule['LAN'].duplicated().any():
        st.warning("Duplicate LAN values found in LMS Schedule. Resolving by keeping the first occurrence.")
        lms_schedule = lms_schedule.drop_duplicates(subset='LAN', keep='first')

    # Prepare a DataFrame for the comparison
    comparison_df = []

    # Create a mapping for unique LANs
    lms_mapping = lms_schedule.set_index('LAN').to_dict(orient='index')
    
    # Prepare a list for the updated schedule
    updated_schedule = []

    # Progress bar
    total_rows = len(partner_schedule)
    progress_bar = st.progress(0)

    # Iterate over partner schedule to compare and adjust LMS
    for idx, partner_row in partner_schedule.iterrows():
        lan = partner_row['LAN']
        partner_amount = partner_row['Amount']
        partner_principal = partner_row['Principal']
        partner_interest = partner_row['Interest']
        partner_due_date = partner_row['InstalmentDate']

        # Get the corresponding LMS row
        lms_row = lms_mapping.get(lan, {})
        
        # Initialize comparison result
        comparison_result = {
            'LAN': lan,
            'Partner Amount': partner_amount,
            'LMS Amount': lms_row.get('Amount', 'N/A'),
            'Amount Match': partner_amount == lms_row.get('Amount', 0),
            'Partner Principal': partner_principal,
            'LMS Principal': lms_row.get('Principal', 'N/A'),
            'Principal Match': partner_principal == lms_row.get('Principal', 0),
            'Partner Interest': partner_interest,
            'LMS Interest': lms_row.get('Interest', 'N/A'),
            'Interest Match': partner_interest == lms_row.get('Interest', 0),
            'Instalment Date': partner_due_date,
            'Remarks': ''
        }
        
        # Add remarks for differences
        if not comparison_result['Amount Match']:
            difference = partner_amount - lms_row.get('Amount', 0)
            comparison_result['Remarks'] += f"Amount Difference: {difference:.2f}. "
        
        if not comparison_result['Principal Match']:
            difference = partner_principal - lms_row.get('Principal', 0)
            comparison_result['Remarks'] += f"Principal Difference: {difference:.2f}. "
        
        if not comparison_result['Interest Match']:
            difference = partner_interest - lms_row.get('Interest', 0)
            comparison_result['Remarks'] += f"Interest Difference: {difference:.2f}. "

        # Append the comparison result to the DataFrame
        comparison_df.append(comparison_result)

        # Update progress bar
        progress_percentage = (idx + 1) / total_rows
        progress_bar.progress(progress_percentage)

    # Create DataFrame for comparison
    comparison_df = pd.DataFrame(comparison_df)

    # Add revised schedule to the DataFrame
    revised_schedule = []

    # Iterate over comparison results for adjustments
    for idx, row in comparison_df.iterrows():
        lan = row['LAN']
        lms_row = lms_mapping.get(lan, {})
        
        if row['Amount Match'] and row['Principal Match'] and row['Interest Match']:
            # If all match, keep the original
            revised_schedule.append({
                'LAN': lan,
                'Revised Amount': lms_row.get('Amount', 0),
                'Revised Principal': lms_row.get('Principal', 0),
                'Revised Interest': lms_row.get('Interest', 0),
                'Remarks': 'No changes needed'
            })
        else:
            # Adjust the principal and amount based on differences
            revised_principal = lms_row.get('Principal', 0) + (row['Partner Principal'] - lms_row.get('Principal', 0))
            revised_amount = revised_principal + lms_row.get('Interest', 0)

            revised_schedule.append({
                'LAN': lan,
                'Revised Amount': revised_amount,
                'Revised Principal': revised_principal,
                'Revised Interest': lms_row.get('Interest', 0),
                'Remarks': 'Adjusted based on differences'
            })

    # Create DataFrame for revised schedule
    revised_schedule_df = pd.DataFrame(revised_schedule)

    # Combine comparison and revised schedule
    final_output = comparison_df.merge(revised_schedule_df, on='LAN', how='left')

    # Save to Excel
    updated_file_name = "Updated_LMS_Schedule.xlsx"
    final_output.to_excel(updated_file_name, index=False)

    return final_output, updated_file_name

# Streamlit UI
st.title("LMS Schedule Status Updater")

# Upload Files
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

if lms_file and partner_file:
    st.write("Processing...")
    output, updated_file_name = update_lms_schedule(lms_file, partner_file)
    
    # Display comparison results
    st.subheader("Comparison and Revised Schedule")
    st.dataframe(output)

    # Auto download link
    with open(updated_file_name, "rb") as file:
        btn = st.download_button(
            label="Download Updated LMS Schedule",
            data=file,
            file_name=updated_file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success(f"Updated LMS Schedule saved to {updated_file_name}")
else:
    st.warning("Please upload both LMS and Partner schedule files.")
