from django.urls import path
from . import views


urlpatterns = [
    path("", views.component_browser, name="component_browser"),
    path("detail/<str:key>/", views.component_detail, name="component_detail"),
    
    path("components/<str:key>/code/", views.component_code, name="component_code"),
    
]
