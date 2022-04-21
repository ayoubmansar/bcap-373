from django import template
register = template.Library()

def phonenumber(value):
    if len(value) == 10:
        # If U.S. based, format it
        phone = '(%s) %s-%s' %(value[0:3],value[3:6],value[6:10])
        return phone
    else:
        # Otherwise it's weird, so just render in plaintext
        return value

register.filter('phonenumber', phonenumber)