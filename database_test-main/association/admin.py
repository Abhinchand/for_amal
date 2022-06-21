from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from association.models import Association, IdenticalProteins, MutantProteinDatabase, FeedbackProteinError


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
    "date",
    "terms_conditions",)


class AssociationResource(resources.ModelResource):
    sequence = Field()

    class Meta:
        model = Association
        # skip_unchanged = False
        # report_skipped = True
        # exclude = ("id",)
        import_id_fields = (
            "id",
        )

        export_id_fields = (
            "sequence",
            "name",
            "partnerprotein",
            "partnerprotein_textbox",
            "target_order",
            "target_species",
            "activity",
            "taxonid",
            "lc50",
            "units",
            "percentage_mortality",
            "publication",
            "other_citations",
            "life_stage",
            "instar",
            "assay_material",
            "assay_method",
            "comment",
            "data_entered_by",
        )

    def dehydrate_sequence(self, association):
        sequence = association.get_sequence()
        return sequence


class AssociationAdmin(ImportExportModelAdmin):
    resource_class = AssociationResource

    search_fields = (
        "name",
        "partnerprotein",
        "partnerprotein_textbox",
        "target_order",
        "target_species",
        "activity",
        "taxonid",
        "lc50",
        "units",
        "percentage_mortality",
        "publication",
        "other_citations",
        "life_stage",
        "instar",
        "assay_material",
        "assay_method",
        "data_entered_by",
    )

    fields = (
        "name",
        "partnerprotein",
        "partnerprotein_textbox",
        "target_order",
        "target_species",
        "activity",
        "taxonid",
        "lc50",
        "units",
        "percentage_mortality",
        "publication",
        "other_citations",
        "life_stage",
        "instar",
        "assay_material",
        "assay_method",
        "comment",
        "data_entered_by",
    )

    list_display = (
        "name",
        "partnerprotein",
        "partnerprotein_textbox",
        "target_order",
        "target_species",
        "activity",
        "taxonid",
        "lc50",
        "units",
        "percentage_mortality",
        "publication",
        "other_citations",
        "life_stage",
        "instar",
        "assay_material",
        "assay_method",
        "comment",
        "data_entered_by",
        "date",
    )


class FeedbackProteinErrorResource(resources.ModelResource):
    class Meta:
        model = FeedbackProteinError
        exclude = ("id",)
        import_id_fields = (
            "name",
        )


class FeedbackProteinErrorAdmin(ImportExportModelAdmin):
    resource_class = FeedbackProteinErrorResource

    fields = (
        "name",
        "subject",
        "email",
        "message",
        "uploaded"
    )

    search_fields = (
        "name",
        "subject",
        "email",
        "message",
        "uploaded"
    )

    list_display = (
        "name",
        "subject",
        "email",
        "message",
        "uploaded"
    )


class MutantProteinsResource(resources.ModelResource):
    # MutantProteinDatabase is ModifiedProteinDatabase
    class Meta:
        model = MutantProteinDatabase
        exclude = ("id",)
        import_id_fields = (
            "name",
            "sequence",
            "comment",
        )


class MutantProteinsAdmin(ImportExportModelAdmin):

    # MutantProteinDatabase is ModifiedProteinDatabase
    resource_class = MutantProteinsResource

    fields = allowed_fields

    search_fields = (
        "name",
        "comment",
    )

    list_display = (
        "name",
        "sequence",
        "comment",
    )


class IdenticalProteinsResource(resources.ModelResource):
    class Meta:
        model = IdenticalProteins
        exclude = ("id",)
        import_id_fields = (
            "proteins",
        )


class IdenticalProteinsAdmin(ImportExportModelAdmin):
    """The protein detail page shows the IdenticalProteins model.

    Example link below
    e.g. https://camtech-bpp.test.ifas.ufl.edu/protein_detail/Cry1Aa9/

    The django management command

    database.management.commands -> identical_proteins.py

    runs biweekly to compare the public database proteins and report only
    the identical proteins in a csv file. Then csv file will be uploaded
    automatically.
    """
    resource_class = IdenticalProteinsResource

    fields = (
        "proteins",
    )

    search_fields = (
        "proteins",
    )

    list_display = (
        "proteins",
    )


admin.site.register(Association, AssociationAdmin)
admin.site.register(IdenticalProteins, IdenticalProteinsAdmin)
admin.site.register(MutantProteinDatabase, MutantProteinsAdmin)
admin.site.register(FeedbackProteinError, FeedbackProteinErrorAdmin)
