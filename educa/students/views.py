from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import CourseEnrollForm, SignupForm
from .tokens import account_activation_token
from courses.models import Course


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation email.'
            message = render_to_string('account_activate_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please, confirm your email address!')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for confirmation!')
    else:
        return HttpResponse('Wrong link!')

# class StudentRegistrationView(CreateView):
#     template_name = 'students/student/registration.html'
#     form_class = UserCreationForm
#     success_url = reverse_lazy('student_course_list')
#
#     def form_valid(self, form):
#         # method will run if form validation is success
#         result = super(StudentRegistrationView, self).form_valid(form)
#         cd = form.cleaned_data
#         user = authenticate(username=cd['username'],
#                             password=cd['password1'])
#         login(self.request, user)
#         return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        queryset = super(StudentCourseListView, self).get_queryset()
        return queryset.filter(students__in=[self.request.user])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        queryset = super(StudentCourseDetailView, self).get_queryset()
        return queryset.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentCourseDetailView, self).get_context_data(**kwargs)
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # current module to show: module_id in arguments
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
            # first module to show: no module_id in arguments
            context['module'] = course.modules.all()[0]
        return context
