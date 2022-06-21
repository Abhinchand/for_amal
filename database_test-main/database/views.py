"""Pesticidal Protein Database related view functions."""


import json
import re
import textwrap
from io import StringIO

from clustalanalysis.forms import AnalysisForm, UserDataForm
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from rich.console import Console
from database.extract_ncbi import _ncbi_domain_extract
from collections import OrderedDict

from database.admin import (
    OldnameNewnameTableLeftResource,
    OldnameNewnameTableRightResource,
)
from association.models import IdenticalProteins, MutantProteinDatabase
from association.forms import DownloadMutantForm
from database.filter_results import Search, filter_one_name
from database.forms import (
    DownloadForm,
    HolotypeForm,
    SearchForm,
    ThreedomainDownloadForm,
)
from database.models import (
    Description,
    OldnameNewnameTableLeft,
    OldnameNewnameTableRight,
    PesticidalProteinDatabase,
    PesticidalProteinPrivateDatabase,
    ProteinDetail,
    StructureDatabase,
    UserUploadData,
)

console = Console()


def cite(request):
    # return render(request, 'database/about_page.html')
    return render(request, "newwebpage/about.html")


def funding(request):
    # return render(request, 'database/about_page.html')
    return render(request, "newwebpage/about.html")


def about(request):
    # return render(request, 'database/about_page.html')
    return render(request, "newwebpage/about.html")


def home(request):
    # return render(request, 'database/about_page.html')
    return render(request, "newwebpage/about.html")


def homepage(request):
    # return render(request, 'database/about_page.html')
    return render(request, "newwebpage/about.html")


def about_page(request):
    return render(request, "database/about_page.html")


def about_protein(request, category=None):
    """Categorize the protein database with unqiue and first three letter pattern.

    Filters the protein based on these categories from public database as well as from private database

    Parameters
    ----------
    arg: str
        First three letter protein structural class (e.g. Cry)

    Returns
    -------
    django model queryset:
        Filtered list of proteins based on the three letter protein
        structural class
    django model queryset:
        Three letter descriptions for the category
    """
    # Public database filtered to display list of proteins based on the pattern
    protein = PesticidalProteinDatabase.objects.filter(
        name__istartswith=category)
    # Private database filtered to display list of proteins based on the pattern
    private = PesticidalProteinPrivateDatabase.objects.filter(
        name__istartswith=category)

    # Combine the list to show in a single table
    protein_list = list(protein) + list(private)

    # Protein names contains numbers, uppercase, and lowercase
    proteins = _sorted_nicely(protein_list, sort_key="name")

    # Category description explanation to display on the html
    # Based on the three letter pattern
    descriptions = Description.objects.filter(
        name__istartswith=category).order_by("name")

    context = {
        "proteins": proteins,
        "descriptions": descriptions,
    }
    return render(request, "list_protein.html", context)


def statistics(request):
    """
    Return the number of categories in the database
    and its corresponding count.

    Holotype is a protein name ends in 1. Example: Cry1Aa1
    A holotype is a single protein name used to name the lower rank based on identity. Cry1Aa2 is named based on the identity to Cry1Aa1
    """
    category_count = {}
    category_holotype_count = {}
    category_prefixes = []
    total_holotype = 0

    categories = PesticidalProteinDatabase.objects.order_by(
        "name").values_list("name", flat=True).distinct()

    for category in categories:
        cat = category[:3]
        if category[-1] == "1" and not category[-2].isdigit():
            total_holotype += 1
            count = category_holotype_count.get(cat, 0)
            count += 1
            category_holotype_count[cat] = count

    category_count["Holotype"] = [total_holotype] * 2

    for category in categories:
        prefix = category[0:3]
        if prefix not in category_prefixes:
            category_prefixes.append(prefix)

    for category in category_prefixes:
        count = PesticidalProteinDatabase.objects.filter(
            name__istartswith=category).count()
        category_count[category] = [
            count,
            category_holotype_count.get(category, 0),
        ]

    prefix_count_dictionary = {}
    for prefix in category_prefixes:
        prefix_count_dictionary[prefix] = category_count[prefix][0]

    prefix_count_dictionary.pop("Holotype", None)

    context = {
        "category_prefixes": category_prefixes,
        "category_count": category_count,
    }

    return render(request, "newwebpage/statistics.html", context)


