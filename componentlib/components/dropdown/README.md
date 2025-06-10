# Dropdown

A reusable, dynamic Django component for rendering `<select>` dropdowns with HTMX integration. Designed to be used without JavaScript and configurable through metadata, example data, or form context.

## Features

- HTMX-enabled form interaction (`hx-get`, `hx-target`, `hx-trigger`)
- Accepts static or dynamic input values
- Supports `placeholder` rendering
- Optional disabling of the dropdown via `disabled` input or form context
- Values can be injected from context using `value_from` / `disabled_from` references
- Pydantic-validated input schema

## Supported Inputs

| Name            | Type     | Required | Description                                                                 |
|-----------------|----------|----------|-----------------------------------------------------------------------------|
| `name`          | `str`    | yes      | Name/ID for the dropdown field                                              |
| `label`         | `str`    | yes      | Label text shown above the select                                           |
| `options`       | `list`   | yes      | List of 2-tuples: `[["value1", "Label 1"], ["value2", "Label 2"]]`          |
| `target_url`    | `str`    | yes      | HTMX endpoint to fetch on change                                           |
| `value`         | `str`    | no       | Selected value. Optional if `value_from` is provided                        |
| `disabled`      | `bool`   | no       | Disable field. Optional if `disabled_from` is used                         |
| `placeholder`   | `str`    | no       | Text shown as first disabled `<option>` if provided                         |
| `value_from`    | `str`    | no       | Context path to inject value, e.g. `"form.vessel.nationality"`             |
| `disabled_from` | `str`    | no       | Context path to inject boolean for `disabled`, e.g. `"form.user_is_ship"`  |
| `form`          | `object` | no       | Optional form object from which values may be dynamically resolved         |
| `attributes`    | `dict`   | no       | Optional dict for injecting extra CSS classes: `{"class": "...", "select_class": "..."}` |

If value is not passed directly, it will be resolved from the value_from path.

Same applies to disabled and disabled_from.

You can extend the component by overriding apply_dynamic_fields() in the base class or customizing metadata.yaml.