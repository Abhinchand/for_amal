"""Sequence submission form."""

import tempfile
import textwrap

from Bio import SeqIO
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    Column,
    Layout,
    Row,
    Submit,
)
from django import forms

from .models import SendEmail, UserSubmission

# from crispy_forms.bootstrap import AppendedText

RECAPTCHA_PUBLIC_KEY = "6LfdQw8eAAAAALkc59jy4xK4zhlRqBJDJQ1QQWUG"
NEEDLE_CORRECT_SEQ_ERROR_MSG = "please paste correct sequence!"

ALLOWED_AMINOACIDS = {
    "E",
    "Q",
    "L",
    "Y",
    "V",
    "W",
    "I",
    "A",
    "H",
    "G",
    "P",
    "S",
    "R",
    "C",
    "T",
    "F",
    "K",
    "N",
    "D",
    "M",
}


def hasNumbers(sequence: str):
    """Returns whether a string has numbers.

    Args:
        String e.g. 'KFQQVISPWKDVEGSAKQLVKVFDEALKEYKQRYN'

    Returns:
        Boolean data type e.g. False
    """
    return any(char.isdigit() for char in sequence)


def invalidSymbol(sequence: str):
    """Returns whether a string has symbols.

    Args:
        String e.g. 'KFQQVISPWKDVEGSAKQLVKVFDEALKEYKQRYN'
        protein sequence as a string

    Returns:
        Boolean data type e.g. False
    """
    invalidsymbols = ["`", "~", "!", "@", "#", "$"]
    return any(i in sequence for i in invalidsymbols)


def write_sequence_file(sequence: str):
    """Write, validate, and return file name

    Args:
        String e.g. 'KFQQVISPWKDVEGSAKQLVKVFDEALKEYKQRYN'
        protein sequence as a string

    Returns:
        Temporary file name e.g. '/var/folders/7q/fm4'
    """

    # open a temperorary file
    tmp_seq = tempfile.NamedTemporaryFile(mode="wb+", delete=False)

    # if sequence is none raise the ValidationError
    if len(str(sequence.strip())) == 0:
        raise forms.ValidationError(NEEDLE_CORRECT_SEQ_ERROR_MSG)

    # Write fasta sequence
    if str(sequence).strip()[0] != ">":
        tmp_seq.write(">seq1\n".encode())

    tmp_seq.write(sequence.encode())
    tmp_seq.close()
    return tmp_seq.name


def guess_if_protein(seq, thresh=0.99):
    """Guess if the given sequence is Protein or DNA.

    Args:
        file path e.g. '/var/folders/7q/fm4'
        file that has protein sequence or DNA sequence

    Returns:
        Boolean data type e.g. False

    I know below there is another function guess_if_dna. It is reduntant
    I should have used only one. But, I don't have test functions ready yet.
    If I change or improve the functions now, I have to go troubleshoot without
    test. It will be hard.
    """
    # protein_letters = ['C', 'D', 'S', 'Q', 'K','I','P','T','F','N','G',
    #                'H','L','R','W','A','V','E','Y','M']
    dna_letters = ["A", "C", "G", "T"]

    for record in SeqIO.parse(seq, "fasta"):
        seq = record.seq

    seq = seq.upper()
    protein_alpha_count = 0
    for letter in dna_letters:
        protein_alpha_count += seq.count(letter)

    return len(seq) == 0 or float(protein_alpha_count) / float(len(seq)) >= thresh


def guess_if_dna(seq, thresh=0.99):
    """Guess if the given sequence is Protein or DNA.

    Args:
        file path e.g. '/var/folders/7q/fm4'
        file that has protein sequence or DNA sequence

    Returns:
        Boolean data type e.g. False
    """
    # protein_letters = ['C', 'D', 'S', 'Q', 'K','I','P','T','F','N','G',
    #                'H','L','R','W','A','V','E','Y','M']
    protein_letters = ["A", "C", "G", "T"]
    # print(seq)

    for record in SeqIO.parse(seq, "fasta"):
        seq = record.seq

    seq = seq.upper()
    protein_alpha_count = 0
    for letter in protein_letters:
        protein_alpha_count += seq.count(letter)

    return len(seq) == 0 or float(protein_alpha_count) / float(len(seq)) <= thresh


