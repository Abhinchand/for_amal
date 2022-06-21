
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource,
    LassoSelectTool,
    WheelZoomTool,
)
from bokeh.palettes import Category20
from bokeh.plotting import figure
from celery import current_app
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from clustalanalysis.forms import (
    AnalysisForm,
    DendogramForm,
    UserDataForm,
)
from clustalanalysis.models import StoreResultFiles
from clustalanalysis.tasks import create_tree
from database.models import (
    Description,
    PesticidalProteinDatabase,
    UserUploadData,
)


def domain_analysis_homepage(request):
    """This loads the bestmatchfinder homepage."""
    form = AnalysisForm()
    context = {
        "form": form,
        "userform": UserDataForm(),
        "descriptions": Description.objects.order_by("name"),
    }
    return render(request, "newwebpage/dendogram_homepage.html", context)


def domain_analysis(request):
    form = AnalysisForm()
    if request.method == "POST":
        post_values = request.POST.copy()
        post_values["session_list_names"] = request.session.get(
            "list_names", [])
        post_values["session_list_nterminal"] = request.session.get(
            "list_nterminal", [])
        post_values["session_list_middle"] = request.session.get(
            "list_middle", [])
        post_values["session_list_cterminal"] = request.session.get(
            "list_cterminal", [])
        post_values["list_activity_names"] = request.session.get(
            "list_activity_names", [])

        userdataids = UserUploadData.objects.filter(
            session_key=request.session.session_key).values_list(
            "id", flat=True
        )

        post_values["userdataids"] = ",".join(str(id) for id in userdataids)

        form = AnalysisForm(post_values, request=request)
        userform = UserDataForm()

        if form.is_valid():
            print("form is valid")
            userdataids = form.cleaned_data["userdataids"]

            context = {}
            inputfile, outputfile, numlines = form.save()
            # print("inputfile", inputfile)
            # print("outputfile", outputfile)

            task = create_tree.delay(inputfile, outputfile)
            #
            context["task_id"] = task.id
            context["task_status"] = task.status
            context["userform"] = userform
            context["analysisform"] = form
            # context['numlines'] = numlines

            return render(
                request,
                "newwebpage/clustal_processing.html",
                context,
            )
        else:
            print(form.errors)
            return render(
                request,
                "newwebpage/search_user_data_update.html",
                {
                    "form": form.errors,
                    "userform": userform,
                    "analysisform": form,
                },
            )

    return render(
        request,
        "newwebpage/search_user_data_update.html",
        {"form": form, "userform": userform, "analysisform": userform},
    )


def dendogram_homepage2(request):
    """This loads the bestmatchfinder homepage."""
    form = DendogramForm()
    context = {
        "form": form,
        "descriptions": Description.objects.order_by("name"),
    }
    return render(request, "newwebpage/dendogram_homepage.html", context)


def dendogram_homepage(request):
    """This loads the bestmatchfinder homepage."""
    form = DendogramForm()
    return render(
        request,
        "newwebpage/domain_cry_tree_d3js.html",
        {"form": form},
    )


def dendogram(request):
    form = DendogramForm()
    if request.method == "POST":
        form = DendogramForm(request.POST)
        if form.is_valid():

            rooted_tree = form.save()

            context = {
                "tree": rooted_tree,
            }
            return render(request, "newwebpage/dendogram.html", context)

        context = {"form": form}
        return render(request, "newwebpage/dendogram.html", context)

    return HttpResponseRedirect("/dendogram_homepage/")


def dendogram_celery(request):
    form = DendogramForm()
    print("dendogram celery is running")
    if request.method == "POST":
        form = DendogramForm(request.POST)
        if form.is_valid():
            context = {}
            input_file, output_file = form.save()

            task = create_tree.delay(input_file, output_file)

            context["task_id"] = task.id
            context["task_status"] = task.status
            context["numlines"] = form.numlines
            # context['radius'] = radius

            # print("outputfile", newlines)
            # print("radius", radius)

            return render(
                request,
                "newwebpage/clustal_processing.html",
                context,
            )

        return render(
            request,
            "newwebpage/dendogram_homepage.html",
            {"form": form},
        )

    return HttpResponseRedirect("/dendogram_homepage2/")


def taskstatus_clustal_celery(request, task_id):

    if request.method == "GET":
        # print("entering the function taskstatus")
        task = current_app.AsyncResult(task_id)
        # print("taskStatus", newlines)
        context = {
            "task_status": task.status,
            "task_id": task.id,
            "task": task,
        }

        if task.status == "SUCCESS":
            (
                context["file"],
                created,
            ) = StoreResultFiles.objects.get_or_create(taskid=task.id, tempfile=task.get())
            # context['file'] = StoreResultFiles.objects.filter(taskid=task.id)
            # context['align'] = task.get()
            return render(request, "newwebpage/dendogram.html", context)

        elif task.status == "PENDING":
            # context['results'] = task
            return render(request, "newwebpage/dendogram.html", context)
        else:
            return render(request, "newwebpage/dendogram.html", context)
    else:
        return render(request, "newwebpage/dendogram.html", context)


def celery_task_status_clustal(request, task_id):

    # print("entering the function taskstatus")
    task = current_app.AsyncResult(task_id)
    # print("taskStatus", task)
    context = {"task_status": task.status, "task_id": task.id}
    return JsonResponse(context)


def protein_analysis(request):

    categories = (
        PesticidalProteinDatabase.objects.order_by(
            "name").values_list("name", flat=True).distinct()
    )  # why you need flat=True

    category_prefixes = []
    for category in categories:
        prefix = category[:3]
        if prefix not in category_prefixes:
            category_prefixes.append(prefix)

    dict_fasta_category = {}
    dict_histo_category = {}
    for category in category_prefixes:
        fasta = ""
        k = PesticidalProteinDatabase.objects.filter(
            name__istartswith=category)
        for s in k:
            fasta += s.fastasequence
        dict_fasta_category[category] = fasta

    for key, value in dict_fasta_category.items():
        x = ProteinAnalysis(value)
        k = x.get_amino_acids_percent()
        dict_m = {}
        for i in k:
            dict_m[i] = round(k[i], 2)
        dict_histo_category[key] = dict_m

    keys, values = zip(*dict_histo_category.items())

    language = list(keys)
    counts = list(values)

    for f, b in zip(language, counts):
        print(type(f))

    p = figure(
        x_range=language,
        plot_height=1000,
        plot_width=1000,
        toolbar_location="below",
        tools="pan, wheel_zoom, box_zoom, reset, hover, tap, crosshair",
    )

    source = ColumnDataSource(
        data=dict(language=language, counts=counts, color=Category20[20]))
    p.add_tools(LassoSelectTool())
    p.add_tools(WheelZoomTool())

    p.vbar(
        x="language",
        top="counts",
        width=0.8,
        color="color",
        legend_group="language",
        source=source,
    )
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"
    p.y_range.start = 0

    script, div = components(p)

    context = {"script": script, "div": div}

    return render(request, "clustalanalysis/protein_analysis.html", context)
