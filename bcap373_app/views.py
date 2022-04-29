from django.shortcuts import render, redirect

from .forms import SignUpForm, ProfileForm, VolunteerRecordForm, FilterForm, EventForm, UpdateUserForm
from .models import VolunteerRecord, EventModel
from django.conf import settings
# Flash messages
from django.contrib import messages
# Signup/Login stuff
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
# Csv stuff
from django.http import HttpResponse
import csv
from django.db.models import Sum
from django.contrib.auth.models import User
# PDF stuff
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
from django.http import FileResponse
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from datetime import datetime
from pytz import timezone
# Paginator
from django.core.paginator import Paginator
from django.views.generic import ListView
# Filters
from .filters import VolunteerFilter, HistoryFilter, EventFilter

# Email Receipt Stuff
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Logging
from django.http import HttpResponse
import logging
logger = logging.getLogger('ex_logger')
logger.info("core.views logger")  # should work 

#Certificate generation
@login_required
def generate_certificate(request):
   person_id = request.GET.get('id','')
   if(request.user.is_staff) and person_id != '':
      # Get the user
      current_user = User.objects.get(id=person_id)
      records = VolunteerRecord.objects.filter(owner = current_user)
      running_total = sum(rec.hours for rec in records)

      # Create a file-like buffer to receive PDF data.
      buffer = io.BytesIO()
      p = canvas.Canvas(buffer, pagesize=landscape(letter))
      p.setTitle('Certificate for ' + current_user.username)
      # Design
      p.setFillColorRGB(0.984, 0.960, 0.756) # https://doc.instantreality.org/tools/color_calculator/
      p.rect(0,0,3000,3000,fill=1)
      p.setFillColorRGB(0,0,0)
      p.setFont('Helvetica', 48, leading=None)
      p.drawCentredString(415, 500, "Volunteer Certificate")
      p.setFont('Helvetica', 24, leading=None)
      p.drawCentredString(415,450,"This certificate is presented to:")
      p.setFont('Helvetica-Bold', 34, leading=None)
      p.drawCentredString(415, 395, str(current_user))
      p.setFont('Helvetica', 20, leading=None)
      p.drawCentredString(415, 350, "for volunteering")
      p.setFont('Helvetica-Bold', 30, leading=None)
      p.drawCentredString(415, 300, str(running_total) + ' hours')
      p.setFont('Helvetica', 20, leading=None)
      p.drawCentredString(415, 250, "at the Bhutanese Community Association of Pittsburgh")
      seal_url = request.build_absolute_uri(staticfiles_storage.url('bcap373_app/img/seal.png'))
      seal = ImageReader(seal_url)
      p.drawImage(seal, 270, 100, width=100, height=100, mask='auto')
      logo_url = request.build_absolute_uri(staticfiles_storage.url('bcap373_app/img/bcap373_logo.png'))
      logo = ImageReader(logo_url)
      p.drawImage(logo, 400, 90, width=180, height=120, mask='auto')
      p.setFont('Helvetica-Oblique', 17, leading=None)
      tz = timezone('US/Eastern')
      p.drawCentredString(420, 40, 'Valid as of ' + datetime.now(tz).strftime("%m/%d/%Y %H:%M:%S"))
      # Display
      p.showPage()
      p.save()
      buffer.seek(0)
      return FileResponse(buffer, as_attachment=False, filename='certificate.pdf')
   else:
      messages.error(request, 'You do not have permission to perform this action.')
      return redirect ('/history')

#Export to csv function
def export_csv(request, start_date, end_date):
   person_id = request.GET.get('id','')
   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="volunteer_history: {} to {}.csv"'.format(start_date, end_date)

   writer = csv.writer(response)
   writer.writerow(['Volunteer', 'Date', 'Hours', 'Description', 'Supervisor'])

   if person_id == '':
      if(request.user.is_staff):
         records = VolunteerRecord.objects.all().filter(date__range=[start_date, end_date])
      else:
         records = VolunteerRecord.objects.filter(owner=request.user, date__range=[start_date, end_date])
   else:
      if request.user.id == int(person_id) or request.user.is_staff:
         requested_user = User.objects.get(id=person_id)
         records = VolunteerRecord.objects.filter(owner=requested_user, date__range=[start_date, end_date])
      else:
         records = []

   records = list(records)
   records.sort(key=lambda rec: rec.date, reverse=True)

   for record in records:
      volunteer = record.owner.first_name + ' ' + record.owner.last_name
      date = record.date
      hours = record.hours
      desc = record.activity
      supervisor = record.supervisor
      writer.writerow((volunteer, date, hours, desc, supervisor))
   
   return response

