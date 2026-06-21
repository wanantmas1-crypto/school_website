from django.contrib import admin
from django import forms
from .models import Inquiry, SitePage, PageImage, PageVideo, Document, Announcement


class SitePageAdminForm(forms.ModelForm):
    class Meta:
        model = SitePage
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={'rows': 18}),
        }
    class Media:
        js = [
            'https://cdn.quilljs.com/1.3.6/quill.js',
            'https://cdn.quilljs.com/1.3.6/quill.snow.css',
            'boarding/js/quill_init.js',
            'boarding/js/admin_ai.js',
            'boarding/js/inline_ordering.js',
        ]


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


class PageImageInline(admin.TabularInline):
    model = PageImage
    fk_name = 'page'
    template = 'admin/edit_inline/tabular.html'
    extra = 1
    fields = ['title', 'caption', 'description', 'image', 'order', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    ordering = ['order', 'uploaded_at']


class PageVideoInline(admin.TabularInline):
    model = PageVideo
    fk_name = 'page'
    template = 'admin/edit_inline/tabular.html'
    extra = 1
    fields = ['title', 'caption', 'description', 'video', 'order', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']
    ordering = ['order', 'uploaded_at']


class DocumentInline(admin.TabularInline):
    model = Document
    fk_name = 'page'
    template = 'admin/edit_inline/tabular.html'
    extra = 1
    fields = ['title', 'description', 'file', 'uploaded_at', 'updated_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'updated_at', 'uploaded_by']


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
            'fields': ('content', 'featured_image'),
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