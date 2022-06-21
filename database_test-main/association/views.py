import re
from difflib import get_close_matches
import textwrap
from io import StringIO
from collections import OrderedDict

import requests
import pandas as pd
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

from database.models import UserUploadData
from association.forms import SearchForm
from association.admin import AssociationResource
from association.models import Association, IdenticalProteins
from database.filter_results import (
    Search,
    filter_one_name,
)
from database.models import PesticidalProteinDatabase
from association.forms import FeedbackProteinForm
from association.models import FeedbackProteinError, MutantProteinDatabase


def download_association(request):
    """Download specificity data (metdatabase). Added two options
    1) Download specificity data without sequence
    2) Download specificity data

    Linked href's are export_association and export_association_seq
    """
    return render(request, "association/download_specificity.html")


def export_association_seq(request):
    """Provides the Association data for the users to download.
    This is the same functionality from the admin export option.

    Related model Association from association
    The association resource is imported from association.admin

    Returns
    -------
    dataset csv file:
        Returns the csv file
    """
    association = AssociationResource()
    dataset = association.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="toxicity-data.csv"'
    return response


def export_association(request):
    """Provides the Association data for the users to download.
    This is the same functionality from the admin export option.
    The only difference is that sequence column is removed from the file.

    Related model Association from association
    The association resource is imported from association.admin

    Returns
    -------
    dataset csv file:
        Returns the csv file
    """
    association = AssociationResource()
    dataset = association.export()
    df = pd.read_csv(StringIO(dataset.csv), sep=",")
    del df['sequence']
    dataset = df.to_csv(encoding='utf-8', index=False)
    response = HttpResponse(dataset, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="toxicity-data.csv"'
    return response


def mutant_download(request):
    if request.method == "POST":
        file = StringIO()

        data = MutantProteinDatabase.objects.order_by("name").distinct()
        if data:
            for item in data:
                fasta = textwrap.fill(item.sequence, 80)
                str_to_write = f">{item.name}\n{fasta}\n"
                file.write(str_to_write)

        response = HttpResponse(file.getvalue(), content_type="text/plain")
        download_file = "mutant_fasta_sequences.txt"
        response["Content-Disposition"] = "attachment;filename=" + download_file
        response["Content-Length"] = file.tell()
        return response


def association_add_cart(request):
    """
    Add the search keywords to the cart.

    Search results provides list of proteins where user's have an option
    to select and add proteins to the cart.

    Add to cart uses 'request.session' to add the selected values.
    """

    if request.method == "POST":

        selected_values = request.POST.getlist("name", [])
        previously_selected_values = request.session.get("list_names", [])
        previously_selected_values.extend(selected_values)
        request.session["list_names"] = previously_selected_values

        selected_nterminal = request.POST.getlist("nterminal", [])
        previously_selected_nterminal = request.session.get(
            "list_nterminal", [])
        previously_selected_nterminal.extend(selected_nterminal)
        request.session["list_nterminal"] = previously_selected_nterminal

        selected_middle = request.POST.getlist("middle", [])
        previously_selected_middle = request.session.get("list_middle", [])
        previously_selected_middle.extend(selected_middle)
        request.session["list_middle"] = previously_selected_middle

        selected_cterminal = request.POST.getlist("cterminal", [])
        previously_selected_cterminal = request.session.get(
            "list_cterminal", [])
        previously_selected_cterminal.extend(selected_cterminal)
        request.session["list_cterminal"] = previously_selected_cterminal

        association_values = request.POST.getlist("activity_name", [])
        previously_selected_association = request.session.get(
            "list_activity_names", [])
        previously_selected_association.extend(association_values)
        request.session["list_activity_names"] = previously_selected_association

        mutant_values = request.POST.getlist("mutant_name", [])
        previously_selected_mutant = request.session.get(
            "list_mutant_names", [])
        previously_selected_mutant.extend(mutant_values)
        request.session["list_mutant_names"] = previously_selected_mutant

    return redirect("search_association")


def remove_cart_association(request, protein_id):
    """
    Remove the selected proteins one by one from the cart.
    Assume you have selected proteins in search page and
    if you view the cart page, there is a table that shows selected prteins.
    These proteins can be removed from the cart using the
    trash-can/delete icon.

    Args:
        database_id:
    """
    print("protein id", protein_id)
    protein = MutantProteinDatabase.objects.get(id=protein_id)

    selected_mutants = request.session.get(
        "list_mutant_names", [])

    print("before selected mutants", selected_mutants)

    selected_mutants.remove(protein.name)
    try:
        selected_mutants.remove(protein.name)
    except:
        pass

    print("after selected mutants", selected_mutants)

    request.session.modified = True

    return redirect("view_cart")


def mutant_proteins(request, protein_name=None):
    """ Filters a mutant protein from mutant database protein based
    on the input protein name.

    Parameters
    ----------
    arg: str
        Mutant protein name (e.g. Cry2Aa)

    Returns
    -------
    django model queryset:
        Filtered queryset of a protein based on the protein name
    """
    proteins = MutantProteinDatabase.objects.filter(
        name=protein_name)

    context = {
        "proteins": proteins,
    }

    return render(request, "association/mutant_proteins.html", context)


def metadatabase_protein_detail(request, name=None):
    """ Filters a protein from specificity metadatabase
    based on the input protein name.

    Parameters
    ----------
    arg: str
        protein name (e.g. Cry2Aa1)

    Returns
    -------
    django model queryset:
        Filtered queryset of a protein based on the protein name
        from association database
    """
    context = {
        "protein": Association.objects.filter(name=name),
    }

    return render(request, "association/metadatabase_protein_detail.html", context)


def _sorted_nicely(l, sort_key=None):
    """Sort the given iterable in the way that humans expect. https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""

    def convert(text):
        return int(text) if text.isdigit() else text

    if sort_key is None:

        def alphanum_key(key):
            return [convert(c) for c in re.split("([0-9]+)", key)]

    else:
        def alphanum_key(key):
            return [convert(c) for c in re.split("([0-9]+)", getattr(key, sort_key))]

    return sorted(l, key=alphanum_key)


def alphanumeric_sort(objects_list, sort_key):
    """ Sort a list of objects by a given key
    This function sort a list of objects by a given
    key common across the objects
    Sorting can be implemented on keys that are either
    alphabets, integers or both
    """
    def convert(text): return int(text) if text.isdigit() else text

    def alphanum_key(key): return [
        convert(c) for c in re.split("([0-9]+)", getattr(key, sort_key))
    ]
    return sorted(objects_list, key=alphanum_key)


def data_association_links(request):
    """This function is not used in the database"""
    context = {"items": Association.objects.all()}

    return render(request, "association/data_association_links.html", context)


def display_protein_data(request, name):
    """This function is not used in the database"""
    context = {"proteins": Association.objects.filter(name=name)}

    return render(request, "association/display_protein_data.html", context)


def example_content(request):
    """This function is not used in the database"""
    return render(request, "association/example_content.html")


def data_teams(request):
    """This function is not used in the database"""
    return render(request, "association/data_teams.html")


def search_association(request):
    """
    Ubound search form from association.forms

    Keywords may contain numbers, uppercase, lowercase.
    eg. Protein name: Cry1Aa1.

    Users can able to search against the following fields
    - Pesticidal Protein Name
    - Target species taxon id
    - Target Species
    - Target Order

    Returns
    -------
    Search form:
        See more details from the association.forms.py
    """
    items_in_cart = request.session.get("list_names", [])
    selected_association = request.session.get(
        "list_activity_name", [])
    selected_association = list(OrderedDict.fromkeys(selected_association))
    items_in_cart += selected_association
    items_in_cart = list(set(items_in_cart))

    dataids = UserUploadData.objects.filter(
        session_key=request.session.session_key).values_list(
        "id", flat=True
    )
    length_userdata = len(dataids)
    length_items_in_cart = len(items_in_cart)
    total_cart = length_userdata + length_items_in_cart

    form = SearchForm()
    return render(request, "association/search_page.html", {"form": form, "total_cart": total_cart, })


def list_proteins(request):
    """This function is not used in the database"""
    category_endswith1 = []

    categories = PesticidalProteinDatabase.objects.order_by(
        "name").values_list("name", flat=True).distinct()
    for category in categories:
        if category[-1] == "1" and not category[-2].isdigit():
            category_endswith1.append(category)

    proteins = _sorted_nicely(category_endswith1)

    context = {"proteins": proteins}

    return render(request, "association/list_proteins.html", context)


def search_data_association(request):
    """
    Filtering user search keywords. Returns the boolean
    value based on the search query. Keywords may contain numeric,
    uppercase, lowercase. eg. Protein name: Cry1Aa1.
    User can able to use keywords like following
    Cry10* -> wildcard search should work
    Cry -> should list all cry category
    Cry1 -> must not return Cry10. Only Cry1's.
    Cry10 -> must not return Cry1. Only Cry10's
    Cry10A -> must return all Cry10A i.e Cry10Aa to Cry10Az
    Cry10Aa -> must return all Cry10Aa i.e Cry10Aa1 to Cry10Aa100
    Cry10Aa1 -> must return only Cry10Aa1
    There is also an option to select the searches and add to cart
    using the checkboxes on the search page. With the help of
    anonymous session we can retrive the names
    in the 'search_database_home'.
    Parameters
    ----------
    arg:
        param1 (str) Keywords e.g. Cry. Single or multiple keywords
        separated by comma, or space or semicolon
        param1 (str) Search Feilds e.g. Name, Old Name, Accession, Holotype
        and Structure
    Returns
    -------
    Search form:
        Download all the holotype sequences
        See more details from the association.forms.py
        ("pesticidal protein name", "Pesticidal Protein Name"),
        ("target species taxon id", "Target species taxon id"),
        ("target species", "Target Species"),
        ("target order", "Target Order"),
    )
    """
    if request.method == "POST":
        form = SearchForm(request.POST)
        proteins = []
        single_digit = False
        if form.is_valid():
            query = form.cleaned_data["search_term"]
            field_type = form.cleaned_data["search_fields"]

            # searches = re.split(r':|, ?|\s |_ |. |; |\n', query)
            searches = re.split(r":|, ?|\s* |\n|;", query)

            if field_type == "pesticidal protein name":
                q_objects = Q()
                q_search = Q()
                q_objects1 = Q()
                for search in searches:
                    if Search(search).is_wildcard():
                        search = search[:-1]
                    elif search.lower() == 'axmi':
                        search = search[:-1]
                    else:
                        search = search
                    k = Search(search)
                    try:
                        if k.is_fullname():
                            q_objects.add(Q(name__iexact=search), Q.OR)
                        if k.is_uppercase():
                            q_objects.add(Q(name__icontains=search), Q.OR)
                        if k.is_lowercase():
                            q_objects.add(Q(name__icontains=search), Q.OR)
                        if k.is_single_digit():
                            single_digit = True
                            q_search.add(Q(name__icontains=search), Q.OR)
                        if k.is_double_digit():
                            q_objects.add(Q(name__icontains=search), Q.OR)
                        if k.is_triple_digit():
                            q_objects.add(Q(name__icontains=search), Q.OR)
                        if k.is_three_letter():
                            q_objects.add(Q(name__icontains=search), Q.OR)
                        if k.is_three_letter_case():
                            q_objects.add(Q(name__icontains=search), Q.OR)
                    except:
                        q_objects.add(Q(name__icontains=search), Q.OR)
                proteins1 = Association.objects.none()
                proteins2 = Association.objects.none()
                if q_objects:
                    proteins1 = Association.objects.filter(
                        q_objects).order_by('name')
                if q_search:
                    proteins2 = Association.objects.filter(
                        q_search).order_by('name')
                if proteins1 and proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = list(proteins1) + proteins2
                    # proteins = _sorted_nicely(proteins, sort_key="name")
                elif proteins1:
                    proteins = proteins1
                elif proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = proteins2

                for search in searches:
                    for protein in proteins:
                        q_objects1.add(Q(proteins__icontains=search), Q.OR)
                        identical_proteins = IdenticalProteins.objects.filter(
                            q_objects1)
                        for value in identical_proteins:
                            if protein.name in value.proteins:
                                protein.new_field = value.proteins

            elif field_type == "target species taxon id":
                q_objects = Q()
                q_objects1 = Q()
                for search in searches:
                    q_objects.add(Q(taxonid__icontains=search), Q.OR)

                proteins = Association.objects.filter(q_objects)
                proteins = _sorted_nicely(proteins, sort_key="name")

                for search in searches:
                    for protein in proteins:
                        q_objects1.add(Q(proteins__icontains=search), Q.OR)
                        identical_proteins = IdenticalProteins.objects.filter(
                            q_objects1)
                        for value in identical_proteins:
                            if protein.name in value.proteins:
                                protein.new_field = value.proteins

                if not proteins:
                    words_taxonid = list(
                        set(Association.objects.values_list("taxonid", flat=True)))
                    new_search = []

                    for search in searches:
                        new_search.append(get_close_matches(
                            search, words_taxonid, 1, 0.3))

                    context = {"new_search": new_search}
                    return render(
                        request,
                        "association/search_results.html",
                        context,
                    )

            elif field_type == "target species":
                q_objects = Q()
                for search in searches:
                    q_objects.add(Q(target_species__icontains=search), Q.OR)

                proteins = Association.objects.filter(q_objects)
                proteins = _sorted_nicely(proteins, sort_key="name")

                q_objects1 = Q()
                for search in searches:
                    for protein in proteins:
                        q_objects1.add(Q(proteins__icontains=search), Q.OR)
                        identical_proteins = IdenticalProteins.objects.filter(
                            q_objects1)
                        for value in identical_proteins:
                            if protein.name in value.proteins:
                                protein.new_field = value.proteins

                if not proteins:
                    species = list(
                        set(Association.objects.values_list("target_species", flat=True)))
                    words_target_species = [
                        i.split(" ", 1)[0] for i in species]
                    new_search = []

                    for search in searches:
                        new_search.append(get_close_matches(
                            search, words_target_species, 1, 0.3))
                    # new_search = [i.split(' ', 1)[0] for i in new_search]

                    context = {"new_search": new_search}
                    return render(
                        request,
                        "association/search_results.html",
                        context,
                    )

                proteins = Association.objects.filter(q_objects)
                proteins = _sorted_nicely(proteins, sort_key="name")

            elif field_type == "target order":
                q_objects = Q()
                for search in searches:
                    q_objects.add(Q(target_order__icontains=search), Q.OR)

                proteins = Association.objects.filter(q_objects)
                proteins = _sorted_nicely(proteins, sort_key="name")
                q_objects1 = Q()
                for search in searches:
                    for protein in proteins:
                        q_objects1.add(Q(proteins__icontains=search), Q.OR)
                        identical_proteins = IdenticalProteins.objects.filter(
                            q_objects1)
                        for value in identical_proteins:
                            if protein.name in value.proteins:
                                protein.new_field = value.proteins

                if not proteins:
                    words_target_order = list(
                        set(Association.objects.values_list("target_order", flat=True)))
                    new_search = []

                    for search in searches:
                        new_search.append(get_close_matches(
                            search, words_target_order, 1, 0.3))

                    context = {"new_search": new_search}
                    return render(
                        request,
                        "association/search_results.html",
                        context,
                    )

        proteins = alphanumeric_sort(proteins, sort_key="name")
        context = {
            "proteins": proteins,
            "searches": searches,
        }

        return render(
            request,
            "association/search_results.html",
            context,
        )
    return HttpResponseRedirect("/search_association/")


def keyword_confirm(request, name=None):
    """."""
    q_objects = Q()
    q_objects.add(Q(target_species__icontains=name), Q.OR)
    confirm_proteins = Association.objects.filter(q_objects)
    confirm_proteins = _sorted_nicely(confirm_proteins, sort_key="name")

    return render(
        request,
        "association/search_results.html",
        {"confirm_proteins": confirm_proteins},
    )


def home(request):
    # use 127.0.0.1:8000/api
    response = requests.get("http://ip-api.com/json/128.227.118.11")
    geodata = response.json()
    return render(request, "association/home_api.html", {"ip": geodata})


def heatmap_activity(request):
    return render(request, "association/heatmap_activity1.html")


def feedback_protein(request, protein_id=None):
    data = {'subject': protein_id}
    protein_name = Association.objects.get(pk=protein_id)
    form = FeedbackProteinForm()

    if request.method == "POST":
        form = FeedbackProteinForm(request.POST)
        if form.is_valid():
            name = request.POST.get("name")
            subject = request.POST.get("subject")
            email = request.POST.get("email")
            message = request.POST.get("message")
            feedback = FeedbackProteinError.objects.create(
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
        form = FeedbackProteinForm(initial=data)

    return render(request, "newwebpage/feedback.html", {"form": form, "protein_name": protein_name})
