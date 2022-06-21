from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.html import strip_tags
from database.models import PesticidalProteinPrivateDatabase as PD


TYPES_CHOICES = (
    ('pending', 'Pending'),
    ('emailed', 'Emailed'),
)


class Feedback(models.Model):
    """Users feedback for the database is stored in this model.

    Example

    name --> Suresh
    Subject --> Cry10Aa1
    email --> suresh.pannersel at ufl.edu
    message --> Link seems inactive for the protein
    """

    name = models.CharField(max_length=75, null=True, blank=True)
    subject = models.CharField(max_length=75, null=True, blank=True)
    email = models.EmailField(max_length=70, null=True, blank=False)
    message = models.TextField(blank=True, null=False)
    uploaded = models.DateTimeField("Uploaded", default=timezone.now)
    contact_status = models.CharField(
        choices=TYPES_CHOICES, default="Pending", max_length=10)

    def __str__(self):
        return "New Feedback " + self.email

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"


class Links(models.Model):
    """
    django-ckeditor is used for this model. Admin users can edit
    the page to add name, description and link.
    The main advantage of this app is admin users
    can change the text size and type.

    Examples

    name --> TOXiTAXi Database

    link --> http://150.254.120.147:7000/

    description --> An online database showing the activity of
    selected pesticidal proteins against a range of insects
    and highlighting antagonisitc and synergistic interactions
    between them.

    Related files
    LinksResource  --> extra.admin.py
    LinksAdmin  --> extra.admin.py
    links --> extra.views.py
    external html file --> newwebpage/links.html
    """
    name = RichTextUploadingField()
    description = RichTextUploadingField()
    link = RichTextUploadingField()

    class Meta:
        verbose_name = "Add External Link"
        verbose_name_plural = "Add External Links"
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def names(self):
        return strip_tags(self.name)

    @property
    def descriptions(self):
        return strip_tags(self.description)

    @property
    def links(self):
        return strip_tags(self.link)


class FaqEditHeading(models.Model):
    """Header title for FAQs

    Add header titles here to show up in the FaqEdit model.

    Example
    Category --> Database FAQ

    Related files
    FaqEditResource  --> extra.admin.py
    FaqEditAdmin  --> extra.admin.py
    faq --> extra.views.py
    external html file --> newwebpage/faqedit.html
    """
    category = RichTextUploadingField()

    class Meta:
        verbose_name = "Add FAQ Heading"
        verbose_name_plural = "Add FAQ Headings"

    def __str__(self):
        return self.categories

    def __unicode__(self):
        return self.category

    @property
    def categories(self):
        from django.utils.html import strip_tags
        return strip_tags(self.category)


class FaqEdit(models.Model):
    """Question and answer page for adding FAQs in the admin page
    category can be chosen from the added headers. Cateogory
    is a ForeignKey

    Example

    category --> Database FAQ

    question --> Can I use the database locally on my laptop?

    answer --> Yes. You can download from here
    https://github.com/bpprc/database and the installation
    instructions are provided.
    """
    category = models.ForeignKey(
        FaqEditHeading, related_name='faqs', on_delete=models.CASCADE,      blank=True, null=True)
    question = RichTextUploadingField()
    answer = RichTextUploadingField()

    class Meta:
        verbose_name = "Add FAQ Q&A"
        verbose_name_plural = "Add FAQ Q&As"
        ordering = ("question",)

    @property
    def categories(self):
        return strip_tags(self.category)

    @property
    def questions(self):
        return strip_tags(self.question)

    @property
    def answers(self):
        return strip_tags(self.answer)

    def __unicode__(self):
        return strip_tags(self.category)

    def __str__(self):
        return strip_tags(self.category)


class NCBIAvailability(models.Model):
    """
    NCBI keeps sequences private until the data are published.
    This model stores accession and NCBI availability
    i.e. whether it is private or public available.
    The NCBI availability are show in UserSubmission
    admin list display.

    Example

    accession --> CAA26943 #accession number
    availability --> private #NCBI database

    """
    accession = models.CharField(max_length=75, blank=True, null=True)
    availability = models.CharField(max_length=75, null=True, blank=True)

    class Meta:
        verbose_name = "NCBI accession public availability"
        verbose_name_plural = "NCBI accession public availability"

    def name(self):
        proteins = PD.objects.all()
        for protein in proteins:
            if self.accession == protein.accession:
                return protein.name
        return ""
