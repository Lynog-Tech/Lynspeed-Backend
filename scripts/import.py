# import os
# import pandas as pd
# from django.core.management.base import BaseCommand
# from questionBank.models import *

# class Command(BaseCommand):
#     help = 'Import questions from Excel files into the database'

#     def handle(self, *args, **kwargs):
#         base_dir = r'C:\Users\DELL\Documents\chibuike\data'
        
#         if not os.path.isdir(base_dir):
#             self.stdout.write(self.style.ERROR(f'The directory "{base_dir}" does not exist.'))
#             return
        
#         for filename in os.listdir(base_dir):
#             if filename.endswith('.xlsx'):
#                 self.import_subject_from_file(os.path.join(base_dir, filename))

#     def import_subject_from_file(self, file_path):
#         subject_name = os.path.splitext(os.path.basename(file_path))[0]
#         subject, created = Subject.objects.get_or_create(name=subject_name)
        
#         if created:
#             self.stdout.write(self.style.SUCCESS(f'Created subject "{subject_name}".'))

#         xls = pd.ExcelFile(file_path)
        
#         for sheet_name in xls.sheet_names:
#             worksheet, created = Worksheet.objects.get_or_create(name=sheet_name, subject=subject)
            
#             if created:
#                 self.stdout.write(self.style.SUCCESS(f'Created worksheet "{sheet_name}" for subject "{subject_name}".'))
            
#             df = pd.read_excel(xls, sheet_name=sheet_name)
            
#             for index, row in df.iterrows():
#                 question_text = row.get('TEXT')
                
#                 if pd.notna(question_text):
#                     question = Question.objects.create(
#                         subject=subject,
#                         worksheet=worksheet,
#                         text=question_text
#                     )
#                     self.stdout.write(self.style.SUCCESS(f'Added question: "{question_text}".'))
                    
#                     # Handle options
#                     options = []
#                     for option_label in ['OPTION -A', 'OPTION -B', 'OPTION -C', 'OPTION -D']:
#                         option_text = row.get(option_label)
#                         if pd.notna(option_text):
#                             option = Option.objects.create(
#                                 question=question,
#                                 text=option_text
#                             )
#                             options.append(option)
#                             self.stdout.write(self.style.SUCCESS(f'Added option: "{option_text}".'))
                    
#                     # Handle correct option
#                     correct_option_text = row.get('CORRECT OPTION')
#                     if pd.notna(correct_option_text):
#                         correct_option = next((opt for opt in options if opt.text == correct_option_text), None)
#                         if correct_option:
#                             question.correct_option = correct_option
#                             question.save()
#                             self.stdout.write(self.style.SUCCESS(f'Set correct option: "{correct_option_text}".'))
