// Importar módulos com depuração
console.log('Carregando scripts.js');
import { showSection, toggleSidebar } from './ui.js';
console.log('ui.js carregado com sucesso');
import { loadDates, loadTdvs, loadReport, loadChart } from './dataLoader.js';
console.log('dataLoader.js carregado com sucesso');
import { updateReportTable, updatePaginatedTable, prevPage, nextPage, sortTable } from './pagination.js';
console.log('pagination.js carregado com sucesso');
import { updateReportChart, updateStatusChart, updateDisponibilidadeChart } from './render.js';
console.log('render.js carregado com sucesso');

// Expor funções no escopo global
window.showSection = showSection;
window.toggleSidebar = toggleSidebar;
window.loadDates = loadDates;
window.loadTdvs = loadTdvs;
window.loadReport = loadReport;
window.loadChart = loadChart;
window.updateReportTable = updateReportTable;
window.updatePaginatedTable = updatePaginatedTable;
window.prevPage = prevPage;
window.nextPage = nextPage;
window.sortTable = sortTable;
window.updateReportChart = updateReportChart;
window.updateStatusChart = updateStatusChart;
window.updateDisponibilidadeChart = updateDisponibilidadeChart;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded disparado');
    showSection('home');
});