def _sorted_nicely(l, sort_key=None):
    """
    Sort the given iterable in the way that humans expect.

    """

    # https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    def convert(text):
        return int(text) if text.isdigit() else text

    if sort_key is None:

        def alphanum_key(key):
            return [convert(c) for c in re.split("([0-9]+)", key)]

    else:

        def alphanum_key(key):
            return [convert(c) for c in re.split("([0-9]+)", getattr(key, sort_key))]

    return sorted(l, key=alphanum_key)


def categorize_database(request, category=None):
    """Categorize the protein database with unqiue and first three letter pattern. Filters the protein based on these categories from public database as well as from private database

    Parameters
    ----------
    arg: str
        First three letter structural class (e.g. App)

    Returns
    -------
    django model queryset:
        Filtered list of proteins based on the three letter
        protein structural class
    django model queryset:
        Three letter descriptions for the category
    """

    # Public database filtered to display list of proteins based on the pattern
    protein = PesticidalProteinDatabase.objects.filter(
        name__istartswith=category)
    # Private database filtered to display list of proteins based on the pattern
    private = PesticidalProteinPrivateDatabase.objects.filter(
        name__istartswith=category)
    # Combine the list to show in a single table
    protein_list = list(protein) + list(private)

    # Protein names contains numbers, uppercase, and lowercase
    proteins = _sorted_nicely(protein_list, sort_key="name")

    # Have to display checkboxes for Cry three domain proteins in html table
    # Users will chose the desired Cry domains (N-terminal, Middle domain and  C-terminal)
    # Other proteins don't have three domains and don't need that checkboxes
    show_extra_data = False
    cry_count = 0
    for protein in proteins:
        if protein.name.startswith("Cry"):
            cry_count += 1
            protein.show_extra_data = True
    if cry_count == len(proteins):
        show_extra_data = True

    # Category description explanation to display on the html
    # Based on the three letter pattern
    descriptions = Description.objects.filter(
        name__istartswith=category).order_by("name")

    context = {
        "proteins": proteins,
        "show_extra_data": show_extra_data,
        "descriptions": descriptions,
    }
    return render(request, "newwebpage/category_display.html", context)


def database(request):
    """
    The idea here is to list the three letter categories
    along with the checkboxes. The user can select
    the desired category and click the download button.

    Returns
    -------
    django model queryset:
        Filtered list of proteins based on the three letter
        protein structural class
    django model queryset:
        Descriptions of the three letter structural class
    django form1:
        Download all other protein sequences based on three letter pattern
    django form2:
        Download all the 3-domain sequences (i.e. Cry)
    django form3:
        Download all the holotype sequences
        See more details from the database.forms.py
    """

    # Filter distinct proteins by name
    categories = PesticidalProteinDatabase.objects.order_by(
        "name").values_list("name").distinct()
    category_prefixes = []
    # Categories the filtered results based on the three letter pattern
    for category in categories:
        prefix = category[0][:3]
        if prefix not in category_prefixes:
            category_prefixes.append(prefix)

    form1 = DownloadForm()
    form2 = ThreedomainDownloadForm()
    form3 = HolotypeForm()

    context = {
        "category_prefixes": category_prefixes,
        "descriptions": Description.objects.all(),
        "form1": form1,
        "form2": form2,
        "form3": form3,
    }
    return render(request, "newwebpage/database.html", context)


