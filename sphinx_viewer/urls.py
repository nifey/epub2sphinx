from django.urls import path
from . import views


urlpatterns = [
    path('', views.EpubFileUploadView.as_view(), name='upload'),
    path('read/', views.ReturnHtmlView.as_view(), name='epub2sphinx')
]
