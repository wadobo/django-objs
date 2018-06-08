from django.contrib import admin

from objs.models import (Iteration, Project, UserDedication,
                         UserDedicationPr, ProjectDedication, Tag,
                         ProjectDedicationTagged)


class UserDedicationInline(admin.TabularInline):
    model = UserDedication


class UserDedicationPrInline(admin.TabularInline):
    model = UserDedicationPr


class IterationAdmin(admin.ModelAdmin):
    inlines = [
        UserDedicationInline,
    ]


class ProjectAdmin(admin.ModelAdmin):
    pass


class UserDedicationAdmin(admin.ModelAdmin):
    list_display = ('it', 'user', 'hours')

    inlines = [
        UserDedicationPrInline,
    ]


class UserDedicationPrAdmin(admin.ModelAdmin):
    pass


class ProjectDedicationAdmin(admin.ModelAdmin):
    list_display = ('it', 'user', 'pr', 'dedicated', 'time', 'commentary')


class ProjectDedicationTaggedAdmin(admin.ModelAdmin):
    list_display = ('project_dedication', 'tag')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_used')


admin.site.register(Iteration, IterationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(UserDedication, UserDedicationAdmin)
admin.site.register(UserDedicationPr, UserDedicationPrAdmin)
admin.site.register(ProjectDedication, ProjectDedicationAdmin)
admin.site.register(ProjectDedicationTagged, ProjectDedicationTaggedAdmin)
admin.site.register(Tag, TagAdmin)
