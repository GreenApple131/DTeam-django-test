from django.contrib import admin
from .models import CV, Skill, Project


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ['name']


class ProjectInline(admin.StackedInline):
    model = Project
    extra = 1
    fields = ['title', 'description', 'technologies', 'url', 'start_date', 'end_date']


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'title', 'email', 'location', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'location']
    search_fields = ['first_name', 'last_name', 'email', 'title']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['skills']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'location')
        }),
        ('Professional Information', {
            'fields': ('title', 'bio')
        }),
        ('Experience & Education', {
            'fields': ('experience', 'education')
        }),
        ('Skills', {
            'fields': ('skills',)
        }),
        ('Links & Portfolio', {
            'fields': ('portfolio_url', 'linkedin_url', 'github_url')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProjectInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'cv', 'get_cv_name', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date', 'cv']
    search_fields = ['title', 'description', 'technologies', 'cv__first_name', 'cv__last_name']
    list_select_related = ['cv']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Project Information', {
            'fields': ('cv', 'title', 'description', 'technologies', 'url')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
    )
    
    def get_cv_name(self, obj):
        return obj.cv.full_name
    get_cv_name.short_description = 'CV Owner'