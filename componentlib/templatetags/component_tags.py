import importlib

def get_component_class(key):
    try:
        mod = importlib.import_module(f"componentlib.components.{key}.component")
        class_name = [name for name in dir(mod) if name.endswith("Component")][0]
        return getattr(mod, class_name)
    except Exception as e:
        return None
