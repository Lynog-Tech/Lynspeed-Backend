import pandas as pd
import os
import sys
import django
from django.db import transaction
from django.conf import settings

print("Script started")

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
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynspeed_project.settings')
    django.setup()
else:
    print("Django settings already configured")

from questionBank.models import Subject, Question, Option

# Base directory where subject folders are stored
base_dir = r'C:\Users\DELL\Documents\chibuike\data'
print(f"Base directory set to: {base_dir}")

def process_subject(subject_dir, subject_name):
    print(f"Processing subject directory: {subject_dir} for subject: {subject_name}")
    for file_name in os.listdir(subject_dir):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(subject_dir, file_name)
            print(f"Loading Excel file: {file_path}")
            try:
                excel_file = pd.ExcelFile(file_path)

                for sheet_name in excel_file.sheet_names:
                    print(f"Processing sheet: {sheet_name} in file: {file_name}")
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    df.columns = df.columns.str.strip().str.lower()  # Normalize column names

                    # Print first few rows of the dataframe to verify data
                    print(f"Data from sheet '{sheet_name}':")
                    print(df.head())

                    for index, row in df.iterrows():
                        try:
                            print(f"\nProcessing row {index + 1} from sheet '{sheet_name}'")
                            print(f"Row data: {row}")

                            subject, created = Subject.objects.get_or_create(name=subject_name)
                            print(f"Subject: {subject.name} {'created' if created else 'exists'}")

                            question_text = row['text']
                            options = {
                                'a': row['option - a'],
                                'b': row['option - b'],
                                'c': row['option - c'],
                                'd': row['option - d']
                            }

                            correct_option_letter = row['correct option']
                            print(f"Question: {question_text}")
                            print(f"Options: {options}")
                            print(f"Correct option letter: {correct_option_letter}")

                            if pd.isna(correct_option_letter):
                                print(f"Warning: Missing correct option for question: {question_text}")
                                continue

                            correct_option_letter = str(correct_option_letter).strip().lower()
                            correct_option_text = options.get(correct_option_letter)

                            if not correct_option_text:
                                print(f"Warning: Invalid correct option for question: {question_text}")
                                continue

                            # Handle image file if it exists
                            image_path = row.get('image')
                            if pd.notna(image_path):
                                image_path = os.path.join(subject_dir, 'images', str(image_path))
                                print(f"Image path: {image_path}")
                                if os.path.exists(image_path):
                                    question = Question.objects.create(subject=subject, text=question_text, image=image_path)
                                else:
                                    print(f"Warning: Image file not found for question: {question_text}")
                                    question = Question.objects.create(subject=subject, text=question_text)
                            else:
                                question = Question.objects.create(subject=subject, text=question_text)

                            # Create all options
                            correct_option = None
                            for letter, option_text in options.items():
                                option = Option.objects.create(question=question, text=option_text)
                                if option_text == correct_option_text:
                                    correct_option = option

                            # Set the correct option for the question
                            if correct_option:
                                question.correct_option = correct_option
                                question.save()
                                print(f"Set correct option for question: {question_text}")
                            else:
                                print(f"Warning: Correct option not found for question: {question_text}")

                            # Print question details after saving
                            print(f"Created question: {question.id} - {question.text}")
                            print(f"Subject: {question.subject.name}")
                            print("Options:")
                            for option in question.options.all():
                                print(f" - {option.text}")
                            if question.correct_option:
                                print(f"Correct Option: {question.correct_option.text}")
                            else:
                                print("No correct option set.")

                        except Exception as e:
                            print(f"Error processing question at row {index + 1} in sheet {sheet_name}: {e}")
                            continue
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                
def display_database_contents():
    print("\nDatabase Contents:")
    subjects = Subject.objects.all()
    for subject in subjects:
        print(f"\nSubject: {subject.name}")
        questions = Question.objects.filter(subject=subject)
        print(f"Number of questions: {questions.count()}")
        for question in questions:
            print(f"  - Question: {question.text}")
            options = Option.objects.filter(question=question)
            for option in options:
                correct = "(Correct)" if option == question.correct_option else ""
                print(f"    * {option.text} {correct}")
        print("--------------------")
def main():
    print("Entering main function")
    # Iterate over each subject directory
    print(f"Base directory: {base_dir}")
    if not os.path.exists(base_dir):
        print(f"Error: Base directory does not exist: {base_dir}")
        return

    subject_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not subject_dirs:
        print(f"Error: No subject directories found in {base_dir}")
        return

    print(f"Found subject directories: {subject_dirs}")

    for subject_name in subject_dirs:
        subject_dir = os.path.join(base_dir, subject_name)
        if os.path.isdir(subject_dir):
            print(f"Processing subject directory: {subject_dir} for subject: {subject_name}")
            process_subject(subject_dir, subject_name)

    print("Data import completed successfully.")
    print(f"Subjects in database: {Subject.objects.count()}")
    print(f"Questions in database: {Question.objects.count()}")
    print(f"Options in database: {Option.objects.count()}")
    
    display_database_contents()
    

if __name__ == "__main__":
    print("Script is being run directly")
    main()
else:
    print("Script is being imported")

print("Script execution completed")

