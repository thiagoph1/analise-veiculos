// Estado da paginação
let currentPage = 1;
let rowsPerPage = 10;
let reportData = [];
let sortColumn = null;
let sortDirection = 'asc';

// Mostrar/Esconder seções
function showSection(sectionId) {
    const sections = document.querySelectorAll('section');
    if (!sections) return;
    sections.forEach(section => section.classList.add('hidden'));
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.remove('hidden');
        if (window.innerWidth < 768) toggleSidebar(); // Fechar menu em mobile
        if (sectionId === 'reports') {
            loadDates('dateSelect'); // Carregar datas para relatórios
            const reportContent = document.getElementById('reportContent');
            if (reportContent) reportContent.classList.add('hidden');
        } else if (sectionId === 'charts') {
            loadDates('chartDateSelect'); // Carregar datas para gráficos
            const chartContent = document.getElementById('chartContent');
            if (chartContent) chartContent.classList.add('hidden');
        }
    }
}

// Alternar menu lateral em mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('open');
}

// Carregar datas disponíveis
function loadDates(selectId) {
    const dateSelect = document.getElementById(selectId);
    if (!dateSelect) {
        console.error(`Elemento ${selectId} não encontrado`);
        return;
    }
    fetch('/dates')
        .then(response => {
            if (!response.ok) throw new Error(`Erro na resposta do servidor: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Erro ao carregar datas:', data.error);
                alert('Erro ao carregar datas: ' + data.error);
                return;
            }
            dateSelect.innerHTML = '<option value="">Selecione uma data</option>';
            if (data.dates && Array.isArray(data.dates)) {
                data.dates.forEach(date => {
                    const option = document.createElement('option');
                    option.value = date;
                    option.textContent = date;
                    dateSelect.appendChild(option);
                });
            } else {
                console.error('Formato de dados inválido:', data);
                alert('Erro: Formato de dados inválido');
            }
        })
        .catch(error => {
            console.error('Erro ao carregar datas:', error);
            alert('Erro ao carregar datas');
        });
}




// Carregar TDVs disponíveis para o filtro
function loadTdvs(date) {
    const tdvFilter = document.getElementById('tdvFilter');
    if (!tdvFilter) {
        console.error('Elemento tdvFilter não encontrado');
        return;
    }
    tdvFilter.innerHTML = '<option value="all">Todos os TDVs</option>';
    if (!date) return;
    
    fetch(`/tdvs/${date}`)
        .then(response => {
            if (!response.ok) throw new Error(`Erro na resposta do servidor: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Erro ao carregar TDVs:', data.error);
                return;
            }
            data.tdvs.forEach(tdv => {
                const option = document.createElement('option');
                option.value = t
dv;
                option.textContent = t
dv;
                tdvFilter.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar TDVs:', error);
        });
}




// Carregar relatório
function loadReport() {
    const type = document.getElementById('reportType')?.value;
    const date = document.getElementById('dateSelect')?.value;
    const tdvFilter = document.getElementById('tdvFilter');
    const tdv = tdvFilter?.value;

    if (!type || !date) {
        alert('Selecione um tipo de relatório e uma data');
        return;
    }

    // Mostrar/esconder filtro de TDV
    if (tdvFilter) tdvFilter.classList.toggle('hidden', type !== 'tdv_unidade');
    if (type === 'tdv_unidade' && date) {
        loadTdvs(date);
    } else if (tdvFilter) {
        tdvFilter.innerHTML = '<option value="all">Todos os TDVs</option>';
    }

    let url;
    let title;
    if (type === 'marcas') {
        url = `/report/${date}`;
        title = 'Relatório de Marcas';
    } else if (type === 'tdv') {
        url = `/report/${date}/tdv`;
        title = 'Relatório de TDV';
    } else if (type === 'tdv_unidade') {
        url = tdv === 'all' ? `/report/${date}/tdv_unidade` : `/report/${date}/tdv_unidade/${tdv}`;
        title = `Relatório de TDV/Unidade${tdv !== 'all' ? ` - ${tdv}` : ''}`;
    } else {
        alert('Tipo de relatório inválido');
        return;
    }

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Erro na resposta do servidor: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Erro ao carregar relatório:', data.error);
                alert('Erro ao carregar relatório: ' + data.error);
                return;
            }
            if (type === 'tdv_unidade') {
                reportData = data.report || [];
                currentPage = 1;
                sortColumn = null;
                sortDirection = 'asc';
                updatePaginatedTable();
            } else {
                updateReportTable(type, data.report || {});
            }
            if (type !== 'tdv_unidade' && data.chart) {
                updateReportChart(data.chart);
                const chartTitle = document.getElementById('chartTitle');
                const reportChart = document.getElementById('reportChart');
                if (chartTitle) chartTitle.classList.remove('hidden');
                if (reportChart) reportChart.classList.remove('hidden');
            } else {
                const chartTitle = document.getElementById('chartTitle');
                const reportChart = document.getElementById('reportChart');
                if (chartTitle) chartTitle.classList.add('hidden');
                if (reportChart) reportChart.classList.add('hidden');
            }
            const reportTitle = document.getElementById('reportTitle');
            if (reportTitle) reportTitle.textContent = title;
            const reportContent = document.getElementById('reportContent');
            if (reportContent) reportContent.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Erro ao carregar relatório:', error);
            alert('Erro ao carregar relatório');
        });
}



