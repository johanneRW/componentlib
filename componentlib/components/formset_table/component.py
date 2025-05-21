from componentlib.components.base import BaseComponent

class FormsetTableComponent(BaseComponent):
    template_filename = "template.html"

    def get_context_data(self):
        print("[DEBUG] FormsetTableComponent.get_context_data KALDT")
        formset = self.context.get("formset", [])
        columns = self.context.get("columns", [])

        rows = []


        print("[DEBUG] columns:", columns)
        print("[DEBUG] formset:", formset)
        print("[DEBUG] rows:", rows)

        for entry in formset:
            if isinstance(entry, dict):
                rows.append(entry)

        print("[DEBUG] columns:", columns)
        print("[DEBUG] formset:", formset)
        print("[DEBUG] rows:", rows)

        return {
            "columns": columns,
            "rows": rows,
        }
