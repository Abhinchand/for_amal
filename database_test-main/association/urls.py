from django.urls import path, re_path

from association import views

urlpatterns = [
    path(
        "data_association_links/",
        views.data_association_links,
        name="data_association_links",
    ),
    path(
        "example_content/",
        views.example_content,
        name="example_content",
    ),
    path("data_teams/", views.data_teams, name="data_teams"),
    path("list_proteins/", views.list_proteins, name="list_proteins"),
    path(
        "search_association/",
        views.search_association,
        name="search_association",
    ),
    path(
        "search_data_association/",
        views.search_data_association,
        name="search_data_association",
    ),
    path("search_data_association/association_add_cart/",
         views.association_add_cart, name="association_add_cart"),
    path(
        "display_protein_data/<slug:name>/",
        views.display_protein_data,
        name="display_protein_data",
    ),
    path(
        "keyword_confirm/<slug:name>/",
        views.keyword_confirm,
        name="keyword_confirm",
    ),
    path("api", views.home, name="home"),
    path(
        "heatmap_activity",
        views.heatmap_activity,
        name="heatmap_activity",
    ),
    path(
        "metadatabase_protein_detail/<slug:name>/",
        views.metadatabase_protein_detail,
        name="metadatabase_protein_detail",
    ),
    path(
        "feedback_protein/<slug:protein_id>/",
        views.feedback_protein,
        name="feedback_protein",
    ),
    re_path(r'mutant_proteins/(?P<protein_name>.*)/$',
            views.mutant_proteins,
            name="mutant_proteins",
            ),
    path(
        "download_association/",
        views.download_association,
        name="download_association",
    ),
    path(
        "mutant_download",
        views.mutant_download,
        name="mutant_download",
    ),
    path(
        "export_association_seq/",
        views.export_association_seq,
        name="export_association_seq",
    ),
    path(
        "export_association/",
        views.export_association,
        name="export_association",
    ),
    path(
        "association_add_cart",
        views.association_add_cart,
        name="association_add_cart",
    ),
    path('remove_cart_association/<slug:protein_id>/',
         views.remove_cart_association,
         name="remove_cart_association",
         ),
]
