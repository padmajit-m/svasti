import pandas as pd
import streamlit as st

def update_lms_schedule(lms_file, partner_file):
    # Read the files
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Initialize a list to collect results for final DataFrame
    combined_schedule = []

    # Initialize progress bar
    progress_bar = st.progress(0)
    total_rows = len(partner_schedule)

    # Iterate through each row in the partner schedule
    for index, partner_row in partner_schedule.iterrows():
        lan = partner_row['LAN']
        partner_amount = partner_row['Amount']
        partner_instalment_number = partner_row['InstalmentNumber']
        partner_instalment_date = partner_row['InstalmentDate']
        partner_principal = partner_row['Principal']
        partner_interest = partner_row['Interest']

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

    # Create DataFrame from combined schedule
    result_df = pd.DataFrame(combined_schedule)

    # Write the result to a new Excel file
    output_file = "Updated_LMS_Schedule.xlsx"
    result_df.to_excel(output_file, index=False)

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
