# Modal

A reusable static HTML modal layout component. By default, it renders an empty modal shell, which can be extended with content using Django's `{% extends %}` and template blocks.

## Features

- Predefined modal structure using Bootstrap classes
- No backend logic or dynamic props required
- Designed to be extended or included as needed
- Ideal for dialogs, confirmations, and overlays
- Clean default layout with header/body/footer blocks

## Usage

### Option 1: Include as-is

```
{% include "components/modal/template.html" %}
```
This will render an empty modal layout, ready to be shown or hidden with JavaScript or HTMX.

### Option 2: Extend and override content

Create a new template file and use {% extends %} to inject custom content:
```
{% extends "components/modal/template.html" %}

{% block modal_title %}
  Confirm Action
{% endblock %}

{% block modal_body %}
  Are you sure you want to proceed with this action?
{% endblock %}

{% block modal_footer %}
  <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
  <button class="btn btn-danger">Confirm</button>
{% endblock %}
```
## Extending

The modal defines standard block sections you can override:

- modal_title – title area at the top

- modal_body – main content

- modal_footer – action buttons / footer content

Use these blocks to inject dynamic forms, alerts, or any custom content inside the modal structure.
Dependencies

The default modal layout assumes you're using Bootstrap 5, but it can be adapted for any frontend framework.