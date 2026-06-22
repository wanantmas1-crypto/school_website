document.addEventListener('DOMContentLoaded', function() {
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: '#id_content',
            height: 420,
            menubar: false,
            plugins: 'link image lists code paste table media',
            toolbar: 'undo redo | styleselect | bold italic underline strikethrough | alignleft aligncenter alignright | bullist numlist | blockquote | link image media | removeformat | code',
            paste_as_text: false,
            paste_data_images: false,
            branding: false,
            entity_encoding: 'raw',
            content_style: 'body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 14px; }'
        });
    }
});
