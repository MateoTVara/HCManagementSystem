function getCookie(name) {
    let cookie = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookie ? cookie.pop() : '';
}

function handleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    
    if (window.innerWidth >= 992) {
        sidebar.classList.remove('sidebar-collapsed');
    }
}

function handleAllergySearch() {
    document.addEventListener('input', function(e) {
        if(e.target && e.target.id === 'allergySearch') {
            const searchTerm = e.target.value.toLowerCase().trim();
            const container = document.getElementById('allergyList');
            
            if(!container) return;
            
            const items = container.getElementsByClassName('allergy-item');
            let visibleCount = 0;

            Array.from(items).forEach(item => {
                const label = item.querySelector('.form-check-label').textContent.toLowerCase();
                const matches = label.includes(searchTerm);
                item.style.display = matches ? 'block' : 'none';
                visibleCount += matches ? 1 : 0;
            });

            const noResults = document.getElementById('noResults');
            if(noResults) {
                noResults.classList.toggle('d-none', visibleCount > 0);
            }
        }
    });
}

function initHandlers() {
    handleAllergySearch();
}

function refreshAllergyList() {
    fetch('/allergy/partial_list/', {
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(r => r.text())
    .then(html => {
        document.getElementById('allergyList').innerHTML = html;
        initHandlers();
    })
    .catch(() => console.error('No se pudo recargar lista de alergias'));
}

function showModal(contentHtml) {
    let existingModal = document.getElementById('ajaxModal');
    if (existingModal) existingModal.remove();

    const modalDiv = document.createElement('div');
    modalDiv.id = 'ajaxModal';
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

    const form = modalDiv.querySelector('form');
    if (form) {
        form.id = 'addAllergyForm';
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
                    modal.hide();
                    modalDiv.addEventListener('hidden.bs.modal', function handler() {
                        modalDiv.remove();
                        if (!document.querySelector('.modal.show')) {
                            document.body.classList.remove('modal-open');
                            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                        }
                        refreshAllergyList();
                        modalDiv.removeEventListener('hidden.bs.modal', handler);
                    });
                } else {
                    const errHtml = Object.values(data.errors).flat().join('<br>');
                    modalDiv.querySelector('.modal-body').insertAdjacentHTML('afterbegin',
                        `<div class="alert alert-danger">${errHtml}</div>`);
                }
            })
            .catch(() => {
                console.error('Error de red al guardar alergia');
            });
        });
    }
}

function showAllergyModal(contentHtml) {
    let existingModal = document.getElementById('ajaxModalAllergy');
    if (existingModal) existingModal.remove();

    const modalDiv = document.createElement('div');
    modalDiv.id = 'ajaxModalAllergy';
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

    const form = modalDiv.querySelector('form');
    if (form) {
        form.id = 'addAllergyForm';
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
                    modal.hide();
                    modalDiv.addEventListener('hidden.bs.modal', function handler() {
                        modalDiv.remove();
                        const patientEditForm = document.querySelector('form[action*="patient/edit"]');
                        if (patientEditForm) {
                            const match = patientEditForm.getAttribute('action').match(/patient\/edit\/(\d+)\//);
                            if (match) {
                                const patientId = match[1];
                                fetch(`/allergy/partial_list/${patientId}/`, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
                                .then(r => r.text())
                                .then(html => {
                                    const allergyList = document.getElementById('allergyList');
                                    if (allergyList) allergyList.innerHTML = html;
                                });
                            }
                        } else {
                            refreshAllergyList();
                        }
                        modalDiv.removeEventListener('hidden.bs.modal', handler);
                    });
                } else {
                    const errHtml = Object.values(data.errors).flat().join('<br>');
                    modalDiv.querySelector('.modal-body').insertAdjacentHTML('afterbegin',
                        `<div class="alert alert-danger">${errHtml}</div>`);
                }
            })
            .catch(() => {
                console.error('Error de red al guardar alergia');
            });
        });
    }
}

