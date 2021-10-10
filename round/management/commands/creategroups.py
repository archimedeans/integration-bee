from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates groups and sets permissions'

    def handle(self, *args, **options):
        contestants_group, created = Group.objects.get_or_create(
            name='Contestants')
        contestants_group.permissions.set(
            [Permission.objects.get(codename='submit_solutions')]
        )
        contestants_group.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                'Successfully created group "Contestants" and set its permissions to "submit_solutions" only.'))
        else:
            self.stdout.write(self.style.WARNING(
                'The "Contestants" group already exists.'
            ))
            self.stdout.write(self.style.SUCCESS(
                'Successfully set its permissions to "submit_solutions" only.'))

        markers_group, created = Group.objects.get_or_create(
            name='Markers')
        markers_group.permissions.set(
            [Permission.objects.get(codename='mark_solutions')]
        )
        markers_group.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                'Successfully created group "Markers" and set its permissions to "view_contestant" only.'))
        else:
            self.stdout.write(self.style.WARNING(
                'The "Markers" group already exists.'
            ))
            self.stdout.write(self.style.SUCCESS(
                'Successfully set its permissions to "view_contestant" only.'))
