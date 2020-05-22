from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('register/',
         # views.StudentRegistrationView.as_view(),
         views.signup,
         name='student_registration'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('enroll-course/',
         views.StudentEnrollCourseView.as_view(),
         name='student_enroll_course'),
    path('courses/',
         views.StudentCourseListView.as_view(),
         name='student_course_list'),
    path('course/<pk>/',
         views.StudentCourseDetailView.as_view(),
         name='student_course_detail'),
    path('course/<pk>/<module_id>/',
         views.StudentCourseDetailView.as_view(),
         name='student_course_detail_module'),
]
