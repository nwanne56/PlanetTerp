from django.core.exceptions import ValidationError
from django.forms import CharField, IntegerField, DateField, ChoiceField
from django.forms.widgets import DateInput, HiddenInput, TextInput
from django.forms import Form, ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Button, HTML
from crispy_forms.bootstrap import FormActions, UneditableField

from .layout_objects.bootstrap_modal import BootstrapModal
from home.utils import AdminAction, slug_in_use_err
from home.models import Review, Professor
from planetterp.settings import DATE_FORMAT

# For verifying unverified reviews in admin panel
class ReviewVerifyForm(Form):
    review_id = IntegerField(required=True, widget=HiddenInput)
    verified = CharField(required=True, widget=HiddenInput, initial=Review.Status.VERIFIED.value)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.REVIEW_VERIFY.value)

    def __init__(self, review_id, **kwargs):
        super().__init__(**kwargs)
        self.fields['review_id'].initial = review_id

        self.helper = FormHelper()
        self.helper.form_id = f"{Review.Status.VERIFIED.value}_{review_id}"
        self.helper.form_class = "unverified_review_form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        submit_button = Button(
            "verify",
            "Verify",
            css_class="btn-success",
            style="border-bottom-right-radius: 0; border-top-right-radius: 0;",
            onClick=f"verifyReview('#{self.helper.form_id}')"
        )
        return Layout(
            'review_id',
            'verified',
            'action_type',
            FormActions(submit_button)
        )

# For rejecting unverified reviews
class ReviewRejectForm(Form):
    review_id = IntegerField(required=True, widget=HiddenInput)
    verified = CharField(required=True, widget=HiddenInput, initial=Review.Status.REJECTED.value)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.REVIEW_VERIFY.value)

    def __init__(self, review_id, **kwargs):
        super().__init__(**kwargs)
        self.fields['review_id'].initial = review_id

        self.helper = FormHelper()
        self.helper.form_id = f"{Review.Status.REJECTED.value}_{review_id}"
        self.helper.form_class = "unverified_review_form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        submit_button = Button(
            "reject",
            "Reject",
            css_class="btn-danger",
            style="border-bottom-left-radius: 0; border-top-left-radius: 0;",
            onClick=f"verifyReview('#{self.helper.form_id}')"
        )
        return Layout(
            'review_id',
            'verified',
            'action_type',
            FormActions(submit_button)
        )

# For sending a help webhook of an unverified review
class ReviewHelpForm(Form):
    review_id = IntegerField(required=True, widget=HiddenInput)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.REVIEW_HELP.value)

    def __init__(self, review_id, **kwargs):
        super().__init__(**kwargs)
        self.fields['review_id'].initial = review_id

        self.helper = FormHelper()
        self.helper.form_id = f"{AdminAction.REVIEW_HELP.value}_{review_id}"
        self.helper.form_class = "unverified_review_form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        submit_button = Button(
            "help",
            "Help",
            css_class="btn-warning",
            onClick=f"sendResponse($('#{self.helper.form_id}').serialize(), 'review_help')"
        )
        return Layout(
            'review_id',
            'action_type',
            FormActions(submit_button)
        )

# For unverifying a verified review. Currently used on /professor
class ReviewUnverifyForm(Form):
    review_id = IntegerField(required=True, widget=HiddenInput)
    verified = CharField(required=True, widget=HiddenInput, initial=Review.Status.PENDING.value)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.REVIEW_VERIFY.value)

    def __init__(self, review_id, **kwargs):
        super().__init__(**kwargs)
        self.fields['review_id'].initial = review_id

        self.helper = FormHelper()
        self.helper.form_id = f"unverify_review_{review_id}"
        self.helper.form_class = "unverify_review"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        submit_button = Button(
            "unverify",
            "Unverify",
            css_class="btn-danger btn-lg",
            onClick=f"unverifyReview('#{self.helper.form_id}')"
        )
        return Layout(
            'review_id',
            'verified',
            'action_type',
            FormActions(submit_button)
        )

