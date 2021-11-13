from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include(('sphinx_viewer.urls', 'sphinx_viewer'), namespace='sphinx_viewer')),
    path('admin/', admin.site.urls),
]
