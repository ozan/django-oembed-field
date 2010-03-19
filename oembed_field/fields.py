import re

from django.core import exceptions
from django.db import models

DEFAULT_PROVIDER_RULES = (
    r'http://vimeo.com/\S*',
    r'http://\S*.youtube.com/watch\S*',
    r'http://video.google.com/videoplay?\S*',
    r'http://qik.com/\S*',
    r'http://\S*?flickr.com/\S*',
)

class OEmbedField(models.URLField):
    """
    A URL pointing to an oEmbed provider.
    
    See http://www.oembed.com/ for information on providers
    """
    
    description = "A URL pointing to an oEmbed provider"
    
    def __init__(self, provider_rules=None, *args, **kwargs):
        """
        Initialise with `provider_rules`, an iterable of regex patterns
        defining valid oEmbed provider url schemes.
        
        As this field will likely be used in conjunction with Eric Florenzano's
        django-oembed (http://github.com/ericflo/django-oembed), where
        `provider_rules` is not provided, an attempt is made to take access
        provider rules through django-oembed's ProviderRule model. If neither
        is available, a selection of default rules are used.
        """
        if not provider_rules:
            try:
                from oembed.models import ProviderRule
                provider_rules = (r.regex for r in ProviderRule.objects.all())
            except ImportError:
                provider_rules = DEFAULT_PROVIDER_RULES
        self.provider_rules = provider_rules
        super(OEmbedField, self).__init__(*args, **kwargs)
        
    def validate(self, value, model_instance):
        for rule in self.provider_rules:
            if re.match(rule, value):
                return
        raise exceptions.ValidationError('Not a valid oEmbed link')
        