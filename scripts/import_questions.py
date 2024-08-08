import pandas as pd
import os
import sys
import django
from django.db import transaction
from django.conf import settings

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to sys.path
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Set up Django environment
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynspeed_project.settings')
    django.setup()

from questionBank.models import Subject, Question, Option

# Base directory where subject folders are stored
base_dir = r'C:\Users\DELL\Documents\chibuike\data'

def process_subject(subject_dir, subject_name):
    """ Process all Excel files in a subject directory """
    for file_name in os.listdir(subject_dir):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(subject_dir, file_name)
            excel_file = pd.ExcelFile(file_path)

            for sheet_name in excel_file.sheet_names:
                print(f"Processing sheet: {sheet_name} in file: {file_name}")
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                df.columns = df.columns.str.strip().str.lower()  # Normalize column names

                for index, row in df.iterrows():
                    with transaction.atomic():
                        try:
                            subject, created = Subject.objects.get_or_create(name=subject_name)

                            question_text = row['text']
                            options = {
                                'a': row['option - a'],
                                'b': row['option - b'],
                                'c': row['option - c'],
                                'd': row['option - d']
                            }

                            correct_option_letter = row['correct option']
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
                            else:
                                print(f"Warning: Correct option not found for question: {question_text}")

                            print(f"Created question: {question_text}")

                        except Exception as e:
                            print(f"Error processing question at row {index + 1} in sheet {sheet_name}: {e}")
                            continue

def main():
    # Iterate over each subject directory
    for subject_name in os.listdir(base_dir):
        subject_dir = os.path.join(base_dir, subject_name)
        if os.path.isdir(subject_dir):
            print(f"Processing subject: {subject_name}")
            process_subject(subject_dir, subject_name)

    print("Data import completed successfully.")

if __name__ == "__main__":
    main()
