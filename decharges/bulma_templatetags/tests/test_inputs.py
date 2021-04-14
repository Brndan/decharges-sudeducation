import pytest
from django import forms

from .utils import element_has_all_attributes, get_dom, render_form

COLOR_CHOICES = (("red", "Red"), ("green", "Green"), ("blue", "Blue"))


@pytest.mark.parametrize(
    "field,label,tag,attributes",
    [
        (
            forms.CharField(),
            "Name",
            "input",
            {
                "name": "input",
                "class": ["control", "input"],
                "type": "text",
                "id": "id_input",
            },
        ),
        (
            forms.EmailField(),
            "Email",
            "input",
            {
                "name": "input",
                "class": ["control", "input"],
                "type": "email",
                "id": "id_input",
            },
        ),
        (
            forms.CharField(widget=forms.NumberInput()),
            "Email",
            "input",
            {
                "name": "input",
                "class": ["control", "input"],
                "type": "number",
                "id": "id_input",
            },
        ),
        (
            forms.CharField(widget=forms.URLInput()),
            "Url",
            "input",
            {
                "name": "input",
                "class": ["control", "input"],
                "type": "url",
                "id": "id_input",
            },
        ),
        (
            forms.CharField(widget=forms.PasswordInput()),
            "Password",
            "input",
            {
                "name": "input",
                "class": ["control", "input"],
                "type": "password",
                "id": "id_input",
            },
        ),
        (
            forms.ChoiceField(choices=[]),
            "Select",
            "select",
            {"name": "input", "class": ["control"], "id": "id_input"},
        ),
        (
            forms.MultipleChoiceField(choices=[]),
            "Multi select",
            "select",
            {"name": "input", "class": ["control"], "multiple": "", "id": "id_input"},
        ),
        (
            forms.CharField(widget=forms.Textarea()),
            "Textarea",
            "textarea",
            {"name": "input", "class": ["control", "textarea"], "id": "id_input"},
        ),
        (
            forms.BooleanField(),
            "Checkbox",
            "input",
            {"name": "input", "type": "checkbox"},
        ),
        (
            forms.MultipleChoiceField(
                choices=COLOR_CHOICES, widget=forms.CheckboxSelectMultiple()
            ),
            "Checkboxes",
            "input",
            {"name": "input", "type": "checkbox", "value": "red"},
        ),
        (
            forms.ChoiceField(choices=COLOR_CHOICES, widget=forms.RadioSelect()),
            "Radios",
            "input",
            {"name": "input", "type": "radio", "value": "red"},
        ),
        (
            forms.FileField(),
            "File input",
            "input",
            {"name": "input", "type": "file", "class": ["file-input"]},
        ),
    ],
)
def test_input_rendering(field, tag, label, attributes):
    class TestForm(forms.Form):
        input = field

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["input"].label = label

    output = render_form(TestForm())
    dom = get_dom(output)

    element_has_all_attributes(
        dom.find(tag), attributes
    ), f"{label} has attributes {str(attributes)}"
    assert dom.find("label").text.strip() == label, f"Field has label {label}"
