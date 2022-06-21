"""Predicts the name for the submitted pesticidal proteins ."""


import tempfile
import textwrap
from celery import current_app
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render

from database.models import (
    PesticidalProteinDatabase,
    PesticidalProteinPrivateDatabase,
)
from naming_package import run_data
from namingalgorithm.models import UserSubmission
from .forms import SendEmailForm, UserSubmissionForm
from namingalgorithm.tasks import namingalgorithm_task


def is_admin(user):
    """Check the user is admin staff."""
    return user.is_staff


@user_passes_test(is_admin)
def naming_algorithm(request):
    """If the user is admin staff, show the naming html page."""
    return render(request, "newwebpage/naming_home.html")


# @login_required
def submit_home(request):
    context = {
        "form": UserSubmissionForm,
    }
    return render(request, "newwebpage/submit.html", context)


def submit(request):
    """Submit the sequence for the naming purpose through user form."""
    if request.method == "POST":
        form = UserSubmissionForm(request.POST)
        # formset = ToxicToFormSet(request.POST)
        # print(form)
        if form.is_valid():
            # print("formset", formset)
            form.save()

            return render(request, "newwebpage/view.html", {"form": form})
        # else:
        #     print(form.errors)
        #     print("Error in form")
        # print("formset", formset)
    else:
        form = UserSubmissionForm()
    #     formset = ToxicToFormSet()
    # helper = ToxicFormSetHelper()

    return render(request, "newwebpage/submit.html", {"form": form})


# @login_required
# def submit(request):
#     """Submit the sequence for the naming purpose through user form."""
#     if request.method == "POST":
#         form = UserSubmissionForm(request.POST)
# formset = ToxicToFormSet(request.POST)
# if form.is_valid():
# form.instance.submittersname = request.user
# form.instance.submittersemail = request.email
# print("formset", formset)
#     form.save()
#
#     return render(
#         request, "newwebpage/view.html", {"form": form}
#     )
# else:
#     print(form.errors)
#     print("Error in form")

# else:
#     form = UserSubmissionForm(
#         initial={
#             "submittersname": request.user,
#             "submittersemail": request.user.email,
#         }
#     )
#     formset = ToxicToFormSet()
# helper = ToxicFormSetHelper()

# return render(request, "newwebpage/submit.html", {"form": form})


def run_align(request):
    """Submit the sequence for the naming purpose."""
    data = request.GET.get("fulltextarea")
    format_data = textwrap.fill(data, 80)
    tmp_seq = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
    with open(tmp_seq.name, "wb") as temp:
        temp.write(format_data.encode())
        tmp_seq.close()

    align = run_data.run_naming_algorithm.run_bug(tmp_seq.name)
    user_submission = UserSubmission.objects.get(
        id=request.GET.get("submission_id"))
    user_submission.alignresults = align
    # print("user submission", user_submission)
    user_submission.save()
    return HttpResponseRedirect("/admin/namingalgorithm/usersubmission/")


def align_results(request):
    """Submit the sequence for the naming purpose."""
    submission_id = request.GET.get("submission_id")
    submission = UserSubmission.objects.get(id=submission_id)
    align = submission.alignresults
    context = {"align": align}
    return render(request, "newwebpage/needle.html", context)


def run_naming_algorithm(request):
    """Submit the sequence for the naming purpose."""
    data = request.GET.get("fulltextarea")
    format_data = textwrap.fill(data, 80)
    tmp_seq = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
    with open(tmp_seq.name, "wb") as temp:
        temp.write(format_data.encode())
        tmp_seq.close()

    align, predicted_name = run_data.predict_name.run_bug(tmp_seq.name)
    # predicted_name = "App1Aa2"

    # (
    #     align,
    #     percentageidentity,
    #     category,
    #     predicted_name,
    #     name,
    # ) = run_data.predict_name.run_bug(tmp_seq.name)
    user_submission = UserSubmission.objects.get(
        id=request.GET.get("submission_id"))
    print("user submission", user_submission)
    user_submission.predict_name = predicted_name
    user_submission.save()

    context = {
        "predicted_name": predicted_name,
        "align": align,
    }
    return render(request, "newwebpage/admin_needle.html", context)


def _trigger_email_everyday(submittersname, submittersemail, accession, message):
    recipient_list = []
    recipient_list.append(submittersemail)
    send_mail(
        subject=accession,
        message=message,
        from_email="admin@bpprc.org",
        recipient_list=recipient_list,
        fail_silently=False,
    )


