export function showSection(sectionId) {
    document.querySelectorAll('section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
    if (window.innerWidth < 768) {
        toggleSidebar(); // Fechar menu em mobile
    }
    if (sectionId === 'reports') {
        loadDates('dateSelect'); // Carregar datas para relatórios
        document.getElementById('reportContent').classList.add('hidden');
    } else if (sectionId === 'charts') {
        loadDates('chartDateSelect'); // Carregar datas para gráficos
        document.getElementById('chartContent').classList.add('hidden');
    }
}

export function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}