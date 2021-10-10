from django.contrib import admin
from .models import Contestant, Problem, Submission

# Register your models here.


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0


@admin.register(Contestant)
class ContestantAdmin(admin.ModelAdmin):
    list_display = ('contestant_id', 'first_name', 'last_name')
    inlines = [SubmissionInline]


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('number',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'contestant', 'problem', 'submission_time')
    list_filter = ('problem',)
    readonly_fields = ('contestant', 'problem')
    fields = ('contestant', 'problem', 'solution', 'submission_time', 'status')
    # fieldsets = (...)
