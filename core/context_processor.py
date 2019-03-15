from django.conf import settings


def global_settings(request):
    return {
        'ORG_LOGO': settings.ORGANIZATION_LOGO,
        'ORG_SITE': settings.ORGANIZATION_SITE,
        'ORG': settings.ORGANIZATION,
    }
