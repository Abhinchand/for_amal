from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    Column,
    Layout,
    Row,
    Submit,
)
from django import forms
from association.models import FeedbackProteinError
from django.core.validators import MinLengthValidator

RECAPTCHA_PUBLIC_KEY = "6LfdQw8eAAAAALkc59jy4xK4zhlRqBJDJQ1QQWUG"


class SearchForm(forms.Form):
    """
    Search Toxicity and Non toxicity data for pesticidal
    proteins.

    Either check localserver or
    http://127.0.0.1:8000/search_association/
    Live server link
    https://camtech-bpp.ifas.ufl.edu/search_data_association/

    One CharField for search_term
       - e.g. Cry1Aa1 (Pesticidal Protein Name)
       - e.g. 689277 (Target species taxon id)
       - e.g. Chrysodeixis includens (Target Species)
       - e.g. Lepidoptera (Target Order)

    Four ChoiceField for search_fields
       - Pesticidal Protein Name
       - Target species taxon id
       - Target Species
       - Target Order

    django-crispy-forms are used here.

    See association.views for more information.
    """

    SEARCH_CHOICES = (
        ("pesticidal protein name", "Pesticidal Protein Name"),
        ("target species taxon id", "Target species taxon id"),
        ("target species", "Target Species"),
        ("target order", "Target Order"),
    )

    search_term = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Search"}),
    )
    search_fields = forms.ChoiceField(choices=SEARCH_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["search_term"].error_messages = {
            "required": "Please type a protein name"}
        self.fields["search_term"].label = "Search term"

        validators = [v for v in self.fields["search_term"].validators if not isinstance(
            v, MinLengthValidator)]
        min_length = 3
        validators.append(MinLengthValidator(min_length))
        self.fields["search_term"].validators = validators

        # self.fields['search_term'].min_length = 3
        self.fields["search_fields"].label = ""
        self.helper = FormHelper()
        self.helper.form_id = "id-SearchForm"
        self.helper.form_class = "SearchForm"
        self.helper.form_method = "post"
        self.helper.form_action = "search_database"
        self.helper.add_input(Submit("submit", "Submit"))
        self.helper.layout = Layout(
            Row(
                Column(
                    "search_term",
                    css_class="form-group input-group-append col-md-6",
                ),
                css_class="form-row",
            ),
            Row(
                Column("search_fields", css_class="form-group col-md-6"),
                css_class="form-row",
            ),
        )


class FeedbackProteinForm(forms.ModelForm):
    """
    Toxicity and Non toxicity data for pesticidal proteins
    lists the protein based on the search_term and search_fields

    Each protein data have an option where users can report
    errors in it. Report error send email url option picks up the
    data id and redirects this form where users can submit their
    name, email and a message. Admin data are stored as
    "Metadatabase Reported Protein Error"

    """
    name = forms.CharField(
        label="Submitter's Name",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=True,
    )

    subject = forms.CharField(
        label="Subject: Protein id",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=False,
    )

    email = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        required=True,
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"placeholder": ""}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(FeedbackProteinForm, self).__init__(*args, **kwargs)
        self.fields['subject'].disabled = True

        self.helper = FormHelper()
        self.helper.form_id = "id-FeedbackForm"
        self.helper.form_class = "FeedbackForm"
        self.helper.form_method = "post"
        self.helper.form_action = "feedback_home"
        self.helper.add_input(Submit("submit", "Submit"))

        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("subject", css_class="form-group mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("email", css_class="form-group mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("message", css_class="form-group mb-0"),
                css_class="form-row",
            ),
            HTML(
                '<div class="form-group col-md-6"><div class="g-recaptcha" data-sitekey="%s"></div></div>'
                % RECAPTCHA_PUBLIC_KEY
            ),
        )

    def clean_subject(self):
        if self.instance:
            return self.instance.subject
        else:
            return self.fields['subject']

    def clean(self):
        name = self.cleaned_data["name"]
        subject = self.cleaned_data['subject']
        message = self.cleaned_data["message"]
        email = self.cleaned_data["email"]

    class Meta:
        model = FeedbackProteinError
        fields = '__all__'


