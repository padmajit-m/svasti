import pandas as pd

# Step 1: Read the uploaded Excel files
partner_schedule = pd.read_excel('partner_schedule.xlsx')
lms_schedule = pd.read_excel('lms_schedule.xlsx')

# Step 2: Handle different date formats
partner_schedule['InstalmentDate'] = pd.to_datetime(partner_schedule['InstalmentDate'], format='%Y/%m/%d')
lms_schedule['InstalmentDate'] = pd.to_datetime(lms_schedule['InstalmentDate'], format='%Y-%m-%d')

# Step 3: Merge the DataFrames on 'LAN' and 'InstalmentNumber'
merged_df = partner_schedule.merge(lms_schedule, on=['LAN', 'InstalmentNumber'], how='outer', suffixes=('_partner', '_lms'), indicator=True)

# Step 4: Compare values and add remarks
def compare_and_adjust(row):
    remarks = []
    
    if row['_merge'] == 'left_only':
        return 'LMS Missing Instalment', row['Amount_partner'], row['Principal_partner'], row['Interest_partner'], row['BalanceOutstanding_partner']
    elif row['_merge'] == 'right_only':
        return 'Partner Missing Instalment', row['Amount_lms'], row['Principal_lms'], row['Interest_lms'], row['BalanceOutstanding_lms']
    else:
        # Calculate mismatches
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
        
        # Adjust upcoming instalments
        adjusted_amount = row['Amount_partner'] if row['Amount_partner'] else row['Amount_lms']
        adjusted_principal = row['Principal_partner'] if row['Principal_partner'] else row['Principal_lms']
        adjusted_interest = row['Interest_partner'] if row['Interest_partner'] else row['Interest_lms']
        adjusted_balance_outstanding = (row['BalanceOutstanding_lms'] - adjusted_principal) if pd.notna(row['BalanceOutstanding_lms']) else row['BalanceOutstanding_partner']
        
        # If there's no mismatch, set 'Match'
        if not remarks:
            remarks = ['Match']
        
        return ', '.join(remarks), adjusted_amount, adjusted_principal, adjusted_interest, adjusted_balance_outstanding

# Apply the function to add remarks and adjusted values
merged_df[['Remarks', 'AdjustedAmount', 'AdjustedPrincipal', 'AdjustedInterest', 'AdjustedBalanceOutstanding']] = merged_df.apply(compare_and_adjust, axis=1, result_type='expand')

# Step 5: Identify missing installments
merged_df['MissingInstallment'] = merged_df['_merge'].apply(lambda x: 'Yes' if x != 'both' else 'No')

# Calculate differences
merged_df['Principal Mismatch (Partner-LMS)'] = merged_df['Principal_partner'] - merged_df['Principal_lms']
merged_df['Interest Mismatch (Partner-LMS)'] = merged_df['Interest_partner'] - merged_df['Interest_lms']
merged_df['Amount Mismatch (Partner-LMS)'] = merged_df['Amount_partner'] - merged_df['Amount_lms']
merged_df['Outstanding Balance Mismatch'] = merged_df['BalanceOutstanding_partner'] - merged_df['BalanceOutstanding_lms']

# Select columns for the final result
final_result = merged_df[[
    'LAN', 'InstalmentNumber', 'InstalmentDate_partner', 'Amount_partner', 'Principal_partner', 'Interest_partner', 'BalanceOutstanding_partner',
    'InstalmentDate_lms', 'Amount_lms', 'Principal_lms', 'Interest_lms', 'BalanceOutstanding_lms',
    'AdjustedAmount', 'AdjustedPrincipal', 'AdjustedInterest', 'AdjustedBalanceOutstanding', 
    'Principal Mismatch (Partner-LMS)', 'Interest Mismatch (Partner-LMS)', 'Amount Mismatch (Partner-LMS)',
    'Outstanding Balance Mismatch', 'Remarks', 'MissingInstallment'
]]

# Format date columns to 'yyyy-mm-dd'
date_columns = ['InstalmentDate_partner', 'InstalmentDate_lms']
final_result[date_columns] = final_result[date_columns].apply(lambda x: x.dt.strftime('%Y-%m-%d'))

# Step 7: Save the result to a new Excel file
output_file = 'detailed_comparison_and_adjustments.xlsx'
final_result.to_excel(output_file, index=False)

print(f"Updated LMS Schedule with adjustments saved to: {output_file}")