@login_required
def export(request):
   if request.method == "POST":
      form = FilterForm(request.POST)
      if form.is_valid():
         start = form.cleaned_data['start_date']
         end = form.cleaned_data['end_date']
         response = export_csv(request, start, end)
         return response
   else:
      form = FilterForm()
   id = request.GET.get('id','')
   name = ''
   if id == '':
      if request.user.is_staff:
         name = 'for all volunteers'
      else:
         name = 'for yourself'
   else:
      if request.user.is_staff:
         name = 'for ' + str(User.objects.get(id=int(id)))
      else:
         messages.error(request, 'You do not have permission to perform this action.')
         return redirect('/history')
   return render(request, 'export.html', {'form':form, 'name':name})

@login_required
def export_contact(request):
   if request.method == "POST":
      form = FilterForm(request.POST)
      if form.is_valid():
         start = form.cleaned_data['start_date']
         end = form.cleaned_data['end_date']
         response = export_contacts(request, start, end)
         return response
   else:
      form = FilterForm()
   return render(request, 'export_contact.html', {'form':form})

def export_contacts(request, start_date, end_date):
   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="volunteer_contacts: {} to {}.csv"'.format(start_date, end_date)

   writer = csv.writer(response)
   writer.writerow(['Full Name', 'Email','Total Hours'])

   if(request.user.is_staff):
      users = User.objects.all().filter(date_joined__range=[start_date, end_date])
   else:
      users = User.objects.filter(owner=request.user, date_joined__range=[start_date, end_date])

   for user in users:
      writer.writerow([user, user.email, user.get_hours()])
   
   return response



   
def landing(request):
   return redirect('/login')
   # return render(request, 'landing.html')

def signup(request):
   if request.method == "POST":
      form = SignUpForm(request.POST)
      if form.is_valid():
         user = form.save()
         user.refresh_from_db() 
         #load profile
         user.profile.phone = form.cleaned_data.get('phone')
         user.profile.birth_date = form.cleaned_data.get('birth_date')
         user.save()
         raw_password = form.cleaned_data.get('password1')
         user = authenticate(username=user.username, password=raw_password)
         login(request, user)
         messages.success(request, 'Welcome, ' + (user.get_full_name()).title() + ', to the BCAP Volunteer System!')
         return redirect('/add_individual_hours')
      else:
         messages.error(request, 'Invalid form submission with signup. Try again.')
         return redirect('/signup')
   else:
      form = SignUpForm()
   return render(request, "signup.html", {
         "user_form" : form,
      })

@login_required
def new_event(request):
   if request.user.is_staff:
      if request.method == "POST":
         form = EventForm(request.POST)
         if form.is_valid():
            event = form.save()
            event.refresh_from_db() 
            event.save()
            messages.success(request, 'Event created successfully')
            return redirect('/events')
         else:
            messages.error(request, 'Invalid form submission.')
            return redirect('/events')
      else:
         form = EventForm()
      return render(request, "new_event.html", {
            "event_form" : form,
         })
   else:
      messages.error(request, 'You are not authorized to perform this action.')
      return redirect('/history')

@login_required
def home(request):
   return redirect('add_individual_hours')

@login_required
def success(request):
    return render(request, "success.html")

@login_required
def add_individual_hours(request):
   if request.method == "POST":
      form = VolunteerRecordForm(request.POST)
      if form.is_valid():
         # Set user field in the form here
         record = form.save(commit = False)
         record.owner = request.user
         record.save()
         #TODO: Ayoub: Disabled email sending for now
         #subject = 'SLO Botanical Garden - Tracking Form Receipt'
         #html_message = render_to_string('email_template.html', {'form': form.cleaned_data}) 
         #plain_message = strip_tags(html_message)
         #from_email = settings.DEFAULT_FROM_EMAIL
         #to = request.user.email
         #mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
         messages.success(request, 'Hours added successfully')
         return redirect('/history')
      else:
         messages.success(request, 'Invalid form submission.')
         return redirect('/history')
   else:
      form = VolunteerRecordForm()

   return render(request, "add_individual_hours.html", {"form": form, "user": request.user})