def search_database_home(request):
    """

    Parameters
    ----------
    arg:
        param1 (str) Keywords e.g. Cry. Single or multiple keywords
        separated by comma, or space or semicolon
        param1 (str) Search Feilds e.g. Name, Old Name, Accession, Holotype
        and Structure

        Holotype is a protein name ends in 1. Example: Cry1Aa1
        A holotype is a single protein name used to name the lower
        rank based on identity. Cry1Aa2 is named based on the
        identity to Cry1Aa1.


    Returns
    -------
    Search form:
        Unbound search form. See database.forms.py
    Anonymous session items:
        User selected items in the cart for further analysis
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
    return render(request, "newwebpage/search_page.html",
                  {"form": form,
                   "total_cart": total_cart, })


def search_database(request):
    """
    Class filtering user search keywords. Returns the boolean
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

        Holotype is a protein name ends in 1. Example: Cry1Aa1
        A holotype is a single protein name used to name the lower
        rank based on identity. Cry1Aa2 is named based on the
        identity to Cry1Aa1.


    Returns
    -------
    django model queryset:
        filtered list of proteins based on the search term
    show extra data:
        if search term is Cry (three-domain protein) three checkboxes should
        be display in the table. True for success, False otherwise

    Note:
        See `database.filter_results` for more information
    """
    if request.method == "POST":
        form = SearchForm(request.POST)
        proteins = []
        private = []
        single_digit = False
        if form.is_valid():
            query = form.cleaned_data["search_term"]
            field_type = form.cleaned_data["search_fields"]

            # searches = re.split(r':|, ?|\s |_ |. |; |\n', query)
            searches = re.split(r":|, ?|\s* |\n|;", query)

            if field_type == "name":
                q_objects = Q()
                q_search = Q()
                for search in searches:
                    if Search(search).is_wildcard():
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
                proteins1 = PesticidalProteinDatabase.objects.none()
                proteins2 = PesticidalProteinDatabase.objects.none()
                proteins3 = PesticidalProteinPrivateDatabase.objects.none()
                proteins4 = PesticidalProteinPrivateDatabase.objects.none()
                if q_objects:
                    proteins1 = PesticidalProteinDatabase.objects.filter(
                        q_objects)
                    proteins3 = PesticidalProteinPrivateDatabase.objects.filter(
                        q_objects)
                if q_search:
                    proteins2 = PesticidalProteinDatabase.objects.filter(
                        q_search)
                    proteins4 = PesticidalProteinPrivateDatabase.objects.filter(
                        q_search)
                if proteins1 and proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = list(proteins1) + proteins2
                    proteins = _sorted_nicely(proteins, sort_key="name")
                elif proteins1:
                    proteins = _sorted_nicely(proteins1, sort_key="name")
                elif proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = _sorted_nicely(proteins2, sort_key="name")
                if proteins3 and proteins4:
                    filtered_protein = filter_one_name(proteins4)
                    proteins4 = filtered_protein
                    private = list(proteins3) + proteins4
                    private = _sorted_nicely(private, sort_key="name")
                elif proteins3:
                    private = _sorted_nicely(proteins3, sort_key="name")
                elif proteins4:
                    filtered_protein = filter_one_name(proteins4)
                    proteins4 = filtered_protein
                    private = _sorted_nicely(proteins4, sort_key="name")

            elif field_type == "old name/other name":
                q_objects = Q()
                q_search = Q()
                for search in searches:
                    if Search(search).is_wildcard():
                        search = search[:-1]
                    else:
                        search = search
                    k = Search(search)
                    if k.is_fullname():
                        q_objects.add(Q(oldname__iexact=search), Q.OR)
                        q_objects.add(Q(othernames__iexact=search), Q.OR)
                    if k.fulltext():
                        q_objects.add(Q(othernames__icontains=search), Q.OR)
                    if k.is_uppercase():
                        q_objects.add(Q(oldname__icontains=search), Q.OR)
                    if k.is_lowercase():
                        q_objects.add(Q(oldname__icontains=search), Q.OR)
                    if k.is_single_digit():
                        single_digit = True
                        q_search.add(Q(oldname__icontains=search), Q.OR)
                    if k.is_double_digit():
                        q_objects.add(Q(oldname__icontains=search), Q.OR)
                    if k.is_triple_digit():
                        q_objects.add(Q(oldname__icontains=search), Q.OR)
                    if k.is_three_letter():
                        q_objects.add(Q(oldname__icontains=search), Q.OR)
                    if k.is_three_letter_case():
                        q_objects.add(Q(oldname__icontains=search), Q.OR)
                    if k.bthur0001_55730():
                        q_objects.add(Q(othernames__iexact=search), Q.OR)
                    else:
                        q_objects.add(Q(othernames__icontains=search), Q.OR)
                        q_objects.add(Q(oldname__iexact=search), Q.OR)

                proteins1 = PesticidalProteinDatabase.objects.none()
                proteins2 = PesticidalProteinDatabase.objects.none()
                if q_objects:
                    proteins1 = PesticidalProteinDatabase.objects.filter(
                        q_objects)
                if q_search:
                    proteins2 = PesticidalProteinDatabase.objects.filter(
                        q_search)
                if proteins1 and proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = list(proteins1) + proteins2
                    proteins = _sorted_nicely(proteins, sort_key="name")
                elif proteins1:
                    proteins = _sorted_nicely(proteins1, sort_key="name")
                elif proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = _sorted_nicely(proteins2, sort_key="name")

            elif field_type == "accession":
                q_objects = Q()
                for search in searches:
                    q_objects.add(Q(accession__icontains=search), Q.OR)

                proteins = PesticidalProteinDatabase.objects.filter(q_objects)
                proteins = _sorted_nicely(proteins, sort_key="name")
            elif field_type == "holotype":
                # categories = \
                #     PesticidalProteinDatabase.objects.order_by(
                #         'name').values_list('name', flat=True).distinct()
                q_objects = Q()
                filtered_q_objects = Q()
                for search in searches:
                    q_objects.add(Q(name__icontains=search), Q.OR)

                categories = PesticidalProteinDatabase.objects.filter(
                    q_objects)

                for category in categories:
                    if category.name[-1] == "1" and not category.name[-2].isdigit():
                        filtered_q_objects.add(
                            Q(name__iexact=category.name), Q.OR)
                proteins = PesticidalProteinDatabase.objects.filter(
                    filtered_q_objects)
                proteins = _sorted_nicely(proteins, sort_key="name")

            elif field_type == "structure":
                q_objects = Q()
                q_search = Q()
                for search in searches:
                    if Search(search).is_wildcard():
                        search = search[:-1]
                    else:
                        search = search
                    k = Search(search)
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
                    else:
                        q_objects.add(Q(name__iexact=search), Q.OR)
                proteins1 = StructureDatabase.objects.none()
                proteins2 = StructureDatabase.objects.none()
                if q_objects:
                    proteins1 = StructureDatabase.objects.filter(q_objects)
                if q_search:
                    proteins2 = StructureDatabase.objects.filter(q_search)
                if proteins1 and proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = list(proteins1) + proteins2
                    proteins = _sorted_nicely(proteins, sort_key="name")
                elif proteins1:
                    proteins = _sorted_nicely(proteins1, sort_key="name")
                elif proteins2:
                    filtered_protein = filter_one_name(proteins2)
                    proteins2 = filtered_protein
                    proteins = _sorted_nicely(proteins2, sort_key="name")

                structures = _sorted_nicely(proteins, sort_key="name")
                return render(
                    request,
                    "newwebpage/filter_structures.html",
                    {"structures": structures},
                )

        show_extra_data = False
        cry_count = 0
        for protein in proteins:
            if protein.name.startswith("Cry"):
                cry_count += 1
                protein.show_extra_data = True
        if cry_count == len(proteins):
            show_extra_data = True

        return render(
            request,
            "newwebpage/search_results.html",
            {
                "proteins": proteins,
                "private": private,
                "show_extra_data": show_extra_data,
                "searches": searches,
            },
        )
    return HttpResponseRedirect("/search_database_home/")


def add_cart(request):
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

    return redirect("search_database_home")


def structures(request):
    """

    List of proteins that has solved structure in the
    protein data bank database.

    Returns
    -------
    django model queryset:
        List of structures available in the structure database
        ordered by name

    """
    structures = StructureDatabase.objects.order_by("name")

    context = {"structures": structures}

    return render(request, "newwebpage/structures.html", context)


def structure_pdbid(request, pdbid=None):
    """
    Categorize the protein database with unqiue, first three letter pattern.

    Args:
        pdbid: Protein Data Bank ID
        More information: https://www.rcsb.org/docs/general-help/identifiers-in-pdb

    Returns:
        - List of proteins in the structure database
        - Specific protein filtered through pdbid

    Note:
        This function is not used in the database.
    """

    protein = StructureDatabase.objects.filter(pdbid__istartswith=pdbid)
    structures = StructureDatabase.objects.order_by("name")

    context = {"proteins": protein, "structures": structures}
    return render(request, "database/display_structure_pdbid.html", context)


def clear_session_database(request):
    """
    As the name suggest, it clears the selected proteins in the cart using database session.
    """

    session_key = list(request.session.keys())

    try:
        for key in session_key:
            del request.session[key]
    except:
        pass
    return redirect("view_cart")


def remove_cart(request, database_id):
    """
    Remove the selected proteins one by one from the cart.
    Assume you have selected proteins in search page and
    if you view the cart page, there is a table that shows selected prteins.
    These proteins can be removed from the cart using the
    trash-can/delete icon.

    Args:
        database_id:
    """

    protein = PesticidalProteinDatabase.objects.get(id=database_id)

    selected_values = request.session.get("list_names")
    nterminal = request.session.get("list_nterminal")
    middle = request.session.get("list_middle")
    cterminal = request.session.get("list_cterminal")
    selected_association = request.session.get(
        "list_activity_name", [])

    try:
        selected_values.remove(protein.name)
    except:
        pass

    try:
        nterminal.remove(protein.name)
    except:
        pass

    try:
        middle.remove(protein.name)
    except:
        pass

    try:
        cterminal.remove(protein.name)
    except:
        pass

    try:
        selected_association.remove(protein.name)
    except:
        pass

    request.session.modified = True

    # if selected_values:
    #     return redirect("view_cart")
    # message_profile = "Please add sequences to the cart"
    # messages.success(request, message_profile)
    return redirect("view_cart")


def cart_value(request):
    """In the search page (link below)
    https://camtech-bpp.ifas.ufl.edu/search_database_home/

    There is a cart value on top right of the search box.
    The cart function counts the select items in the cart and are
    shown.
    """
    # Full name proteins (all the category proteins)
    selected_values = request.session.get("list_names", [])
    # N-terminal Cry domain proteins
    nterminal = request.session.get("list_nterminal", [])
    # Middle domain Cry proteins
    middle = request.session.get("list_middle", [])
    # C-terminal Cry domain proteins
    cterminal = request.session.get("list_cterminal", [])
    # Association proteins (Specificity/Metadatabase)
    selected_association = request.session.get(
        "list_activity_name", [])
    values = []

    if nterminal:
        values += nterminal
    if middle:
        values += middle
    if cterminal:
        values += cterminal
    if selected_values:
        values += selected_values
    if selected_association:
        values += selected_association

    values = list(set(values))
    if values:
        number_of_proteins = len(values)
        return HttpResponse(
            json.dumps({"number_of_proteins": number_of_proteins}),
            content_type="application/json",
        )
    else:
        return HttpResponse(
            json.dumps({"number_of_proteins": None}),
            content_type="application/json",
        )


def view_cart(request):
    """
    View the selected proteins in the session and user uploaded sequences.
    """

    selected_values = request.session.get("list_names", [])
    selected_nterminal = request.session.get("list_nterminal", [])
    selected_middle = request.session.get("list_middle", [])
    selected_cterminal = request.session.get("list_cterminal", [])
    userdata = request.session.get("userdataids", [])
    # selected_associations = request.session.get(
    #     "list_activity_names", [])
    selected_mutants = request.session.get(
        "list_mutant_names", [])

    values = []
    selected_mutants_all = []

    form_data = {
        "list_names": str(selected_values),
        "list_nterminal": str(selected_nterminal),
        "list_middle": str(selected_middle),
        "list_cterminal": str(selected_cterminal),
        "userdata": str(userdata),
        "list_mutant_names": str(selected_mutants),
    }

    analysisform = AnalysisForm(form_data, request=request)
    userform = UserDataForm()
    analysisform.is_valid()

    if selected_nterminal:
        values += selected_nterminal
    if selected_middle:
        values += selected_middle
    if selected_cterminal:
        values += selected_cterminal
    if selected_values:
        values += selected_values
    if selected_mutants:
        selected_mutants_all += selected_mutants

    userdata = UserUploadData.objects.filter(
        session_key=request.session.session_key)

    if request.method == "POST":
        userform = UserDataForm(
            request.POST, request.FILES, session=request.session)

        if userform.is_valid():
            userform = UserDataForm()

    values = list(OrderedDict.fromkeys(values))
    selected_mutants_all = list(OrderedDict.fromkeys(selected_mutants_all))
    proteins = PesticidalProteinDatabase.objects.filter(name__in=values)
    modified = MutantProteinDatabase.objects.filter(
        name__in=selected_mutants_all)

    context = {
        "proteins": proteins,
        "selected_mutants": modified,
        "userdata": userdata,
        "analysisform": analysisform,
        "userform": userform,
    }

    return render(request, "newwebpage/search_user_data_update.html", context)


def clear_session_user_data(request):
    """Remove all the user uploaded proteins from the cart."""

    UserUploadData.objects.filter(
        session_key=request.session.session_key).delete()

    return redirect("view_cart")


def user_data_remove(request, id):
    """Remove the user uploaded proteins individually"""

    instance = UserUploadData.objects.get(
        session_key=request.session.session_key, id=id)
    instance.delete()

    return redirect("view_cart")


# def user_data(request):
#     """A user will upload the protein sequences in fasta format
#     and stored temporarily using the session."""
#
#     if request.method == 'POST':
#         file = request.POST['fulltextarea']
#         if not file:
#             message_profile = "Please add some sequences"
#             messages.success(request, message_profile)
#             return redirect("view_cart")
#
#         content = ContentFile(file)
#         content = filter(None, content)
#
#         for rec in SeqIO.parse(content, "fasta"):
#             name = rec.id
#             sequence = str(rec.seq)
#             UserUploadData.objects.create(
#                 session_key=request.session.session_key,
#                 name=name, sequence=sequence)
#         message_profile = "Added the user sequences"
#         messages.info(request, message_profile)
#
#     return redirect("view_cart")


