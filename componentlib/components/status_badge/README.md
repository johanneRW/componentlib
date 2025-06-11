# Status Badge

A visual badge component that displays a status label such as "Approved", "Draft", or "Rejected" with contextual styling. Typically used to show object or form state at a glance.

## Features

- Dynamically maps a status string to a Bootstrap-based badge class
- Reads `form.status` and applies a corresponding class
- Outputs `form.get_status_display` inside the badge
- Designed for Django models with a status field
- Can be used inline or inside lists/tables

## Requirements

This component expects a `form` or `object` context with the following:

- `.status` attribute (e.g., `"DRAFT"`, `"APPROVED"`)
- `.get_status_display()` method

## Example Context

```json
{
  "form": {
    "status": "REJECTED"
  }
}