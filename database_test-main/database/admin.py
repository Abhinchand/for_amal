"""
This encapsulates the logic for displaying the models in the Django admin.

Public database -> PesticidalProteinDatabase

Private database -> PesticidalProteinPrivateDatabase

Protein category description -> Description

OldnameNewname -> OldnameNewnameTableLeft -> Organized by old name

OldnameNewname -> OldnameNewnameTableRight -> Organized by new name

ProteinDetail -> Three domain details of Cry proteins

StructureDatabase -> Available protein structures of Pesticidal Protein

PesticidalProteinHiddenSequence -> Only used by naming algorithm

"""


from Bio import Entrez
from django.contrib import admin
from django.contrib.admin.checks import BaseModelAdminChecks
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from django.contrib.contenttypes.admin import GenericStackedInline
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.html import format_html
from import_export import resources, widgets
from extra.models import NCBIAvailability
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from database.models import (
    Description,
    OldnameNewnameTableLeft,
    OldnameNewnameTableRight,
    PesticidalProteinDatabase,
    PesticidalProteinHiddenSequence,
    PesticidalProteinPrivateDatabase,
    ProteinDetail,
    StructureDatabase,
)


# used by biopython for NCBI
Entrez.email = "admin@bpprc.org"


# model fields import order for public as well as private database
import_order = (
    "submittersname",
    "submittersemail",
    "name",
    "oldname",
    "othernames",
    "accession",
    "year",
    "sequence",
    "taxonid",
    "bacterium",
    "bacterium_textbox",
    "partnerprotein",
    "partnerprotein_textbox",
    "nontoxic",
    "dnasequence",
    "date",
    "publication",
    "comment",
)


# # model fields export order for public as well as private database
export_order = (
    "submittersname",
    "submittersemail",
    "name",
    "oldname",
    "othernames",
    "accession",
    "year",
    "sequence",
    "bacterium",
    "bacterium_textbox",
    "taxonid",
    "partnerprotein",
    "partnerprotein_textbox",
    "toxicto",
    "nontoxic",
    "dnasequence",
    "date",
    "publication",
    "comment",)


# exclude model fields for public as well as private database during export
exclude_items = ("id", "name_category", "predict_name",
                 "created_by", "created_on", "edited_by", "edited_on", "published", "public", "alignresults", "fastasequence_file", "terms_conditions", "uploaded")


# allowed model fields for public as well as private database during export
allowed_fields = (
    "submittersname",
    "submittersemail",
    "name",
    "oldname",
    "othernames",
    "accession",
    "year",
    "sequence",
    "bacterium",
    "bacterium_textbox",
    "taxonid",
    "partnerprotein",
    "partnerprotein_textbox",
    "toxicto",
    "nontoxic",
    "dnasequence",
    "pdbcode",
    "publication",
    "comment",
    "admin_user",
    "admin_comments",
    "date",)


# model fields displayed on the admin for public as well as private database
display = (
    "name",
    "oldname",
    "accession_url",
    "accession_availability",
    "year",
)


# model search fields on the admin for public as well as private database
search_fields = (
    "name",
    "oldname",
    "othernames",
    "accession",
    "year",
)


# display public as well as private databases ordered by name
ordering = ("name",)


# https://blog.askesis.pl/post/2019/02/django-admin-inline.html
class ModelAdminLog(GenericStackedInline):

    """
    A log message that stores the admin user, log in time, edited model class.
    """

    model = LogEntry

    # All fields are read-only, obviously
    readonly_fields = fields = ["action_time", "user", "change_message"]

    # No extra fields so noone can add new logs
    extra = 0

    # No one can delete logs
    can_delete = False

    # This is a hackity hack! See below
    checks_class = BaseModelAdminChecks

    def change_message(self, obj):
        return obj.get_change_message()


