from componentlib.components.base import BaseComponent

class ProductCardComponent(BaseComponent):
    def __init__(self, product, theme="bootstrap", button_class=None):
        self.product = product
        self.theme = theme
        self.button_class = button_class or "btn btn-primary"

    def get_context_data(self):
        return {
            "product": self.product,
            "theme": self.theme,
            "button_class": self.button_class,
        }
