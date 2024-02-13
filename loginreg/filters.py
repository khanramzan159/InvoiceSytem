import django_filters
from django import forms
from .models import User

class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search Username:'}),
        label='',
    )

    class Meta:
        model = User
        fields = ['name']