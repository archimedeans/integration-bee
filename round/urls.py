from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('countdown-json', views.countdown_json, name='countdown_json'),
    path('submission-not-open/', views.submission_not_open, name='submission_not_open'),
    path('problems/', views.ProblemListView.as_view(), name='problems'),
    path('submission/', views.SubmissionSummaryView.as_view(), name='submission_summary'),
    path('submit/<int:problem_number>/', views.submit_sol_for_problem, name='submit_sol_for_problem'),
    path('submission-statistics/', views.submission_statistics, name='submission_statistics'),
    path('contestants/', views.ContestantListView.as_view(), name='contestants'),
    path('contestant/<int:pk>', views.ContestantDetailView.as_view(), name='contestant_details'),
    path('contact-us', views.contact_us, name='contact_form'),
    # can also use regular expression, see
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views#URL_mapping_2
]
