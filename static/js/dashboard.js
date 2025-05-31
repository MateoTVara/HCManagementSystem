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

function attachFormHandlers() {
    document.querySelectorAll('form').forEach(form => {
        if (form.id === 'addAllergyForm') return;
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
            });
        });
    });
    initHandlers();
}

document.getElementById('sidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('sidebar-collapsed');
});

document.querySelectorAll('[data-ajax]').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        fetch(this.href, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(response => response.text())
        .then(html => {
            document.getElementById('mainContent').innerHTML = html;
            attachFormHandlers();
        });
    });
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
});

document.addEventListener('DOMContentLoaded', function() {
    initHandlers();
    handleSidebar();
});

window.addEventListener('resize', handleSidebar);
handleSidebar();