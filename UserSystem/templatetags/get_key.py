from django.template.defaulttags import register

@register.filter
def get_dictionary_item(dictionary, key):
    return dictionary.get(key)


register.tag('get_dictionary_item', get_dictionary_item)