@login_required
def edit_individual_hours(request):
   if request.user.is_staff:
      record_id = request.GET.get('id', '')
      if record_id != '':
         if request.method == "POST":
            form = VolunteerRecordForm(request.POST, instance=VolunteerRecord.objects.get(id=record_id))
            if form.is_valid():
               # Set user field in the form here
               record = form.save(commit = False)
               record.owner = request.user
               record.save()
               messages.success(request, 'Hour record updated successfully.')
               return redirect('/history')
            else:
               messages.error(request, 'Invalid form submission.')
               return redirect('/history')
         else:
            try:
               form = VolunteerRecordForm(instance=VolunteerRecord.objects.get(id=record_id))
               return render(request, "edit_individual_hours.html", {"form": form, "user": request.user})
            except:
               messages.error(request, 'Invalid ID.')
               return redirect('/history')
      else:
         messages.error(request, 'Invalid ID.')
         return redirect('/history')
   else:
      messages.error(request, 'You are not authorized to perform this action.')
      return redirect('/history')

@login_required
def events(request):
   if request.user.is_staff:
      records = EventModel.objects.all()
      myFilter = EventFilter(request.GET, queryset=records)
      records = myFilter.qs
      paginator = Paginator(records, settings.PAGINATOR_COUNT)
      page_number = request.GET.get('page')
      page_obj = paginator.get_page(page_number)
      return render(request, "events.html", {"page_obj" : page_obj, 'myFilter': myFilter})
   else:
      messages.error(request, 'You do not have permission to access this resource.')
      return redirect('/history')

@login_required
def volunteers(request):
   if request.user.is_staff:
      records = User.objects.all()

      myFilter = VolunteerFilter(request.GET, queryset=records)
      records = myFilter.qs

      paginator = Paginator(records, settings.PAGINATOR_COUNT)
      page_number = request.GET.get('page')
      page_obj = paginator.get_page(page_number)
      return render(request, "volunteers.html", {"page_obj" : page_obj, 'myFilter': myFilter})
   else:
      messages.error(request, 'You do not have permission to access this resource.')
      return redirect('/history')

@login_required
def history(request):
   current_user = request.user
   title = ''
   person_id = request.GET.get('owner', '')
   running_total = 0
   if person_id == '':
      # Not filtering by person, so display all records (or only user's current records)
      if current_user.is_staff:
         title = 'All Volunteer Hours'
         records = VolunteerRecord.objects.all()
      else:
         title = 'Your Volunteer Hours'
         records = VolunteerRecord.objects.filter(owner = current_user)
   else:
      # Otherwise, filter by that ID, and ensure user has access
      if int(person_id) == current_user.id or current_user.is_staff:
         try:
            user_obj = User.objects.get(id=person_id)
            records = VolunteerRecord.objects.filter(owner = user_obj)
            title = 'Volunteer Hours for ' + str(user_obj)
         except:
            messages.error(request, 'Invalid user ID.')
            return redirect('/history')
      else:
         messages.error(request, 'You do not have permission to do that.')
         return redirect('/history')
   running_total = sum(rec.hours for rec in records)
   
   myFilter = HistoryFilter(request.GET, queryset=records)
   records = myFilter.qs

   paginator = Paginator(records, settings.PAGINATOR_COUNT)
   page_number = request.GET.get('page')
   page_obj = paginator.get_page(page_number)
   return render(request, "history.html", {"page_obj" : page_obj, "running_total": running_total, "title": title, "id":person_id, 'myFilter': myFilter})


@login_required
def profile(request):
   current_user = request.user
   profile_form = ProfileForm(instance=request.user.profile)
   hours = VolunteerRecord.objects.filter(
      owner = current_user).all().aggregate(
         total_hours=Sum('hours'))['total_hours'] or 0
   return render(request, "profile.html", {'hours' : hours, 'user': current_user, 'profile_form': profile_form})

@login_required
def update_profile(request):
   if request.method == "POST":
      user_form = SignUpForm(request.POST, instance=request.user)
      profile_form = ProfileForm(request.POST, instance=request.user.profile)
      if user_form.is_valid() and profile_form.is_valid():
         user_form.save()
         profile_form.save()
         return redirect('/profile')
      else:
         messages.error(request, 'Invalid form submission (are you sure your passwords match?).')
         return redirect('/update_profile')
   else:
      user_form = SignUpForm(instance=request.user)
      profile_form = ProfileForm(instance=request.user.profile)
      return render(request, 'update_profile.html', {
         'user_form': user_form,
         'profile_form': profile_form
      })

