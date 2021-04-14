from .forms import FormExample
from .utils import render_template


def test_bulma_form_tag():
    output = render_template(
        """
        {% load bulma_tags %}
        {% block content %}
            <form>{{ form|bulma }}</form>
        {% endblock content %}
        """,
        context={"form": FormExample()},
    )

    assert '<div class="field"' in output, "Fields are rendered"
