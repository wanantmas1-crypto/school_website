from django.utils.safestring import mark_safe
from django.contrib import admin
from django import forms
from django.utils.text import slugify
from django.core.files.base import ContentFile
import time
from .models import Inquiry, SitePage, PageImage, PageVideo, Document, Announcement, HistoryImage, SchoolAnthem, GalleryCategory, Leadership
from .models import SiteSettings
from .validators import compress_image, get_file_size_display


class RichTextAdminForm(forms.ModelForm):
    rich_text_fields = ()

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.rich_text_fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'rows': 18,
                    'style': 'width: 100%; min-height: 420px; box-sizing: border-box;',
                    'data-quill-editor': 'true',
                })
                field.help_text = (
                    f'{field.help_text} ' if field.help_text else ''
                ) + 'Use the toolbar to format content, or choose HTML to edit the source directly.'


class SitePageAdminForm(RichTextAdminForm):
    rich_text_fields = ('content',)

    class Meta:
        model = SitePage
        fields = '__all__'
        widgets = {
            'sections': forms.Textarea(attrs={
                'rows': 18,
                'style': 'width: 100%; min-height: 300px; font-family: monospace; resize: vertical; box-sizing: border-box;'
            }),
        }

    class Media(RichTextAdminForm.Media):
        js = RichTextAdminForm.Media.js + [
            'boarding/js/admin_image_preview.js',
            'boarding/js/inline_ordering.js',
            'boarding/js/upload_progress.js',
        ]

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


class SiteSettingsAdminForm(RichTextAdminForm):
    rich_text_fields = ('principal_message',)

    class Meta:
        model = SiteSettings
        fields = '__all__'

    class Media(RichTextAdminForm.Media):
        js = RichTextAdminForm.Media.js + [
            'boarding/js/admin_image_preview.js',
            'boarding/js/upload_progress.js',
        ]


class SchoolAnthemAdminForm(RichTextAdminForm):
    rich_text_fields = ('lyrics',)

    class Meta:
        model = SchoolAnthem
        fields = '__all__'


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HistoryImage)
class HistoryImageAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'created_at']
    search_fields = ['year', 'title', 'description']
    ordering = ['year', 'created_at']
    readonly_fields = ['created_at']