class SendEmailForm(forms.ModelForm):
    """Sequence submission form."""

    submittersname = forms.CharField(
        label="Submitter's Name",
        widget=forms.TextInput(attrs={"placeholder": ""}),
    )

    submittersemail = forms.CharField(
        label="Submitter's Email",
        widget=forms.TextInput(attrs={"placeholder": ""}),
    )

    accession = forms.CharField(
        label="Accession Number",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"placeholder": ""}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(SendEmailForm, self).__init__(*args, **kwargs)

        self.fields["submittersname"].widget.attrs["cols"] = 50
        self.fields["submittersemail"].widget.attrs["cols"] = 50
        self.fields["accession"].widget.attrs["cols"] = 20
        self.fields["message"].widget.attrs["cols"] = 50
        # self.fields['message'].widget.attrs['cols'] = 20

        self.helper = FormHelper()
        self.helper.form_id = "id-SendEmailForm"
        self.helper.form_class = "SendEmailForm"
        self.helper.form_method = "post"
        self.helper.form_action = "contact"
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = SendEmail
        fields = "__all__"


class UserSubmissionForm(forms.ModelForm):
    """Sequence submission form."""

    submittersname = forms.CharField(
        label="Submitter's Name",
        widget=forms.TextInput(attrs={"placeholder": ""}),
    )

    submittersemail = forms.CharField(
        label="Submitter's Email",
        widget=forms.TextInput(attrs={"placeholder": ""}),
    )

    name = forms.CharField(
        label="Your name for the protein",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )

    year = forms.CharField(
        label="Year",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )
    sequence = forms.CharField(
        label="Protein Sequence (plain sequence only)",
        widget=forms.Textarea(attrs={"placeholder": ""}),
        required=True,
    )

    public_or_private = forms.TypedChoiceField(
        label="Do you require the sequence to be maintained privately?",
        coerce=lambda x: x == "True",
        choices=(
            ("", "Select one option"),
            (False, "No"),
            (True, "Yes"),
        ),
        required=True,
    )

    bacterium = forms.ChoiceField(
        choices=((True, "Yes"), (False, "No")),
        label="Bacterium",
        widget=forms.RadioSelect(attrs={"placeholder": ""}),
        initial=True,
        required=False,
    )

    bacterium_textbox = forms.CharField(
        label="Name of source bacterium (ideally taxonid)",
        # label='',
        widget=forms.TextInput(attrs={"placeholder": ""}),
    )

    accession = forms.CharField(
        label="Genbank accession Number",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=True,
    )

    dnasequence = forms.CharField(
        label="DNA Sequence (plain sequence only)",
        widget=forms.Textarea(attrs={"placeholder": ""}),
    )

    partnerprotein = forms.ChoiceField(
        label="Partner Protein required for toxicity?",
        choices=((True, "Yes"), (False, "No")),
        widget=forms.RadioSelect(),
        initial=False,
        required=False,
    )

    partnerprotein_textbox = forms.CharField(
        label="Partner Protein Name",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )

    toxicto = forms.CharField(
        label="Toxic to",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )

    nontoxic = forms.CharField(
        label="Nontoxic to",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )
    pdbcode = forms.CharField(
        label="PDB code",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )

    publication = forms.CharField(
        label="Publication",
        widget=forms.Textarea(attrs={"placeholder": ""}),
        required=False,
    )

    comment = forms.CharField(
        label="Comments",
        widget=forms.Textarea(attrs={"placeholder": ""}),
        required=False,
    )

    terms_conditions = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"size": "10"}),
        label="By using our service and submitting your sequences of pesticidal proteins to us, you agree to the following:  You acknowledge that our services are being provided on our regularly operating IT systems, and we cannot guarantee the complete security of your submission.  OUR SERVICE IS PROVIDED ???AS IS???.  WE EXPRESSLY DISCLAIM ALL WARRANTIES WITH RESPECT TO THE SERVICES.  WE MAKE NO WARRANTIES OR GUARANTEES WHATSOEVER, EXPRESS OR IMPLIED, INCLUDING, ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.  WE ARE NOT LIABLE FOR ANY USE OF THE SERVICES, OR FOR ANY LOSS, CLAIM, DAMAGE, OR LIABILITY OF ANY KIND OR NATURE WHICH MAY ARISE FROM OR IN CONNECTION WITH THIS SERVICE OR OUR STORAGE OF YOUR SUBMISSION.",
    )

    def __init__(self, *args, **kwargs):
        super(UserSubmissionForm, self).__init__(*args, **kwargs)

        self.fields["sequence"].widget.attrs["cols"] = 50
        # self.fields['sequence'].widget.attrs['cols'] = 20
        self.fields["bacterium_textbox"].widget.attrs["cols"] = 10
        self.fields["comment"].widget.attrs["cols"] = 50
        # self.fields['comment'].widget.attrs['cols'] = 20

        self.fields["toxicto"].label = "Toxic to"
        self.helper = FormHelper()
        self.helper.form_id = "id-UserSubmissionForm"
        self.helper.form_class = "UserSubmissionForm"
        self.helper.form_method = "post"
        self.helper.form_action = "submit"
        self.helper.add_input(Submit("submit", "Submit"))

        self.helper.layout = Layout(
            Row(
                Column(
                    "submittersname",
                    css_class="form-group col-md-6 mb-0",
                ),
                Column(
                    "submittersemail",
                    css_class="form-group col-md-6 mb-0",
                ),
                css_class="form-row",
            ),
            Row(
                Column("name", css_class="form-group col-md-10 mb-0"),
                Column("year", css_class="form-group col-md-2 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("bacterium", css_class="form-group col-md-2 mb-0"),
                Column(
                    "bacterium_textbox",
                    css_class="form-group col-md-6 mb-0",
                ),
                # Column('taxonid',
                #        css_class='form-group col-md-5 mb-0'),
                css_class="form-row",
            ),
            Row(
                Column("accession", css_class="form-group col-md-3 mb-0"),
                css_class="form-row",
            ),
            "dnasequence",
            "sequence",
            "public_or_private",
            Row(
                Column(
                    "partnerprotein",
                    css_class="form-group col-md-3 mb-0",
                ),
                Column(
                    "partnerprotein_textbox",
                    css_class="form-group col-md-9 mb-0",
                ),
                css_class="form-row",
            ),
            "toxicto",
            "nontoxic",
            "pdbcode",
            "publication",
            "comment",
            "terms_conditions",
            HTML(
                '<div class="form-group col-md-6"><div class="g-recaptcha" data-sitekey="%s"></div></div>'
                % RECAPTCHA_PUBLIC_KEY
            ),
            # ButtonHolder(
            #     Submit('submit', 'Submit')
            # )
        )

    def clean_sequence(self):
        sequence_in_form = self.cleaned_data["sequence"]

        # invalidsymbols = invalid_symbol(sequence_in_form)
        if invalidSymbol(sequence_in_form):
            raise forms.ValidationError(
                "There are invalid symbols in the sequence")

        if hasNumbers(sequence_in_form):
            raise forms.ValidationError(
                "There are numbers in the sequence. Please paste protein sequence only")

        if sequence_in_form:
            filename = write_sequence_file(sequence_in_form)
            sequence_is_protein = guess_if_protein(filename)

        if not sequence_in_form:
            raise forms.ValidationError("Please paste valid protein sequences")

        if sequence_is_protein:
            raise forms.ValidationError(
                "Please paste only protein sequences here")
        # print(self.cleaned_data)
        formatted_sequence = textwrap.fill(sequence_in_form, 60)

        return formatted_sequence

    def clean_dnasequence(self):
        dnasequence_in_form = self.cleaned_data["dnasequence"]

        if invalidSymbol(dnasequence_in_form):
            raise forms.ValidationError(
                "There are invalid symbols in the sequence")

        if hasNumbers(dnasequence_in_form):
            raise forms.ValidationError(
                "There are numbers in the sequence. Please paste DNA sequence only")

        if dnasequence_in_form:
            filename = write_sequence_file(dnasequence_in_form)
            sequence_is_dna = guess_if_dna(filename)

        if not dnasequence_in_form:
            raise forms.ValidationError("Please paste valid DNA sequences")

        if sequence_is_dna:
            raise forms.ValidationError("Please paste only DNA sequences here")

        formatted_dnasequence = textwrap.fill(dnasequence_in_form, 60)

        return formatted_dnasequence

    class Meta:
        model = UserSubmission
        fields = [
            "submittersname",
            "submittersemail",
            "name",
            "year",
            "sequence",
            "public_or_private",
            "bacterium",
            "bacterium_textbox",
            "accession",
            "dnasequence",
            "partnerprotein",
            "partnerprotein_textbox",
            "toxicto",
            "nontoxic",
            "pdbcode",
            "publication",
            "comment",
            "terms_conditions",
        ]


# ToxicToFormSet = modelformset_factory(
#     UserSubmission,
#     fields=('toxicto',),
#     extra=1,
#     widgets={'name': forms.TextInput(attrs={
#         'placeholder': 'Toxic to'
#     })
#     }
#
#
# )
#
#
# class ToxicFormSetHelper(FormHelper):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.form_method = 'post'
#         self.layout = Layout(
#             'toxicto'
#         )
#         self.render_required_fields = False
