from django.contrib import admin
from councilmatic_core.models import Person, Membership, Organization
from philadelphia.models import PhilaBill
# import your models

# Register your models here.
# admin.site.register(YourModel)

admin.site.register(Person)
admin.site.register(PhilaBill)
admin.site.register(Membership)
admin.site.register(Organization)


