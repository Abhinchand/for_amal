from django.urls import path

from namingalgorithm import views

urlpatterns = [
    # path('', views.send_mail, name='sendmail'),
    path("run_naming_algorithm_celery/", views.run_naming_algorithm_celery,
         name="run_naming_algorithm_celery"),
    path("taskstatus_naming_celery/<str:task_id>/", views.taskstatus_naming_celery,
         name="taskstatus_naming_celery"),
    path("admin/contact/", views.contact_email, name="contact"),
    path("admin/success/", views.success_email, name="success"),
    path("submit_home/", views.submit_home, name="submit_home"),
    path("submit/", views.submit, name="submit"),
    path(
        "naming_algorithm/",
        views.naming_algorithm,
        name="naming_algorithm",
    ),
    path(
        "run_naming_algorithm/",
        views.run_naming_algorithm,
        name="run_naming_algorithm",
    ),
    path("run_align/", views.run_align, name="run_align"),
    path("align_results/", views.align_results, name="align_results"),
    # path('clone_user_submission/', views.cloneUserSubmission,
    #      name='clone_user_submission')
]
