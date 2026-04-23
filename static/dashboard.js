/* Dashboard table: search, filter, sort */
document.addEventListener('DOMContentLoaded', function() {
    const search = document.getElementById('search');
    const filter = document.getElementById('status-filter');
    const table = document.getElementById('device-table');
    if (!table) return;
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    function applyFilters() {
        const q = (search ? search.value : '').toLowerCase();
        const status = filter ? filter.value : '';
        rows.forEach(function(row) {
            const text = row.textContent.toLowerCase();
            const rowStatus = row.getAttribute('data-status');
            const matchSearch = !q || text.includes(q);
            const matchStatus = !status || rowStatus === status;
            row.style.display = (matchSearch && matchStatus) ? '' : 'none';
        });
    }

    if (search) search.addEventListener('input', applyFilters);
    if (filter) filter.addEventListener('change', applyFilters);

    // Column sorting
    var sortCol = null, sortAsc = true;
    table.querySelectorAll('th[data-sort]').forEach(function(th) {
        th.addEventListener('click', function() {
            var key = th.getAttribute('data-sort');
            if (sortCol === key) { sortAsc = !sortAsc; } else { sortCol = key; sortAsc = true; }
            var idx = Array.from(th.parentNode.children).indexOf(th);
            rows.sort(function(a, b) {
                var va = a.children[idx].textContent.trim();
                var vb = b.children[idx].textContent.trim();
                if (va === '—') va = '';
                if (vb === '—') vb = '';
                var cmp = va.localeCompare(vb, undefined, {numeric: true});
                return sortAsc ? cmp : -cmp;
            });
            rows.forEach(function(row) { tbody.appendChild(row); });
        });
    });
});
