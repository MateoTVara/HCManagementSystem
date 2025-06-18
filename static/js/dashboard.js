// Utilidades
function getCookie(name) {
    let cookie = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookie ? cookie.pop() : '';
}

// Sidebar responsive
function handleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    if (window.innerWidth >= 992) {
        sidebar.classList.remove('sidebar-collapsed');
    }
}
window.addEventListener('resize', handleSidebar);

// Búsqueda de alergias en tiempo real
function handleAllergySearch() {
    document.addEventListener('input', function(e) {
        if (e.target && e.target.id === 'allergySearch') {
            const searchTerm = e.target.value.toLowerCase().trim();
            const container = document.getElementById('allergyList');
            if (!container) return;
            const items = container.getElementsByClassName('allergy-item');
            let visibleCount = 0;
            Array.from(items).forEach(item => {
                const label = item.querySelector('.form-check-label').textContent.toLowerCase();
                const matches = label.includes(searchTerm);
                item.style.display = matches ? 'block' : 'none';
                visibleCount += matches ? 1 : 0;
            });
            const noResults = document.getElementById('noResults');
            if (noResults) {
                noResults.classList.toggle('d-none', visibleCount > 0);
            }
        }
    });
}

// Recarga lista de alergias por AJAX
function refreshAllergyList(patientId = null) {
    let url = '/allergy/partial_list/';
    if (!patientId) {
        // Intenta obtener el patientId del DOM si no se pasa explícitamente
        const allergyListDiv = document.getElementById('allergyList');
        if (allergyListDiv && allergyListDiv.dataset.patientId) {
            patientId = allergyListDiv.dataset.patientId;
        }
    }
    if (patientId) {
        url = `/allergy/partial_list/${patientId}/`;
    }
    fetch(url, {
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(r => r.text())
    .then(html => {
        document.getElementById('allergyList').innerHTML = html;
        handleAllergySearch();
    })
    .catch(() => console.error('No se pudo recargar lista de alergias'));
}

// Modal genérico AJAX
function showModal(contentHtml, modalId = 'ajaxModal') {
    let existingModal = document.getElementById(modalId);
    if (existingModal) existingModal.remove();
    const modalDiv = document.createElement('div');
    modalDiv.id = modalId;
    modalDiv.className = 'modal fade';
    modalDiv.tabIndex = -1;
    modalDiv.innerHTML = `
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
        <div class="modal-header">
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
            ${contentHtml}
        </div>
        </div>
    </div>
    `;
    document.body.appendChild(modalDiv);
    let modal = new bootstrap.Modal(modalDiv);
    modal.show();
    return modalDiv;
}

// Handlers para formularios en modales (edición de cita, paciente, doctor)
function attachEditFormHandler(modalDiv, url, refreshUrl, callback) {
    const form = modalDiv?.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    bootstrap.Modal.getOrCreateInstance(modalDiv).hide();
                    document.body.classList.remove('modal-open');
                    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                    fetch(refreshUrl, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
                    .then(r => r.text())
                    .then(html => {
                        document.getElementById('mainContent').innerHTML = html;
                        if (callback) callback();
                    });
                } else {
                    const errHtml = Object.values(data.errors).flat().join('<br>');
                    modalDiv.querySelector('.modal-body').insertAdjacentHTML('afterbegin',
                        `<div class="alert alert-danger">${errHtml}</div>`);
                }
            });
        });
    }
}

// Handler para formularios principales (prescripción, consulta, examen, historial)
function attachFormHandlers() {
    // Excluye forms especiales
    document.querySelectorAll('form').forEach(form => {
        if (
            form.id === 'addAllergyForm' ||
            form.id === 'prescriptionForm' ||
            form.id === 'examForm' ||
            form.id === 'consultationNotesForm'
        ) return;
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const isSearch = form.method.toLowerCase() === 'get';
            fetch(isSearch ? `${form.action}?${new URLSearchParams(new FormData(form))}` : form.action, {
                method: form.method,
                body: isSearch ? null : new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    ...(!isSearch && {'X-CSRFToken': getCookie('csrftoken')})
                }
            })
            .then(response => response.text())
            .then(html => {
                document.getElementById('mainContent').innerHTML = html;
                attachFormHandlers();
                attachPrescriptionFormHandler();
                attachExamFormHandler();
            });
        });
    });
    attachPrescriptionFormHandler();
    attachConsultationNotesFormHandler();
    handleAllergySearch();
    setupDiagnosisTreatmentToggles();
    setupDiseaseSearch();
}

