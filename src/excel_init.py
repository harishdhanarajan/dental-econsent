import pandas as pd
import os

# Define the Excel file path
excel_file = os.path.join('data', 'patient_data.xlsx')

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize Excel file with required sheets if it doesn't exist
if not os.path.exists(excel_file):
    # Create DataFrame for Patients sheet
    patients_df = pd.DataFrame(columns=[
        'Patient ID', 'Registration Date', 'Full Name', 'Age', 'Gender', 
        'Date of Birth', 'Address', 'Phone', 'Email', 'Emergency Contact', 
        'Relationship', 'Emergency Phone', 'Medical Conditions', 
        'Dental Issues', 'First Dental Visit', 'Reason for Visit'
    ])
    
    # Create DataFrame for Follow-ups sheet
    followups_df = pd.DataFrame(columns=[
        'Patient ID', 'Visit Date', 'Treatment', 'Diagnosis', 
        'Prescription', 'Notes', 'Next Appointment'
    ])
    
    # Write both DataFrames to Excel file
    with pd.ExcelWriter(excel_file) as writer:
        patients_df.to_excel(writer, sheet_name='Patients', index=False)
        followups_df.to_excel(writer, sheet_name='Follow-ups', index=False)
    
    print('Excel file initialized with required sheets')
else:
    print('Excel file already exists')
    
    # Validate existing Excel file structure
    try:
        with pd.ExcelFile(excel_file) as xls:
            sheets = xls.sheet_names
            
            # Check if both required sheets exist
            if 'Patients' not in sheets or 'Follow-ups' not in sheets:
                print('Warning: Excel file is missing required sheets')
                
                # Read existing data if available
                if 'Patients' in sheets:
                    patients_df = pd.read_excel(excel_file, sheet_name='Patients')
                else:
                    patients_df = pd.DataFrame(columns=[
                        'Patient ID', 'Registration Date', 'Full Name', 'Age', 'Gender', 
                        'Date of Birth', 'Address', 'Phone', 'Email', 'Emergency Contact', 
                        'Relationship', 'Emergency Phone', 'Medical Conditions', 
                        'Dental Issues', 'First Dental Visit', 'Reason for Visit'
                    ])
                
                if 'Follow-ups' in sheets:
                    followups_df = pd.read_excel(excel_file, sheet_name='Follow-ups')
                else:
                    followups_df = pd.DataFrame(columns=[
                        'Patient ID', 'Visit Date', 'Treatment', 'Diagnosis', 
                        'Prescription', 'Notes', 'Next Appointment'
                    ])
                
                # Rewrite the Excel file with all required sheets
                with pd.ExcelWriter(excel_file) as writer:
                    patients_df.to_excel(writer, sheet_name='Patients', index=False)
                    followups_df.to_excel(writer, sheet_name='Follow-ups', index=False)
                
                print('Excel file structure has been corrected')
            else:
                print('Excel file structure is valid')
    except Exception as e:
        print(f'Error validating Excel file: {str(e)}')
