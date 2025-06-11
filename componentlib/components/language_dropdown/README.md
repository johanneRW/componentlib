# Language Dropdown

A language selector component for switching the site's active language, rendered as a styled `<select>` element. Automatically submits the form on change using JavaScript.

## Features

- Displays all languages defined in `settings.LANGUAGES`
- Automatically selects the current active language
- Submits the language form on change
- Built with Django's `{% get_language_info_list %}` template tag
- No external JavaScript dependencies
- Can be extended or themed using custom CSS

## Requirements

This component expects:
- A working `{% url 'set_language' %}` view (standard in Django)
- `{% load i18n %}` available in the template
- `LANGUAGES` and `LANGUAGE_CODE` provided via context (automatically added in preview)

## Example Context

You typically don't need to pass explicit props for this component.
If used outside a Django template context, ensure the following are present:

```json
{
  "LANGUAGES": [["en", "English"], ["fr", "French"]],
  "LANGUAGE_CODE": "en"
}