def contact_email(request):
    if request.method == "GET":
        form = SendEmailForm(initial=request.GET.dict())
    else:
        form = SendEmailForm(request.POST)
        if form.is_valid():
            submittersname = form.cleaned_data["submittersname"]
            submittersemail = form.cleaned_data["submittersemail"]
            accession = form.cleaned_data["accession"]
            message = form.cleaned_data["message"]
            try:
                _trigger_email_everyday(
                    submittersname, submittersemail, accession, message)
                form.save()
            except:
                return HttpResponse("Invalid header found.")

            context = {
                "submittersname": submittersname,
                "submittersemail": submittersemail,
            }
            return render(request, "newwebpage/email_success.html", context)
    return render(request, "newwebpage/email.html", {"form": form})


def success_email(request):
    return HttpResponse("Success! Your message sent. See SendEmail for the list of emails")


# def cloneUserSubmission(request):
#     id = request.GET['id']
#     model = request.GET['model']
#     instance = UserSubmission.objects.get(id=id)
#     created_model = None
#
#     if model == 'private':
#         try:
#             created_model = PesticidalProteinPrivateDatabase.objects.create(
#                 submittersname=instance.submittersname,
#                 submittersemail=instance.submittersemail,
#                 name=instance.name,
#                 sequence=instance.sequence,
#                 bacterium=instance.bacterium,
#                 bacterium_textbox=instance.bacterium_textbox,
#                 taxonid=instance.taxonid,
#                 year=instance.year,
#                 accession=instance.accession,
#                 partnerprotein=instance.partnerprotein,
#                 partnerprotein_textbox=instance.partnerprotein_textbox,
#                 toxicto=instance.toxicto,
#                 nontoxic=instance.nontoxic,
#                 dnasequence=instance.dnasequence,
#                 pdbcode=instance.pdbcode,
#                 publication=instance.publication,
#                 comment=instance.comment,
#                 admin_comments=instance.admin_comments,
#             )
#         except psycopg2.errors.NotNullViolation:
#             return HttpResponse("Name cannot be empty", status=400)
#     else:
#         created_model = PesticidalProteinDatabase.objects.create(
#             submittersname=instance.submittersname,
#             submittersemail=instance.submittersemail,
#             name=instance.name,
#             sequence=instance.sequence,
#             bacterium=instance.bacterium,
#             bacterium_textbox=instance.bacterium_textbox,
#             taxonid=instance.taxonid,
#             year=instance.year,
#             accession=instance.accession,
#             partnerprotein=instance.partnerprotein,
#             partnerprotein_textbox=instance.partnerprotein_textbox,
#             toxicto=instance.toxicto,
#             nontoxic=instance.nontoxic,
#             dnasequence=instance.dnasequence,
#             pdbcode=instance.pdbcode,
#             publication=instance.publication,
#             comment=instance.comment,
#             admin_comments=instance.admin_comments,
#         )
#
#     return HttpResponse(created_model.id)
def run_naming_algorithm_celery(request):
    filename = request.GET.get("name")
    print("running this function naming algorith celery")
    context = {}
    # tmp_seq = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
    task = namingalgorithm_task.delay(filename)
    print("filename..", filename)
    # print('view task result', task)

    context["task_id"] = task.id
    context["task_status"] = task.status
    context["task"] = task.info

    return render(request, "newwebpage/admin_needle_processing.html", context)


def taskstatus_naming_celery(request, task_id):

    if request.method == "GET":
        print("entering the function naming algorith taskstatus")
        task = current_app.AsyncResult(task_id)
        # print("taskStatus", task)
        context = {
            "task_status": task.status,
            "task_id": task.id,
            "task": task,
        }

        if task.status == "SUCCESS":
            # percentageidentity = task.get("percentageidentity")
            # predicted_name = task.get("predicted_name")
            # name = task.get("name")
            align = task.get("align")
            # predicted_name = task.get("predicted_name")
            # print("predicted name", predicted_name)
            # user_submission = UserSubmission.objects.get(
            #     id=request.GET.get("submission_id"))
            # print("user submission", user_submission)
            # user_submission.predict_name = "App1Aa2"
            # user_submission.save()
            context = {
                "align": align,
                "predicted_name": "App1Aa2"
            }
            # context["predicted_name"] = task.get("predicted_name")
            # context["percentageidentity"] = task.get("percentageidentity")
            # print("predicted_name", context["predicted_name"])
            return render(request, "newwebpage/admin_needle.html", context)

        elif task.status == "PENDING":
            context["results"] = task
            return render(request, "newwebpage/admin_needle_processing.html", context)

        context["error"] = task
        # print(task)
        return render(request, "newwebpage/admin_needle_processing.html", context)
