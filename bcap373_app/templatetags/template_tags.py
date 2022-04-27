from django import template
register = template.Library()

@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url
    
def phonenumber(value):
    if len(value) == 10:
        # If U.S. based, format it
        phone = '(%s) %s-%s' %(value[0:3],value[3:6],value[6:10])
        return phone
    else:
        # Otherwise it's weird, so just render in plaintext
        return value

register.filter('phonenumber', phonenumber)