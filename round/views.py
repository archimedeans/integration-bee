from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse  # HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView

from .forms import SubmitForProblemForm, ContactForm
from .models import Contestant, Problem, Submission
from . import time_status, webhooks

# Create your views here.


def index(request):
    """View function for home page of site."""
    if request.user.is_authenticated:
        return render(request, 'round/index.html')

    return render(request, 'landing.html')


def countdown_json(request):
    """Handles a request for the amount time of left."""
    time_left = time_status.get_millisec_time_until_start()
    if time_left > 0:
        description = 'until Round Two starts'
        enable = True
    else:
        time_left = time_status.get_millisec_time_until_end()
        if time_left > 0:
            description = 'until Round Two ends'
            enable = True
        else:
            time_left = -1
            round_status = time_status.get_round_status()
            if round_status == time_status.RoundStatus.EXTRA_SUBMISSION_TIME:
                description = 'Submission will close soon'
            elif round_status == time_status.RoundStatus.EMBARGO_IN_PLACE:
                description = 'The embargo is still in place'
            else:
                description = 'Round Two has ended'
            enable = False
    return JsonResponse({
        'timeLeft': time_left,
        'enable': enable,
        'description': description
    })
    # return HttpResponse('%d' % time_status.get_millisec_time(), content_type='text/plain')


class ContestantListView(PermissionRequiredMixin, ListView):
    model = Contestant
    permission_required = 'round.mark_solutions'
    paginate_by = 10
    # for more customisations such as template variable name, more context data
    # https://docs.djangoproject.com/en/3.1/topics/class-based-views/generic-display/
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views#View_class-based
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views#Views


class ContestantDetailView(PermissionRequiredMixin, DetailView):
    model = Contestant
    permission_required = 'round.mark_solutions'


class ProblemListView(LoginRequiredMixin, ListView):
    model = Problem

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reveal'] = time_status.round_has_started()
        return context


class SubmissionSummaryView(PermissionRequiredMixin, ListView):
    model = Submission
    permission_required = 'round.submit_solutions'
    template_name = 'round/submission_summary.html'

    # Alternatively, with UserPassesTestMixin
    # def test_func(self):
    #     return self.request.user.groups.filter(name='Participants').exists()

    def get_queryset(self):
        # ISSUE: What if the user has not been associated with a Contestant object?
        return self.request.user.contestant.submissions.order_by('problem__number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission_open'] = time_status.submission_is_open()
        return context


@login_required
@permission_required('round.submit_solutions', raise_exception=True)
def submit_sol_for_problem(request, problem_number):
    submission = get_object_or_404(
        Submission,
        contestant__contestant_user=request.user,
        problem__number=problem_number
    )

    if not time_status.submission_is_open():
        return HttpResponseRedirect(reverse('submission_not_open'))

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        submission_time = time_status.get_datetime()

        # Create a form instance and populate it with data from the request (binding):
        form = SubmitForProblemForm(request.POST, request.FILES)

        # Check if the form is valid:
        if form.is_valid():
            # submission.solution = form.cleaned_data['solution']
            submission.solution.delete(save=False)
            submission.solution = request.FILES['solution']
            submission.status = Submission.Status.ATTEMPTED
            submission.submission_time = submission_time
            submission.save()

            # ISSUE: What if submitted after being marked

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('submission_summary'))

    # If this is a GET (or any other method) create the default form.
    else:
        form = SubmitForProblemForm()
        # form = SubmitForProblemForm(initial={
        #     'solution': submission.solution,
        # })

    context = {
        'form': form,
        'submission': submission,
    }

    return render(request, 'round/submit_sol_for_problem.html', context)


def submission_not_open(request):
    return render(request, 'round/submission_not_open.html')


def submission_statistics(request):
    """View function for the submission statistics page."""

    # Generate counts of some of the main objects
    num_contestants = Contestant.objects.exclude(
        contestant_id__lte=200009).count()
    attempts = Submission.objects.exclude(
        status=Submission.Status.NOT_ATTEMPTED
    ).exclude(
        contestant__contestant_id__lte=200009
    )
    num_attempts = [(p, attempts.filter(problem__number=p).count())
                    for p in range(1, 5)]  # hard-coded for speed

    context = {
        'num_contestants': num_contestants,
        'num_attempts': num_attempts,
    }

    # Render the HTML template submission_statistics.html with the data in the context variable
    return render(request, 'round/submission_statistics.html', context=context)


@login_required
def contact_us(request):
    """View function for the contact form page."""

    could_not_send = False

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            # ISSUE: hard-coded at two places (the other is round/forms.py)
            subject_choices = {
                'paper': 'Contest paper',
                'website': 'Website',
                'other': 'Other'
            }

            user_is_contestant = Contestant.objects.filter(contestant_user=request.user).exists()
            if user_is_contestant:
                contestant = request.user.contestant
                author = f'{contestant.fl_name} ({contestant.contestant_id})'
            else:
                author = f'{request.user.first_name} {request.user.last_name}'
            email = form.cleaned_data['email']
            subject = subject_choices[form.cleaned_data['subject']]
            webhook_message = f'Subject: **{subject}**\nReply at: {email}\n\n' + \
                '> ' + form.cleaned_data['message'].replace('\n', '\n> ')

            could_not_send = not webhooks.send_message(author, webhook_message)

            if not could_not_send:
                return render(request, 'round/contact_form_sent.html')

    else:
        form = ContactForm(initial={
            'email': request.user.email,
        })

    context = {
        'form': form,
        'could_not_send': could_not_send,
    }

    return render(request, 'round/contact_form.html', context)
