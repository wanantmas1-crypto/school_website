function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function createAIButton() {
    const contentEl = document.getElementById('id_content');
    if (!contentEl) return;

    // Avoid duplicate
    if (document.getElementById('ai-assist-btn')) return;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'ai-assist-btn';
    btn.className = 'button';
    btn.style.margin = '8px 0 12px 0';
    btn.textContent = 'AI Assist: Suggest Summary & SEO';

    contentEl.parentNode.insertBefore(btn, contentEl.nextSibling);

    const resultBox = document.createElement('textarea');
    resultBox.id = 'ai-result-box';
    resultBox.style.width = '100%';
    resultBox.style.minHeight = '140px';
    resultBox.style.marginTop = '8px';
    resultBox.placeholder = 'AI suggestions will appear here...';
    contentEl.parentNode.insertBefore(resultBox, btn.nextSibling);

    const applyBtn = document.createElement('button');
    applyBtn.type = 'button';
    applyBtn.textContent = 'Apply Summary to Content (append)';
    applyBtn.style.marginTop = '8px';
    applyBtn.style.display = 'block';
    resultBox.parentNode.insertBefore(applyBtn, resultBox.nextSibling);

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = 'Generating...';
        const csrftoken = getCookie('csrftoken');
        const quill = window.__quill_editors && window.__quill_editors['id_content'];
        const tiny = window.tinymce && window.tinymce.activeEditor;
        const content = quill ? quill.getText() : tiny ? tiny.getContent({ format: 'text' }) : contentEl.value;
        try {
            const resp = await fetch('/ai/admin/suggest/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({ content })
            });
            const data = await resp.json();
            resultBox.value = 'Summary:\n' + data.summary + '\n\nSEO Title:\n' + data.seo_title + '\n\nMeta Description:\n' + data.meta_description;
        } catch (err) {
            resultBox.value = 'Error: ' + err.message;
        }
        btn.disabled = false;
        btn.textContent = 'AI Assist: Suggest Summary & SEO';
    });

    applyBtn.addEventListener('click', () => {
        const text = resultBox.value;
        if (!text) return;
        const quill = window.__quill_editors && window.__quill_editors['id_content'];
        const tiny = window.tinymce && window.tinymce.activeEditor;
        if (quill) {
            const cur = quill.root.innerHTML;
            quill.root.innerHTML = cur + '<p>' + text.replace(/\n/g, '<br>') + '</p>';
        } else if (tiny) {
            tiny.setContent(tiny.getContent() + '<p>' + text.replace(/\n/g, '<br>') + '</p>');
        } else {
            const el = document.getElementById('id_content');
            el.value = el.value + "\n\n" + text;
        }
        resultBox.value = '';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    createAIButton();
});