function attachEditAppointmentFormHandler() {
    const modalDiv = document.getElementById('ajaxModal');
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
                    fetch('/appointment/list/', {headers: {'X-Requested-With': 'XMLHttpRequest'}})
                    .then(r => r.text())
                    .then(html => {
                        document.getElementById('mainContent').innerHTML = html;
                        attachFormHandlers();
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

function attachEditPatientFormHandler() {
    const modalDiv = document.getElementById('ajaxModal');
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
                    fetch('/patient/list/', {headers: {'X-Requested-With': 'XMLHttpRequest'}})
                    .then(r => r.text())
                    .then(html => {
                        document.getElementById('mainContent').innerHTML = html;
                        attachFormHandlers();
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

function attachEditDoctorFormHandler() {
    const modalDiv = document.getElementById('ajaxModal');
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
                    fetch('/doctor/list/', {headers: {'X-Requested-With': 'XMLHttpRequest'}})
                    .then(r => r.text())
                    .then(html => {
                        document.getElementById('mainContent').innerHTML = html;
                        attachFormHandlers();
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
                if(data.success) {
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

function attachConsultationNotesFormHandler() {
    const notesForm = document.getElementById('consultationNotesForm');
    if (notesForm) {
        notesForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const form = this;
            const data = new FormData(form);

            // Agrega los datos del caso (MedicalRecord)
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

function attachMedicalRecordFormHandler() {
    const form = document.getElementById('medicalRecordForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
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
                const msg = document.getElementById('medicalRecordMsg');
                if (data.success) {
                    msg.innerHTML = `<span class="text-success">Caso actualizado</span>`;
                } else {
                    msg.innerHTML = `<span class="text-danger">${data.error || "Error al actualizar el caso."}</span>`;
                }
            });
        });
    }
}

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
                if(data.success) {
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

function attachFormHandlers() {
    document.querySelectorAll('form').forEach(form => {
        if (form.id === 'addAllergyForm' || form.id === 'prescriptionForm' || form.id === 'examForm') return;
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
    initHandlers();
}

document.getElementById('sidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('sidebar-collapsed');
});

document.addEventListener('click', function(e) {
    const link = e.target.closest('a[data-ajax]');
    if (link) {
        e.preventDefault();
        console.log('Interceptado AJAX', link.href);
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

document.addEventListener('click', function(e) {
    const btn = e.target.closest('#btnAddAllergy');
    if (btn) {
        e.preventDefault();
        const url = btn.getAttribute('data-url');
        fetch(url, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.text())
        .then(html => {
            showAllergyModal(html);
        });
    }

    const btnEdit = e.target.closest('.btnEditAppointment');
    if (btnEdit) {
        e.preventDefault();
        const url = btnEdit.getAttribute('data-url');
        fetch(url, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.text())
        .then(html => {
            showModal(html, 'Editar Cita');
            attachEditAppointmentFormHandler();
        });
    }

    const btnEditPatient = e.target.closest('.btnEditPatient');
    if (btnEditPatient) {
        e.preventDefault();
        const url = btnEditPatient.getAttribute('data-url');
        fetch(url, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.text())
        .then(html => {
            showModal(html, 'Editar Paciente');
            attachEditPatientFormHandler();
        });
    }

    const btnEditDoctor = e.target.closest('.btnEditDoctor');
    if (btnEditDoctor) {
        e.preventDefault();
        const url = btnEditDoctor.getAttribute('data-url');
        fetch(url, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.text())
        .then(html => {
            showModal(html, 'Editar Médico');
            attachEditDoctorFormHandler();
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
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
                if(data.success) {
                    form.reset();
                } else {
                    msgDiv.innerHTML = `<div class="alert alert-danger">${data.error || "Error al registrar prescripción."}</div>`;
                }
            });
        });
    }
    initHandlers();
    handleSidebar();
});

window.addEventListener('resize', handleSidebar);
handleSidebar();