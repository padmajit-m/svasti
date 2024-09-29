import pandas as pd
import streamlit as st
from datetime import datetime

def update_lms_schedule(lms_file, partner_file):
    # Read the files
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Convert Partner InstalmentDate format from YYYY/MM/DD to YYYY-MM-DD
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], format='%Y/%m/%d').dt.strftime('%Y-%m-%d')

    # Initialize a list to collect results for final DataFrame
    combined_schedule = []
    revised_schedule = []
    
    # Initialize variables to track total due and projected amounts
    total_due_amount = 0
    total_projected_amount = 0

    # Initialize progress bar
    progress_bar = st.progress(0)
    total_rows = len(partner_schedule)

    # Today's date and projected end date
    today = datetime.now()
    projected_end_date = datetime(2024, 3, 31)

    # Iterate through each row in the partner schedule
    for index, partner_row in partner_schedule.iterrows():
        lan = partner_row['LAN']
        partner_amount = partner_row['Amount']
        partner_instalment_number = partner_row['InstalmentNumber']
        partner_instalment_date = partner_row['InstalmentDate']
        partner_principal = partner_row['Principal']
        partner_interest = partner_row['Interest']
        partner_status = partner_row['Status']  # Assuming there's a Status column indicating 'Satisfied' or not

        # Find corresponding LMS rows
        lms_rows = lms_schedule[lms_schedule['LAN'] == lan]

        if not lms_rows.empty:
            for _, lms_row in lms_rows.iterrows():
                lms_amount = lms_row['Amount']
                lms_instalment_number = lms_row['InstalmentNumber']
                lms_instalment_date = lms_row['InstalmentDate']
                lms_principal = lms_row['Principal']
                lms_interest = lms_row['Interest']

                # Check for matches
                instalment_number_match = "Match" if partner_instalment_number == lms_instalment_number else "No Match"
                instalment_date_match = "Match" if partner_instalment_date == lms_instalment_date else "No Match"
                amount_match = "Match" if partner_amount == lms_amount else "No Match"
                principal_match = "Match" if partner_principal == lms_principal else "No Match"
                interest_match = "Match" if partner_interest == lms_interest else "No Match"

                # Append result to combined schedule
                combined_schedule.append({
                    "LAN": lan,
                    "Partner Instalment Number": partner_instalment_number,
                    "LMS Instalment Number": lms_instalment_number,
                    "Instalment Number Match": instalment_number_match,
                    "Partner Instalment Date": partner_instalment_date,
                    "LMS Instalment Date": lms_instalment_date,
                    "Instalment Date Match": instalment_date_match,
                    "Partner Amount": partner_amount,
                    "LMS Amount": lms_amount,
                    "Amount Match": amount_match,
                    "Partner Principal": partner_principal,
                    "LMS Principal": lms_principal,
                    "Principal Match": principal_match,
                    "Partner Interest": partner_interest,
                    "LMS Interest": lms_interest,
                    "Interest Match": interest_match,
                    "Remarks": "All details match." if all([instalment_number_match == "Match",
                                                              instalment_date_match == "Match",
                                                              amount_match == "Match",
                                                              principal_match == "Match",
                                                              interest_match == "Match"]) else "Mismatch found"
                })

                # Adjust upcoming due if the status is satisfied
                if partner_status == "Satisfied":
                    if amount_match == "No Match":
                        # Calculate the adjustment needed
                        adjustment = partner_amount - lms_amount
                        # Calculate the new amount for the first upcoming installment
                        if index + 1 < len(partner_schedule):
                            next_due_row = partner_schedule.iloc[index + 1]
                            next_due_row['Amount'] += adjustment  # Adjust the next due amount
                            revised_schedule.append({
                                "LAN": lan,
                                "Revised Instalment Number": next_due_row['InstalmentNumber'],
                                "Revised Instalment Date": next_due_row['InstalmentDate'],
                                "Revised Amount": next_due_row['Amount'],
                                "Revised Principal": next_due_row['Principal'] + adjustment,  # Adjust the principal
                                "Revised Interest": next_due_row['Interest'],  # Keep interest as is or adjust as per logic
                                "Remarks": "Adjustment applied to next due."
                            })

                # Add to total due amounts
                total_due_amount += partner_amount

        else:
            # If no corresponding LMS row found
            combined_schedule.append({
                "LAN": lan,
                "Partner Instalment Number": partner_instalment_number,
                "LMS Instalment Number": "N/A",
                "Instalment Number Match": "N/A",
                "Partner Instalment Date": partner_instalment_date,
                "LMS Instalment Date": "N/A",
                "Instalment Date Match": "N/A",
                "Partner Amount": partner_amount,
                "LMS Amount": "N/A",
                "Amount Match": "N/A",
                "Partner Principal": partner_principal,
                "LMS Principal": "N/A",
                "Principal Match": "N/A",
                "Partner Interest": partner_interest,
                "LMS Interest": "N/A",
                "Interest Match": "N/A",
                "Remarks": "No corresponding LMS entry found."
            })

        # Update progress bar
        progress = (index + 1) / total_rows
        progress_bar.progress(progress)

    # Calculate projected amounts until 31st March 2024
    for entry in revised_schedule:
        # Assuming a simple projection logic based on current amounts and installments
        projected_amount = entry['Revised Amount'] * ((projected_end_date - today).days // 30)  # Simplified for example
        total_projected_amount += projected_amount
        entry['Projected Amount'] = projected_amount

    # Create DataFrames from combined schedule and revised schedule
    result_df = pd.DataFrame(combined_schedule)
    revised_df = pd.DataFrame(revised_schedule)

    # Write the result to a new Excel file
    output_file = "Updated_LMS_Schedule.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        result_df.to_excel(writer, sheet_name='Comparison', index=False)
        revised_df.to_excel(writer, sheet_name='Revised Schedule', index=False)

    st.success(f"Updated LMS Schedule saved to {output_file}")
    return output_file

# Streamlit UI part
lms_file = st.file_uploader("Upload LMS Schedule", type=['xlsx'])
partner_file = st.file_uploader("Upload Partner Schedule", type=['xlsx'])

if lms_file and partner_file:
    updated_file = update_lms_schedule(lms_file, partner_file)
    # Provide a download link for the updated file
    with open(updated_file, "rb") as f:
        st.download_button("Download Updated Schedule", f, file_name=updated_file)
