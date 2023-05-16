from django.forms import DateInput, SelectDateWidget
from django_filters import FilterSet, DateFromToRangeFilter
from django_filters.widgets import RangeWidget

from .models import Article


class PostFilter(FilterSet):
    post_date = DateFromToRangeFilter(label='Dates From To Range', widget=RangeWidget(attrs={'type': 'date'}))

    class Meta:
        model = Article
        fields = {
            'title': ['icontains'],
            'category': ['exact'],
        }