def user_data(request):
    """A user will upload the protein sequences in fasta format
    and stored temporarily using the session."""

    if request.method == "POST":
        form = UserDataForm(request.POST, request.FILES,
                            session=request.session)

        if form.is_valid():
            # print("form")
            messages.success(request, "file upload successful")
        # print(form.errors)

    # return redirect("view_cart")
    return render(request, "newwebpage/search_user_data_update.html", form)


@ csrf_exempt
def download_sequences(request):
    """Download the selected and/or user uploaded protein sequences."""

    selected_values = request.session.get("list_names", [])
    list_nterminal = request.session.get("list_nterminal", [])
    list_middle = request.session.get("list_middle", [])
    list_cterminal = request.session.get("list_cterminal", [])
    selected_association = request.session.get(
        "list_activity_name", [])

    values = []

    if list_nterminal:
        values += list_nterminal
    if list_middle:
        values += list_middle
    if list_cterminal:
        values += list_cterminal
    if selected_values:
        values += selected_values
    if selected_association:
        values += selected_association
    if selected_association:
        selected_association += selected_association
    values = list(set(values))
    data = PesticidalProteinDatabase.objects.filter(name__in=values)
    modfied_data = MutantProteinDatabase.objects.filter(
        name__in=selected_association)

    userdata = UserUploadData.objects.filter(
        session_key=request.session.session_key)

    combined_selection = []

    if list_nterminal:
        combined_selection += list_nterminal
    if list_middle:
        combined_selection += list_middle
    if list_cterminal:
        combined_selection += list_cterminal
    if selected_values:
        combined_selection += selected_values
    if selected_association:
        combined_selection += selected_association
    if selected_association:
        selected_association += selected_association

    accession = {}

    data = PesticidalProteinDatabase.objects.filter(
        name__in=combined_selection)
    if data:
        for item in data:
            accession[item.accession] = item

    protein_detail = ProteinDetail.objects.filter(
        accession__in=list(accession.keys()))

    file = StringIO()
    # buffer = BytesIO()
    for item in data:
        output = ""
        item_name = item.name
        # print("item_name", item_name)
        if item.name in list_nterminal:
            nterminal = [
                protein for protein in protein_detail if protein.accession == item.accession]
            item_name += "_d1"
            for item1 in nterminal:
                output += item1.get_endotoxin_n()
        if item.name in list_middle:
            middle = [
                protein for protein in protein_detail if protein.accession == item.accession]
            item_name += "_d2"
            for item1 in middle:
                output += item1.get_endotoxin_m()
        if item.name in list_cterminal:
            cterminal = [
                protein for protein in protein_detail if protein.accession == item.accession]
            # print(cterminal)
            item_name += "_d3"
            for item1 in cterminal:
                output += item1.get_endotoxin_c()
                # print("download output", output)
        if item.name in selected_values:
            fasta = textwrap.fill(item.sequence, 80)
            output += fasta
            # print(str_to_write)
            # file.write(str_to_write)

        if output:
            str_to_write = f">{item_name}\n{output}\n"
            file.write(str_to_write)

    for item in userdata:
        fasta = textwrap.fill(item.sequence, 80)
        if len(item.name) > 10:
            item.name = item.name[:10]
        str_to_write = f">{item.name}\n{fasta}\n"
        file.write(str_to_write)

    for item in modfied_data:
        fasta = textwrap.fill(item.sequence, 80)
        if len(item.name) > 10:
            item.name = item.name[:10]
        str_to_write = f">{item.name}\n{fasta}\n"
        file.write(str_to_write)

    response = HttpResponse(file.getvalue(), content_type="text/plain")
    download_file = "cart_fasta_sequences.txt"
    response["Content-Disposition"] = "attachment;filename=" + download_file
    response["Content-Length"] = file.tell()
    return response


