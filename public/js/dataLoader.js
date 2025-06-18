export function loadDates(selectId) {
    fetch('/dates')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Erro ao carregar datas:', data.error);
                alert('Erro ao carregar datas: ' + data.error);
                return;
            }
            const dateSelect = document.getElementById(selectId);
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

export function loadTdvs(date) {
    const tdvFilter = document.getElementById('tdvFilter');
    tdvFilter.innerHTML = '<option value="all">Todos os TDVs</option>';
    if (!date) return;
    
    fetch(`/tdvs/${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Erro ao carregar TDVs:', data.error);
                return;
            }
            data.tdvs.forEach(tdv => {
                const option = document.createElement('option');
                option.value = tdv;
                option.textContent = t
                dv;
                tdvFilter.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar TDVs:', error);
        });
}

export function loadIdealQuantities(fileInput) {
    return new Promise((resolve, reject) => {
        const file = fileInput.files[0];
        if (!file) {
            reject(new Error('Nenhum arquivo XLSX selecionado'));
            return;
        }
        const reader = new FileReader();
        reader.onload = function(e) {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            const sheet = workbook.Sheets[workbook.SheetNames[0]];
            const rawData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
            const headers = rawData[0]; // ["OM", "P-0", "P-1", ...]
            const tdvTypes = headers.slice(1); // ["P-0", "P-1", ..., "E-28"]
            const idealData = [];

            for (let i = 1; i < rawData.length; i++) {
                const row = rawData[i];
                const unidade = row[0];
                for (let j = 1; j < row.length; j++) {
                    const quantidade = parseInt(row[j]) || 0;
                    if (quantidade > 0) {
                        idealData.push({
                            Unidade: unidade,
                            Tdv: tdvTypes[j - 1],
                            QuantidadeIdeal: quantidade
                        });
                    }
                }
            }
            resolve(idealData);
        };
        reader.onerror = () => reject(new Error('Erro ao ler o arquivo XLSX'));
        reader.readAsArrayBuffer(file);
    });
}

export async function saveIdealToMongoDB(idealData) {
    try {
        const response = await fetch('/api/ideal-quantities', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(idealData)
        });
        if (!response.ok) throw new Error('Erro ao salvar no MongoDB');
        console.log('Quantidades ideais salvas com sucesso');
    } catch (error) {
        console.error('Erro ao salvar no MongoDB:', error);
        alert('Erro ao salvar quantidades ideais');
    }
}

export function loadReport() {
    const type = document.getElementById('reportType').value;
    const date = document.getElementById('dateSelect').value;
    const tdvFilter = document.getElementById('tdvFilter');
    const tdv = tdvFilter.value;
    const fileInput = document.getElementById('idealFileInput');
    
    tdvFilter.classList.toggle('hidden', type !== 'tdv_unidade');
    if (type === 'tdv_unidade') {
        loadTdvs(date);
    } else {
        tdvFilter.innerHTML = '<option value="all">Todos os TDVs</option>';
    }

    if (!date) {
        alert('Selecione uma data');
        return;
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
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Erro ao carregar relatório:', data.error);
                alert('Erro ao carregar relatório: ' + data.error);
                return;
            }
            if (type === 'tdv_unidade' && fileInput) {
                loadIdealQuantities(fileInput).then(idealData => {
                    saveIdealToMongoDB(idealData); // Salva no MongoDB
                    import('./pagination.js').then(module => {
                        module.setReportData(data.report);
                        module.idealQuantities = idealData; // Armazena os dados ideais
                        module.updatePaginatedTable();
                    }).catch(err => {
                        console.error('Erro ao importar pagination.js:', err);
                    });
                }).catch(err => {
                    console.error('Erro ao carregar quantidades ideais:', err);
                    alert('Erro ao carregar quantidades ideais: ' + err.message);
                });
            } else {
                updateReportTable(type, data.report);
            }
            if (type !== 'tdv_unidade') {
                updateReportChart(data.chart);
                document.getElementById('chartTitle').classList.remove('hidden');
                document.getElementById('reportChart').classList.remove('hidden');
            } else {
                document.getElementById('chartTitle').classList.add('hidden');
                document.getElementById('reportChart').classList.add('hidden');
            }
            document.getElementById('reportTitle').textContent = title;
            document.getElementById('reportContent').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Erro ao carregar relatório:', error);
            alert('Erro ao carregar relatório');
        });
}

export function loadChart() {
    const type = document.getElementById('chartType').value;
    const date = document.getElementById('chartDateSelect').value;
    const unitFilter = document.getElementById('unitFilter').value;
    if (!date) {
        alert('Selecione uma data');
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

    fetch(url)
        .then(response => response.json())
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
            document.getElementById('chartTitle').textContent = title;
            document.getElementById('chartContent').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Erro ao carregar gráfico:', error);
            alert('Erro ao carregar gráfico');
        });
}