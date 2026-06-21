document.addEventListener('DOMContentLoaded', function() {
    // Find order inputs in any inline forms
    const orderInputs = Array.from(document.querySelectorAll('input[name$="-order"]'));
    if (!orderInputs.length) return;

    // Group by formset table row
    orderInputs.forEach((input) => {
        const row = input.closest('tr') || input.closest('.inline-related') || input.closest('fieldset');
        if (!row) return;

        // Avoid duplicate controls
        if (row.querySelector('.order-controls')) return;

        const controls = document.createElement('div');
        controls.className = 'order-controls inline-flex flex-col gap-1';
        controls.style.marginLeft = '6px';

        const up = document.createElement('button');
        up.type = 'button';
        up.title = 'Move up';
        up.innerHTML = '↑';
        up.className = 'btn-order-up';
        up.style.cursor = 'pointer';
        up.style.padding = '2px 6px';

        const down = document.createElement('button');
        down.type = 'button';
        down.title = 'Move down';
        down.innerHTML = '↓';
        down.className = 'btn-order-down';
        down.style.cursor = 'pointer';
        down.style.padding = '2px 6px';

        controls.appendChild(up);
        controls.appendChild(down);

        // Insert controls into the first cell of the row
        const firstCell = row.querySelector('th, td');
        if (firstCell) {
            firstCell.style.display = 'flex';
            firstCell.style.alignItems = 'center';
            firstCell.appendChild(controls);
        }

        function swapWith(otherRow) {
            if (!otherRow) return;
            const otherInput = otherRow.querySelector('input[name$="-order"]');
            if (!otherInput) return;
            // swap values
            const tmp = input.value;
            input.value = otherInput.value;
            otherInput.value = tmp;
            // swap DOM positions for visual feedback
            const parent = row.parentNode;
            if (parent && otherRow.parentNode === parent) {
                parent.insertBefore(row, otherRow);
            }
        }

        up.addEventListener('click', function() {
            // find previous sibling row that contains an order input
            let prev = row.previousElementSibling;
            while (prev) {
                if (prev.querySelector && prev.querySelector('input[name$="-order"]')) break;
                prev = prev.previousElementSibling;
            }
            if (prev) swapWith(prev);
        });

        down.addEventListener('click', function() {
            let next = row.nextElementSibling;
            while (next) {
                if (next.querySelector && next.querySelector('input[name$="-order"]')) break;
                next = next.nextElementSibling;
            }
            if (next) swapWith(next);
        });
    });

    // Add a normalize button to each inline area to resequence orders
    const inlineAreas = Array.from(document.querySelectorAll('.inline-group, .tabular, .inline-related, .dynamic-related'));
    inlineAreas.forEach(area => {
        if (area.querySelector('.normalize-order-btn')) return;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'normalize-order-btn button';
        btn.textContent = 'Normalize Order';
        btn.style.margin = '8px 0 12px 0';
        area.insertBefore(btn, area.firstChild);
        btn.addEventListener('click', () => {
            const inputs = Array.from(area.querySelectorAll('input[name$="-order"]'));
            inputs.sort((a,b) => a.closest('tr')?.rowIndex - b.closest('tr')?.rowIndex);
            inputs.forEach((inp, idx) => { inp.value = idx + 1; });
            btn.textContent = 'Order normalized';
            setTimeout(() => btn.textContent = 'Normalize Order', 1200);
        });
    });
});
