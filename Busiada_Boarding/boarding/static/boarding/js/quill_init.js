document.addEventListener('DOMContentLoaded', function () {
    const textareas = Array.from(document.querySelectorAll('textarea[data-quill-editor="true"]'));
    if (!textareas.length) return;

    if (!window.Quill) {
        textareas.forEach((textarea) => {
            const message = document.createElement('p');
            message.className = 'quill-load-warning';
            message.textContent = 'The rich-text editor could not load. You can still enter content as HTML in this field.';
            textarea.parentNode.insertBefore(message, textarea);
        });
        return;
    }

    window.__quill_editors = window.__quill_editors || {};

    const toolbarOptions = [
        [{ header: [1, 2, 3, 4, 5, 6, false] }],
        [{ font: [] }, { size: ['small', false, 'large', 'huge'] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ color: [] }, { background: [] }],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ indent: '-1' }, { indent: '+1' }],
        [{ align: [] }, { direction: 'rtl' }],
        ['blockquote', 'code-block', 'link', 'clean']
    ];

    textareas.forEach((textarea, index) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'quill-admin-editor';
        textarea.parentNode.insertBefore(wrapper, textarea.nextSibling);

        const controls = document.createElement('div');
        controls.className = 'quill-admin-controls';
        wrapper.appendChild(controls);

        const addButton = (label, title, onClick) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'quill-admin-button';
            button.textContent = label;
            button.title = title;
            button.setAttribute('aria-label', title);
            button.addEventListener('click', onClick);
            controls.appendChild(button);
            return button;
        };

        const toolbarContainer = document.createElement('div');
        toolbarContainer.className = 'quill-admin-toolbar';
        wrapper.appendChild(toolbarContainer);

        const editorContainer = document.createElement('div');
        editorContainer.className = 'quill-editor-container';
        wrapper.appendChild(editorContainer);

        const sourceEditor = document.createElement('textarea');
        sourceEditor.className = 'quill-html-source';
        sourceEditor.setAttribute('aria-label', 'HTML source');
        sourceEditor.spellcheck = false;
        sourceEditor.hidden = true;
        wrapper.appendChild(sourceEditor);

        const quill = new Quill(editorContainer, {
            theme: 'snow',
            modules: {
                toolbar: toolbarOptions,
                history: { delay: 1000, maxStack: 100, userOnly: true }
            },
            placeholder: 'Write and format your content here...'
        });

        const toolbar = quill.getModule('toolbar');
        if (toolbar && toolbar.container) toolbarContainer.appendChild(toolbar.container);

        const sourceButton = addButton('HTML', 'Edit the HTML source', () => {
            if (sourceEditor.hidden) {
                sourceEditor.value = quill.root.innerHTML;
                sourceEditor.hidden = false;
                editorContainer.hidden = true;
                sourceButton.textContent = 'Visual editor';
                sourceButton.setAttribute('aria-pressed', 'true');
                sourceEditor.focus();
            } else {
                quill.root.innerHTML = sourceEditor.value;
                sourceEditor.hidden = true;
                editorContainer.hidden = false;
                sourceButton.textContent = 'HTML';
                sourceButton.setAttribute('aria-pressed', 'false');
                quill.focus();
            }
        });
        sourceButton.setAttribute('aria-pressed', 'false');

        addButton('Undo', 'Undo the last change', () => quill.history.undo());
        addButton('Redo', 'Redo the last undone change', () => quill.history.redo());

        const expandButton = addButton('Expand', 'Expand the editor', () => {
            const expanded = wrapper.classList.toggle('quill-admin-editor-expanded');
            expandButton.textContent = expanded ? 'Close' : 'Expand';
            expandButton.setAttribute('aria-pressed', String(expanded));
        });
        expandButton.setAttribute('aria-pressed', 'false');

        const editorId = textarea.id || `quill_editor_${index}`;
        if (textarea.value) quill.root.innerHTML = textarea.value;
        textarea.style.display = 'none';

        const form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', function () {
                textarea.value = sourceEditor.hidden ? quill.root.innerHTML : sourceEditor.value;
            });
        }

        wrapper.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && wrapper.classList.contains('quill-admin-editor-expanded')) {
                wrapper.classList.remove('quill-admin-editor-expanded');
                expandButton.textContent = 'Expand';
                expandButton.setAttribute('aria-pressed', 'false');
            }
        });

        window.__quill_editors[textarea.id || editorId] = quill;
    });

    const styles = document.createElement('style');
    styles.textContent = `
        .quill-admin-editor {
            width: 100%;
            color: #1e293b;
        }
        .quill-admin-controls {
            display: flex;
            flex-wrap: wrap;
            gap: .5rem;
            padding: .65rem;
            border: 1px solid #cbd5e1;
            border-bottom: 0;
            border-radius: .65rem .65rem 0 0;
            background: #f1f5f9;
        }
        .quill-admin-button {
            padding: .35rem .7rem;
            border: 1px solid #cbd5e1;
            border-radius: .4rem;
            background: #fff;
            color: #1e3a5f;
            font: inherit;
            font-size: .8rem;
            font-weight: 600;
            cursor: pointer;
        }
        .quill-admin-button:hover,
        .quill-admin-button[aria-pressed="true"] {
            border-color: #2b6cb0;
            background: #ebf4ff;
        }
        .quill-admin-toolbar .ql-toolbar.ql-snow {
            border: 1px solid #cbd5e1;
            border-bottom: 0;
            background: #fff;
        }
        .quill-admin-editor .ql-container.ql-snow {
            min-height: 22rem;
            border: 1px solid #cbd5e1;
            border-radius: 0 0 .65rem .65rem;
            background: #fff;
            font-size: 1rem;
        }
        .quill-admin-editor .ql-editor {
            min-height: 22rem;
            padding: 1rem;
            color: #1e293b;
        }
        .quill-html-source {
            display: block;
            width: 100%;
            min-height: 22rem;
            padding: 1rem;
            border: 1px solid #cbd5e1;
            border-radius: 0 0 .65rem .65rem;
            background: #0f172a;
            color: #e2e8f0;
            font:  .9rem/1.6 ui-monospace, SFMono-Regular, Consolas, monospace;
            tab-size: 2;
        }
        .quill-html-source[hidden],
        .quill-editor-container[hidden] {
            display: none;
        }
        .quill-load-warning {
            color: #9a3412;
            font-weight: 600;
        }
        .quill-admin-editor-expanded {
            position: fixed;
            z-index: 10000;
            inset: 1rem;
            display: flex;
            flex-direction: column;
            width: auto;
            padding: 1rem;
            overflow: auto;
            border: 1px solid #cbd5e1;
            border-radius: .75rem;
            background: #fff;
            box-shadow: 0 20px 60px rgba(15, 23, 42, .3);
        }
        .quill-admin-editor-expanded .quill-editor-container,
        .quill-admin-editor-expanded .quill-html-source {
            flex: 1;
            min-height: 0;
        }
        .quill-admin-editor-expanded .ql-container.ql-snow,
        .quill-admin-editor-expanded .ql-editor {
            min-height: 0;
            height: 100%;
        }
        @media (max-width: 700px) {
            .quill-admin-editor .ql-toolbar.ql-snow {
                padding: .5rem;
            }
            .quill-admin-editor .ql-formats {
                margin-right: .4rem;
            }
        }
    `;
    document.head.appendChild(styles);
});
