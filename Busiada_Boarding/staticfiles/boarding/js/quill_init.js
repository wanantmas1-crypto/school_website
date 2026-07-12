document.addEventListener('DOMContentLoaded', function () {
    const textareas = Array.from(document.querySelectorAll('textarea[data-quill-editor="true"]'));
    if (!textareas.length) return;

    // Theme can be 'dark' or 'light' — change here if desired.
    const THEME = 'dark';

    const isDark = THEME === 'dark';
    const toolbarBg = isDark ? '#0b1220' : '#f1f5f9';
    const toolbarColor = isDark ? '#ffffff' : '#0f172a';
    const editorBg = isDark ? '#000000' : '#ffffff';
    const editorColor = isDark ? '#ffffff' : '#000000';

    window.__quill_editors = window.__quill_editors || {};

    const toolbarOptions = [
        [{ 'font': [] }, { 'size': ['small', false, 'large', 'huge'] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
        [{ 'script': 'sub' }, { 'script': 'super' }],
        [{ 'list': 'ordered' }, { 'list': 'bullet' }],
        [{ 'indent': '-1' }, { 'indent': '+1' }],
        [{ 'align': [] }],
        ['blockquote', 'code-block', 'link', 'image', 'clean']
    ];

    textareas.forEach((textarea, index) => {
        // hide original textarea
        textarea.style.display = 'none';

        // Build containers
        const container = document.createElement('div');
        container.className = 'quill-wrapper';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.width = '100%';

        const toolbarContainer = document.createElement('div');
        toolbarContainer.className = 'quill-toolbar';
        toolbarContainer.style.background = toolbarBg;
        toolbarContainer.style.color = toolbarColor;
        toolbarContainer.style.padding = '6px 8px';
        toolbarContainer.style.borderRadius = '4px 4px 0 0';

        const editorContainer = document.createElement('div');
        editorContainer.className = 'quill-editor-container ql-container ql-snow';
        editorContainer.style.minHeight = '420px';
        editorContainer.style.background = editorBg;
        editorContainer.style.color = editorColor;
        editorContainer.style.margin = '0';
        editorContainer.style.padding = '0';
        editorContainer.style.boxSizing = 'border-box';
        editorContainer.style.border = '1px solid rgba(0,0,0,0.08)';
        editorContainer.style.borderRadius = '0 0 4px 4px';
        editorContainer.style.boxShadow = '0 1px 2px rgba(16,24,40,0.05)';

        // Insert wrapper into DOM (replace textarea visually)
        textarea.parentNode.insertBefore(container, textarea.nextSibling);
        container.appendChild(toolbarContainer);
        container.appendChild(editorContainer);

        const editorId = textarea.id || `quill_editor_${index}`;
        editorContainer.id = editorId + '_container';

        // Create Quill with toolbar options, then move generated toolbar into our toolbarContainer
        const quill = new Quill(editorContainer, {
            theme: 'snow',
            modules: { toolbar: toolbarOptions },
            placeholder: 'Compose content here...'
        });

        try {
            const toolbarModule = quill.getModule('toolbar');
            if (toolbarModule && toolbarModule.container) {
                // detach and reattach toolbar to our styled toolbarContainer
                toolbarModule.container.parentNode && toolbarModule.container.parentNode.removeChild(toolbarModule.container);
                toolbarContainer.appendChild(toolbarModule.container);
                toolbarModule.container.style.background = 'transparent';
            }
        } catch (e) { }

        // Style the editor root
        try {
            quill.root.style.background = editorBg;
            quill.root.style.color = editorColor;
            quill.root.style.padding = '12px';
            quill.root.style.minHeight = '360px';
            quill.root.style.outline = 'none';
            quill.enable(true);
        } catch (e) { }

        // Hide or remove common legacy editor elements that might remain
        try {
            const siblings = Array.from(container.parentNode.children);
            siblings.forEach(sib => {
                if (sib === container || sib === textarea) return;
                const cls = (sib.className || '').toLowerCase();
                if (cls.indexOf('codemirror') !== -1 || cls.indexOf('mce') !== -1 || cls.indexOf('cke') !== -1 || sib.tagName === 'IFRAME') {
                    sib.style.display = 'none';
                }
            });
        } catch (e) { }

        // Load initial content
        try {
            if (textarea.value) quill.root.innerHTML = textarea.value;
        } catch (e) { }

        // Ensure HTML is synced back to original textarea on submit
        const form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', function () {
                textarea.value = quill.root.innerHTML;
            });
        }

        // expose editor globally for debugging
        window.__quill_editors[textarea.id || editorId] = quill;
    });
});
