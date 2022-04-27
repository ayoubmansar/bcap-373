import django_filters
from django_filters import DateFilter, CharFilter, NumberFilter, OrderingFilter
from .models import *

class EventFilter(django_filters.FilterSet):
    def name(queryset, name, value):
        if value is not None:
            records = EventModel.objects.all()
            ids = [record.id for record in records if value.lower() in str(record.owner).lower()]
            return queryset.filter(id__in=ids)
        return queryset
    # Excluded (non-default filters)
    name = CharFilter(method=name, label='Event name contains')
    start_date = DateFilter(field_name="date", lookup_expr='gte')
    end_date = DateFilter(field_name="date", lookup_expr='lte')
    # hours
    class Meta:
        ordering = ['-id']
        model = EventModel
        fields = []
    
    def __init__(self, *args, **kwargs):
       super(EventFilter, self).__init__(*args, **kwargs)

class HistoryFilter(django_filters.FilterSet):
    def name(queryset, name, value):
        if value is not None:
            records = VolunteerRecord.objects.all()
            ids = [record.id for record in records if value.lower() in str(record.owner).lower()]
            return queryset.filter(id__in=ids)
        return queryset
    # Excluded (non-default filters)
    name = CharFilter(method=name, label='Full name contains')
    start_date = DateFilter(field_name="date", lookup_expr='gte')
    end_date = DateFilter(field_name="date", lookup_expr='lte')
    # Ordering
    o = OrderingFilter(
        fields=(
            ('name','name'),
            ('hours','hours'),
            ('activity','activity'),
            ('date','date')
        ),
        field_labels={
            'name': 'Full name',
            'hours': 'Volunteer hours',
            'activity': 'Event',
            'date': 'Date added'
        }
    )
    class Meta:
        ordering = ['-id']
        model = VolunteerRecord
        fields = ['activity','supervisor','hours','owner']
    
    def __init__(self, *args, **kwargs):
       super(HistoryFilter, self).__init__(*args, **kwargs)
       self.filters['hours'].label="Hours equal to"
       self.filters['owner'].label=""


class VolunteerFilter(django_filters.FilterSet):
    # Custom filtering functions
    def total_hours(queryset, name, value):
        if value is not None:
            users = User.objects.all()
            ids = [user.id for user in users if float(user.get_hours()) >= float(value)]
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