@login_required
def update_user(request):
   if request.user.is_staff:
      user_id = request.GET.get('id', '')
      if user_id != '':
         if request.method == "POST":
            user = User.objects.get(id=int(user_id))
            form = UpdateUserForm(request.POST)
            if form.is_valid():
               try:
                  user.first_name = form.cleaned_data['first_name']
                  user.last_name = form.cleaned_data['last_name']
                  user.email = form.cleaned_data['email']
                  if form.cleaned_data['phone'] != '':
                     user.profile.phone = int(form.cleaned_data['phone'])
                  user.profile.birth_date = form.cleaned_data['birth_date']
                  user.profile.waiver = form.cleaned_data['waiver']
                  if form.cleaned_data['is_staff'] != '0':
                     user.is_staff = form.cleaned_data['is_staff'] == '1'
                  user.save()
                  messages.success(request, user.get_full_name() + ' was updated successfully.')
                  return redirect('/view_user/?user=' + user_id)
               except Exception as e:
                  exception_msg = str(e)
                  messages.error(request, 'Sorry, an error occurred (2: ' + exception_msg + ').')
                  return redirect('/view_user/?user=' + user_id)
            else:
               messages.error(request, 'Sorry, an error occurred (1).')
               return redirect('/view_user/?user=' + user_id)
         else:
            user = User.objects.get(id=int(user_id))
            form = UpdateUserForm()
            return render(request, 'update_user.html', {
               'form': form,
               'user': user
            })
      else:
         messages.error(request, 'Invalid user ID.')
         return redirect('/volunteers')
   else:
      messages.error(request, 'You do not have permission to do that.')
      return redirect('/history')

@login_required
def update_event(request):
   event_id = request.GET.get('id', '')
   if request.user.is_staff and event_id != '' and EventModel.objects.filter(id=int(event_id)).count() == 1:
      if request.method == "POST":
         event_form = EventForm(request.POST, instance=EventModel.objects.filter(id=int(event_id)).first())
         if event_form.is_valid():
            event_form.save()
            messages.success(request, 'Event updated successfully')
            return redirect('/events')
         else:
            messages.error(request, 'Invalid form submission')
            return redirect('/events')
      else:
         event_form = EventForm(instance=EventModel.objects.filter(id=int(event_id)).first())
      return render(request, 'update_event.html', {
         'event_form': event_form, 'id': event_id
      })
   else:
      messages.error(request, 'An error occurred.')
      return redirect('/history')

@login_required
def view_user(request):
   if request.user.is_staff:
      user_id = request.GET.get('user', '')
      if user_id == '':
        user_id = request.user.id
      else:
        user_id = int(user_id)
      try:
         current_user = User.objects.get(id=user_id)
         profile_form = ProfileForm(instance=request.user.profile)
         hours = VolunteerRecord.objects.filter(
         owner = current_user).all().aggregate(
                     total_hours=Sum('hours'))['total_hours'] or 0
         return render(request, "profile_view.html", {'hours': hours, 'user': request.user, 'view_user': current_user, 'profile_form': profile_form})
      except:
         messages.error(request, 'Invalid user ID.')
         return redirect('/history')
   else:
      messages.error(request, 'You do not have permission to do that.')
      return redirect('/history')

@login_required
def delete_volunteer_record(request):
   record_id = request.GET.get('id', '')
   if record_id == '':
      messages.error(request, 'Invalid volunteer record ID')
      return redirect ('/history')
   else:
      try:
         vol_record = VolunteerRecord.objects.get(id=int(record_id))
         if vol_record.owner == request.user or request.user.is_staff:
            vol_record.delete()
            messages.warning(request, 'Volunteer record deleted successfully.')
            return redirect ('/history')
         else:
            messages.error(request, 'You do not have permission to perform this action.')
            return redirect ('/history')
      except:
         messages.error(request, 'Invalid ID.')
         return redirect ('/history')


@login_required
def delete_event(request):
   if request.user.is_staff:
      record_id = request.GET.get('id', '')
      if record_id != '' and request.user.is_staff:
         try:
            event_record = EventModel.objects.get(id=int(record_id))
            event_record.delete()
            messages.warning(request, 'Event delected successfully')
            return redirect ('/events')
         except:
            messages.error(request, 'Invalid ID.')
            return redirect ('/events')
      else:
         messages.error(request, 'Missing ID.')
         return redirect ('/events')
   else:
      messages.error(request, 'You do not have permission to perform this action.')
      return redirect ('/history')
