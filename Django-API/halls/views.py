from django.shortcuts import render,redirect
from django.urls import reverse_lazy,reverse
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView,DetailView,UpdateView,DeleteView,TemplateView
from django.contrib.auth import authenticate,login
from django.http import HttpResponseRedirect
from halls.forms import VideoForm,SearchForm
from django.forms.utils import ErrorList
from django.http import Http404,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import urllib
import requests
# Create your views here.
from halls.models import Hall,Video
YOUTUBE_API_KEY='Your Youtube API Key'
def home(request):
    popular_halls=[Hall.objects.get(pk=5),Hall.objects.get(pk=6),Hall.objects.get(pk=8),Hall.objects.get(pk=10)]
    recent_halls=Hall.objects.all().order_by('id')[:3]

    return render(request,'halls/home.html',context={'recent_halls':recent_halls,'popular_halls':popular_halls})

class about(TemplateView):
    template_name="halls/about.html"
@login_required()
def dashboard(request):
    halls=Hall.objects.filter(user=request.user)
    return render(request,'halls/dashboard.html',context={'halls':halls})
@login_required()
def video_search(request):
    search_form=SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term=urllib.parse.quote(search_form.cleaned_data['search_form'])
        response=requests.get(f'https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={ encoded_search_term }&key={ YOUTUBE_API_KEY }')
        jsonreturn=search_form.cleaned_data['search_form']
        return JsonResponse(response.json())
    return JsonResponse({'error':'Not able to validate form'})

@login_required()
def add_video(request,pk):
    form=VideoForm()
    search_form=SearchForm()
    hall=Hall.objects.get(pk=pk)
    if not hall.user==request.user:
        raise Http404
    if request.method=='POST':
        form=VideoForm(request.POST)
        if form.is_valid():
            video=Video()
            video.hall=hall
            video.url=form.cleaned_data['url']
            parsed_url=urllib.parse.urlparse(video.url)
            video_id=urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id=video_id[0]
                response=requests.get(f'https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={ video_id[0] }&key={YOUTUBE_API_KEY}')
                json=response.json()
                title=json['items'][0]['snippet']['title']
                video.title=title
                video.save()
                return redirect('detail_hall',pk)

            else:
                errors = form._errors.setdefault("url", ErrorList())
                errors.append('Needs to be a Youtube URL')
    return render(request,'halls/add_video.html',context={'form':form,'search_form':search_form,'hall':hall})

class SignUp(CreateView):
    form_class=UserCreationForm
    success_url=reverse_lazy('dashboard')
    template_name='registration/signup.html'

    # def form_valid(self, form):
    #     valid=super().form_valid(form)
    #     username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
    #     user = authenticate(username=username, password=password)  # This returns None
    #     login(self.request, user)
    #     return valid

    def form_valid(self, form):
        #save the new user first
        form.save()
        #get the username and password
        # username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        # or
        username = self.request.POST['username']
        password = self.request.POST['password1']
        #authenticate user then login
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return HttpResponseRedirect(reverse('dashboard'))
class CreateHall(CreateView,LoginRequiredMixin):
    model=Hall
    fields=['title']
    success_url=reverse_lazy('dashboard')
    template_name='halls/create_hall.html'
    def form_valid(self,form):
        form.instance.user=self.request.user
        view=super().form_valid(form)
        return view

class DetailHall(DetailView):
    model=Hall
    context_object_name='hall_detail'

class UpdateHall(UpdateView,LoginRequiredMixin):
    model=Hall
    fields=['title']
    context_object_name='update_hall'
    success_url=reverse_lazy('dashboard')
    def get_object(self):
        hall=super().get_object()
        if hall.user.id != self.request.user.id:
            raise Http404
        else:
            return hall

class DeleteHall(DeleteView,LoginRequiredMixin):
    model=Hall
    context_object_name='delete_hall'
    success_url=reverse_lazy('dashboard')
    def get_object(self):
        hall=super().get_object()
        if hall.user.id != self.request.user.id:
            raise Http404
        else:
            return hall

class DeleteVideo(DeleteView,LoginRequiredMixin):
    model=Video
    context_object_name='delete_video'
    template_name='halls/delete_video.html'
    success_url=reverse_lazy('dashboard')
    def get_object(self):
        video=super().get_object()
        if video.hall.user != self.request.user:
            raise Http404
        else:
            return video
