import streamlit as st
import pandas as pd

def update_lms_data(file):
    # Read the uploaded Excel file
    df = pd.read_excel(file)

    # Assuming the date column is named 'DateDue'
    df['DateDue'] = pd.to_datetime(df['DateDue'])

    # Create a new 'Remarks' column
    df['Remarks'] = ""

    # Process each row in the dataframe
    for index, row in df.iterrows():
        # Skip rows with DateDue before 31st March 2024
        if row['DateDue'] < pd.Timestamp('2024-03-31'):
            continue
        
        # Check for mismatches and update the values
        if row['Partner Amount'] != row['Amount_lms_updated']:
            df.at[index, 'Amount_lms_updated'] = row['Partner Amount']
            df.at[index, 'Remarks'] = "Amount updated"

        if row['Partner Principal'] != row['Principal_lms_updated']:
            df.at[index, 'Principal_lms_updated'] = row['Partner Principal']
            df.at[index, 'Remarks'] += " | Principal updated" if df.at[index, 'Remarks'] else "Principal updated"

        if row['Partner Interest'] != row['Interest_lms_updated']:
            df.at[index, 'Interest_lms_updated'] = row['Partner Interest']
            df.at[index, 'Remarks'] += " | Interest updated" if df.at[index, 'Remarks'] else "Interest updated"
    
    return df

def main():
    st.title('LMS Data Update Tool')
    st.write("Upload your Excel file to process LMS data")

    # File upload
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        st.success("File uploaded successfully")
        # Process the file
        result_df = update_lms_data(uploaded_file)
        
        # Show the updated dataframe
        st.write("Updated Data Preview:")
        st.dataframe(result_df)

        # Download the updated file
        st.download_button(
            label="Download Updated Excel",
            data=result_df.to_excel(index=False, engine='openpyxl'),
            file_name="updated_lms_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == '__main__':
    main()
