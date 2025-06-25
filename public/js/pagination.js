// Estado interno da paginação
let currentPage = 1;
let rowsPerPage = 10;
let reportData = [];
let sortColumn = null;
let sortDirection = 'asc';

// Função para atualizar reportData
export function setReportData(data) {
    reportData = data; // Atualiza o estado interno
    updatePaginatedTable(); // Atualiza a tabela automaticamente
}

export function updatePaginatedTableWithIdeal(reportDataInput, idealQuantities) {
    reportData = reportDataInput.map(item => {
        const ideal = idealQuantities.find(i => i.Unidade === item.Unidade && i.Tdv === item.Tdv);
        return {
            ...item,
            QuantidadeIdeal: ideal ? ideal.QuantidadeIdeal : 0
        };
    });
    updatePaginatedTable(); // Atualiza a tabela
}

// Função principal para atualizar a tabela paginada
export function updatePaginatedTable() {
    const thead = document.getElementById('reportTableHead');
    const tbody = document.getElementById('reportTableBody');
    thead.innerHTML = `
        <tr class="bg-gray-200">
            <th class="p-1 text-left cursor-pointer" onclick="sortTable('Tdv')">TDV</th>
            <th class="p-1 text-left cursor-pointer" onclick="sortTable('Unidade')">Unidade</th>
            <th class="p-1 text-left cursor-pointer" onclick="sortTable('Quantidade')">Quantidade</th>
            <th class="p-1 text-left cursor-pointer" onclick="sortTable('QuantidadeIdeal')">Ideal</th>
        </tr>
    `;
    tbody.innerHTML = '';

    if (!reportData || reportData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="p-1">Nenhum dado disponível</td></tr>';
        document.getElementById('pagination').classList.add('hidden');
        return;
    }

    let sortedData = [...reportData];
    if (sortColumn) {
        sortedData.sort((a, b) => {
            let valA = a[sortColumn];
            let valB = b[sortColumn];
            if (sortColumn === 'Quantidade' || sortColumn === 'QuantidadeIdeal') {
                valA = Number(valA);
                valB = Number(valB);
            }
            if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = sortedData.slice(start, end);

    paginatedData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-1">${item.Tdv || ''}</td>
            <td class="p-1">${item.Unidade || ''}</td>
            <td class="p-1">${item.Quantidade || 0}</td>
            <td class="p-1">${item.QuantidadeIdeal || 0}</td>
        `;
        tbody.appendChild(row);
    });

    const totalPages = Math.ceil(reportData.length / rowsPerPage);
    document.getElementById('pageInfo').textContent = `Página ${currentPage} de ${totalPages}`;
    document.getElementById('pagination').classList.remove('hidden');
    document.querySelector('button[onclick="prevPage()"]').disabled = currentPage === 1;
    document.querySelector('button[onclick="nextPage()"]').disabled = currentPage === totalPages;
}

// Funções de paginação
export function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        updatePaginatedTable();
    }
}

export function nextPage() {
    const totalPages = Math.ceil(reportData.length / rowsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        updatePaginatedTable();
    }
}

// Ordenar tabela
export function sortTable(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }
    updatePaginatedTable();
}

// Atualizar tabela de relatório
export function updateReportTable(type, report) {
    const thead = document.getElementById('reportTableHead');
    const tbody = document.getElementById('reportTableBody');
    thead.innerHTML = '';
    tbody.innerHTML = '';
    document.getElementById('pagination').classList.add('hidden');

    if (type === 'marcas' || type === 'tdv') {
        thead.innerHTML = `
            <tr class="bg-gray-200">
                <th class="p-2 text-left">${type === 'marcas' ? 'Marca' : 'TDV'}</th>
                <th class="p-2 text-left">Quantidade</th>
            </tr>
        `;
        if (!report || Object.keys(report).length === 0) {
            tbody.innerHTML = '<tr><td colspan="2" class="p-2">Nenhum dado disponível</td></tr>';
            return;
        }
        for (const [key, quantidade] of Object.entries(report)) {
            const row = document.createElement('tr');
            row.innerHTML = `<td class="p-2">${key}</td><td class="p-2">${quantidade}</td>`;
            tbody.appendChild(row);
        }
    } else if (type === 'tdv_unidade') {
        updatePaginatedTable();
    }
}