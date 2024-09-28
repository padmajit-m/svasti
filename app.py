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

    # Initialize a new DataFrame for the updated LMS schedule
    updated_schedule = lms_schedule.copy()

    # Process entries
    for index, row in updated_schedule.iterrows():
        instalment_date = pd.to_datetime(row['InstalmentDate'])
        
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
                
                # Reset satisfied cases after adjustment to avoid double adjustment
                satisfied_cases = satisfied_cases[satisfied_cases['InstalmentDate'] != instalment_date]

    # Save the updated LMS schedule
    output_file = "Adjusted_LMS_Schedule.xlsx"
    updated_schedule.to_excel(output_file, index=False)
    
    # Provide a download link for the updated schedule
    st.download_button("Download Updated LMS Schedule", data=output_file, file_name=output_file)

    # Display the final adjusted schedule
    st.write("Updated LMS Schedule:")
    st.dataframe(updated_schedule)

