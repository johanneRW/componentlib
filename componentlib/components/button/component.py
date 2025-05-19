from django.template.loader import render_to_string

class ButtonComponent:
    def __init__(self, **kwargs):
        self.context = kwargs

    def render(self):
        return render_to_string("components/button/template.html", self.context)
