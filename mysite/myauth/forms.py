from django import forms


from .models import Profile


class MyAuthForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = 'avatar',
        # fields = 'user', 'bio', 'agreement_accepted', 'avatar',

