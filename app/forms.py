from django import forms
from .models import ContactSubmission

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['full_name', 'email', 'phone', 'address', 'rooms', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'rooms': forms.NumberInput(attrs={'placeholder': 'Enter number of rooms', 'min': 1}),
        }