def download_data(request):
    """List the categories for download."""

    categories = PesticidalProteinDatabase.objects.order_by(
        "name").values_list("name").distinct()

    category_prefixes = []
    for category in categories:
        prefix = category[0][:3]
        if prefix not in category_prefixes:
            category_prefixes.append(prefix)

    context = {
        "proteins": PesticidalProteinDatabase.objects.all(),
        "category_prefixes": category_prefixes,
        "descriptions": Description.objects.order_by("name"),
    }
    return render(request, "newwebpage/download_category.html", context)


def download_single_sequence(request, proteinname=None):
    """Download the fasta sequence by name."""

    protein = PesticidalProteinDatabase.objects.get(name=proteinname)
    file = StringIO()
    fasta = textwrap.fill(protein.sequence, 80)
    str_to_write = f">{protein.name}\n{fasta}\n"
    file.write(str_to_write)

    response = HttpResponse(file.getvalue(), content_type="text/plain")
    download_file = f"{proteinname}_fasta_sequence.txt"
    response["Content-Disposition"] = "attachment;filename=" + download_file
    response["Content-Length"] = file.tell()
    return response


def download_category_form(request):

    form = DownloadForm()
    return render(request, "newwebpage/download_form.html", form)


def download_category(request, category=None):
    """Download the fasta sequences for the category."""

    if request.method == "POST":
        form = DownloadForm(request.POST)
        if form.is_valid():
            category = category.title()

            context = {
                "proteins": PesticidalProteinDatabase.objects.all(),
                "descriptions": Description.objects.order_by("name"),
            }

            file = StringIO()
            data = list(context.get("proteins"))

            for item in data:
                if category in item.name:
                    fasta = textwrap.fill(item.sequence, 80)
                    str_to_write = f">{item.name}\n{fasta}\n"
                    file.write(str_to_write)
                else:
                    pass

            if "All" in category:
                for item in data:
                    fasta = textwrap.fill(item.sequence, 80)
                    str_to_write = f">{item.name}\n{fasta}\n"
                    file.write(str_to_write)

            response = HttpResponse(file.getvalue(), content_type="text/plain")
            download_file = f"{category}_fasta_sequences.txt"
            response["Content-Disposition"] = "attachment;filename=" + \
                download_file
            response["Content-Length"] = file.tell()
            return response
    form = DownloadForm()
    return render(request, "newwebpage/download_form.html", form)


