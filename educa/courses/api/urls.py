from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('subjects/',
         views.SubjectListView.as_view(),
         name='subject_list'),
    path('subjects/<pk>/',
         views.SubjectDerailView.as_view(),
         name='subject_detail'),
]