class FilterByCategories(admin.SimpleListFilter):
    """
    A filter categories in the admin login to filter the data based on the category. This is visible on the right hand side of the admin page in public database.
    """

    title = "Categories"
    parameter_name = "q"

    def lookups(self, request, model_admin):
        return [
            ("App", "App"),
            ("Cry", "Cry"),
            ("Cyt", "Cyt"),
            ("Gpp", "Gpp"),
            ("Mcf", "Mcf"),
            ("Mpp", "Mpp"),
            ("Mtx", "Mtx"),
            ("Spp", "Spp"),
            ("Tpp", "Tpp"),
            ("Vip", "Vip"),
            ("Vpa", "Vpa"),
            ("Vpb", "Vpb"),
            ("Xpp", "Xpp"),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.distinct().filter()


class StructureDatabaseResource(resources.ModelResource):
    class Meta:
        model = StructureDatabase
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = (
            "name",
            "oldname",
            "accession",
            "pdbid",
            "doi",
            "pubmedid",
            "year",
            "modified",
            "comment",
        )


class StructureDatabaseAdmin(ImportExportModelAdmin):
    resource_class = StructureDatabaseResource

    search_fields = (
        "name",
        "oldname",
        "accession",
        "pdbid",
        "doi",
        "pubmedid",
        "year",
    )
    fields = (
        "name",
        "oldname",
        "accession",
        "pdbid",
        "doi",
        "modified",
        "pubmedid",
        "year",
        "comment",
    )
    list_display = (
        "name",
        "oldname",
        "accession",
        "pdbid",
        "doi",
        "modified",
        "pubmedid",
        "year",
        "comment",
    )

    ordering = ordering


class BacteriumWidget(widgets.BooleanWidget):
    def Clean(self, value, row=None, *args, **kwargs):
        if value.lower() == 'yes':
            value = True
        if value.lower() == 'no':
            value = False
        return value


class PesticidalProteinPrivateDatabaseResource(resources.ModelResource):

    partnerprotein = Field(column_name='partnerprotein',
                           attribute='partnerprotein',
                           default=False, widget=BacteriumWidget())
    bacterium = Field(column_name='bacterium',
                      attribute='bacterium',
                      default=True, widget=BacteriumWidget())

    class Meta:
        model = PesticidalProteinPrivateDatabase
        # skip_unchanged = True
        # report_skipped = True
        exclude = ('id', 'fastasequence_file', 'name_category',
                   'terms_conditions', 'predict_name', 'public', 'admin_user', 'admin_comments')

        # to export only date not time
        # widgets = {
        #     'date': {'format': '%d-%m-%Y'},
        # }
        fields = import_order
        import_order = import_order
        export_order = import_order
        import_id_fields = import_order
        export_id_fields = import_order

    def dehydrate_bacterium(self, PesticidalProteinPrivateDatabase):
        d = PesticidalProteinPrivateDatabase.bacterium
        if d is False:
            return '%s' % ('No')
        else:
            return '%s' % ('Yes')

    def dehydrate_partnerprotein(self, PesticidalProteinPrivateDatabase):
        d = PesticidalProteinPrivateDatabase.partnerprotein
        if d is False:
            return '%s' % ('No')
        else:
            return '%s' % ('Yes')


class PesticidalProteinPrivateDatabaseAdmin(ImportExportModelAdmin):
    resource_class = PesticidalProteinPrivateDatabaseResource

    search_fields = search_fields
    fields = allowed_fields
    list_display = display
    ordering = ordering

    def accession_url(self, obj):
        return format_html(
            '<a href="%s%s" target="_blank">%s</a>'
            % (
                "https://www.ncbi.nlm.nih.gov/protein/",
                obj.accession,
                obj.accession,
            )
        )

    accession_url.allow_tags = True
    accession_url.description = "View the accession number as an URL"

    def accession_availability(self, obj):
        accession = obj.accession
        if not accession:
            return format_html("<body> <p>No accession number</p> </body>")

        a = NCBIAvailability.objects.filter(
            accession=accession).values()

        status = ''

        for status in a:
            if status['availability'] == 'Private':
                status = 'Private'
            elif status['availability'] == 'Public':
                status = 'Public'
        if status == 'Public':
            return format_html('<body> <p style="color:#FF0000";>Sequence is Public</p> </body>')
        if status == 'Private':
            return format_html("<body> <p>Sequence is Private</p> </body>")

    accession_availability.allow_tags = True
    accession_availability.description = "Accession Available in NCBI"


class PesticidalProteinHiddenSequenceResource(resources.ModelResource):
    class Meta:
        model = PesticidalProteinHiddenSequence
        skip_unchanged = True
        report_skipped = True
        exclude = (
            "id",
            "submittersname",
            "submittersemail",
            "uploaded",
            "alignresults",
            "predict_name",
            "terms_conditions",
            "admin_user",
            "admin_comments",
            "public",
            "fastasequence_file",
        )
        import_id_fields = (
            "name",
            "othernames",
            "accession",
            "year",
            "sequence",
            "bacterium_textbox",
            "strain",
            "publication",
            "family",
            "toxicto",
            "nontoxic",
            "mammalian_active",
            "pdbcode",
            "comment",
        )


class PesticidalProteinHiddenSequenceAdmin(ImportExportModelAdmin):
    resource_class = PesticidalProteinHiddenSequenceResource

    search_fields = (
        "name",
        "othernames",
        "accession",
        "year",
        "public",
    )
    fields = (
        "name",
        "othernames",
        "accession",
        "year",
        "sequence",
        "bacterium_textbox",
        "strain",
        "publication",
        "family",
        "toxicto",
        "nontoxic",
        "mammalian_active",
        "pdbcode",
        "comment",
    )
    list_display = ("name", "othernames", "accession", "year", "public")
    ordering = ordering


class PesticidalProteinDatabaseResource(resources.ModelResource):
    """
    ModelResource is from django-import-export app and is a subclass
    for handling Django models.
    """
    partnerprotein = Field(column_name='partnerprotein',
                           attribute='partnerprotein',
                           default=False, widget=BacteriumWidget())
    bacterium = Field(column_name='bacterium',
                      attribute='bacterium',
                      default=True, widget=BacteriumWidget())

    class Meta:
        model = PesticidalProteinDatabase
        # skip_unchanged = True
        # report_skipped = True
        exclude = ('id', 'fastasequence_file', 'name_category',
                   'terms_conditions', 'predict_name', 'public', 'admin_user', 'admin_comments')
        fields = import_order
        import_order = import_order
        export_order = import_order
        import_id_fields = import_order
        export_id_fields = import_order

    def dehydrate_bacterium(self, PesticidalProteinDatabase):
        d = PesticidalProteinDatabase.bacterium
        if d is False:
            return '%s' % ('No')
        else:
            return '%s' % ('Yes')

    def dehydrate_partnerprotein(self, PesticidalProteinDatabase):
        d = PesticidalProteinDatabase.partnerprotein
        if d is False:
            return '%s' % ('No')
        else:
            return '%s' % ('Yes')


class PesticidalProteinDatabaseAdmin(ImportExportModelAdmin):
    resource_class = PesticidalProteinDatabaseResource

    search_fields = search_fields
    fields = allowed_fields
    list_display = (
        "name",
        "oldname",
        "accession_url",
        "Pfam_Info",
        "year",)

    list_filter = ["date", FilterByCategories]

    def accession_url(self, obj):
        return format_html(
            '<a href="%s%s" target="_blank">%s</a>'
            % (
                "https://www.ncbi.nlm.nih.gov/protein/",
                obj.accession,
                obj.accession,
            )
        )

    def Pfam_Info(self, obj):
        if obj.name.startswith("Cry"):
            try:
                domain_details = ProteinDetail.objects.get(
                    accession=obj.accession)
            except ProteinDetail.DoesNotExist:
                domain_details = None
            if domain_details:
                return format_html("<p>Data Available</p>")
            return format_html('<p style="color:#FF0000";>Three domain data needed</p>')

    ordering = ordering
    accession_url.allow_tags = True
    accession_url.description = "View the align results"


class DescriptionResource(resources.ModelResource):
    class Meta:
        model = Description


class DescriptionAdmin(ImportExportModelAdmin):
    resource_class = DescriptionResource
    fields = ("name", "description")
    list_display = ("name", "description")
    search_fields = ("name", "description")


class OldnameNewnameTableLeftResource(resources.ModelResource):
    class Meta:
        model = OldnameNewnameTableLeft
        exclude = "id"


class OldnameNewnameTableLeftAdmin(ImportExportModelAdmin):
    resource_class = OldnameNewnameTableLeftResource
    fields = ("name_2020", "name_1998", "alternative_name")
    list_display = ("name_2020", "name_1998", "alternative_name")
    search_fields = ("name_2020", "name_1998", "alternative_name")


class OldnameNewnameTableRightResource(resources.ModelResource):
    class Meta:
        model = OldnameNewnameTableRight
        exclude = "id"


class OldnameNewnameTableRightAdmin(ImportExportModelAdmin):
    resource_class = OldnameNewnameTableRightResource
    fields = ("name_1998", "name_2020", "alternative_name")
    list_display = ("name_1998", "name_2020", "alternative_name")
    search_fields = ("name_2020", "name_1998", "alternative_name")


class ProteinDetailResource(resources.ModelResource):
    class Meta:
        model = ProteinDetail
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "name", "accession_name")

        import_id_fields = (
            "accession",
            "sequence"
            "fulllength",
            "domain_N",
            "pfam_N",
            "cdd_N",
            "start_N",
            "end_N",
            "domain_M",
            "pfam_M",
            "cdd_M",
            "start_M",
            "end_M",
            "domain_C",
            "pfam_C",
            "cdd_C",
            "start_C",
            "end_C",
        )


