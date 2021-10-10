import pathlib
from django.core.management.base import BaseCommand
from round.models import Problem


# For each contestant specified in a CSV file,
# creates a user, a corresponding contestant and empty submissions.
# CSV format: contestant_id,first_name,last_name,email,username,password

class Command(BaseCommand):
    help = 'Load a problem into the database'

    def add_arguments(self, parser):
        parser.add_argument('number', nargs=1, type=int)
        parser.add_argument('prompt_path', nargs=1, type=pathlib.Path)

    def handle(self, *args, **options):
        number = options['number'][0]
        problem, _ = Problem.objects.get_or_create(number=number)

        with open(options['prompt_path'][0], newline='') as f:
            problem.prompt = f.read()
            # ISSUE: What if the file is too large?

        problem.save()
            
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded Problem %d into the database.' % number)
        )
