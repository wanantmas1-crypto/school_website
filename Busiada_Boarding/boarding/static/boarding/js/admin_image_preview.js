// Lightweight admin file input preview
document.addEventListener('DOMContentLoaded', function () {
  // inject minimal styles if not present
  if (!document.getElementById('admin-image-preview-styles')) {
    const style = document.createElement('style');
    style.id = 'admin-image-preview-styles';
    style.textContent = '\n.admin-file-preview img{border-radius:6px;max-width:240px;max-height:160px;object-fit:cover;display:block;box-shadow:0 6px 18px rgba(10,20,30,0.12)}\n.admin-file-preview{margin-top:0.5rem}\n.admin-file-preview--container{display:flex;gap:0.75rem;align-items:flex-start}\n.admin-file-preview-label{font-size:0.78rem;color:#444}\n.admin-file-preview-img{max-width:240px;max-height:160px;object-fit:cover;border-radius:6px;box-shadow:0 6px 18px rgba(10,20,30,0.12)}\n.admin-file-preview-server .admin-file-preview-img{opacity:0.95}\n.admin-file-preview-selection .admin-file-preview-label{color:#1E3A5F;font-weight:600}\n';
    document.head.appendChild(style);
  }
  function ensurePreview(input) {
    if (!input || input.dataset.previewInitialized) return;
    input.dataset.previewInitialized = '1';

    // container for preview
    const previewId = input.id + '-preview';
    let preview = document.getElementById(previewId);
    if (!preview) {
      preview = document.createElement('div');
      preview.id = previewId;
      preview.className = 'admin-file-preview';
      preview.style.marginTop = '0.5rem';
      input.parentNode.insertBefore(preview, input.nextSibling);
    }

    // create a side-by-side area: left = current server image (if any), right = selected file preview
    let container = preview.querySelector('.admin-file-preview--container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'admin-file-preview--container';
      container.style.display = 'flex';
      container.style.gap = '0.75rem';
      preview.appendChild(container);
    }

    function clearPreview() {
      container.innerHTML = '';
    }

    function buildImageBlock(src, labelText) {
      const wrap = document.createElement('div');
      wrap.style.display = 'flex';
      wrap.style.flexDirection = 'column';
      wrap.style.alignItems = 'flex-start';
      wrap.style.gap = '0.35rem';

      const img = document.createElement('img');
      img.src = src;
      img.alt = labelText || '';
      img.className = 'admin-file-preview-img';

      const label = document.createElement('div');
      label.className = 'admin-file-preview-label';
      label.textContent = labelText || '';

      wrap.appendChild(img);
      wrap.appendChild(label);
      return wrap;
    }

    input.addEventListener('change', function (ev) {
      const f = input.files && input.files[0];
      if (!f) {
        // If no file selected, show only server-side preview (if present)
        // keep container as-is
        container.querySelectorAll('.admin-file-preview-selection').forEach(n => n.remove());
        return;
      }
      if (window.FileReader) {
        const reader = new FileReader();
        reader.onload = function (e) {
          // remove previous selection block
          container.querySelectorAll('.admin-file-preview-selection').forEach(n => n.remove());
          const sel = buildImageBlock(e.target.result, 'Selected file');
          sel.className = 'admin-file-preview-selection';
          container.appendChild(sel);
        };
        reader.readAsDataURL(f);
      }
    });

    // attempt to find an existing server-side image/link and render it in the preview
    (function attachServerPreview() {
      // typical admin markup: a <a> link to file, sometimes with an <img> inside
      const parent = input.parentNode;
      const existingImg = parent.querySelector('a img') || parent.querySelector('img');
      const existingLink = parent.querySelector('a');
      if (existingImg || existingLink) {
        let src = null;
        if (existingImg && existingImg.src) src = existingImg.src;
        else if (existingLink && existingLink.href) src = existingLink.href;
        if (src) {
          const serverBlock = buildImageBlock(src, 'Current');
          serverBlock.className = 'admin-file-preview-server';
          // insert server block first
          container.insertBefore(serverBlock, container.firstChild);
        }
      }
    }());

    // support clear checkbox (Django ClearableFileInput uses name ending with "-clear")
    const name = input.name;
    if (name) {
      const clearCheck = document.querySelector(`input[type=checkbox][name="${CSS.escape(name)}-clear"]`) || document.querySelector(`input[type=checkbox][name="${CSS.escape(name)}"]`);
      if (clearCheck) {
        clearCheck.addEventListener('change', function () { if (this.checked) clearPreview(); });
      }
    }
  }

  const inputs = document.querySelectorAll('input[type=file]');
  inputs.forEach(ensurePreview);

  // support dynamically-added inlines (mutation observer)
  const adminForms = document.querySelectorAll('.inline-group');
  if (adminForms.length) {
    const mo = new MutationObserver((mutations) => {
      mutations.forEach((m) => {
        m.addedNodes && m.addedNodes.forEach((n) => {
          if (n.querySelectorAll) {
            n.querySelectorAll('input[type=file]').forEach(ensurePreview);
          }
        });
      });
    });
    adminForms.forEach((f) => mo.observe(f, { childList: true, subtree: true }));
  }
});