class ProteinDetailAdmin(ImportExportModelAdmin):
    search_fields = [
        "name",
        "accession",
        "start_N",
        "end_N",
        "start_M",
        "end_M",
        "start_C",
        "end_C",
    ]

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "20"})},
        models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 80})},
    }
    fields = (
        "name",
        "accession",
        "sequence",
        "fulllength",
        "domain_N",
        "pfam_N",
        "cdd_N",
        "start_N",
        "end_N",
        "domain_M",
        "pfam_M",
        "cdd_M",
        "start_M",
        "end_M",
        "domain_C",
        "pfam_C",
        "cdd_C",
        "start_C",
        "end_C",
    )
    list_display = (
        "id",
        "name",
        "accession_url",
        "domain_N",
        "start_N",
        "end_N",
        "domain_M",
        "start_M",
        "end_M",
        "domain_C",
        "start_C",
        "end_C",
    )
    ordering = ("name",)

    # def Protein_Name(self, obj):
    #     protein = PesticidalProteinDatabase.objects.get(
    #         accession=obj.accession)
    #     if protein:
    #         return protein.name

    def accession_url(self, obj):
        return format_html(
            '<a href="%s%s" target="_blank">%s</a>'
            % (
                "https://www.ncbi.nlm.nih.gov/protein/",
                obj.accession,
                obj.accession,
            )
        )


admin.site.site_header = "BPPRC Admin Dashboard"
admin.site.index_title = "BPPRC Available Features"
admin.site.site_title = "BPPRC adminstration"

admin.site.register(PesticidalProteinDatabase, PesticidalProteinDatabaseAdmin)
admin.site.register(Description, DescriptionAdmin)
admin.site.register(ProteinDetail, ProteinDetailAdmin)
admin.site.register(
    PesticidalProteinPrivateDatabase,
    PesticidalProteinPrivateDatabaseAdmin,
)
admin.site.register(
    PesticidalProteinHiddenSequence,
    PesticidalProteinHiddenSequenceAdmin,
)
admin.site.register(StructureDatabase, StructureDatabaseAdmin)
admin.site.register(OldnameNewnameTableLeft, OldnameNewnameTableLeftAdmin)
admin.site.register(OldnameNewnameTableRight, OldnameNewnameTableRightAdmin)
admin.site.unregister(Group)