// Diagnóstico y tratamiento toggles
function setupDiagnosisTreatmentToggles() {
    const diagnosisCheckbox = document.getElementById('showDiagnosis');
    const diagnosisContainer = document.getElementById('diagnosisContainer');
    const treatmentCheckbox = document.getElementById('showTreatment');
    const treatmentContainer = document.getElementById('treatmentContainer');
    if (diagnosisCheckbox && diagnosisContainer) {
        diagnosisCheckbox.onchange = function() {
            diagnosisContainer.classList.toggle('d-none', !this.checked);
        };
        diagnosisContainer.classList.toggle('d-none', !diagnosisCheckbox.checked);
    }
    if (treatmentCheckbox && treatmentContainer) {
        treatmentCheckbox.onchange = function() {
            treatmentContainer.classList.toggle('d-none', !this.checked);
        };
        treatmentContainer.classList.toggle('d-none', !treatmentCheckbox.checked);
    }
}

// Búsqueda y selección de enfermedades (diagnóstico)
function setupDiseaseSearch() {
    const searchInput = document.getElementById('disease_search');
    const select = document.getElementById('disease');
    const descDiv = document.getElementById('disease_desc');
    let lastQuery = '';
    let diseaseDescriptions = {};

    if (searchInput && select) {
        searchInput.addEventListener('input', function() {
            const query = searchInput.value.trim();
            if (!query) {
                select.innerHTML = '<option value="">Seleccione...</option>';
                descDiv.textContent = '';
                lastQuery = '';
                diseaseDescriptions = {};
                return;
            }
            if (query.length < 2 || query === lastQuery) return;
            lastQuery = query;
            fetch(`/ajax/disease-search/?q=${encodeURIComponent(query)}`)
                .then(r => r.json())
                .then(data => {
                    select.innerHTML = '<option value="">Seleccione...</option>';
                    diseaseDescriptions = {};
                    data.results.forEach(d => {
                        const opt = document.createElement('option');
                        opt.value = d.id;
                        opt.textContent = `${d.text} - ${d.desc}`;
                        select.appendChild(opt);
                        diseaseDescriptions[d.id] = d.desc;
                    });
                    descDiv.textContent = '';
                });
        });

        select.addEventListener('change', function() {
            const selectedId = select.value;
            descDiv.textContent = diseaseDescriptions[selectedId] || '';
        });
    }

    // Botón para agregar diagnóstico
    const btn = document.getElementById('addDiagnosisBtn');
    const form = document.getElementById('consultationNotesForm');
    if (btn && form) {
        btn.addEventListener('click', function() {
            const disease = form.disease.value;
            const diagnosis_notes = form.diagnosis_notes.value;
            if (!disease) return alert("Seleccione una enfermedad");
            const data = new FormData();
            data.append('disease', disease);
            data.append('diagnosis_notes', diagnosis_notes);

            fetch(form.action, {
                method: "POST",
                body: data,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.success && data.diagnosis_html) {
                    document.getElementById('diagnosisList').innerHTML = data.diagnosis_html;
                    form.disease.value = "";
                    form.diagnosis_notes.value = "";
                    descDiv.textContent = "";
                }
            });
        });
    }
}

