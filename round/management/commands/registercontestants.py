import csv
import pathlib
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from round.models import Contestant, Problem, Submission


# For each contestant specified in a CSV file,
# creates a user, a corresponding contestant and empty submissions.
# Requires the "Contestants" group and all problems to be in the database.
# CSV format: contestant_id,first_name,last_name,email,username,password

class Command(BaseCommand):
    help = 'Register contestants from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', nargs=1, type=pathlib.Path)

    def handle(self, *args, **options):
        contestants_group = Group.objects.get(name='Contestants')

        with open(options['csv_path'][0], newline='') as csvfile:
            contestants_reader = csv.reader(csvfile)
            i = 0
            for row in contestants_reader:
                if User.objects.filter(username=row[4]).exists():
                    self.stderr.write(self.style.NOTICE(
                        f'A user under the username \'{row[4]}\' already exists.')
                    )
                    continue
                if Contestant.objects.filter(contestant_id=int(row[0])).exists():
                    self.stderr.write(self.style.NOTICE(
                        f'A contestant with ID \'{row[0]}\' already exists.')
                    )
                    continue
                # Create user and save it to the database
                user = User.objects.create_user(
                    username=row[4], email=row[3], password=row[5])
                # Add the new user to the "Contestants" group
                user.groups.add(contestants_group)
                # Set names of the new user
                user.first_name = row[1]
                user.last_name = row[2]
                user.save()
                # Create contestant and save it to the database
                cid = int(row[0])
                contestant = Contestant.objects.create(
                    contestant_id=cid,
                    contestant_user=user
                )
                # Create empty submissions and save them to the database
                for p in Problem.objects.all():
                    fallback_number = cid * 10 + p.number
                    Submission.objects.create(
                        contestant=contestant,
                        problem=p,
                        fallback_number=fallback_number
                    )
                i += 1
            self.stdout.write(self.style.SUCCESS(
                'Successfully registered %d contestants and created empty submissions for them.' % i)
            )