# For verifying unverified professors
class ProfessorVerifyForm(Form):
    professor_id = IntegerField(required=True, widget=HiddenInput)
    verified = CharField(required=True, widget=HiddenInput, initial=Professor.Status.VERIFIED.value)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.PROFESSOR_VERIFY.value)

    def __init__(self, professor_id, **kwargs):
        super().__init__(**kwargs)
        self.fields['professor_id'].initial = professor_id

        self.helper = FormHelper()
        self.helper.form_id = f"{Professor.Status.VERIFIED.value}_{professor_id}"
        self.helper.form_class = "unverified_professor_form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        submit_button = Button(
            "verify",
            "Verify",
            css_class="btn-success rounded-left",
            style="border-bottom-right-radius: 0; border-top-right-radius: 0;",
            onClick=f"verifyProfessor('#{self.helper.form_id}')"
        )
        return Layout(
            'professor_id',
            'verified',
            'action_type',
            FormActions(submit_button)
        )

# For rejecting unverified professors
class ProfessorRejectForm(Form):
    professor_id = IntegerField(required=True, widget=HiddenInput)
    verified = CharField(required=True, widget=HiddenInput, initial=Professor.Status.REJECTED.value)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.PROFESSOR_VERIFY.value)

    def __init__(self, professor_id, **kwargs):
        super().__init__(**kwargs)
        self.fields['professor_id'].initial = professor_id

        self.helper = FormHelper()
        self.helper.form_id = f"{Professor.Status.REJECTED.value}_{professor_id}"
        self.helper.form_class = "unverified_professor_form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        submit_button = Button(
            "reject",
            "Reject",
            css_class="btn-danger rounded-right",
            style="border-bottom-left-radius: 0; border-top-left-radius: 0;",
            onClick=f"verifyProfessor('#{self.helper.form_id}')"
        )
        return Layout(
            'professor_id',
            'verified',
            'action_type',
            FormActions(submit_button)
        )

# For deleting unverified professors. This action cannot be undone.
# Use carefully: Once a professor is deleted, all their data is lost
# and cannot be retrived!
class ProfessorDeleteForm(Form):
    professor_id = IntegerField(required=True, widget=HiddenInput)
    professor_type = CharField(required=True, widget=HiddenInput)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.PROFESSOR_DELETE.value)

    def __init__(self, professor: Professor, **kwargs):
        super().__init__(**kwargs)
        self.fields['professor_id'].initial = professor.pk
        self.fields['professor_type'].initial = professor.type

        self.helper = FormHelper()
        self.helper.form_id = f"delete_{professor.pk}"
        self.helper.form_class = "unverified_professor_form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        submit_button = Button(
            "delete",
            "Delete",
            css_class="btn-dark",
            onClick=f"deleteProfessor('#{self.helper.form_id}')"
        )
        return Layout(
            'professor_id',
            'professor_type',
            'action_type',
            FormActions(submit_button)
        )

