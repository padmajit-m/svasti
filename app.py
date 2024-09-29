import pandas as pd
import streamlit as st
import io  # For handling file streams

def update_lms_schedule(lms_file, partner_file):
    # Load the LMS and Partner schedules
    lms_schedule = pd.read_excel(lms_file)
    partner_schedule = pd.read_excel(partner_file)

    # Convert InstalmentDate columns to datetime format
    lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'], errors='coerce')
    partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], errors='coerce')

    # Initialize progress bar and status text
    total_steps = len(partner_schedule)
    progress_bar = st.progress(0)
    status_text = st.empty()
    remarks = []

    # Display some initial rows for verification
    st.subheader("Initial Rows from Partner Schedule")
    st.dataframe(partner_schedule.head())

    st.subheader("Initial Rows from LMS Schedule")
    st.dataframe(lms_schedule.head())

    # Loop through the partner schedule to adjust LMS schedule
    for idx, partner_row in enumerate(partner_schedule.iterrows(), 1):
        _, partner_row = partner_row
        lan = partner_row['LAN']
        partner_date = partner_row['InstalmentDate']

        # Log current progress
        status_text.text(f"Processing {idx}/{total_steps}: LAN {lan}")
        st.write(f"Processing {idx}/{total_steps} - LAN {lan} - InstalmentDate: {partner_date}")

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

        # Update progress bar
        progress_bar.progress(idx / total_steps)

    # Add remarks to LMS schedule (expand list to match the length of LMS schedule)
    lms_schedule['Remarks'] = pd.Series(remarks + [''] * (len(lms_schedule) - len(remarks)))

    # Display some final rows for verification
    st.subheader("Final Adjusted Rows from LMS Schedule")
    st.dataframe(lms_schedule.head())

    # Save the updated LMS schedule to a new Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        lms_schedule.to_excel(writer, index=False, sheet_name='Updated Schedule')
    
    # Reset pointer of BytesIO object
    output.seek(0)
    
    # Complete progress bar
    progress_bar.progress(1)
    status_text.text("Completed processing all rows.")
    
    return output

# Streamlit interface
st.title("LMS Schedule Status Updater")

# File upload for LMS schedule
lms_file = st.file_uploader("Upload LMS Schedule File", type=["xlsx"])

# File upload for Partner schedule
partner_file = st.file_uploader("Upload Partner Schedule File", type=["xlsx"])

# Debugging: Show uploaded files
if lms_file is not None and partner_file is not None:
    st.write("LMS File Uploaded:", lms_file)
    st.write("Partner File Uploaded:", partner_file)

    st.info("Processing files, please wait...")
    
    try:
        updated_lms_schedule = update_lms_schedule(lms_file, partner_file)
        
        # Provide download button for the updated LMS schedule
        st.download_button(
            label="Download Updated LMS Schedule",
            data=updated_lms_schedule,
            file_name="Updated_LMS_Schedule.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("The updated LMS schedule is ready for download.")
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.warning("Please upload both LMS and Partner schedule files.")