// Handler para formulario de prescripción
function attachPrescriptionFormHandler() {
    const prescriptionForm = document.getElementById('prescriptionForm');
    if (prescriptionForm) {
        prescriptionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const form = this;
            const data = new FormData(form);
            fetch(form.action, {
                method: "POST",
                body: data,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(r => r.json())
            .then(data => {
                const msgDiv = document.getElementById('prescriptionMsg');
                if (data.success) {
                    form.reset();
                    if (data.html) {
                        document.getElementById('prescriptionList').innerHTML = data.html;
                    }
                } else {
                    msgDiv.innerHTML = `<div class="alert alert-danger">${data.error || "Error al registrar prescripción."}</div>`;
                }
            });
        });
    }
}

// Handler para formulario de consulta (notas)
function attachConsultationNotesFormHandler() {
    const notesForm = document.getElementById('consultationNotesForm');
    if (notesForm) {
        notesForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const form = this;
            const data = new FormData(form);
            data.append('mr_status', document.getElementById('mr_status').value);
            data.append('mr_notes', document.getElementById('mr_notes').value);

            fetch(form.action, {
                method: "POST",
                body: data,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    fetch('/consultation/list/', {headers: {'X-Requested-With': 'XMLHttpRequest'}})
                    .then(r => r.text())
                    .then(html => {
                        document.getElementById('mainContent').innerHTML = html;
                        attachFormHandlers();
                        attachConsultationNotesFormHandler();
                    });
                }
            });
        });
    }
}

// Handler para formulario de exámenes
function attachExamFormHandler() {
    const examForm = document.getElementById('examForm');
    if (examForm) {
        examForm.onsubmit = null;
        examForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const form = this;
            const data = new FormData(form);
            fetch(form.action, {
                method: "POST",
                body: data,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(r => r.json())
            .then(data => {
                const msgDiv = document.getElementById('examMsg');
                if (data.success) {
                    form.reset();
                    if (data.html) {
                        document.getElementById('examList').innerHTML = data.html;
                    }
                } else {
                    msgDiv.innerHTML = `<div class="alert alert-danger">${data.error || "Error al registrar examen."}</div>`;
                }
            });
        });
    }
}

// Handler para formulario de alergias
function attachAddAllergyFormHandler() {
    const addAllergyForm = document.getElementById('addAllergyForm');
    if (addAllergyForm) {
        addAllergyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const name = document.getElementById('newAllergyName').value.trim();
            const common_reactions = document.getElementById('newAllergyReactions').value.trim();
            const errorDiv = document.getElementById('addAllergyError');
            errorDiv.textContent = '';

            fetch(addAllergyForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(addAllergyForm)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Cierra el modal correctamente
                    const modalEl = document.getElementById('addAllergyModal');
                    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                    modal.hide();
                    document.body.classList.remove('modal-open');
                    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                    addAllergyForm.reset();
                    // Recarga la lista de alergias
                    refreshAllergyList();
                } else {
                    errorDiv.textContent = data.error || 'Error al registrar la alergia.';
                }
            })
            .catch(() => {
                errorDiv.textContent = 'Error de red.';
            });
        });
    }
}

// AJAX navigation (sidebar, links)
document.getElementById('sidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('sidebar-collapsed');
});

