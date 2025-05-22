from django.core.management.base import BaseCommand
from componentlib.helpers.codegen import generate_model_class

class Command(BaseCommand):
    help = "Generate types.py from metadata.yaml"

    def add_arguments(self, parser):
        parser.add_argument("component_name")

    def handle(self, *args, **options):
        generate_model_class(options["component_name"])