@admin.register(SchoolAnthem)
class SchoolAnthemAdmin(admin.ModelAdmin):
    form = SchoolAnthemAdminForm
    list_display = ['title', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'role_category', 'is_active', 'order']
    list_filter = ['role_category', 'is_active']
    search_fields = ['name', 'position', 'description']
    ordering = ['role_category', 'order', 'name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Leadership profile', {
            'fields': ('name', 'position', 'role_category', 'description', 'portrait', 'is_active', 'order'),
            'description': 'Active profiles are published on the School Leadership page. Portraits are optional; a matching SVG icon is shown when no portrait is uploaded.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'portrait' in form.files:
            obj.portrait = compress_image(form.files['portrait'], quality=85)
        super().save_model(request, obj, form, change)


class PageImageInline(admin.TabularInline):
    model = PageImage
    fk_name = 'page'
    template = 'admin/edit_inline/tabular.html'
    extra = 0
    fields = ['title', 'caption', 'description', 'image', 'category', 'order', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    ordering = ['order', 'uploaded_at']
    
    class Media:
        js = [
            'boarding/js/upload_progress.js',
        ]
    
    def save_model(self, request, obj, form, change):
        # Compress image if provided
        if 'image' in form.files:
            image_file = form.files['image']
            obj.image = compress_image(image_file, quality=85)
        obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


class PageVideoInline(admin.TabularInline):
    model = PageVideo
    fk_name = 'page'
    template = 'admin/edit_inline/tabular.html'
    verbose_name_plural = 'Videos (first ordered video on Home takes priority over homepage images and is used as the hero background)'
    extra = 0
    fields = ['title', 'caption', 'description', 'video', 'order', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    ordering = ['order', 'uploaded_at']
    
    class Media:
        js = [
            'boarding/js/upload_progress.js',
        ]
    
    def save_model(self, request, obj, form, change):
        obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


class DocumentInline(admin.TabularInline):
    model = Document
    fk_name = 'page'
    template = 'admin/edit_inline/tabular.html'
    extra = 0
    fields = ['title', 'description', 'file', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    
    class Media:
        js = [
            'boarding/js/upload_progress.js',
        ]
    
    def save_model(self, request, obj, form, change):
        obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


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
            'classes': ('wide',),
            'description': 'featured_image is used in page galleries and carousels. background_image is used as the page background. On student-life pages, featured_image is an optional hero photo and Page Images add an optional gallery; both are omitted when no media is uploaded. On the School Gallery page, assign each Page Image a category from the dropdown. Use the + icon beside Category to add a category, or manage them from Gallery categories in the admin. New categories automatically become School Gallery filters. On the School Chaplaincy page, background_image is the hero background; featured_image and multiple Page Images below create an automatically transitioning introduction slideshow, while Page Images also populate the Growing Through Connection gallery. On the Home page, uploaded Page Images are used as an automatically transitioning hero slideshow in admin order; an uploaded video takes priority, and background_image is the fallback when no hero images or video are available. To add photos to the “Why Parents Choose Us” homepage slideshow, add Page Images to Home and choose the “Why Parents Choose Us Slideshow” category; order controls the slideshow sequence. On the CBE page, add any number of Page Images titled “STEM”, “Social Sciences”, or “Arts & Sports Science” to populate each pathway gallery. STEM Laboratory and Computer Lab titles are also treated as STEM images. Images appear in their admin-defined order; pathways without uploads show no image area. On the 8-4-4 Curriculum page, upload Documents to the pages with slugs “844-assignments”, “844-revision-materials”, and “844-past-kcse-papers” to publish downloads on the matching resource pages.'
        }),
        ('Senior School Pathway Populations', {
            'fields': ('stem_learner_population', 'social_sciences_learner_population'),
            'description': 'Optional learner counts shown on the Senior School 2-6-3-3-3 pathway cards. Leave blank until confirmed.'
        }),
        ('Metadata', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        
        # Compress images if provided
        if 'featured_image' in form.files:
            obj.featured_image = compress_image(form.files['featured_image'], quality=85)
        if 'background_image' in form.files:
            obj.background_image = compress_image(form.files['background_image'], quality=80)
        
        super().save_model(request, obj, form, change)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'is_featured', 'is_important', 'date', 'event_date']
    list_filter = ['is_active', 'is_featured', 'is_important', 'category', 'date']
    search_fields = ['title', 'subtitle', 'content']
    readonly_fields = ['date', 'image_preview']
    fieldsets = (
        ('Announcement', {
            'fields': (
                'title', 'subtitle', 'category', 'content', 'image',
                'video_url', 'is_live_event', 'event_start', 'event_end',
                'event_location', 'event_link', 'document_link', 'document_label',
                'is_active', 'is_featured', 'is_important',
            )
        }),
        ('Event / CTA', {
            'fields': ('event_date', 'cta_text', 'cta_link'),
            'classes': ('collapse',)
        }),
    )
    def image_preview(self, obj):
        if obj and getattr(obj, 'image'):
            try:
                url = obj.image.url
            except Exception:
                url = None
            if url:
                return mark_safe(f"<img src=\"{url}\" style=\"max-height:180px; max-width:320px; object-fit:contain; border-radius:6px;\" />")
        return ''
    image_preview.short_description = 'Current image'
    
    class Media:
        js = [
            'boarding/js/upload_progress.js',
        ]
    
    def save_model(self, request, obj, form, change):
        # Compress image if provided
        if 'image' in form.files:
            obj.image = compress_image(form.files['image'], quality=85)
        super().save_model(request, obj, form, change)


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
    
    class Media:
        js = [
            'boarding/js/upload_progress.js',
        ]
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    list_display = ['site_name', 'tagline']
    readonly_fields = ['logo_preview', 'principal_image_preview']
    fieldsets = (
        ('Branding', {'fields': ('site_name', 'tagline', 'phone_number', 'logo')}),
        ('Principal Message', {'fields': ('principal_name', 'principal_title', 'principal_image', 'principal_message')}),
    )

    def logo_preview(self, obj):
        if obj and getattr(obj, 'logo'):
            try:
                url = obj.logo.url
            except Exception:
                url = None
            if url:
                return mark_safe(f"<img src=\"{url}\" style=\"max-height:120px; max-width:220px; object-fit:contain; border-radius:6px;\" />")
        return ''
    logo_preview.short_description = 'Current logo'

    def principal_image_preview(self, obj):
        if obj and getattr(obj, 'principal_image'):
            try:
                url = obj.principal_image.url
            except Exception:
                url = None
            if url:
                return mark_safe(f"<img src=\"{url}\" style=\"max-height:160px; max-width:160px; object-fit:cover; border-radius:6px;\" />")
        return ''
    principal_image_preview.short_description = 'Principal image'

    class Media:
        js = [
            'boarding/js/upload_progress.js',
        ]
    
    def save_model(self, request, obj, form, change):
        # Compress images if provided
        if 'logo' in form.files:
            obj.logo = compress_image(form.files['logo'], quality=90)
        if 'principal_image' in form.files:
            obj.principal_image = compress_image(form.files['principal_image'], quality=85)
        super().save_model(request, obj, form, change)

    def image_preview(self, obj):
        if obj and getattr(obj, 'image'):
            try:
                url = obj.image.url
            except Exception:
                url = None
            if url:
                return mark_safe(f"<img src=\"{url}\" style=\"max-height:180px; max-width:320px; object-fit:contain; border-radius:6px;\" />")
        return ''
    image_preview.short_description = 'Current image'