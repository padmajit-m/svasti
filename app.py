import pandas as pd
import streamlit as st

def update_lms_schedule(lms_file, partner_file):
    # Load the LMS and Partner schedules
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Convert InstalmentDate columns to datetime format
    lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'], errors='coerce')
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], errors='coerce')

    # Initialize a list to collect remarks
    remarks = []

    # Loop through the partner schedule to adjust LMS schedule
    for _, partner_row in partner_schedule.iterrows():
        lan = partner_row['LAN']
        partner_date = partner_row['InstalmentDate']
        
        # Filter LMS schedule for the matching LAN
        lms_matches = lms_schedule[lms_schedule['LAN'] == lan]

        # Check for satisfied status in LMS schedule
        satisfied_rows = lms_matches[lms_matches['status'] == 'Satisfied']
        
        # If there are satisfied entries, skip them for changes
        if not satisfied_rows.empty:
            continue

        # Find the corresponding rows in LMS that are Due or Projected
        due_or_projected_rows = lms_matches[(lms_matches['status'] == 'Due') | (lms_matches['status'] == 'Projected')]
        
        # Adjust the LMS schedule according to the partner schedule
        for _, lms_row in due_or_projected_rows.iterrows():
            if lms_row['InstalmentDate'] > pd.Timestamp('2024-03-31'):
                # Calculate adjustments based on partner schedule
                principal_adjustment = partner_row['Principal'] - lms_row['Principal']
                interest_adjustment = partner_row['Interest'] - lms_row['Interest']

                # Apply adjustments
                lms_row['Principal'] += principal_adjustment
                lms_row['Interest'] += interest_adjustment
                
                # Record remarks for adjustments
                remarks.append(f"Adjusted for LAN {lan} on {lms_row['InstalmentDate'].date()} | "
                               f"Adjusted Principal: {principal_adjustment}, "
                               f"Adjusted Interest: {interest_adjustment}")

    # Add remarks to LMS schedule (expand list to match the length of LMS schedule)
    lms_schedule['Remarks'] = pd.Series(remarks + [''] * (len(lms_schedule) - len(remarks)))

    # Match demands for unmatched cases
    for _, lms_row in lms_schedule.iterrows():
        if lms_row['status'] in ['Due', 'Projected']:
            lan = lms_row['LAN']
            partner_demand_count = partner_schedule[partner_schedule['LAN'] == lan].shape[0]
            lms_demand_count = lms_schedule[lms_schedule['LAN'] == lan].shape[0]

            if partner_demand_count > lms_demand_count:
                remarks.append(f"Added {partner_demand_count - lms_demand_count} demands for LAN {lan}.")
                # Logic to add dummy entries or handle this according to your requirement goes here

    # Save the updated LMS schedule to a new Excel file
    output_file = 'Updated_LMS_Schedule.xlsx'
    lms_schedule.to_excel(output_file, index=False)
    
    return output_file

# Streamlit interface
st.title("LMS Schedule Status Updater")

# File upload for LMS schedule
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])

# File upload for Partner schedule
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

# Debugging: Show uploaded files
st.write("LMS File Uploaded:", lms_file)
st.write("Partner File Uploaded:", partner_file)

if lms_file is not None and partner_file is not None:
    output = update_lms_schedule(lms_file, partner_file)
    st.success(f"Updated LMS Schedule saved to {output}")
else:
    st.warning("Please upload both LMS and Partner schedule files.")