# For manually entering a professor's slug when
# the system couldn't automatically generate one
class ProfessorSlugForm(Form):
    slug = CharField(required=False, widget=TextInput, label=False)
    professor_id = IntegerField(required=True, widget=HiddenInput)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.PROFESSOR_SLUG.value)

    def __init__(self, professor: Professor, modal_title="", **kwargs):
        super().__init__(**kwargs)
        self.professor = professor
        self.modal_title = modal_title
        self.fields['professor_id'].initial = self.professor.pk

        self.helper = FormHelper()
        self.helper.form_id = f"slug-form-{self.professor.pk}"
        self.helper.form_class = "slug-form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        slug_errors = HTML(
            '''
            {% if form.slug.errors %}
                <div id="slug_errors" class="invalid-feedback" style="font-size: 15px">
                    {{ form.slug.errors|striptags }}
                </div>
            {% endif %}
            '''
        )
        return Layout(
            BootstrapModal(
                Field(
                    'slug',
                    id=f"slug-form-slug-{self.professor.pk}",
                    placeholder="Enter a slug"
                ),
                slug_errors,
                Field(
                    'professor_id',
                    id=f"slug-form-id-{self.professor.pk}"
                ),
                'action_type',
                FormActions(
                    Button(
                        "done",
                        "Done",
                        id=f"submit-slug-form-{self.professor.pk}",
                        css_class="btn-primary float-right mt-3",
                        onClick=f"verifySlug('#slug-form-{self.professor.pk}')"
                    )
                ),
                css_id=f"slug-modal-{self.professor.pk}",
                title_id=f"slug-modal-label-{self.professor.pk}",
                title=self.modal_title
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        slug = str(cleaned_data.get("slug"))

        slug = slug.lower().strip().replace(" ", "_")
        professor = Professor.objects.filter(slug=slug).first()

        if slug == '' or slug.isspace():
            error_msg = "You must enter a slug"
            error = ValidationError(error_msg, code='Empty')
            self.add_error('slug', error)

        if professor:
            error_msg = slug_in_use_err(slug, professor.name)
            error = ValidationError(error_msg, code='Exists')
            self.add_error('slug', error)

        return cleaned_data

# For editing a professor via the professor
# feature on /professor
class ProfessorUpdateForm(ModelForm):
    # Only reason I explicitly declare name, slug, and type
    #   as form fields is to remove the form_suffix. Doing
    #   this overrides the model field so I need to explicitly
    #   state the choices for the type field.
    name = CharField(
        required=False,
        label_suffix=None
    )

    slug = CharField(
        required=False,
        label_suffix=None
    )

    type = ChoiceField(
        required=False,
        label_suffix=None,
        choices=[(tup[0],tup[0]) for tup in Professor.Type.choices]
    )

    created_at = DateField(
        required=False,
        label_suffix=None,
        label="Date Created",
        disabled=True,
        widget=DateInput(format=DATE_FORMAT)
    )

    professor_id = CharField(
        required=False,
        label_suffix=None,
        label="ID",
        disabled=True
    )

    action_type = CharField(
        required=True,
        widget=HiddenInput,
        initial=AdminAction.PROFESSOR_EDIT.value
    )

    # Using the 'disabled' option removes the field from
    # the POST data. This work-around is neccessary as long
    # as the slug isn't unique.
    hidden_professor_id = IntegerField(
        required=True,
        widget=HiddenInput
    )

    class Meta:
        model = Professor
        exclude = ['status']

    def __init__(self, professor: Professor, **kwargs):
        super().__init__(**kwargs)
        self.professor = professor
        self.helper = FormHelper()
        self.helper.form_id = "edit-professor-form"
        self.helper.form_show_errors = False
        self.field_responses = self.create_field_responses()

        self.fields['created_at'].initial = self.professor.created_at
        self.fields['professor_id'].initial = self.professor.pk
        self.fields['hidden_professor_id'].initial = self.professor.pk

        self.helper.layout = self.generate_layout()

    def create_field_responses(self):
        field_response = {}
        for field in self.fields.keys():
            response_html = f'<div id="{field}_response" class="invalid-feedback text-center" style="font-size: 12px">{{{{ form.{field}.errors|striptags }}}}</div>'
            field_response[field] = HTML(response_html)

        return field_response

    def generate_layout(self):
        layout = Layout(
            BootstrapModal(
                'action_type',
                'hidden_professor_id',
                Div(
                    Div(
                        Field('name', id="edit_name"),
                        self.field_responses['name'],
                        css_class="form-group col-md-8"
                    ),
                    Div(
                        Field('slug', id="edit_slug"),
                        self.field_responses['slug'],
                        css_class="form-group col-md-4"
                    ),
                    css_class="form-row"
                ),
                Div(
                    Div(
                        Field('type', id="edit_type"),
                        self.field_responses['type'],
                        css_class="form-group col-md-4"
                    ),
                    Div(
                        UneditableField('created_at'),
                        css_class="form-group col-md-4"
                    ),
                    Div(
                        UneditableField('professor_id'),
                        css_class="form-group col-md-4"
                    ),
                    css_class="form-row"
                ),
                Div(
                    Button(
                        'update',
                        'Update',
                        css_id="update-professor",
                        css_class="btn-primary",
                        onClick='sendResponse($("#edit-professor-form").serialize(), "professor_edit");'
                    ),
                    Button(
                        'merge',
                        'Merge',
                        css_id="merge-professor",
                        css_class="btn-secondary"
                    ),
                    Button(
                        'unverify',
                        'Unverify',
                        css_class="btn-danger",
                        onClick='sendResponse($("#unverify-professor-form").serialize(), "professor_verify");'
                    ),
                    css_class="btn-group mt-3 float-right"
                ),
                css_id="edit-professor-modal",
                title_id="edit-professor-label",
                title=f'Viewing info for {self.professor.name}. Click a field to edit its contents.'
            )
        )
        return layout

    def clean(self):
        cleaned_data = super().clean()
        professor_id = int(cleaned_data.get("hidden_professor_id"))
        name = str(cleaned_data.get("name"))
        slug = str(cleaned_data.get("slug"))

        professor = Professor.objects.get(pk=professor_id)

        if not (name.strip() == "" or name == professor.name):
            professor_obj = Professor.objects.filter(name=name).exclude(pk=professor_id)

            if professor_obj.exists():
                error_msg = "A professor with this name already exists"
                error = ValidationError(error_msg, code='Exists')
                self.add_error('name', error)
            else:
                cleaned_data['name'] = name.strip()
        else:
            cleaned_data['name'] = professor.name.strip().lower().replace(" ", "_")


        if not (slug.strip() == "" or slug == professor.slug):
            professor_obj = Professor.objects.filter(slug=slug).exclude(pk=professor_id)

            if professor_obj.exists():
                error_msg = slug_in_use_err(slug, professor_obj.first().name)
                error = ValidationError(error_msg, code='Exists')
                self.add_error('slug', error)
            else:
                cleaned_data['slug'] = slug.strip().lower().replace(" ", "_")
        else:
            cleaned_data['slug'] = professor.slug.strip().lower().replace(" ", "_")


        return cleaned_data

# For unverifying a professor in the edit professor modal
# on /professor
class ProfessorUnverifyForm(Form):
    professor_id = IntegerField(required=True, widget=HiddenInput)
    action_type = CharField(required=True, widget=HiddenInput, initial=AdminAction.PROFESSOR_VERIFY.value)
    verified = CharField(required=True, widget=HiddenInput, initial=Professor.Status.PENDING.value)

    def __init__(self, professor_id, **kwargs):
        super().__init__(**kwargs)
        self.fields['professor_id'].initial = professor_id
        self.helper = FormHelper()
        self.helper.form_id = "unverify-professor-form"
        self.helper.form_show_errors = False
        self.helper.layout = self.generate_layout()

    def generate_layout(self):
        return Layout(
            'professor_id',
            'action_type',
            'verified'
        )

# For merging two professors together. The optional merge_subject
# param is used on /professor to pre-fill the merge_subject
# field on the form.
# merge_subject = Professor being merged. Will be deleted afterwards.
# merge_target = Professor that will contain all the subject's data. Will remain afterwards.
class ProfessorMergeForm(Form):
    action_type = CharField(
        required=True,
        widget=HiddenInput,
        initial=AdminAction.PROFESSOR_MERGE.value
    )

    merge_subject = CharField(
        required=False
    )

    subject_id = IntegerField(
        required=True,
        widget=HiddenInput
    )

    merge_target = CharField(
        required=False
    )

    target_id = IntegerField(
        required=True,
        widget=HiddenInput
    )

    source_page = CharField(
        required=False,
        widget=HiddenInput
    )

    def __init__(self, request, merge_subject: Professor=None, use_large_inputs=False, **kwargs):
        super().__init__(**kwargs)
        self.input_css_classes = "form-control-lg" if use_large_inputs else ""
        self.button_css_classes = "btn-lg w-100" if use_large_inputs else ""

        self.helper = FormHelper()
        self.helper.form_id = "merge-professor-form"
        self.helper.form_show_errors = False
        self.helper.form_show_labels = False
        self.helper.layout = self.generate_layout()

        if request:
            self.fields['source_page'].initial = request.path

        # subject_id and/or target_id have hard-coded negative values to determine if the input belongs to a real professor.
        # If it does, the value will be replaced with that professor's id. These values must be different or the validation
        # will think the inputs are the same and return an error. These values must also be negative because a professor
        # could have an id of any non-negative number.
        if merge_subject:
            self.professor = merge_subject
            self.fields['merge_subject'].initial = merge_subject.name
            self.fields['subject_id'].initial = merge_subject.pk
            self.fields['target_id'].initial = "-1"
        else:
            self.fields['subject_id'].initial = "-1"
            self.fields['target_id'].initial = "-2"

    def generate_layout(self):
        layout = Layout(
            'source_page',
            'action_type',
            HTML(
                '''
                <div id="merge-professor-errors" class="merge-errors invalid-feedback hidden text-center mb-1">
                    {% if form.merge_subject.errors or form.merge_subject.errors and form.merge_target.errors %}
                        {{ form.merge_subject.errors|striptags }}
                    {% elif form.merge_target.errors %}
                        {{ form.merge_target.errors|striptags }}
                    {% endif %}
                </div>
                '''
            ),
            Div(
                Div(
                    # font-awesome icons don't render with the crispy_forms Button()
                    # element so this was my work around.
                    HTML(
                        '''
                        <button class="btn btn-outline-secondary fas fa-question-circle" type="button"
                        data-toggle="tooltip" data-placement="left"
                        title="All data for the instructor on the left will be merged into the
                        instructor on the right. The instructor on the left will be
                        deleted after the merge."></button>

                        <button class="btn btn-outline-secondary fas fa-sync-alt" type="button"
                        data-toggle="tooltip" data-placement="top" title="Swap inputs"
                        onclick="swapInputs()"></button>
                        '''
                    ),
                    css_class="input-group-prepend"
                ),
                Field(
                    'merge_subject',
                    placeholder="Merge Subject",
                    type="search",
                    css_class="rounded-0 " + self.input_css_classes,
                    wrapper_class="mb-0"
                ),
                'subject_id',
                Div(
                    HTML('<button class="input-group-text fas fa-arrow-right" type="button"></button>'),
                    css_class="input-group-prepend"
                ),
                Field(
                    'merge_target',
                    placeholder="Merge Target",
                    type="search",
                    css_class="rounded-right " + self.input_css_classes,
                    wrapper_class="mb-0"
                ),
                'target_id',
                css_class="input-group justify-content-center mb-1"
            ),
            Button(
                'merge',
                'Merge',
                css_class="btn-primary float-right mt-3 " + self.button_css_classes,
                onClick='sendResponse($("#merge-professor-form").serialize(), "professor_merge")'
            )
        )

        return layout

    def clean(self):
        cleaned_data = super().clean()
        merge_subject_id = cleaned_data['subject_id']
        merge_target_id = cleaned_data['target_id']

        merge_subject = merge_subject_id >= 0
        merge_target = merge_target_id >= 0
        if not (merge_subject and merge_target):
            error_msg = "Please fill in both fields"
            error = ValidationError(error_msg, code='Empty')
            if not merge_subject:
                self.add_error('merge_subject', error)
            if not merge_target:
                self.add_error('merge_target', error)
        else:
            if merge_subject_id == merge_target_id:
                error_msg = "You can't merge someone with themselves"
                error = ValidationError(error_msg, code='Self-Merge')
                self.add_error('merge_target', error)
            else:
                subject = Professor.objects.filter(pk=merge_subject_id).first()
                target = Professor.objects.filter(pk=merge_target_id).first()
                error_msg = f'''The highlighted {"names don't" if not (subject or target) else "name doesn't"} exist'''
                error = ValidationError(error_msg, code='DNE')
                if not subject:
                    self.add_error('merge_subject', error)
                if not target:
                    self.add_error('merge_target', error)

        return cleaned_data

# Same form as above placed inside a bootstrap modal.
# Works anywhere modals work.
class ProfessorMergeFormModal(ProfessorMergeForm):
    def generate_layout(self):
        layout = Layout(
            BootstrapModal(
                super().generate_layout(),
                css_id="merge-professor-modal",
                title_id="merge-professor-label",
                title='Search for a professor/TA to merge with'
            )
        )
        return layout
