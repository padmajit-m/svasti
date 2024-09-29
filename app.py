import pandas as pd
import streamlit as st

# Title of the app
st.title("LMS and Partner Schedule Comparison")

# Step 1: Upload files using Streamlit's file uploader
uploaded_files = st.file_uploader("Upload Partner and LMS Schedule files", type=["xlsx"], accept_multiple_files=True)

# Initialize variables
partner_schedule = None
lms_schedule = None

# Read the uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Check file name and read accordingly
        if "partner_schedule" in uploaded_file.name:
            partner_schedule = pd.read_excel(uploaded_file)
            st.write("Partner Schedule loaded successfully.")
        elif "lms_schedule" in uploaded_file.name:
            lms_schedule = pd.read_excel(uploaded_file)
            st.write("LMS Schedule loaded successfully")

    # Check if both schedules are loaded
    if partner_schedule is not None and lms_schedule is not None:
        # Step 2: Handle different date formats
        partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], format='%Y/%m/%d')
        lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'], format='%Y-%m-%d')

        # Step 3: Merge the DataFrames on 'LAN' and 'InstalmentNumber'
        merged_df = partner_schedule.merge(lms_schedule, on=['LAN', 'InstalmentNumber'], how='outer', suffixes=('_partner', '_lms'), indicator=True)

        # Function to compare values and add remarks
        def compare_rows(row):
            remarks = []
            if row['_merge'] == 'left_only':
                return 'LMS Missing Instalment'
            elif row['_merge'] == 'right_only':
                return 'Partner Missing Instalment'
            else:
                if row['InstalmentDate_partner'] != row['InstalmentDate_lms']:
                    remarks.append('InstalmentDate Mismatch')
                if row['Amount_partner'] != row['Amount_lms']:
                    remarks.append('Amount Mismatch')
                if row['Principal_partner'] != row['Principal_lms']:
                    remarks.append('Principal Mismatch')
                if row['Interest_partner'] != row['Interest_lms']:
                    remarks.append('Interest Mismatch')
                if row['BalanceOutstanding_partner'] != row['BalanceOutstanding_lms']:
                    remarks.append('BalanceOutstanding Mismatch')
                return ', '.join(remarks) if remarks else 'Match'

        # Apply the comparison function to each row
        merged_df['Remarks'] = merged_df.apply(compare_rows, axis=1)

        # Identify missing installments
        merged_df['MissingInstallment'] = merged_df['_merge'].apply(lambda x: 'Yes' if x != 'both' else 'No')

        # Calculate differences
        merged_df['principle_mismatch (E-J)'] = merged_df['Principal_partner'] - merged_df['Principal_lms']
        merged_df['interest_mismatch (F-K)'] = merged_df['Interest_partner'] - merged_df['Interest_lms']
        merged_df['Diff amount (partner-encore)'] = merged_df['Amount_partner'] - merged_df['Amount_lms']
        merged_df['Outstanding balance'] = merged_df['BalanceOutstanding_partner'] - merged_df['BalanceOutstanding_lms']
        merged_df['Diff principle(partner-encore)'] = merged_df['Principal_partner'] - merged_df['Principal_lms']
        merged_df['Diff int(partner-encore)'] = merged_df['Interest_partner'] - merged_df['Interest_lms']

        # Select and rename the necessary columns
        result = merged_df[[  
            'LAN', 'InstalmentNumber', 'InstalmentDate_partner', 'Amount_partner', 'Principal_partner', 
            'Interest_partner', 'BalanceOutstanding_partner',
            'InstalmentDate_lms', 'Amount_lms', 'Principal_lms', 'Interest_lms', 'BalanceOutstanding_lms',
            'principle_mismatch (E-J)', 'interest_mismatch (F-K)', 'Remarks', 'MissingInstallment',
            'Diff amount (partner-encore)', 'Outstanding balance', 'Diff principle(partner-encore)', 
            'Diff int(partner-encore)'
        ]]

        # Format date columns to 'yyyy-mm-dd'
        date_columns = ['InstalmentDate_partner', 'InstalmentDate_lms']
        result[date_columns] = result[date_columns].apply(lambda x: x.dt.strftime('%Y-%m-%d'))

        # Save the result to a new Excel file
        output_file = 'detailed_comparison_report_with_mismatches_and_differences.xlsx'
        result.to_excel(output_file, index=False)
        
        # Step 8: Provide download link for the generated Excel file
        st.download_button(label="Download Detailed Comparison Report", data=output_file, file_name=output_file)

        # Display the results in the Streamlit app
        st.write("Comparison Results:")
        st.dataframe(result)

    else:
        st.warning("Please upload both LMS and Partner schedule files.")
else:
    st.info("Please upload the required Excel files.")
