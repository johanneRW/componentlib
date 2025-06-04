import importlib
from django.urls import path
from pathlib import Path

BASE_COMPONENTS_PATH = Path(__file__).resolve().parent / "components"
URL_PREFIX = "htmx"

urlpatterns = []

for component_dir in BASE_COMPONENTS_PATH.iterdir():
    if not component_dir.is_dir():
        continue

    module_path = f"componentlib.components.{component_dir.name}.view"

    try:
        mod = importlib.import_module(module_path)

        for attr in dir(mod):
            view_func = getattr(mod, attr)
            if callable(view_func) and getattr(view_func, "_is_htmx_view", False):
                # Brug funktionen navn som sidste del af url
                route = f"{URL_PREFIX}/{component_dir.name}/{attr}/"
                urlpatterns.append(path(route, view_func))
    except ModuleNotFoundError:
        continue
