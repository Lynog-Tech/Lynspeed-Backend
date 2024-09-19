import os
import sys
import pandas as pd
import django
from django.conf import settings
from django.db import IntegrityError

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")

# Add the parent directory to sys.path
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
print(f"Parent directory added to sys.path: {parent_dir}")

# Set up Django environment
if not settings.configured:
    print("Configuring Django settings")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynspeed_project.settings')  # Replace with your actual project settings
    django.setup()
else:
    print("Django settings already configured")

# Import your models after setting up Django
from questionBank.models import Subject, Worksheet, Question  # Make sure these model names are correct

# Base directory where subject folders are stored
base_dir = r'C:\Users\DELL\Documents\chibuike\data\subject'
print(f"Base directory set to: {base_dir}")

def import_questions_from_excel(directory):
    print(f"Starting import from directory: {directory}")

    # Ensure the directory exists
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    # Iterate over Excel files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx'):
            subject_name = os.path.splitext(filename)[0]
            print(f"Processing subject: {subject_name}")

            # Create or get the subject
            subject, created = Subject.objects.get_or_create(name=subject_name)
            print(f"Subject created: {subject}, New: {created}")

            # Load the Excel file
            file_path = os.path.join(directory, filename)
            excel_file = pd.ExcelFile(file_path)

            # Loop through each sheet (worksheet)
            for sheet_name in excel_file.sheet_names:
                print(f"Processing worksheet: {sheet_name}")

                # Read the worksheet into a DataFrame
                worksheet_df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Create or get the worksheet
                worksheet, created = Worksheet.objects.get_or_create(name=sheet_name, subject=subject)
                print(f"Worksheet created: {worksheet.name}, New: {created}")

                # Check if worksheet is empty
                if worksheet_df.empty:
                    print(f"Worksheet {sheet_name} is empty.")
                    continue

                # Print column names to verify headers
                print(f"Columns in {sheet_name}: {worksheet_df.columns.tolist()}")

                # Iterate over each row in the worksheet and create questions
                for index, row in worksheet_df.iterrows():
                    # Print out the row being processed for debugging
                    print(f"Processing row {index}: {row.to_dict()}")

                    # Read the question and options
                    question_text = row.get('TEXT', None)
                    option_a = row.get('OPTION - A', None)
                    option_b = row.get('OPTION - B', None)
                    option_c = row.get('OPTION - C', None)
                    option_d = row.get('OPTION - D', None)
                    correct_option = row.get('CORRECT OPTION', None)

                    # Check if all required data is present
                    if question_text and option_a and option_b and option_c and option_d and correct_option:
                        # Check if question already exists
                        question_exists = Question.objects.filter(
                            worksheet=worksheet,
                            text=question_text,
                            option_a=option_a,
                            option_b=option_b,
                            option_c=option_c,
                            option_d=option_d,
                            correct_option=correct_option
                        ).exists()

                        if not question_exists:
                            # Create a question entry linked to the worksheet
                            try:
                                question = Question.objects.create(
                                    worksheet=worksheet,
                                    text=question_text,  # Updated field name
                                    option_a=option_a,
                                    option_b=option_b,
                                    option_c=option_c,
                                    option_d=option_d,
                                    correct_option=correct_option
                                )
                                print(f"Created question: {question_text} under worksheet {worksheet.name}")
                            except IntegrityError as e:
                                print(f"Error creating question: {e}")
                        else:
                            print(f"Question already exists: {question_text}")
                    else:
                        print(f"Skipping row {index} due to missing data.")

    # After import, check how many questions were created in the DB
    total_questions = Question.objects.count()
    print(f"Total questions in the database after import: {total_questions}")

    # List all subjects and their associated worksheets and questions
    subjects = Subject.objects.all()
    for subject in subjects:
        print(f"Subject: {subject.name}")
        worksheets = subject.worksheets.all()
        for worksheet in worksheets:
            print(f"  Worksheet: {worksheet.name}")
            questions = worksheet.questions.all()
            if questions.exists():
                for question in questions:
                    print(f"    Question: {question.text}")  # Updated field name
            else:
                print(f"    No questions found for worksheet: {worksheet.name}")

    print("Import completed.")

# Call the function to import questions
import_questions_from_excel(base_dir)
