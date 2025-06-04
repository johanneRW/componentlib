import re

class CaseUtils:
    @staticmethod
    def to_pascal_case(snake_str):
        return ''.join(word.capitalize() for word in snake_str.split('_'))

    @staticmethod
    def to_title_case(snake_str):
        return ' '.join(word.capitalize() for word in snake_str.split('_'))

    @staticmethod
    def to_snake_case(name):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name.replace("-", "_")).lower()

    @staticmethod
    def is_valid_component_name(name):
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name)
