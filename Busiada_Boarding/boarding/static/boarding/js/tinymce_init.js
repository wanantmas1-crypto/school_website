document.addEventListener('DOMContentLoaded', function() {
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: '#id_content',
            height: 420,
            menubar: false,
            plugins: 'link image lists code paste table media',
            toolbar: 'undo redo | styleselect | bold italic underline | alignleft aligncenter alignright | bullist numlist | link image media | removeformat | code',
            branding: false,
            entity_encoding: 'raw'
        });
    }
});
