# knowledgebase/management/commands/create_editors.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
import csv

class Command(BaseCommand):
    help = 'Creates editor user accounts from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing user data.')


    def handle(self, *args, **options):
        editor_group_name = "Editors" 
        csv_file_path = options['csv_file']
        try:
            editor_group = Group.objects.get(name=editor_group_name)
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Group "{editor_group_name}" does not exist.'))
            return

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row['name']
                    email = row['email']
                    first_name, *last_name_parts = name.split()  # Take first word as first name
                    last_name = " ".join(last_name_parts)
                    username = email.split('@')[0]

                    try:
                        password = "TempPass!"
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            password=password,
                            is_staff=True
                        )
                        user.groups.add(editor_group)
                        user.save()
                        self.stdout.write(self.style.SUCCESS(f'User "{username}" created and added to "{editor_group_name}". Temporary Password: {password}'))

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating user "{email}": {e}'))
        except FileNotFoundError:
             self.stdout.write(self.style.ERROR(f'File "{csv_file_path}" not found.'))
        except Exception as e:
              self.stdout.write(self.style.ERROR(f'Error processing the file: {e}'))