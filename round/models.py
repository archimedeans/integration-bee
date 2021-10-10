from datetime import datetime
from hashlib import sha3_256
import struct
from django.db import models
from django.conf import settings
from django.core import validators
from django.utils.translation import gettext_lazy
from django.urls import reverse

# Create your models here.


class Contestant(models.Model):
    contestant_id = models.IntegerField(
        primary_key=True,
        editable=False,
        validators=[validators.MinValueValidator(200000),
                    validators.MaxValueValidator(999999)],
        verbose_name='Contestant ID',
    )
    contestant_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ['contestant_id']

    @property
    def first_name(self):
        if self.contestant_user:
            return self.contestant_user.first_name
        return ''

    @property
    def last_name(self):
        if self.contestant_user:
            return self.contestant_user.last_name
        return ''

    @property
    def fl_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.contestant_id} ({self.fl_name})'

    def get_absolute_url(self):
        return reverse('contestant_details', args=[str(self.contestant_id)])


class Problem(models.Model):
    number = models.IntegerField(
        primary_key=True,
        editable=False,
        validators=[validators.MinValueValidator(1),
                    validators.MaxValueValidator(4)],
    )
    prompt = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'Problem {self.number}'

    def get_absolute_url(self):
        return reverse('problem-details', args=[str(self.number)])


def contestant_problem_path(instance, filename):
    # del filename
    cid = instance.contestant.contestant_id
    m = sha3_256()
    m.update(instance.contestant.fl_name.encode('utf-8'))
    m.update(struct.pack('>f', datetime.now().timestamp()))
    m.update(struct.pack('>i', instance.contestant.contestant_id))
    # Return an obfuscated path relative to MEDIA_ROOT
    return f'uploads/{cid}/{instance.problem.number}/{m.hexdigest()}/{filename}'


class Submission(models.Model):
    contestant = models.ForeignKey(
        Contestant,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name='submissions',
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name='submissions',
    )
    # In case of contestant/problem deletion,
    # use contestant.contestant_id * 10 + problem.number as a fallback
    # Assumes problem.number < 10
    fallback_number = models.IntegerField(
        editable=False,
        validators=[validators.MinValueValidator(2000000),
                    validators.MaxValueValidator(9999999)],
    )
    solution = models.FileField(
        upload_to=contestant_problem_path,
        max_length=140,
    )
    submission_time = models.DateTimeField(
        null=True,
    )

    class Status(models.TextChoices):
        NOT_ATTEMPTED = 'DNA', gettext_lazy('Not Attempted')
        ATTEMPTED = 'ATT', gettext_lazy('Attempted')
        MARKED = 'MKD', gettext_lazy('Marked')

    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.NOT_ATTEMPTED,
    )

    class Meta:
        ordering = ['contestant', 'problem']
        permissions = [('submit_solutions', 'Can submit solutions'),
                       ('mark_solutions', 'Can mark solutions')]

    # def contestant_id(self):
    #     return self.contestant.contestant_id
    # contestant_id.short_description = 'Contestant ID'
    # contestant_id.admin_order_field = 'contestant_id'

    def __str__(self):
        if self.contestant is None or self.problem is None:
            return f'Submission (fallback number: {self.fallback_number})'
        return f'Submission for {self.problem} by {self.contestant.contestant_id}'
