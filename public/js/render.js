// Usar o Chart.js já carregado globalmente
const Chart = window.Chart;

// Verificar se o plugin datalabels está disponível
const ChartDataLabels = window['chartjs-plugin-datalabels'];
if (!ChartDataLabels) {
    console.error('Plugin chartjs-plugin-datalabels não encontrado. Certifique-se de que foi carregado.');
} else {
    Chart.register(ChartDataLabels);
}

// Atualizar gráfico de relatório (Marcas, TDV)
let reportChartInstance = null;
export function updateReportChart(chartData) {
    const ctx = document.getElementById('reportChart').getContext('2d');
    if (!chartData || !chartData.labels || !chartData.values) {
        console.error('Dados do gráfico inválidos:', chartData);
        alert('Erro: Dados do gráfico inválidos');
        return;
    }
    if (reportChartInstance) {
        reportChartInstance.destroy();
    }
    const label = document.getElementById('reportType').value === 'marcas' ? 'Quantidade por Marca' : 'Quantidade por TDV';
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
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// Atualizar gráfico de Status Patrimônio (Pizza)
let chartInstance = null;
export function updateStatusChart(chartData) {
    const ctx = document.getElementById('chartCanvas').getContext('2d');
    if (!chartData || !chartData.labels || !chartData.values) {
        console.error('Dados do gráfico inválidos:', chartData);
        alert('Erro: Dados do gráfico inválidos');
        return;
    }
    if (chartInstance) {
        chartInstance.destroy();
    }
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
                    'rgba(34, 197, 94, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)'
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Atualizar gráfico de Disponibilidade
export function updateDisponibilidadeChart(chartData) {
    const ctx = document.getElementById('chartCanvas').getContext('2d');
    if (!chartData || !chartData.labels || !chartData.datasets) {
        console.error('Dados do gráfico inválidos:', chartData);
        alert('Erro: Dados do gráfico inválidos');
        return;
    }
    if (chartInstance) {
        chartInstance.destroy();
    }

    const totalDisponivel = chartData.datasets[0].data.reduce((sum, val) => sum + val, 0);
    const totalIndisponivel = chartData.datasets[1].data.reduce((sum, val) => sum + val, 0);
    const totals = chartData.datasets[0].data.map((val, index) => val + (chartData.datasets[1].data[index] || 0));

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: `Disponível (${totalDisponivel})`,
                    data: chartData.datasets[0].data,
                    backgroundColor: 'rgba(68, 114, 196, 1)',
                    borderColor: 'rgba(68, 114, 196, 1)',
                    borderWidth: 1
                },
                {
                    label: `Indisponível (${totalIndisponivel})`,
                    data: chartData.datasets[1].data,
                    backgroundColor: 'rgba(237, 125, 49, 1)',
                    borderColor: 'rgba(237, 125, 49, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                x: { stacked: true },
                y: { beginAtZero: true, stacked: true }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'DISPONIBILIDADE DA FROTA'
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12,
                            color: 'black' // Quantidade em preto nos labels
                        }
                    }
                },
                datalabels: {
                    anchor: function(context) {
                        const datasetIndex = context.datasetIndex;
                        return datasetIndex === 0 ? 'center' : 'center'; // Centralizar dentro das barras
                    },
                    align: function(context) {
                        const datasetIndex = context.datasetIndex;
                        return datasetIndex === 0 ? 'center' : 'center'; // Centralizar dentro das barras
                    },
                    formatter: function(value, context) {
                        const datasetIndex = context.datasetIndex;
                        if (datasetIndex === 0 || datasetIndex === 1) {
                            return value; // Mostrar o valor individual dentro da barra
                        }
                        const total = totals[context.dataIndex];
                        return total > 0 ? total.toString() : ''; // Total geral acima (opcional, ajustar posição)
                    },
                    color: 'black',
                    font: {
                        weight: 'bold'
                    },
                    clamp: true // Garante que os labels fiquem dentro das barras
                }
            }
        }
    });
}