from django import forms
from halls.models import Video

class VideoForm(forms.ModelForm):
    class Meta():
        fields=['url']
        model=Video
        labels={'url':'Youtube URL'}

class SearchForm(forms.Form):
    search_form=forms.CharField(max_length=255,label='Search For Videos')