def category_form(request):
    form1 = DownloadForm()
    form2 = ThreedomainDownloadForm()
    form3 = HolotypeForm()
    download = DownloadMutantForm()

    context = {
        "form1": form1,
        "form2": form2,
        "form3": form3,
        "download": download,
    }
    return render(request, "newwebpage/download_form.html", context)


def category_download(request):
    if request.method == "POST":
        categories = request.POST.getlist("category")
        print(categories)

        context = {"proteins": PesticidalProteinDatabase.objects.all()}

        file = StringIO()
        data = list(context.get("proteins"))

        for item in data:
            if "All" in categories or item.name[:3].lower() in str(categories):
                fasta = textwrap.fill(item.sequence, 80)
                str_to_write = f">{item.name}\n{fasta}\n"
                file.write(str_to_write)

        # if :
        #     for item in data:
        #         fasta = textwrap.fill(item.sequence, 80)
        #         str_to_write = f">{item.name}\n{fasta}\n"
        #         file.write(str_to_write)

        response = HttpResponse(file.getvalue(), content_type="text/plain")
        download_file = f"{'_'.join(categories)}_fasta_sequences.txt"
        response["Content-Disposition"] = "attachment;filename=" + download_file
        response["Content-Length"] = file.tell()
        return response


def threedomain_download(request):
    if request.method == "POST":
        type_option = request.POST.getlist("threedomain")
        file = StringIO()

        accession = {}
        output = ""

        data = PesticidalProteinDatabase.objects.filter(
            name__istartswith="cry").order_by("name")
        if data:
            for item in data:
                # if item.name[-1] == '1' and not item.name[-2].isdigit():
                accession[item.accession] = item

        protein_detail = ProteinDetail.objects.filter(
            accession__in=list(accession.keys()))

        protein_data = PesticidalProteinDatabase.objects.filter(
            accession__in=list(accession.keys()))

        count = 0
        for item in protein_data:
            output = ""
            domain_name = ""
            if "domain1" in type_option:
                nterminal = [
                    protein for protein in protein_detail if protein.accession == item.accession]
                for item1 in nterminal:
                    count += 1
                    output += item1.get_endotoxin_n()
                    domain_name += "_d1"
            if "domain2" in type_option:
                nterminal = [
                    protein for protein in protein_detail if protein.accession == item.accession]
                for item1 in nterminal:
                    count += 1
                    output += item1.get_endotoxin_m()
                    domain_name += "_d2"
            if "domain3" in type_option:
                nterminal = [
                    protein for protein in protein_detail if protein.accession == item.accession]
                for item1 in nterminal:
                    count += 1
                    output += item1.get_endotoxin_c()
                    domain_name += "_d3"
            # if "full_length" in type_option:
            #     nterminal = [
            #         protein for protein in protein_detail if protein.accession == item.accession]
            #     for item1 in nterminal:
            #         count += 1
            #         output += item1.sequence
            #         domain_name += "_full_length"
            if output:
                str_to_write = f">{item.name}{domain_name}\n{output}\n"
                file.write(str_to_write)

        response = HttpResponse(file.getvalue(), content_type="text/plain")
        download_file = f"{'_'.join(type_option)}_threedomain_fasta_sequences.txt"
        response["Content-Disposition"] = "attachment;filename=" + download_file
        response["Content-Length"] = file.tell()
        return response


