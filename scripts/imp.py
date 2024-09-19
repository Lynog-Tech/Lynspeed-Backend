import os
import django
import sys
import pandas as pd
from django.conf import settings

current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")

# Add the parent directory to sys.path
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
print(f"Parent directory added to sys.path: {parent_dir}")

# Set up Django environment
if not settings.configured:
    print("Configuring Django settings")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynspeed_project.settings')
    django.setup()
else:
    print("Django settings already configured")
from questionBank.models import Subject, Worksheet, Question

def import_excel_files(base_dir):
    print(f"Starting import process from directory: {base_dir}")
    
    for subject_name in os.listdir(base_dir):
        subject_path = os.path.join(base_dir, subject_name)
        if os.path.isdir(subject_path):
            print(f"Processing subject: {subject_name}")
            subject, created = Subject.objects.get_or_create(name=subject_name)
            if created:
                print(f"Created new subject: {subject_name}")
            
            process_subject_directory(subject, subject_path)

def process_subject_directory(subject, subject_path):
    for file_name in os.listdir(subject_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(subject_path, file_name)
            print(f"Processing file: {file_path}")
            
            worksheet_name = os.path.splitext(file_name)[0]
            worksheet, created = Worksheet.objects.get_or_create(
                subject=subject,
                name=worksheet_name,
                defaults={'file_path': file_path}
            )
            if created:
                print(f"Created new worksheet: {worksheet_name}")
            
            import_questions_from_excel(worksheet, file_path)

def import_questions_from_excel(worksheet, file_path):
    try:
        df = pd.read_excel(file_path)
        print(f"Found {len(df)} rows in the Excel file")
        
        for index, row in df.iterrows():
            question_text = row['TEXT']
            option_a = row['OPTION -A']
            option_b = row['OPTION -B']
            option_c = row['OPTION -C']
            option_d = row['OPTION -D']
            correct_option = row['CORRECT OPTION']

            # Create or update the question
            question, created = Question.objects.update_or_create(
                worksheet=worksheet,
                text=question_text,
                defaults={
                    'option_a': option_a,
                    'option_b': option_b,
                    'option_c': option_c,
                    'option_d': option_d,
                    'correct_option': correct_option,
                    'order': index
                }
            )
            
            if created:
                print(f"Created new question: {question_text[:50]}...")
            else:
                print(f"Updated existing question: {question_text[:50]}...")
        
        print(f"Finished processing {file_path}")
    
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")

if __name__ == "__main__":
    base_directory = r'C:\Users\DELL\Documents\chibuike\data'  # Update this path
    import_excel_files(base_directory)
    print("Import process completed.")