import pandas as pd

def update_lms_schedule(lms_file, partner_file, system_file):
    # Load the LMS, Partner, and System schedules
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)
    system_schedule = pd.read_excel(system_file)

    # Convert InstalmentDate columns to datetime format
    lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'], errors='coerce')
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], errors='coerce')
    system_schedule['InstalmentDate'] = pd.to_datetime(system_schedule['InstalmentDate'], errors='coerce')

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
                principal_difference = partner_row['Principal'] - lms_row['Principal']
                interest_difference = partner_row['Interest'] - lms_row['Interest']

                # Adjust Principal and Interest
                lms_row['Principal'] += principal_difference
                lms_row['Interest'] += interest_difference

                # Record remarks for adjustments
                remarks.append(f"Adjusted for LAN {lan} on {lms_row['InstalmentDate'].date()} | "
                               f"Adjusted Principal: {principal_difference}, "
                               f"Adjusted Interest: {interest_difference}")

        # Handle mismatched demands
        partner_demands = partner_schedule[partner_schedule['LAN'] == lan].shape[0]
        lms_demands = lms_matches.shape[0]

        if partner_demands > lms_demands:
            remarks.append(f"Matched {partner_demands - lms_demands} additional demands for LAN {lan} based on partner schedule.")

    # Update the remarks in the LMS schedule
    lms_schedule['Remarks'] = pd.Series(remarks)

    # Save the updated LMS schedule to a new Excel file
    output_file = 'Updated_LMS_Schedule.xlsx'
    lms_schedule.to_excel(output_file, index=False)
    
    return output_file

# Example usage
lms_file_path = 'path_to_your_lms_schedule.xlsx'  # Replace with your LMS schedule file path
partner_file_path = 'path_to_your_partner_schedule.xlsx'  # Replace with your Partner schedule file path
system_file_path = 'path_to_your_system_schedule.xlsx'  # Replace with your System schedule file path
output = update_lms_schedule(lms_file_path, partner_file_path, system_file_path)
print(f"Updated LMS Schedule saved to {output}")
