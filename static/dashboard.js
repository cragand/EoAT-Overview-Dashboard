/* Dashboard: search, filter, sort */
document.addEventListener('DOMContentLoaded', function() {
    var search = document.getElementById('search');
    var statusFilter = document.getElementById('status-filter');
    var typeFilter = document.getElementById('type-filter');
    var assignmentFilter = document.getElementById('assignment-filter');
    var table = document.getElementById('device-table');
    if (!table) return;
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));

    function applyFilters() {
        var q = (search ? search.value : '').toLowerCase();
        var status = statusFilter ? statusFilter.value : '';
        var type = typeFilter ? typeFilter.value : '';
        var assignment = assignmentFilter ? assignmentFilter.value : '';
        rows.forEach(function(row) {
            var text = row.textContent.toLowerCase();
            var show = (!q || text.includes(q))
                && (!status || row.getAttribute('data-status') === status)
                && (!type || row.getAttribute('data-type') === type)
                && (!assignment || row.getAttribute('data-assignment') === assignment);
            row.style.display = show ? '' : 'none';
        });
    }

    [search, statusFilter, typeFilter, assignmentFilter].forEach(function(el) {
        if (el) el.addEventListener(el.tagName === 'INPUT' ? 'input' : 'change', applyFilters);
    });

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
                return sortAsc ? va.localeCompare(vb, undefined, {numeric: true})
                               : vb.localeCompare(va, undefined, {numeric: true});
            });
            rows.forEach(function(row) { tbody.appendChild(row); });
        });
    });
});
