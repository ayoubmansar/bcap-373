import django_filters
from django_filters import DateFilter, CharFilter, NumberFilter
from .models import *



class VolunteerFilter(django_filters.FilterSet):
    # Custom filtering functions
    def total_hours(queryset, name, value):
        if value is not None:
            print('Checking ' + name + ' for >= ' + str(value))
            users = User.objects.all()
            for user in users:
                print(user.get_hours())
                print(float(user.get_hours()) >= float(value))
            ids = [user.id for user in users if float(user.get_hours()) >= float(value)]
            print(ids)
            return queryset.filter(id__in=ids)
        return queryset
    # Excluded (non-default filters)
    total_hours = NumberFilter(method=total_hours, label='Total hours greater than or equal to')
    first_name = CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = CharFilter(field_name='last_name', lookup_expr='icontains')
    # Meta class
    class Meta:
        ordering = ['-id'] # To avoid pagination issues
        model = User
        fields = ['username','last_login','is_superuser','first_name','last_name','email','date_joined']
        exclude = ['last_login','date_joined', 'first_name', 'last_name'] # this overrides anything in 'fields'
    
    def __init__(self, *args, **kwargs):
       super(VolunteerFilter, self).__init__(*args, **kwargs)
       self.filters['is_superuser'].label="Is BCAP staff"