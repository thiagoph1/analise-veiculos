// Importar módulos com depuração
import { showSection, toggleSidebar } from './ui.js';
import { loadDates, loadTdvs, loadReport, loadChart } from './dataLoader.js';
import { updateReportTable, updatePaginatedTable, prevPage, nextPage, sortTable } from './pagination.js';
import { updateReportChart, updateStatusChart, updateDisponibilidadeChart } from './render.js';

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