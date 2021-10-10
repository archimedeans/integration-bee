import csv
import pathlib
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand


# For each contestant specified in a CSV file,
# creates a user, a corresponding contestant and empty submissions.
# Requires the "Contestants" group and all problems to be in the database.
# CSV format: first_name,last_name,email,username,password

class Command(BaseCommand):
    help = 'Register contestants from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', nargs=1, type=pathlib.Path)

    def handle(self, *args, **options):
        markers_group = Group.objects.get(name='Markers')

        with open(options['csv_path'][0], newline='') as csvfile:
            contestants_reader = csv.reader(csvfile)
            i = 0
            for row in contestants_reader:
                if User.objects.filter(username=row[3]).exists():
                    self.stderr.write(self.style.NOTICE(
                        f'A user under the username \'{row[3]}\' already exists.')
                    )
                    continue
                # Create user and save it to the database
                user = User.objects.create_user(
                    username=row[3], email=row[2], password=row[4])
                # Add the new user to the "Markers" group
                user.groups.add(markers_group)
                # Set names of the new user
                user.first_name = row[0]
                user.last_name = row[1]
                user.save()
                i += 1
            self.stdout.write(self.style.SUCCESS(
                'Successfully registered %d markers.' % i)
            )
