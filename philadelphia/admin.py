from django.contrib import admin
from councilmatic_core.models import Person, Membership, Organization
from philadelphia.models import PhilaBill
from opencivicdata.core.models import Person as OCDPerson
# import your models

# Register your models here.
# admin.site.register(YourModel)


class OCDPersonAdmin(admin.ModelAdmin):
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        return inline_instances




class PersonAdmin(admin.ModelAdmin):
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        return inline_instances

#admin.site.unregister(OCDPerson)
#admin.site.register(OCDPerson, OCDPersonAdmin)
admin.site.register(PhilaBill)
admin.site.register(Membership)
admin.site.register(Organization)


