from django.urls import path
from . import views
from componentlib.htmx_router import urlpatterns as htmx_urls

urlpatterns = [
    path("", views.component_browser, name="component_browser"),
    path("detail/<str:key>/", views.component_detail, name="component_detail"),
    path("components/<str:key>/import/", views.component_import_hint, name="component_import_hint"),
    path("components/<str:key>/code/", views.component_code, name="component_code"),
    path("components/<str:key>/import/", views.component_import_hint, name="component_import_hint"),


    *htmx_urls,
]
