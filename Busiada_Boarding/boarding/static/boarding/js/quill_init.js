document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('id_content');
    if (!textarea) return;

    // hide the textarea but keep it in the form
    textarea.style.display = 'none';

    // create editor container
    const editorContainer = document.createElement('div');
    editorContainer.id = 'quill_editor';
    editorContainer.style.minHeight = '300px';
    editorContainer.style.background = '#fff';
    textarea.parentNode.insertBefore(editorContainer, textarea.nextSibling);

    // init Quill
    const quill = new Quill('#quill_editor', {
        theme: 'snow',
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline', 'strike'],
                ['color', 'background'],
                [{ 'header': [1, 2, 3, false] }],
                [{ 'align': [] }],
                [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                ['blockquote', 'code-block', 'link', 'image']
            ]
        }
    });

    // set initial content from textarea (assume HTML)
    try {
        quill.root.innerHTML = textarea.value;
    } catch (e) { }

    // on form submit, copy HTML back to textarea
    const form = textarea.closest('form');
    if (form) {
        form.addEventListener('submit', function() {
            textarea.value = quill.root.innerHTML;
        });
    }

    // Expose quill on window for other admin scripts
    window.__quill_for_admin = quill;
});