class DownloadMutantForm(forms.Form):
    mutant = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices="",
        label="",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(DownloadMutantForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "mutant"
        self.helper.form_class = "mutantform"
        self.helper.form_method = "post"
        self.helper.form_action = "mutant_download"

        self.helper.add_input(Submit("submit", "Download"))

        self.category_options = [("mutant", "mutant")]

        self.fields["mutant"].choices = self.category_options
        self.fields["mutant"].label = ""


# class UserSubmissionToxicityDataForm(forms.ModelForm):
#     """Sequence submission form."""
#     submittersname = forms.CharField(
#         label="Submitter's Name",
#         widget=forms.TextInput(
#             attrs={'placeholder': ''})
#     )
#
#     submittersemail = forms.CharField(
#         label="Submitter's Email",
#         widget=forms.TextInput(
#             attrs={'placeholder': ''})
#     )
#
#     name = forms.CharField(
#         label='Your name for the protein',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#
#     year = forms.CharField(
#         label='Year',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#     sequence = forms.CharField(
#         label='Protein Sequence',
#         widget=forms.Textarea(
#             attrs={'placeholder': ""}),
#         required=True
#     )
#
#     public_or_private = forms.TypedChoiceField(
#         label='Do you require the sequence to be maintained privately?',
#         coerce=lambda x: x == 'True',
#         choices=(('', 'Select one option'), (False, 'Yes'), (True, 'No')),
#         required=True
#     )
#
#     bacterium = forms.ChoiceField(
#         choices=((True, "Yes"), (False, "No")),
#         label='Bacterium',
#         widget=forms.RadioSelect(
#             attrs={'placeholder': ''}
#         ),
#         initial=True,
#         required=False,
#     )
#
#     bacterium_textbox = forms.CharField(
#         label='Name of source bacterium (ideally taxonid)',
#         # label='',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''})
#     )
#
#     accession = forms.CharField(
#         label='Genbank accession Number',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''}),
#         required=True
#     )
#
#     dnasequence = forms.CharField(
#         label='DNA Sequence',
#         widget=forms.Textarea(
#             attrs={'placeholder': ""})
#     )
#
#     partnerprotein = forms.ChoiceField(
#         label='Partner Protein required for toxicity?',
#         choices=((True, "Yes"), (False, "No")),
#         widget=forms.RadioSelect(),
#         initial=False,
#         required=False,
#     )
#
#     partnerprotein_textbox = forms.CharField(
#         label='Partner Protein Name',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#
#     toxicto = forms.CharField(
#         label='Toxic to',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#
#     nontoxic = forms.CharField(
#         label='Nontoxic to',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#     pdbcode = forms.CharField(
#         label='PDB code',
#         widget=forms.TextInput(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#
#     publication = forms.CharField(
#         label='Publication',
#         widget=forms.Textarea(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#
#     comment = forms.CharField(
#         label='Comments',
#         widget=forms.Textarea(
#             attrs={'placeholder': ''}),
#         required=False
#     )
#
#     terms_conditions = forms.BooleanField(
#         required=True,
#         widget=forms.CheckboxInput(attrs={'size': '10'}),
#         label='By using our service and submitting your sequences of pesticidal proteins to us, you agree to the following:  You acknowledge that our services are being provided on our regularly operating IT systems, and we cannot guarantee the complete security of your submission.  OUR SERVICE IS PROVIDED ???AS IS???.  WE EXPRESSLY DISCLAIM ALL WARRANTIES WITH RESPECT TO THE SERVICES.  WE MAKE NO WARRANTIES OR GUARANTEES WHATSOEVER, EXPRESS OR IMPLIED, INCLUDING, ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.  WE ARE NOT LIABLE FOR ANY USE OF THE SERVICES, OR FOR ANY LOSS, CLAIM, DAMAGE, OR LIABILITY OF ANY KIND OR NATURE WHICH MAY ARISE FROM OR IN CONNECTION WITH THIS SERVICE OR OUR STORAGE OF YOUR SUBMISSION.'
#     )
#
#     def __init__(self, *args, **kwargs):
#         super(UserSubmissionForm, self).__init__(*args, **kwargs)
#
#         self.fields['sequence'].widget.attrs['cols'] = 50
#         # self.fields['sequence'].widget.attrs['cols'] = 20
#         self.fields['bacterium_textbox'].widget.attrs['cols'] = 10
#         self.fields['comment'].widget.attrs['cols'] = 50
#         # self.fields['comment'].widget.attrs['cols'] = 20
#
#         self.fields['toxicto'].label = 'Toxic to'
#         self.helper = FormHelper()
#         self.helper.form_id = 'id-UserSubmissionForm'
#         self.helper.form_class = 'UserSubmissionForm'
#         self.helper.form_method = 'post'
#         self.helper.form_action = 'submit'
#         self.helper.add_input(Submit('submit', 'Submit'))
#
#         self.helper.layout = Layout(
#             Row(
#                 Column('submittersname',
#                        css_class='form-group col-md-6 mb-0'),
#                 Column('submittersemail',
#                        css_class='form-group col-md-6 mb-0'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('name',
#                        css_class='form-group col-md-10 mb-0'),
#                 Column('year',
#                        css_class='form-group col-md-2 mb-0'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('bacterium',
#                        css_class='form-group col-md-2 mb-0'),
#                 Column('bacterium_textbox',
#                        css_class='form-group col-md-6 mb-0'),
#                 # Column('taxonid',
#                 #        css_class='form-group col-md-5 mb-0'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('accession',
#                        css_class='form-group col-md-3 mb-0'),
#                 css_class='form-row'
#             ),
#             'dnasequence',
#             'sequence',
#             'public_or_private',
#             Row(
#                 Column('partnerprotein',
#                        css_class='form-group col-md-3 mb-0'),
#                 Column('partnerprotein_textbox',
#                        css_class='form-group col-md-9 mb-0'),
#                 css_class='form-row'
#             ),
#             'toxicto',
#             'nontoxic',
#             'pdbcode',
#             'publication',
#             'comment',
#             'terms_conditions',
#             HTML('<div class="form-group col-md-6"><div class="g-recaptcha" data-sitekey="%s"></div></div>' %
#                  RECAPTCHA_PUBLIC_KEY),
#             # ButtonHolder(
#             #     Submit('submit', 'Submit')
#             # )
#
#         )
#
#     def clean_sequence(self):
#         sequence_in_form = self.cleaned_data['sequence']
#
#         #invalidsymbols = invalid_symbol(sequence_in_form)
#         if invalidSymbol(sequence_in_form):
#             raise forms.ValidationError(
#                 "There are invalid symbols in the sequence")
#
#         if hasNumbers(sequence_in_form):
#             raise forms.ValidationError(
#                 "There are numbers in the sequence. Please paste protein sequence only")
#
#         if sequence_in_form:
#             filename = write_sequence_file(sequence_in_form)
#             sequence_is_protein = guess_if_protein(filename)
#
#         if not sequence_in_form:
#             raise forms.ValidationError("Please paste valid protein sequences")
#
#         if sequence_is_protein:
#             raise forms.ValidationError(
#                 "Please paste only protein sequences here")
#         # print(self.cleaned_data)
#         formatted_sequence = textwrap.fill(sequence_in_form, 60)
#
#         return formatted_sequence
#
#     def clean_dnasequence(self):
#         dnasequence_in_form = self.cleaned_data['dnasequence']
#
#         if invalidSymbol(dnasequence_in_form):
#             raise forms.ValidationError(
#                 "There are invalid symbols in the sequence")
#
#         if hasNumbers(dnasequence_in_form):
#             raise forms.ValidationError(
#                 "There are numbers in the sequence. Please paste DNA sequence only")
#
#         if dnasequence_in_form:
#             filename = write_sequence_file(dnasequence_in_form)
#             sequence_is_dna = guess_if_dna(filename)
#
#         if not dnasequence_in_form:
#             raise forms.ValidationError("Please paste valid DNA sequences")
#
#         if sequence_is_dna:
#             raise forms.ValidationError(
#                 "Please paste only DNA sequences here")
#
#         formatted_dnasequence = textwrap.fill(dnasequence_in_form, 60)
#
#         return formatted_dnasequence
#
#     class Meta:
#         model = UserSubmissionDataAssociation
#         fields = ['submittersname',
#                   'submittersemail',
#                   'name',
#                   'year',
#                   'sequence',
#                   'public_or_private',
#                   'bacterium',
#                   'bacterium_textbox',
#                   'accession',
#                   'dnasequence',
#                   'partnerprotein',
#                   'partnerprotein_textbox',
#                   'toxicto',
#                   'nontoxic',
#                   'pdbcode',
#                   'publication',
#                   'comment',
#                   'terms_conditions']