// Carregar gráfico (restante do código segue o mesmo padrão de robustez)
function loadChart() {
    const type = document.getElementById('chartType')?.value;
    const date = document.getElementById('chartDateSelect')?.value;
    const unitFilter = document.getElementById('unitFilter')?.value;
    if (!type || !date) {
        alert('Selecione um tipo de gráfico e uma data');
        return;
    }

    let url;
    let title;
    if (type === 'status_patrimonio') {
        url = unitFilter === 'all' ? `/chart/${date}/status_patrimonio` : `/chart/${date}/status_patrimonio/${unitFilter}`;
        title = `Gráfico de Status Patrimônio${unitFilter !== 'all' ? ` - ${unitFilter === 'elos' ? 'Elos do SISTRAN' : 'Extras'}` : ''}`;
    } else if (type === 'disponibilidade') {
        url = unitFilter === 'all' ? `/chart/${date}/disponibilidade` : `/chart/${date}/disponibilidade/${unitFilter}`;
        title = `DISPONIBILIDADE DA FROTA${unitFilter !== 'all' ? ` - ${unitFilter === 'elos' ? 'Elos do SISTRAN' : 'Extras'}` : ''}`;
    } else {
        alert('Tipo de gráfico inválido');
        return;
    }
    // Ajuste para o contexto do deploy, se necessário
    url = '/app' + url; // Remova ou ajuste com base no contexto real
    console.log('URL gerada:', url);
    console.log('Tipo:', type, 'Data:', date, 'Filtro:', unitFilter);

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Erro na resposta do servidor: ${response.status} - ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Erro ao carregar gráfico:', data.error);
                alert('Erro ao carregar gráfico: ' + data.error);
                return;
            }
            if (type === 'status_patrimonio') {
                updateStatusChart(data.chart);
            } else if (type === 'disponibilidade') {
                updateDisponibilidadeChart(data.chart);
            }
            const chartTitle = document.getElementById('chartTitle');
            if (chartTitle) chartTitle.textContent = title;
            const chartContent = document.getElementById('chartContent');
            if (chartContent) chartContent.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Erro ao carregar gráfico:', error);
            alert('Erro ao carregar gráfico');
        });
}


