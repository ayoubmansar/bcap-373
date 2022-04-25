from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

class EventModel(models.Model):
	name = models.CharField(max_length=256, blank=False)
	def __str__(self):
		return self.name
	
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phone = models.CharField(max_length=20, blank=True,
		help_text="Please enter your phone number in the following format: (XXX) XXX-XXXX")
	birth_date = models.DateField(null=True, blank=True)
	waiver = models.CharField(null=True, max_length=300, help_text="If you have this user's waiver on file, please indicate this in this box (and give a link to where it can be found, e.g. on Google Drive)")
	def __str__(self):
		return "{} {}".format(self.user.first_name, self.user.last_name)

class VolunteerRecord(models.Model):
	activity = models.ForeignKey(EventModel, on_delete=models.SET_NULL, null=True)
	hours = models.FloatField(blank=False)
	date = models.DateField(auto_now=False, auto_now_add=False, blank=False)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True}, related_name='supervisor')
	description = models.CharField(max_length=1000, blank=True, default='')
	owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return "Owner: {}, Date: {}, Activity: {}".format(self.owner, self.date, self.activity)
	
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

def get_user_name(self):
	'''
	This method gets a user object and looks up the corresponding profile
	(which has the same ID) and returns the first and last name.
	'''
	uid = self.id
	profile = Profile.objects.get(id=uid)
	return str(profile).title()

def get_hours(self):
	'''
	This method gets a user object and looks up the number
	of hours they may have.
	'''
	hours = VolunteerRecord.objects.filter(
            owner = self).all().aggregate(
                    total_hours=Sum('hours'))['total_hours'] or 0
	return str(hours)


User.add_to_class("__str__", get_user_name)
User.add_to_class("get_hours", get_hours)