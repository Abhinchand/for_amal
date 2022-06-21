from django.contrib import admin
from django.utils.html import format_html
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.http import HttpResponse
from django.db import models
from django.urls import path
from django.utils.html import strip_tags

from extra.models import Feedback, Links, FaqEdit, FaqEditHeading, NCBIAvailability
from extra.views import help


class FaqEditResource(resources.ModelResource):
    """ To integrate django-import-export with our FaqEdit model,
    we will create a ModelResource class in admin.py that will
    describe how this resource can be imported or exported:

    FaqEdit - Model name -> extra.models.py
    Fields in the model are answer, and question. Category is a
    ForeignKey. One issue is when exported django-ckeditor provides
    html tag in the excel.To fix this, a custom field is created
    where we strip html tags.

    Related class --> FaqEditAdmin
    """

    categories = fields.Field()
    questions = fields.Field()
    answers = fields.Field()

    class Meta:
        model = FaqEdit
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "category", "answer", "question")
        export_id_fields = (
            "categories",
            "questions",
            "answers",
        )
        import_id_fields = (
            "categories",
            "questions",
            "answers",
        )

    def dehydrate_categories(self, faqedit):
        return strip_tags(faqedit.categories)

    def dehydrate_questions(self, faqedit):
        return strip_tags(faqedit.questions)

    def dehydrate_answers(self, faqedit):
        return strip_tags(faqedit.answers)


class FaqEditAdmin(ImportExportModelAdmin):
    resource_class = FaqEditResource

    list_display = ('id', "categories", "questions", "answers")

    ordering = ('id',)

    search_fields = ('id', "categories", "questions", "answers")

    def __str__(self):
        return self.category


class LinksResource(resources.ModelResource):
    """ To integrate django-import-export with our Links model,
    we will create a ModelResource class in admin.py that will
    describe how this resource can be imported or exported:

    Links - Model name -> extra.models.py
    Fields in the model are name, description and link. One issue
    is when exported django-ckeditor provides html tag in the excel.
    To fix this, a custom field is created where we strip html tags.

    Related class --> LinksAdmin
    """

    names = fields.Field()
    descriptions = fields.Field()
    links = fields.Field()

    class Meta:
        model = Links
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "name", "description", "link")
        export_id_fields = (
            "names",
            "descriptions",
            "links",
        )
        import_id_fields = (
            "names",
            "descriptions",
            "links",
        )

    def dehydrate_names(self, links):
        return strip_tags(links.names)

    def dehydrate_descriptions(self, links):
        return strip_tags(links.descriptions)

    def dehydrate_links(self, links):
        return strip_tags(links.links)


class LinksAdmin(ImportExportModelAdmin):
    resource_class = LinksResource

    list_display = ("id", "names", "descriptions", "link_url")

    search_fields = ("names", "descriptions", "link_url")

    ordering = ('id',)

    def __str__(self):
        return self.name

    def link_url(self, obj):
        return format_html(
            '<a href="%s" target="_blank">%s</a>' % (obj.link, obj.link))

    # def names(self, obj):
    #     return strip_tags(self.names)
    #
    # def descriptions(self, obj):
    #     return strip_tags(self.descriptions)
    #
    # def links(self, obj):
    #     return strip_tags(self.links)


class FeedbackResource(resources.ModelResource):
    """ To integrate django-import-export with our Feedback model,
    we will create a ModelResource class in admin.py that will
    describe how this resource can be imported or exported:

    Feedback - Model name -> extra.models.py
    Fields in the model are name, subject, email, uploaded,
    and contact_status.

    Related class --> LinksAdmin
    """
    class Meta:
        model = Feedback


class FeedbackAdmin(ImportExportModelAdmin):
    resource_class = FeedbackResource

    list_editable = ("contact_status",)

    list_display = ("name", "subject", "email", "uploaded", "contact_status",)

    search_fields = ("name", "subject", "email", "uploaded",)

    def __str__(self):
        return self.name


class Help(models.Model):
    """Help page in django admin. Screenshots images are
    attached for help."""

    class Meta:
        verbose_name_plural = 'Help'
        app_label = 'extra'


def my_custom_view(request):
    return HttpResponse('Admin Custom View')


class HelpAdmin(admin.ModelAdmin):
    model = Help

    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('', help, name=view_name),
        ]


class NCBIAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'accession_url', 'accession_availability')
    search_fields = ('accession', 'availability')
    ordering = ('id',)

    def accession_url(self, obj):
        return format_html(
            '<a href="%s%s" target="_blank">%s</a>'
            % (
                "https://www.ncbi.nlm.nih.gov/protein/",
                obj.accession,
                obj.accession,
            )
        )

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


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Links, LinksAdmin)
admin.site.register(FaqEdit, FaqEditAdmin)
admin.site.register(FaqEditHeading)
admin.site.register(Help, HelpAdmin)
admin.site.register(NCBIAvailability, NCBIAvailabilityAdmin)