def holotype_download(request):
    if request.method == "POST":
        type_option = request.POST.getlist("holotype")
        file = StringIO()

        accession = {}
        output = ""

        data = PesticidalProteinDatabase.objects.filter(
            name__istartswith="cry").order_by("name").distinct()
        if data:
            for item in data:
                if item.name[-1] == "1" and not item.name[-2].isdigit():
                    str_to_write = f">{item.name}\n{item.sequence}\n"
                    file.write(str_to_write)

        response = HttpResponse(file.getvalue(), content_type="text/plain")
        download_file = f"{'_'.join(type_option)}_fasta_sequences.txt"
        response["Content-Disposition"] = "attachment;filename=" + download_file
        response["Content-Length"] = file.tell()
        return response


def protein_detail(request, name):

    q_objects1 = Q()
    q_objects1.add(Q(proteins__icontains=name), Q.OR)
    identical_proteins = IdenticalProteins.objects.filter(q_objects1)

    proteins = PesticidalProteinDatabase.objects.filter(name=name)
    for protein in proteins:
        print('protein', protein.name)
        for value in identical_proteins:
            if protein.name in value.proteins:
                protein.new_field = value.proteins

    context = {
        "proteins": proteins,
    }

    return render(request, "newwebpage/protein_detail.html", context)


