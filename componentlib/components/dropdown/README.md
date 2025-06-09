## Dropdown

The `DropdownComponent` is an HTMX-powered `<select>` field designed for use in dynamic forms, without requiring any JavaScript. It allows users to select from a list of options, and automatically triggers an HTTP request to update the interface based on the selected value.

### Features

- HTMX integration for dynamic updates on value change
- Optional `placeholder` field for default unselected state
- Works without any JavaScript


### Inputs

| Name         | Type                  | Required | Description                                                             |
|--------------|-----------------------|----------|-------------------------------------------------------------------------|
| `form_fields`| `list`                | ✅        | A list of key-value pairs to be used as dropdown options               |
| `target_url` | `string`              | ✅        | URL to fetch new content when the value changes                         |
| `placeholder`| `string` _(optional)_ | ❌        | Text shown as the default unselected value (e.g., `"Select a country"`) |

If `placeholder` is not provided, the component defaults to a simple `"________"` label.

