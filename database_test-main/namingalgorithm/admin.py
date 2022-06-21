"""Submit the sequence by user and name of the protein is predicted."""

from django.contrib import admin
from django.contrib.admin.checks import BaseModelAdminChecks
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.html import format_html, mark_safe
from import_export import resources, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from database.models import (
    PesticidalProteinDatabase,
    PesticidalProteinPrivateDatabase,
)
from namingalgorithm.models import AuditEntry

from .models import Archive, SendEmail, UserSubmission
import tempfile
import textwrap
from django.http import HttpResponseRedirect
from naming_package import run_data
from namingalgorithm.tasks import namingalgorithm_task


import_order = (
    "submittersname",
    "submittersemail",
    "predict_name",
    "sequence",
    "bacterium",
    "bacterium_textbox",
    "taxonid",
    "year",
    "accession",
    "partnerprotein",
    "partnerprotein_textbox",
    'toxicto',
    "nontoxic",
    "dnasequence",
    "pdbcode",
    "publication",
    "user_comments",
    "user_provided_proteinname",
    "admin_comments",
    "date",
)


@admin.register(AuditEntry)
class AuditEntryLogAdmin(admin.ModelAdmin):
    list_display = [
        "action",
        "username",
        "ip",
    ]
    list_filter = [
        "action",
    ]


class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = (
        "content_type",
        "user",
        "action_time",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class ModelAdminLog(GenericStackedInline):
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
        message = obj.get_change_message()
        return message


class ArchiveResource(resources.ModelResource):
    class Meta:
        model = Archive


class ArchiveAdmin(ImportExportModelAdmin):
    resource_class = ArchiveResource

    search_fields = ["submittersemail", "submittersname"]
    list_display = (
        "submittersname",
        "accession",
        "date",
        # 'admin_user',
        "admin_comments",
    )

    # inlines = [ModelAdminLog]
    #
    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)
    #     if change:
    #         change_message = "{} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {}".format(
    #             obj.submittersname,
    #             obj.submittersemail,
    #             obj.name,
    #             obj.year,
    #             obj.sequence,
    #             obj.bacterium,
    #             obj.bacterium_textbox,
    #             obj.taxonid,
    #             obj.accession,
    #             obj.partnerprotein,
    #             obj.partnerprotein_textbox,
    #             obj.toxicto,
    #             obj.nontoxic,
    #             obj.dnasequence,
    #             obj.pdbcode,
    #             obj.publication,
    #             obj.admin_user,
    #             obj.admin_comments,
    #             obj.comment,
    #             obj.uploaded,
    #             obj.predict_name,
    #             obj.user_provided_proteinname,
    #         )
    #         LogEntry.objects.create(
    #             user=request.user,
    #             content_type=get_content_type_for_model(obj),
    #             object_id=obj.id,
    #             action_flag=2,
    #             change_message=change_message,
    #             object_repr=obj.__str__()[:200],
    #         )


class BacteriumWidget(widgets.BooleanWidget):
    def Clean(self, value, row=None, *args, **kwargs):
        if value.lower() == 'yes':
            value = True
        if value.lower() == 'no':
            value = False
        return value


class UserSubmissionResource(resources.ModelResource):

    partnerprotein = Field(column_name='partnerprotein',
                           attribute='partnerprotein',
                           default=False, widget=BacteriumWidget())
    bacterium = Field(column_name='bacterium',
                      attribute='bacterium',
                      default=True, widget=BacteriumWidget())

    class Meta:
        model = UserSubmission
        exclude = ('id', 'terms_conditions',
                   'contact_status', 'public', 'private',)

        fields = import_order
        import_order = import_order
        export_order = import_order
        import_id_fields = import_order
        export_id_fields = import_order

    def dehydrate_bacterium(self, UserSubmissionDatabase):
        d = UserSubmissionDatabase.bacterium
        if d is True:
            return '%s' % ('Yes')
        else:
            return '%s' % ('No')

    def dehydrate_partnerprotein(self, UserSubmissionDatabase):
        d = UserSubmissionDatabase.partnerprotein
        if d is True:
            return '%s' % ('Yes')
        else:
            return '%s' % ('No')


