from django import forms
from .models import SignVideo, TrainedModel

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = SignVideo
        fields = ['word', 'video']

class ModelUploadForm(forms.ModelForm):
    class Meta:
        model = TrainedModel
        fields = ['name', 'description', 'file', 'accuracy']

class DataProcessorForm(forms.Form):
    data_file = forms.FileField(
        label="Data File",
        help_text="Upload a processed data file (.pickle format)"
    )

class ModelTrainerForm(forms.Form):
    pickle_file = forms.FileField()
