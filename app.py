import pandas as pd
import streamlit as st

# Title of the application
st.title("Loan Repayment Schedule Adjuster")

# Upload LMS Schedule File
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])
# Upload Partner Schedule File
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

if lms_file and partner_file:
    # Load the files into DataFrames
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Display the uploaded data for reference
    st.write("LMS Schedule Data:")
    st.dataframe(lms_schedule)
    
    st.write("Partner Schedule Data:")
    st.dataframe(partner_schedule)

    # Filter out satisfied cases
    satisfied_cases = lms_schedule[lms_schedule['status'] == 'Satisfied']
    unsatisfied_cases = lms_schedule[lms_schedule['status'] != 'Satisfied']

    # Initialize a new DataFrame for the updated LMS schedule
    updated_schedule = lms_schedule.copy()

    # Initialize a list for remarks
    remarks = []

    # Process entries for unsatisfied cases
    for index, row in unsatisfied_cases.iterrows():
        instalment_date = pd.to_datetime(row['InstalmentDate'])
        lan = row['LAN']
        
        # Adjust only if the date is greater than March 31, 2024
        if instalment_date > pd.Timestamp('2024-03-31'):
            # Check if the status is due or projected
            if row['status'] in ['Due', 'Projected']:
                # Calculate the total excess from satisfied cases
                excess_principal = satisfied_cases['Principal'].sum()
                excess_interest = satisfied_cases['Interest'].sum()

                # Adjust the principal and interest
                updated_schedule.at[index, 'Principal'] += excess_principal
                updated_schedule.at[index, 'Interest'] += excess_interest

                # Generate remarks for the adjustment
                remarks.append(f"Adjusted principal and interest by {excess_principal} and {excess_interest} respectively for LAN {lan}.")

    # Match demands as per partner schedule for unsatisfied cases
    for lan in unsatisfied_cases['LAN'].unique():
        # Get the number of demands in partner schedule for this LAN
        partner_demands = partner_schedule[partner_schedule['LAN'] == lan]
        total_partner_demands = len(partner_demands)

        # Get the number of demands in LMS for this LAN
        current_demand_count = len(updated_schedule[updated_schedule['LAN'] == lan])

        # If partner demands are more than current demands, add the missing demands
        if total_partner_demands > current_demand_count:
            needed_demands = total_partner_demands - current_demand_count
            remarks.append(f"Added {needed_demands} demands for LAN {lan} to match partner schedule.")

            for _ in range(needed_demands):
                # Create a new row with adjusted values
                new_row = {
                    'LAN': lan,
                    'InstalmentNumber': current_demand_count + 1,  # Increment demand number
                    'InstalmentDate': instalment_date + pd.DateOffset(months=1),  # Next month
                    'Amount': 0,  # Placeholder for Amount
                    'Principal': 0,  # Placeholder for Principal
                    'Interest': 0,  # Placeholder for Interest
                    'BalanceOutstanding': 0,  # Placeholder for BalanceOutstanding
                    'status': 'Projected',  # Default to Projected
                }
                updated_schedule = updated_schedule.append(new_row, ignore_index=True)
                current_demand_count += 1  # Update current demand count for the next iteration

    # Add remarks to the updated schedule
    updated_schedule['Remarks'] = remarks + [''] * (len(updated_schedule) - len(remarks))

    # Save the updated LMS schedule
    output_file = "Adjusted_LMS_Schedule.xlsx"
    updated_schedule.to_excel(output_file, index=False)
    
    # Provide a download link for the updated schedule
    st.download_button("Download Updated LMS Schedule", data=output_file, file_name=output_file)

    # Display the final adjusted schedule
    st.write("Updated LMS Schedule:")
    st.dataframe(updated_schedule)