class UserSubmissionAdmin(ImportExportModelAdmin):
    resource_class = UserSubmissionResource

    """Submit the sequence by user and name of the protein is predicted."""

    search_fields = ["submittersemail", "submittersname", "accession"]
    list_editable = ("contact_status",)
    list_display = (
        "submittersname",
        "accession_url",
        "naming_algorithm",
        "availability",
        'copy_to_public',
        'copy_to_private',
        "refresh",
        "send_email",
        "date",
        "contact_status"
    )
    exclude = ["alignresults"]

    def accession_url(self, obj):
        return format_html(
            '<a href="%s%s" target="_blank">%s</a>'
            % (
                "https://www.ncbi.nlm.nih.gov/protein/",
                obj.accession,
                obj.accession,
            )
        )

    def naming_algorithm(self, obj):
        if ">" in str(obj.sequence).split("\n")[0]:
            obj.sequence = "\n".join(str(obj.sequence).split("\n")[1:])

        format_data = textwrap.fill(obj.sequence, 80)
        tmp_seq = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
        with open(tmp_seq.name, "wb") as temp:
            temp.write(format_data.encode())
            tmp_seq.close()
        # task = namingalgorithm_task.delay(tmp_seq.name)
        # #align = run_data.run_naming_algorithm.run_bug(tmp_seq.name)
        #
        # return HttpResponseRedirect("/run_naming_algorithm/")

        # return format_html(
        #     '<a href="/run_naming_algorithm_celery/?name={0}" target="_blank">Naming Algorithm</a>'.format(tmp_seq.name))
        return format_html(
            '<a href="/run_naming_algorithm/?fulltextarea={0}&submission_id={1}" target="_blank">Naming Algorithm</a>'.format(
                obj.sequence, obj.id
            )
        )

    def align_results(self, obj):
        """Submit the sequence by user and name of the protein is predicted."""
        if obj.alignresults:
            return format_html(
                '<a href="/align_results/?submission_id={0}" target="_blank">View Result</a>'.format(
                    obj.id)
            )
        return ""

    def copy_to_public(self, obj):
        """Submit the sequence by user and name of the protein is predicted."""
        return format_html('<a href="/admin/database/pesticidalproteindatabase/add/?name={0}&sequence={1}&submittersname={2}&submittersemail={3}" target="_blank">Copy to public</a>'.format(obj.predict_name or '', obj.sequence, obj.submittersname, obj.submittersemail))

    def copy_to_private(self, obj):
        """Submit the sequence by user and name of the protein is predicted."""
        return format_html('<a href="/admin/database/pesticidalproteinprivatedatabase/add/?name={0}&sequence={1}&submittersname={2}&submittersemail={3}" target="_blank">Copy to private</a>'.format(obj.predict_name or '', obj.sequence, obj.submittersname, obj.submittersemail))

    def refresh(self, obj):
        """Submit the sequence by user and name of the protein is predicted."""
        return format_html('<a href="/admin/namingalgorithm/usersubmission/">refresh</a>')

    def send_email(self, obj):
        return format_html(
            '<a href="/admin/contact/?submittersname={0}&submittersemail={1}&accession={2}" target="_blank">Send Email</a>'.format(
                obj.submittersname, obj.submittersemail, obj.accession
            )
        )

    def availability(self, obj):
        accession_number = obj.accession
        if not accession_number:
            return format_html("<body> <p>No accession number</p> </body>")
        public = PesticidalProteinDatabase.objects.filter(
            accession=accession_number)
        private = PesticidalProteinPrivateDatabase.objects.filter(
            accession=accession_number)
        if public:
            # print(accession_number)
            return format_html('<body> <p style="color:#0000FF";>Available in Public Database</p></body>')
        if private:
            return format_html('<body> <p style="color:#FF0000";>Private Database</p></body>')

    def Pfam(self, obj):
        return format_html()

    naming_algorithm.allow_tags = True
    naming_algorithm.description = "Run the align link for the submission"

    align_results.allow_tags = True
    align_results.description = "View the align results"

    align_results.allow_tags = True
    align_results.description = "Create new data in the database"


class SendEmailAdmin(admin.ModelAdmin):
    list_display = (
        "submittersname",
        "submittersemail",
        "accession",
        "message",
    )

    search_fields = (
        "submittersname",
        "submittersemail",
        "accession",
        "message",
    )

    inlines = [ModelAdminLog]


# class ArchiveAdmin(admin.ModelAdmin):
#     search_fields = ('name', 'year', 'submittersname',
#                      'submittersemail')
#     fields = ('submittersname', 'submittersemail', 'name', 'year', 'sequence', 'bacterium', 'bacterium_textbox', 'taxonid', 'accession', 'partnerprotein', 'partnerprotein_textbox', 'toxicto', 'nontoxic', 'dnasequence', 'pdbcode', 'publication', 'comment', 'uploaded', 'predict_name', 'alignresults', 'terms_conditions')
#     list_display = ('name', 'submittersname',
#                      'accession', 'uploaded',)
#     ordering = ('-uploaded',)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(UserSubmission, UserSubmissionAdmin)
admin.site.register(Archive, ArchiveAdmin)
admin.site.register(SendEmail, SendEmailAdmin)
