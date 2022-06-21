from django.urls import path
from extra import views

urlpatterns = [
    path("help_screenshot/", views.help_screenshot, name="help_screenshot"),
    path("feedback_home/", views.feedback_home, name="feedback_home"),
    path("github_home/", views.github_home, name="github_home"),
    path("faq/", views.faq, name="faq"),
    path("links/", views.links, name="links"),
    path("tutorial/", views.tutorial, name="tutorial"),
    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),
    path("analytics/", views.analytics, name="analytics"),
]
