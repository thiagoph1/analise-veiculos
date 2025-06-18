// Importar módulos
import { showSection, toggleSidebar } from './ui.js';
import { loadDates, loadTdvs, loadReport, loadChart } from './dataLoader.js';
import { updateReportTable, updatePaginatedTable, prevPage, nextPage, sortTable } from './pagination.js';
import { updateReportChart, updateStatusChart, updateDisponibilidadeChart } from './render.js';

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    showSection('home');
});