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

    // AI features disabled for privacy — provide manual helpers only
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'content-assist-btn';
    btn.className = 'button';
    btn.style.margin = '8px 0 12px 0';
    btn.textContent = 'Assist: Insert Template Summary';

    contentEl.parentNode.insertBefore(btn, contentEl.nextSibling);

    const resultBox = document.createElement('textarea');
    resultBox.id = 'assist-result-box';
    resultBox.style.width = '100%';
    resultBox.style.minHeight = '140px';
    resultBox.style.marginTop = '8px';
    resultBox.placeholder = 'Use this box for notes or manual summaries...';
    contentEl.parentNode.insertBefore(resultBox, btn.nextSibling);

    const applyBtn = document.createElement('button');
    applyBtn.type = 'button';
    applyBtn.textContent = 'Apply Summary to Content (append)';
    applyBtn.style.marginTop = '8px';
    applyBtn.style.display = 'block';
    resultBox.parentNode.insertBefore(applyBtn, resultBox.nextSibling);

    btn.addEventListener('click', () => {
        // Insert a simple template to help editors write summaries
        const template = 'Summary:\n- (Add a 1–2 sentence summary here)\n\nSEO Title:\n- (Short title, max 60 chars)\n\nMeta Description:\n- (Describe the page in 1–2 sentences)';
        resultBox.value = template;
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