// Atualizar tabela de relatório (mantido como original, mas com verificações)
function updateReportTable(type, report) {
    const thead = document.getElementById('reportTableHead');
    const tbody = document.getElementById('reportTableBody');
    if (!thead || !tbody) return;
    thead.innerHTML = '';
    tbody.innerHTML = '';
    document.getElementById('pagination')?.classList.add('hidden');

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



// Atualizar tabela paginada para TDV/Unidade (mantido como original, mas com verificações)
function updatePaginatedTable() {
    const thead = document.getElementById('reportTableHead');
    const tbody = document.getElementById('reportTableBody');
    if (!thead || !tbody) return;
    thead.innerHTML = `
        <tr class="bg-gray-200">
            <th class="p-1 text-left cursor-pointer" onclick="sortTable('Tdv')">TDV</th>
            <th class="p-1 text-left cursor-pointer" onclick="sortTable('Unidade')">Unidade</th>
            <th class="p-1 text-left cursor-pointer" onclick="sortTable('Quantidade')">Quantidade</th>
        </tr>
    `;
    tbody.innerHTML = '';

    if (!reportData || reportData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="p-1">Nenhum dado disponível</td></tr>';
        document.getElementById('pagination')?.classList.add('hidden');
        return;
    }

    // Ordenar dados
    let sortedData = [...reportData];
    if (sortColumn) {
        sortedData.sort((a, b) => {
            let valA = a[sortColumn];
            let valB = b[sortColumn];
            if (sortColumn === 'Quantidade') {
                valA = Number(valA) || 0;
                valB = Number(valB) || 0;
            }
            return valA < valB ? (sortDirection === 'asc' ? -1 : 1) : valA > valB ? (sortDirection === 'asc' ? 1 : -1) : 0;
        });
    }

    // Calcular índices de paginação
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = sortedData.slice(start, end);

    // Preencher tabela
    paginatedData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-1">${item.Tdv || ''}</td>
            <td class="p-1">${item.Unidade || ''}</td>
            <td class="p-1">${item.Quantidade || 0}</td>
        `;
        tbody.appendChild(row);
    });

    // Atualizar paginação
    const totalPages = Math.ceil(reportData.length / rowsPerPage);
    const pageInfo = document.getElementById('pageInfo');
    if (pageInfo) pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
    const pagination = document.getElementById('pagination');
    if (pagination) pagination.classList.remove('hidden');
    const prevButton = document.querySelector('button[onclick="prevPage()"]');
    const nextButton = document.querySelector('button[onclick="nextPage()"]');
    if (prevButton) prevButton.disabled = currentPage === 1;
    if (nextButton) nextButton.disabled = currentPage === totalPages;
}



// Funções de paginação (mantidas como original com verificações)
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        updatePaginatedTable();
    }
}

function nextPage() {
    const totalPages = Math.ceil(reportData.length / rowsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        updatePaginatedTable();
    }
}



// Ordenar tabela (mantida como original)
function sortTable(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }
    updatePaginatedTable();
}



// Atualizar gráfico de relatório (Marcas, TDV)
let reportChartInstance = null;
function updateReportChart(chartData) {
    const ctx = document.getElementById('reportChart')?.getContext('2d');
    if (!ctx || !chartData || !chartData.labels || !chartData.values) {
        console.error('Dados do gráfico inválidos:', chartData);
        alert('Erro: Dados do gráfico inválidos');
        return;
    }
    if (reportChartInstance) reportChartInstance.destroy();
    const label = document.getElementById('reportType')?.value === 'marcas' ? 'Quantidade por Marca' : 'Quantidade por TDV';
    reportChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: label,
                data: chartData.values,
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });
}



// Atualizar gráfico de Status Patrimônio (Pizza)
let chartInstance = null;
function updateStatusChart(chartData) {
    const ctx = document.getElementById('chartCanvas')?.getContext('2d');
    if (!ctx || !chartData || !chartData.labels || !chartData.values) {
        console.error('Dados do gráfico inválidos:', chartData);
        alert('Erro: Dados do gráfico inválidos');
        return;
    }
    if (chartInstance) chartInstance.destroy();
    const total = chartData.values.reduce((sum, val) => sum + val, 0);
    const percentages = chartData.values.map(val => ((val / total) * 100).toFixed(1));
    chartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.labels.map((label, index) => `${label} (${percentages[index]}%, ${chartData.values[index]})`),
            datasets: [{
                label: 'Quantidade por Status Patrimônio',
                data: chartData.values,
                backgroundColor: [
                    'rgba(34, 197, 94, 0.6)', 'rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)'
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)', 'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: { position: 'bottom', labels: { font: { size: 12 } } }
            }
        }
    });
}



// Atualizar gráfico de Disponibilidade
function updateDisponibilidadeChart(chartData) {
    const ctx = document.getElementById('chartCanvas')?.getContext('2d');
    if (!ctx || !chartData || !chartData.labels || !chartData.datasets) {
        console.error('Dados do gráfico inválidos:', chartData);
        alert('Erro: Dados do gráfico inválidos');
        return;
    }
    if (chartInstance) chartInstance.destroy();
    const totalDisponivel = chartData.datasets[0].data.reduce((sum, val) => sum + val, 0);
    const totalIndisponivel = chartData.datasets[1].data.reduce((sum, val) => sum + val, 0);
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                { label: `Disponível (${totalDisponivel})`, data: chartData.datasets[0].data, backgroundColor: 'rgba(68, 114, 196, 1)', borderColor: 'rgba(68, 114, 196, 1)', borderWidth: 1 },
                { label: `Indisponível (${totalIndisponivel})`, data: chartData.datasets[1].data, backgroundColor: 'rgba(237, 125, 49, 1)', borderColor: 'rgba(237, 125, 49, 1)', borderWidth: 1 }
            ]
        },
        options: {
            scales: { x: { stacked: true }, y: { beginAtZero: true, stacked: true } },
            plugins: {
                title: { display: true, text: 'DISPONIBILIDADE DA FROTA' },
                legend: { position: 'bottom', labels: { font: { size: 12 } } }
            }
        }
    });
}


// Mostrar tela inicial por padrão
document.addEventListener('DOMContentLoaded', () => {
    showSection('home');
});