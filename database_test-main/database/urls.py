from django.urls import path

from database import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("about/", views.about, name="about"),
    path("funding/", views.about, name="about"),
    path("cite/", views.about, name="about"),
    path("home/", views.home, name="home"),
    path("about_page/", views.about_page, name="about_page"),
    path("database/", views.database, name="database"),
    path("ncbi_domain/<str:accession>/", views.ncbi_domain, name="ncbi_domain"),
    path(
        "categorize_database_<str:category>",
        views.categorize_database,
        name="categorize_database",
    ),
    path(
        "search_database_home/",
        views.search_database_home,
        name="search_database_home",
    ),
    path(
        "search_database/",
        views.search_database,
        name="search_database",
    ),
    path("statistics/", views.statistics, name="statistics"),
    path("search_database/add_cart/", views.add_cart, name="add_cart"),
    path(
        "remove_cart/<int:database_id>/",
        views.remove_cart,
        name="remove_cart",
    ),
    path(
        "clear_session_database/",
        views.clear_session_database,
        name="clear_session_database",
    ),
    path("view_cart/", views.view_cart, name="view_cart"),
    path(
        "download_sequences/",
        views.download_sequences,
        name="download_sequences",
    ),
    path(
        "clear_session_user_data/",
        views.clear_session_user_data,
        name="clear_session_user_data",
    ),
    path(
        "user_data_remove/<int:id>/",
        views.user_data_remove,
        name="user_data_remove",
    ),
    path("user_data/", views.user_data, name="user_data"),
    path("cart_value/", views.cart_value, name="cart_value"),
    path("download_data/", views.download_data, name="download_data"),
    path(
        "download_single_sequence/<str:proteinname>/",
        views.download_single_sequence,
        name="download_single_sequence",
    ),
    path(
        "download_category_<str:category>",
        views.download_category,
        name="download_category",
    ),
    path("category_form", views.category_form, name="category_form"),
    path(
        "category_download",
        views.category_download,
        name="category_download",
    ),
    path(
        "threedomain_download",
        views.threedomain_download,
        name="threedomain_download",
    ),
    path(
        "holotype_download",
        views.holotype_download,
        name="holotype_download",
    ),
    path(
        "protein_detail/<slug:name>/",
        views.protein_detail,
        name="protein_detail",
    ),
    path(
        "old_name_new_name/",
        views.old_name_new_name,
        name="old_name_new_name",
    ),
    path(
        "export_old_name_table/",
        views.export_old_name_table,
        name="export_old_name_table",
    ),
    path(
        "export_new_name_table/",
        views.export_new_name_table,
        name="export_new_name_table",
    ),
    path("structures/", views.structures, name="structures"),
    path(
        "structure_pdbid_<str:pdbid>",
        views.structure_pdbid,
        name="structure_pdbid",
    ),
]