def old_name_new_name(request):
    table1 = OldnameNewnameTableLeft.objects.all()
    table2 = OldnameNewnameTableRight.objects.all()

    context = {
        "table1": table1,
        "table2": table2,
    }
    return render(request, "newwebpage/old_name_new_name.html", context)


def export_new_name_table(request):
    left_resource = OldnameNewnameTableLeftResource()
    dataset_left = left_resource.export()
    response = HttpResponse(dataset_left.xlsx, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="organized_newname.xlsx"'
    return response


def export_old_name_table(request):
    right_resource = OldnameNewnameTableRightResource()
    dataset_right = right_resource.export()
    response = HttpResponse(dataset_right.xlsx, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="organized_oldname.xlsx"'
    return response

# def ncbi_domain(request, accession):
#     return render(request, "newwebpage/ncbi_domains.html")


def ncbi_domain(request, accession):
    print("runs accession")
    if _ncbi_domain_extract(accession):
        print("hi accession")
        Endotoxin_N, Endotoxin_N_start, Endotoxin_N_end, Endotoxin_M, Endotoxin_M_start, Endotoxin_M_end, Endotoxin_C, Endotoxin_C_start, Endotoxin_C_end = _ncbi_domain_extract(
            accession)

        # Update three domain model using accession, name etc...

        context = {
            "Endotoxin_N": Endotoxin_N,
            "Endotoxin_N_start": Endotoxin_N_start,
            "Endotoxin_N_end": Endotoxin_N_end,
            "Endotoxin_M": Endotoxin_N,
            "Endotoxin_M_start": Endotoxin_N_start,
            "Endotoxin_M_end": Endotoxin_N_end,
            "Endotoxin_C": Endotoxin_C,
            "Endotoxin_C_start": Endotoxin_C_start,
            "Endotoxin_C_end": Endotoxin_C_end,
        }
    else:
        context = {'none': 'none'}
    return render(request, "newwebpage/ncbi_domains.html", context)
