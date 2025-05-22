from pydantic import BaseModel, Field
import yaml
from pathlib import Path

def generate_model_class(component_name: str):
    component_dir = Path("componentlib/components") / component_name
    metadata_path = component_dir / "metadata.yaml"
    if not metadata_path.exists():
        print(f"[codegen] No metadata.yaml found for '{component_name}'")
        return

    with open(metadata_path, "r") as f:
        meta = yaml.safe_load(f)

    inputs = meta.get("inputs", {})
    class_name = meta.get("class_name", f"{component_name.capitalize()}Component")
    model_name = f"{class_name}Props"

    lines = [f"class {model_name}(BaseModel):"]

    type_map = {
        "string": "str",
        "number": "float",
        "boolean": "bool",
        "list": "list",
        "dict": "dict"
    }

    for key, config in inputs.items():
        py_type = type_map.get(config["type"], "str")
        default = config.get("default", ...)
        field_line = f"    {key}: {py_type} = Field({repr(default)}, description={repr(config.get('description', ''))})"
        lines.append(field_line)

    model_code = "\n".join(lines)
    output_path = component_dir / "types.py"
    output_path.write_text(f"from pydantic import BaseModel, Field\n\n{model_code}\n")
    print(f"[codegen] Generated {model_name} in {output_path}")
