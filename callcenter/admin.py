from django.contrib import admin
from .models import Table, Main, Sources, Contractor
# Register your models here.

admin.site.register(Main)
admin.site.register(Table)
admin.site.register(Sources)
admin.site.register(Contractor)
