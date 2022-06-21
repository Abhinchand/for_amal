from allauth.account import app_settings
from allauth.account.utils import complete_signup
from django.shortcuts import render
from extra.forms import FeedbackForm
from extra.models import Feedback, Links, FaqEditHeading


def analytics(request):
    """Help page for admin manipulations. FAQs page can be edited by admin"""
    return render(request, "extra/google-analytics.html")


def help(request):
    """Help page for admin manipulations. FAQs page can be edited by admin"""
    return render(request, "extra/help.html")


def help_screenshot(request):
    """Few screenshots images to help admins to see the
    avaialble functionality"""
    return render(request, "extra/screenshots.html")


def feedback_home(request):
    """Feedback page form as well as POST details in the same function"""
    form = FeedbackForm()

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = request.POST.get("name")
            subject = request.POST.get("subject")
            email = request.POST.get("email")
            message = request.POST.get("message")
            feedback = Feedback.objects.create(
                name=name, subject=subject, email=email, message=message)

            context = {
                "name": name,
                "subject": subject,
                "message": message,
                "email": email,
            }
            return render(
                request,
                "newwebpage/feedback.html",
                {"context": context},
            )
        else:
            return render(request, "newwebpage/feedback.html", {"form": form})

    else:
        form = FeedbackForm()

    return render(request, "newwebpage/feedback.html", {"form": form})


def github_home(request):
    """Returns the page for bpprc developers github link"""
    return render(request, "newwebpage/github.html")


def privacy_policy(request):
    """privacy policy. Not used yet in the project"""
    return render(request, "extra/privacy-policy.html")


def page_not_found(request, exception):
    """Return 404 error page. For live server only"""
    return render(request, "extra/404.html", status=404)


def server_error(request):
    """Return server error. For live server only"""
    return render(request, "extra/500.html", status=500)


# def signup(request):
#     if request.method == "POST":
#         form = UserCreateForm(request.POST)
#         if form.is_valid():
#             user = form.save(request)
#             # Added this!
#             complete_signup(
#                 request, user, app_settings.EMAIL_VERIFICATION, "/")


def links(request):
    """Link page provides (https://camtech-bpp.ifas.ufl.edu/links/)
    list of external links in the database page.
    Only admin users can edit/add the pages in the Links model

    example data
    >>> data = {'name': 'hello',
                'description': 'An online database showing the activity of
                selected pesticidal proteins against a range of insects
                and highlighting antagonisitc and synergistic interactions
                between them',
               'link': 'http://150.254.120.147:7000/',}
    """

    # order by name
    context = {"links": Links.objects.order_by("name")}

    return render(request, "newwebpage/links.html", context)


def faq(request):
    """FAQs provides list of FAQs with different type of headers.
    Each headers, questions, and answers can be updated only by
    admin users.
    """
    # Distinct objects ordered by headers (category)
    categories = FaqEditHeading.objects.all().distinct().order_by('category')

    context = {
        "categories": categories,
    }

    return render(request, "newwebpage/faqedit.html", context)


def tutorial(request):
    """YouTube tutorial page is linked here"""
    return render(request, "newwebpage/tutorial.html")
