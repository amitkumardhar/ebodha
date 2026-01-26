export const downloadDataAsCSV = (data, columns, tableName, username) => {
    if (!data || !data.length) {
        alert("No data to download");
        return;
    }

    // Filter out actions column
    const exportCols = columns.filter(c => c.key !== 'actions');

    // Header row
    const headers = exportCols.map(c => `"${c.title}"`).join(',');

    // Data rows
    const rows = data.map(row => {
        return exportCols.map(col => {
            let val = row;
            // Handle nested keys (e.g. 'course.code')
            const keys = col.key.split('.');
            for (const k of keys) {
                val = val?.[k];
            }

            // Handle arrays (e.g. roles) or objects
            if (Array.isArray(val)) {
                // simple join for arrays of primitives or specific handling
                // For roles: [{role: 'student'}] -> 'student'
                if (val.length && typeof val[0] === 'object') {
                    // Try to find a common display field or just stringify
                    // Specific hack for roles/exams if needed, or generic JSON
                    val = val.map(v => v.name || v.role || v.exam_name || JSON.stringify(v)).join('; ');
                } else {
                    val = val.join('; ');
                }
            } else if (typeof val === 'object' && val !== null) {
                val = JSON.stringify(val);
            }

            // Escape quotes
            const str = String(val === null || val === undefined ? '' : val);
            return `"${str.replace(/"/g, '""')}"`;
        }).join(',');
    });

    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    // Filename: [TableName]_[Username].csv
    // Sanitize
    const cleanTableName = tableName.replace(/[^a-zA-Z0-9-_]/g, '_');
    const cleanUsername = username.replace(/[^a-zA-Z0-9-_]/g, '_');

    link.setAttribute('href', url);
    link.setAttribute('download', `${cleanTableName}_${cleanUsername}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
