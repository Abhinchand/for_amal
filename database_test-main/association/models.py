import datetime
import textwrap

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from database.models import PesticidalProteinDatabase
from django.core.validators import RegexValidator
from Bio.SeqUtils.ProtParam import ProteinAnalysis

TRUE_FALSE_CHOICES = ((True, "Yes"), (False, "No"))


# class KeywordDatabase(models.Model):
#
#     keyword_id = models.AutoField(primary_key=True)
#
#     def get_database_name_as_list(self):
#         return ', '.join(self.Association_set.values_list('name', flat=True))
#
#     def get_database_target_species_as_list(self):
#         return ', '.join(self.Association_set.values_list('target_species', flat=True))
#
#     def get_database_target_order_as_list(self):
#         return ', '.join(self.Association_set.values_list('target_order', flat=True))
#
#     def get_database_taxonid_as_list(self):
#         return ', '.join(self.Association_set.values_list('taxonid', flat=True))

class MutantProteinDatabase(models.Model):

    # User who submits the sequence through "sequence submit form"
    submittersname = models.CharField(
        max_length=125, blank=True, null=True, default="Uploaded by default admin user")

    # User corresponding email
    submittersemail = models.EmailField(max_length=70, blank=True, null=True)

    # 2020 Nomenclature New Name
    name = models.CharField(max_length=15, null=True)

    # 1998 Nomenclature name
    oldname = models.CharField(max_length=105, blank=True, null=True)

    # Several different names of the same protein mentioned in the literature by various authors i.e. multiple names for the protein
    # Specially before the Nomenclature system (1998)
    othernames = models.TextField(
        blank=True, null=True)

    # National Center for Biotechnology Information (NCBI) accession number
    # https://www.ncbi.nlm.nih.gov/genbank/sequenceids/
    # https://www.ncbi.nlm.nih.gov/genbank/acc_prefix/
    accession = models.CharField(
        max_length=25, blank=True, null=True, verbose_name="NCBI accession number")

    # Sequence released year
    year = models.CharField(max_length=5, blank=True, null=True)

    # Protein sequence
    sequence = models.TextField(null=True, verbose_name="Protein Sequence")

    # Is it a bacterium sequence?. If the choice is "yes" then name of the
    # bacteria should be in the bacterium textbox. If the choice is "no" then explanation about the source.
    # Note: The BPPRC doesn't normally assign names to proteins that are not
    # of bacterial origin. If user wish to make a special case for the
    # sequence, the explanation can be stored in the text box.
    bacterium = models.BooleanField(
        default=True, choices=TRUE_FALSE_CHOICES, blank=True, null=True)

    # NCBI taxon id
    # https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi
    id_regex = RegexValidator(
        regex=r'\d{1,25}$', message="digits allowed.")
    taxonid = models.CharField(max_length=25, validators=[
                               id_regex], blank=True, null=True)

    bacterium_textbox = models.CharField(max_length=250, blank=True, null=True)

    # Partner protein required for toxicity?. If the choice is "yes", then
    # user can mention name of the protein
    partnerprotein = models.BooleanField(
        default=False, choices=TRUE_FALSE_CHOICES, blank=True, null=True)
    partnerprotein_textbox = models.CharField(
        max_length=250, blank=True, null=True)

    # If toxic to the organism. User can mention the name.
    toxicto = models.CharField(max_length=250, blank=True, null=True)

    # If nontoxic to the organism. User can mention the name.
    nontoxic = models.CharField(max_length=250, blank=True, null=True)

    # Correponding DNA sequence information
    dnasequence = models.TextField(blank=True, null=True)

    # DOI publication or PubMed ID or Publication text
    publication = models.TextField(blank=True, null=True)
    comment = models.TextField(
        blank=True, null=True, verbose_name="User comments")
    date = models.DateField(
        'Uploaded date', default=datetime.date.today, blank=True, null=True)
    uploaded = models.DateTimeField("Uploaded", default=timezone.now)
    # fastasequence_file = models.FileField(
    #     upload_to="fastasequence_files/", storage=OverwriteStorage(), blank=True, null=True)
    name_category = models.CharField(max_length=15, blank=True, null=True)

    # # If the sequence is public or not, based on the boolean operator
    # public = models.BooleanField(default=True, null=True)

    # Protein Data Bank identifier
    # https://proteopedia.org/wiki/index.php/PDB_code
    # https://www.rcsb.org/pages/about-us/index
    pdbcode = models.CharField(max_length=10, blank=True, null=True)
    predict_name = models.TextField(blank=True, null=True)

    # Whether user accepted BPPRC terms & conditions
    terms_conditions = models.BooleanField(
        default=True, choices=TRUE_FALSE_CHOICES, blank=True, null=True)

    # Admin user who submits the sequence
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    # Admin user comments for future reference
    admin_comments = models.TextField(blank=True, null=True)

    # Audit entries details. This is similar to log entry for the sequence
    # Information like who edited the sequence or modified the field are
    # logged automatically
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
        blank=True, null=True
    )
    created_on = models.DateTimeField(
        "Created on", blank=True, null=True, default=timezone.now)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name="%(class)s_edited_by",
    )
    edited_on = models.DateTimeField(
        "Edited on", blank=True, null=True, default=timezone.now)
    published = models.BooleanField(
        default=False, choices=TRUE_FALSE_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Mutant Sequence"
        verbose_name_plural = "Mutant Sequences"

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     self.name_category = re.search(
    #         r"[A-Z][a-z]{2}\d{1,3}", self.name).group()
    #     self.oldname_category = re.search(
    #         r"[A-Z][a-z]{2}\d{1,3}", self.name).group()
    #     # TODO clear out old file before saving new one?
    #     filename = "{}".format(self.name)
    #     file_contents = ">{}\n{}\n".format(self.name, self.sequence)
    #     # print(file_contents)
    #     content = ContentFile(file_contents)
    #     self.fastasequence_file.save(filename, content, save=False)
    #     super().save(*args, **kwargs)

    def category_name(self):
        return self.name[:3]

    def get_fastasequence(self):
        fasta = textwrap.fill(str(self.sequence), 80)
        str_to_write = f"{self.name}\n{fasta}\n"
        return str_to_write

    def get_sequence_length(self):
        return len(self.sequence)

    def get_sequence_aromaticity(self):
        x = ProteinAnalysis(self.sequence)
        return "{0:0.2f}".format(x.aromaticity())

    def get_sequence_molecular_weight(self):
        x = ProteinAnalysis(self.sequence)
        x = x.molecular_weight() / 1000
        # x = x.molecular_weight()
        # return "{0:0.2f}".format(x.molecular_weight())
        return "{0:0.2f}".format(x)

    def get_sequence_instability_index(self):
        x = ProteinAnalysis(self.sequence)
        return "{0:0.2f}".format(x.instability_index())

    def get_sequence_isoelectric_point(self):
        x = ProteinAnalysis(self.sequence)
        return "{0:0.2f}".format(x.isoelectric_point())

    def get_sequence_count_aminoacids(self):
        x = ProteinAnalysis(self.sequence)
        return x.count_amino_acids()  # how to draw histogram

    def get_sequence_get_amino_acids_percent(self):
        x = ProteinAnalysis(self.sequence)
        return x.get_amino_acids_percent()

    def get_secondary_structure(self):
        x = ProteinAnalysis(self.sequence)
        sec_stru = x.secondary_structure_fraction()
        helix = "{0:0.2f}".format(sec_stru[0])
        turn = "{0:0.2f}".format(sec_stru[1])
        sheet = "{0:0.2f}".format(sec_stru[2])
        return helix, turn, sheet


class IdenticalProteins(models.Model):
    # protein1 = models.CharField(max_length=25, blank=True, null=True)
    # protein2 = models.CharField(max_length=25, blank=True, null=True)
    proteins = ArrayField(models.TextField(
        max_length=100000, null=True), default=list)
    #
    # def save(self, *args, **kwargs):
    #     self.proteins.save(proteinlist content, save=False)
    #     super().save(*args, **kwargs)


class Association(models.Model):
    name = models.TextField(blank=True, null=True, verbose_name="Protein Name")
    #sorte = NaturalSortField('name', blank=True, null=True)
    # oldname = models.TextField(blank=True, verbose_name="Old Name")
    # accession = models.TextField(
    #     blank=True, verbose_name="NCBI accession number")
    partnerprotein = models.CharField(
        max_length=255, default="No", editable=True)
    partnerprotein_textbox = models.TextField(
        blank=True, default="No", editable=True)
    target_order = models.TextField(blank=True, null=True)
    target_species = models.TextField(blank=True, null=True)
    activity = models.CharField(max_length=7, default="Yes", editable=True)
    taxonid = models.TextField(blank=True, null=True)
    lc50 = models.TextField(blank=True, null=True)
    units = models.TextField(blank=True, null=True)
    non_toxic = models.TextField(blank=True, null=True)
    percentage_mortality = models.TextField(blank=True, null=True)
    publication = models.TextField(blank=True, null=True)
    other_citations = models.TextField(blank=True, null=True)
    life_stage = models.TextField(blank=True, null=True)
    instar = models.TextField(blank=True, null=True)
    assay_material = models.TextField(blank=True, null=True)
    assay_method = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    data_entered_by = models.TextField(blank=True, null=True)
    date = models.DateField(
        'Uploaded date', default=datetime.date.today, blank=True, null=True)
    # keywords_data = models.ForeignKey(
    #     'KeywordDatabase', on_delete=models.CASCADE, null=True, default=None)

    def __str__(self):
        return self.name

    def get_target_order(self):
        return self.target_order

    def get_target_species(self):
        return self.target_species

    def href(self):
        proteins = PesticidalProteinDatabase.objects.all()
        mutants = MutantProteinDatabase.objects.all()
        for protein in proteins:
            if self.name == protein.name:
                return "/protein_detail/" + protein.name
        for mutant in mutants:
            if self.name == mutant.name:
                return "/mutant_proteins/" + mutant.name
        return ""

    def name_href(self):
        proteins = PesticidalProteinDatabase.objects.all()
        mutants = MutantProteinDatabase.objects.all()
        for protein in proteins:
            if self.name == protein.name:
                return "name"
        for mutant in mutants:
            if self.name == mutant.name:
                return "mutant_name"
        return ""

    # def report(self):
    #     proteins = PesticidalProteinDatabase.objects.all()
    #     mutants = MutantProteinDatabase.objects.all()
        # for protein in proteins:
        #     if self.name == protein.name:
        #         return "/feedback_protein/" + str(protein.id)
        # for mutant in mutants:
        #     if self.name == mutant.name:
        #         return "/feedback_mutant/" + str(mutant.id)

    def starname(self):
        mutants = MutantProteinDatabase.objects.all()
        for mutant in mutants:
            if self.name == mutant.name:
                return "*"
        return None

    def mutant(self):
        proteins = PesticidalProteinDatabase.objects.all()
        mutants = MutantProteinDatabase.objects.all()
        for protein in proteins:
            if self.name == protein.name:
                return False
        for mutant in mutants:
            if self.name == mutant.name:
                return True
        return None

    def get_sequence(self):
        str_to_write = ''
        proteins = PesticidalProteinDatabase.objects.all()
        mutants = MutantProteinDatabase.objects.all()
        for protein in proteins:
            if self.name == protein.name:
                fasta = textwrap.fill(str(protein.sequence), 80)
                # str_to_write = f"{protein.name}\n{fasta}\n"
                str_to_write = f"{fasta}\n"
                return str_to_write
        for mutant in mutants:
            if self.name == mutant.name:
                fasta = textwrap.fill(str(protein.sequence), 80)
                # str_to_write = f"{mutant.name}\n{fasta}\n"
                str_to_write = f"{fasta}\n"
                return str_to_write
        # return str_to_write

    # def related_proteins(self, related_proteins):
    #     #related_proteins = []
    #     return related_proteins

    # def get_database_target_species_as_list(self):
    #     return ', '.join(self.Association.values('target_species', flat=True))
    #
    # def get_database_target_order_as_list(self):
    #     return self.target_order
    #
    # def get_database_taxonid_as_list(self):
    #     return ', '.join(self.Association.values('taxonid', flat=True))
    #
    # def get_target_order(self):
    #     return json.loads(self.target_order)

    class Meta:
        verbose_name = "Meta database"
        verbose_name_plural = "Metadatabase"
        ordering = ['name']


class FeedbackProteinError(models.Model):
    """ """
    name = models.CharField(max_length=75, null=True, blank=True)
    subject = models.CharField(max_length=75, null=True, blank=True)
    email = models.EmailField(max_length=70, null=True, blank=False)
    message = models.TextField(blank=True, null=False)
    uploaded = models.DateTimeField("Uploaded", default=timezone.now)

    def __str__(self):
        return "New Feedback " + self.email

    class Meta:
        verbose_name = "Metadatabase Reported Protein Error"
        verbose_name_plural = "Metadatabase Reported Protein Errors"
