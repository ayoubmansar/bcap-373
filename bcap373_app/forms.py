from .models import VolunteerRecord, Profile

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DateInput(forms.DateInput):
    input_type = 'date'

class NumberInput(forms.NumberInput):
    input_type = 'number'

class SignUpForm(UserCreationForm):
    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )

    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required. Please provide a valid email address.')

    # Profile Fields
    phone = forms.CharField(max_length=30, required=False, help_text='U.S. phone number')
    birth_date = forms.DateField(help_text='Format: YYYY-MM-DD', required=False, widget=DateInput(attrs={'id':'dateTimePicker'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2','phone','birth_date')
        

class ProfileForm(forms.ModelForm):
    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )

    phone = forms.CharField(max_length=30, required=False, help_text='Required.')
    birth_date = forms.DateField(help_text='Format: YYYY-MM-DD', required=False, 
                                    widget=DateInput(attrs={'id':'dateTimePicker'}))

    class Meta:
        model = Profile
        fields = ('phone', 'birth_date')

class VolunteerRecordForm(forms.ModelForm):
    class Meta:
        model = VolunteerRecord
        fields = ('activity', 'hours', 'date', 'supervisor', 'description')
        hours = forms.FloatField(min_value=0)
        widgets = {
            'date' : DateInput(attrs={'id': 'dateTimePicker'}),
            'hours' : NumberInput(attrs={'id': 'form_hours', 'step': "0.25", 'min': 0.25}),
            'description' : forms.Textarea(attrs={'id': 'form_desc','rows':4, 'cols':20})
        }


class FilterForm(forms.Form):
    start_date = forms.DateField(widget=DateInput)
    end_date = forms.DateField(widget=DateInput)


    def is_valid(self):

        valid = super(FilterForm, self).is_valid()
        if not valid:
            return valid


        start_year = self.cleaned_data['start_date'].year
        start_month = self.cleaned_data['start_date'].month
        start_day = self.cleaned_data['start_date'].day

        end_year = self.cleaned_data['end_date'].year
        end_month = self.cleaned_data['end_date'].month
        end_day = self.cleaned_data['end_date'].day

        if(start_year < end_year):
            return True
        elif(start_year > end_year):
            return False
        
        if(start_month < end_month):
            return True
        elif(start_month > end_month):
            return False

        if(start_day <= end_day):
            return True

        return False
