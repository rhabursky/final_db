const programsContainer = document.getElementById('programs');
const detailPanel = document.getElementById('program-detail');
const emptyState = document.getElementById('detail-empty');
const titleElement = document.getElementById('program-title');
const degreeElement = document.getElementById('degree-type');
const minorElement = document.getElementById('minor');
const salaryBox = document.getElementById('salary-box');
const salaryValue = document.getElementById('salary-value');
const sourceDegree = document.getElementById('source-degree');
const showMoneyButton = document.getElementById('show-money');
const clearButton = document.getElementById('clear-selection');

let selectedProgramId = null;
let selectedSalary = null;

async function fetchPrograms() {
    const response = await fetch('/api/programs');
    const programs = await response.json();

    programsContainer.innerHTML = programs
        .map(
            (program) =>
                `<button class="program-item" data-id="${program.id}">${program.title}</button>`,
        )
        .join('');

    document.querySelectorAll('.program-item').forEach((button) => {
        button.addEventListener('click', () => {
            const programId = button.dataset.id;
            loadProgram(programId);
        });
    });
}

async function loadProgram(programId) {
    const response = await fetch(`/api/programs/${programId}`);
    if (!response.ok) {
        alert('Could not load program details.');
        return;
    }

    const program = await response.json();

    selectedProgramId = program.id;
    selectedSalary = program.average_salary;

    titleElement.textContent = program.title;
    degreeElement.textContent = program.degree_type || 'N/A';
    minorElement.textContent = program.minor || 'N/A';
    salaryValue.textContent = program.average_salary || 'N/A';
    sourceDegree.textContent = program.source_degree || 'No source available';

    salaryBox.classList.add('hidden');
    showMoneyButton.classList.remove('hidden');
    detailPanel.classList.remove('hidden');
    emptyState.classList.add('hidden');
}

showMoneyButton.addEventListener('click', () => {
    salaryBox.classList.remove('hidden');
    showMoneyButton.classList.add('hidden');
});

clearButton.addEventListener('click', () => {
    selectedProgramId = null;
    selectedSalary = null;
    detailPanel.classList.add('hidden');
    emptyState.classList.remove('hidden');
    showMoneyButton.classList.remove('hidden');
});

window.addEventListener('DOMContentLoaded', fetchPrograms);