document.addEventListener('click', function(e) {
    const link = e.target.closest('a[data-ajax]');
    if (link) {
        e.preventDefault();
        fetch(link.href, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(response => response.text())
        .then(html => {
            document.getElementById('mainContent').innerHTML = html;
            attachFormHandlers();
            attachExamFormHandler();
        });
        return false;
    }
});

// Botones de edición y modales
document.addEventListener('click', function(e) {
    // Alergia
    const btnAllergy = e.target.closest('#btnAddAllergy');
    if (btnAllergy) {
        e.preventDefault();
        const url = btnAllergy.getAttribute('data-url');
        fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
        .then(r => r.text())
        .then(html => {
            showModal(html, 'addAllergyModal');
            attachAddAllergyFormHandler();
        });
    }
    // Editar cita
    const btnEdit = e.target.closest('.btnEditAppointment');
    if (btnEdit) {
        e.preventDefault();
        const url = btnEdit.getAttribute('data-url');
        fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
        .then(r => r.text())
        .then(html => {
            const modalDiv = showModal(html, 'ajaxModal');
            attachEditFormHandler(modalDiv, url, '/appointment/list/', attachFormHandlers);
        });
    }
    // Editar paciente
    const btnEditPatient = e.target.closest('.btnEditPatient');
    if (btnEditPatient) {
        e.preventDefault();
        const url = btnEditPatient.getAttribute('data-url');
        fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
        .then(r => r.text())
        .then(html => {
            const modalDiv = showModal(html, 'ajaxModal');
            attachEditFormHandler(modalDiv, url, '/patient/list/', attachFormHandlers);
        });
    }
    // Editar doctor
    const btnEditDoctor = e.target.closest('.btnEditDoctor');
    if (btnEditDoctor) {
        e.preventDefault();
        const url = btnEditDoctor.getAttribute('data-url');
        fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
        .then(r => r.text())
        .then(html => {
            const modalDiv = showModal(html, 'ajaxModal');
            attachEditFormHandler(modalDiv, url, '/doctor/list/', attachFormHandlers);
        });
    }
});

// Botones de eliminar (diagnóstico, prescripción, examen)
document.addEventListener('click', function(e) {
    // Diagnóstico
    if (e.target.closest('.btn-delete-diagnosis')) {
        const btn = e.target.closest('.btn-delete-diagnosis');
        const id = btn.getAttribute('data-id');
        if (confirm('¿Eliminar este diagnóstico?')) {
            fetch(`/consultation/diagnosis/delete/${id}/`, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken')}
            })
            .then(r => r.json())
            .then(data => {
                if (data.success && data.diagnosis_html) {
                    document.getElementById('diagnosisList').innerHTML = data.diagnosis_html;
                }
            });
        }
    }
    // Prescripción
    if (e.target.closest('.btn-delete-prescription')) {
        const btn = e.target.closest('.btn-delete-prescription');
        const id = btn.getAttribute('data-id');
        if (confirm('¿Eliminar esta prescripción?')) {
            fetch(`/consultation/prescription/delete/${id}/`, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken')}
            })
            .then(r => r.json())
            .then(data => {
                if (data.success && data.html) {
                    document.getElementById('prescriptionList').innerHTML = data.html;
                }
            });
        }
    }
    // Examen
    if (e.target.closest('.btn-delete-exam')) {
        const btn = e.target.closest('.btn-delete-exam');
        const id = btn.getAttribute('data-id');
        if (confirm('¿Eliminar este examen?')) {
            fetch(`/consultation/exam/delete/${id}/`, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken')}
            })
            .then(r => r.json())
            .then(data => {
                if (data.success && data.html) {
                    document.getElementById('examList').innerHTML = data.html;
                }
            });
        }
    }
});

// Navegación del calendario (meses)
document.addEventListener('click', function(e) {
    if (e.target.closest('#prevMonthBtn') || e.target.closest('#nextMonthBtn')) {
        e.preventDefault();
        const btn = e.target.closest('button');
        const month = btn.getAttribute('data-month');
        const year = btn.getAttribute('data-year');
        fetch(`/appointment/calendar/?month=${month}&year=${year}`, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.text())
        .then(html => {
            document.getElementById('mainContent').innerHTML = html;
        });
    }
});

// Listado de citas por día
document.addEventListener('click', function(e) {
    const dayLink = e.target.closest('.calendar-day-link');
    if (dayLink) {
        e.preventDefault();
        const date = dayLink.getAttribute('data-date');
        fetch(`/appointment/list/?date=${date}`, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.text())
        .then(html => {
            document.getElementById('mainContent').innerHTML = html;
            attachFormHandlers();
        });
    }
});

// Navegación al perfil del usuario
document.addEventListener('click', function(e) {
    const profileBtn = e.target.closest('#profileShortcut');
    if (profileBtn) {
        e.preventDefault();
        fetch('/profile/', {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.text())
        .then(html => {
            document.getElementById('mainContent').innerHTML = html;
            attachFormHandlers();
        });
    }
});

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    handleSidebar();
    attachFormHandlers();
});