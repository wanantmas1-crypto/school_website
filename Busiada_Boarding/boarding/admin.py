from django.contrib import admin
from django import forms
from django.utils.text import slugify
import time
from .models import Inquiry, SitePage, PageImage, PageVideo, Document, Announcement, Leadership, SchoolAnthem, HistoryImage
from .models import SiteSettings


class SitePageAdminForm(forms.ModelForm):
    class Meta:
        model = SitePage
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 18,
                'style': 'width: 100%; min-height: 420px; box-sizing: border-box;',
                'data-quill-editor': 'true',
            }),
            'sections': forms.Textarea(attrs={
                'rows': 18,
                'style': 'width: 100%; min-height: 300px; font-family: monospace; resize: vertical; box-sizing: border-box;'
            }),
        }

    class Media:
        js = [
            'https://cdn.quilljs.com/1.3.6/quill.js',
            'boarding/js/quill_init.js',
            'boarding/js/inline_ordering.js',
        ]
        css = {
            'all': [
                'https://cdn.quilljs.com/1.3.6/quill.snow.css',
            ]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Present sections as pretty JSON for easier editing
        import json
        if 'sections' in self.fields:
            try:
                value = getattr(self.instance, 'sections', None)
                self.fields['sections'].initial = json.dumps(value or [], indent=2)
            except Exception:
                self.fields['sections'].initial = '[]'
        if 'slug' in self.fields:
            self.fields['slug'].help_text = (
                'Leave blank to auto-generate from title. If the slug already exists, '
                'a unique version will be created automatically.'
            )

    def clean_slug(self):
        slug = self.cleaned_data.get('slug') or ''
        title = self.cleaned_data.get('title') or getattr(self.instance, 'title', '') or ''
        if not slug and title:
            slug = slugify(title)
        if not slug:
            slug = f'page-{int(time.time())}'
        base = slugify(slug) or slug
        candidate = base[:200]
        counter = 1
        exclude_pk = getattr(self.instance, 'pk', None)
        while SitePage.objects.exclude(pk=exclude_pk).filter(slug=candidate).exists():
            candidate = f"{base[:195]}-{counter}"
            counter += 1
        return candidate

    def clean_sections(self):
        import json
        data = self.cleaned_data.get('sections')
        # If admin provided a JSON string (from the textarea), parse it
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
            except Exception as e:
                raise forms.ValidationError('Invalid JSON for sections: %s' % e)
            # basic validation: should be a list
            if not isinstance(parsed, list):
                raise forms.ValidationError('Sections must be a JSON array of blocks')
            return parsed
        return data


class SiteSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'principal_message': forms.Textarea(attrs={
                'rows': 18,
                'style': 'width: 100%; min-height: 420px; box-sizing: border-box;',
                'data-quill-editor': 'true',
            }),
        }

    class Media:
        js = [
            'https://cdn.quilljs.com/1.3.6/quill.js',
            'boarding/js/quill_init.js',
        ]
        css = {
            'all': [
                'https://cdn.quilljs.com/1.3.6/quill.snow.css',
            ]
        }


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


class PageImageInline(admin.StackedInline):
    model = PageImage
    fk_name = 'page'
    extra = 1
    max_num = 15
    fields = ['title', 'caption', 'description', 'image', 'order', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    ordering = ['order', 'uploaded_at']
    can_delete = True


class PageVideoInline(admin.StackedInline):
    model = PageVideo
    fk_name = 'page'
    extra = 1
    max_num = 10
    fields = ['title', 'caption', 'description', 'video', 'order', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    ordering = ['order', 'uploaded_at']
    can_delete = True


class DocumentInline(admin.StackedInline):
    model = Document
    fk_name = 'page'
    extra = 1
    max_num = 20
    fields = ['title', 'description', 'file', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    can_delete = True


@admin.register(HistoryImage)
class HistoryImageAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'created_at']
    search_fields = ['year', 'title']
    readonly_fields = ['created_at']
    fieldsets = (
        ('History Slide', {
            'fields': ('year', 'title', 'description', 'image')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SitePage)
class SitePageAdmin(admin.ModelAdmin):
    form = SitePageAdminForm
    list_display = ['title', 'category', 'slug', 'status', 'author', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PageImageInline, PageVideoInline, DocumentInline]
    
    fieldsets = (
        ('Page Information', {
            'fields': ('title', 'slug', 'category', 'status')
        }),
        ('Content', {
            'fields': ('content', 'featured_image', 'background_image', 'sections'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Ensure inline uploads record the uploading user."""
        instances = formset.save(commit=False)
        for instance in instances:
            # Set uploaded_by when missing
            if hasattr(instance, 'uploaded_by') and not instance.uploaded_by:
                instance.uploaded_by = request.user
            instance.save()
        # handle deletions and other default behavior
        formset.save_m2m()

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'is_featured', 'date', 'event_date']
    list_filter = ['is_active', 'is_featured', 'category', 'date']
    search_fields = ['title', 'subtitle', 'content']
    readonly_fields = ['date']
    fieldsets = (
        ('Announcement', {
            'fields': (
                'title', 'subtitle', 'category', 'content', 'image',
                'video_url', 'is_live_event', 'event_start', 'event_end',
                'event_location', 'event_link', 'document_link', 'document_label',
                'is_active', 'is_featured',
            )
        }),
        ('Event / CTA', {
            'fields': ('event_date', 'cta_text', 'cta_link'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'page', 'uploaded_by', 'uploaded_at', 'updated_at']
    list_filter = ['uploaded_at', 'updated_at', 'page']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at', 'updated_at']
    
    fieldsets = (
        ('Document Info', {
            'fields': ('title', 'description', 'file')
        }),
        ('Metadata', {
            'fields': ('page', 'uploaded_by', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    list_display = ['site_name', 'tagline']
    readonly_fields = []
    fieldsets = (
        ('Branding', {'fields': ('site_name', 'tagline', 'logo')}),
        ('Principal Message', {'fields': ('principal_name', 'principal_title', 'principal_image', 'principal_message')}),
    )


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'role_category', 'order', 'is_active']
    list_filter = ['role_category', 'is_active', 'created_at']
    search_fields = ['name', 'position', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['role_category', 'order', 'name']
    
    fieldsets = (
        ('Leadership Info', {
            'fields': ('name', 'position', 'role_category', 'description', 'color_scheme', 'order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SchoolAnthem)
class SchoolAnthmAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'uploaded_by']
    
    fieldsets = (
        ('Anthem Content', {
            'fields': ('title', 'lyrics')
        }),
        ('Audio File', {
            'fields': ('audio_file',),
            'description': 'Upload an MP3, WAV, OGG, or other audio format. Recommended: MP3 format for best browser compatibility.'
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)