***Magenta Component Library***

This project contains a number of UI components for Django/HTML/HTMX, as well as a component browser displaying examples and documentation for each component.

**How to install**

1. Add `componentlib` to your `requirements.txt`:

> pip install "componentlib@git+https://github.com/johanneRW/componentlib.git"

2. Update settings:

- Add `componentlib` to your `INSTALLED_APPS` (in `settings.py`)
- Unless you have `APP_DIRS = True` in `TEMPLATES`, you also need to add:

```
import componentlib
componentlib_path = Path(componentlib.__file__).parent

TEMPLATES = [
    {
        ...,
        "DIRS": [
            ...,
            componentlib_path,
        ],
        ...
    }
]
```

3. Add `componentlib` URLs to your project `urls.py`:

```
if settings.DEBUG:
    urlpatterns.append(
        path("componentlib/", include("componentlib.urls")),
    )
```

The last step will make the component browser available in your current Django project at the `/componentlib/` URL.

**How to add a new component**

> python manage.py create_component

This will take you through an interactive guide, asking you what sort of component you want to create. After answering the questions, a new component will be added to the `componentlib/components/` folder.

*How to keep `props.py` files up-to-date*

> python manage.py update_props

This will update the `props.py` file of each component, based on any changes in the corresponding `template.html` and `example.json` files.

**How to update `props.py` on the fly**

If you wish to keep `props.py` files updated on the fly while you edit code, you can run:

> python manage.py watch_components

This will run a continuous process (similar to `runserver`) watching all components for changes. To stop this process, press Ctrl-C.
