document.getElementById('sidebarToggle').addEventListener('click', () => {
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

function getCookie(name) {
    let cookie = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookie ? cookie.pop() : '';
}

function handleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    
    if (window.innerWidth < 992) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('sidebar-collapsed');
        });
    } else {
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
      showModal(html);
    });
  }

  // Handler para editar cita
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
});

// Función para mostrar el modal, acepta título opcional
function showModal(contentHtml, title = 'Nueva Alergía') {
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
        <h5 class="modal-title">${title}</h5>
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
}

// Handler para el formulario de edición de cita
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
          // Cierra el modal y recarga la lista de citas
          bootstrap.Modal.getOrCreateInstance(modalDiv).hide();
          document.body.classList.remove('modal-open');
          document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
          // Recarga la lista de citas (puedes refinar esto según tu UX)
          fetch(window.location.href, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
            .then(r => r.text())
            .then(html => {
              document.getElementById('mainContent').innerHTML = html;
            });
        } else {
          // Muestra errores
          const errHtml = Object.values(data.errors).flat().join('<br>');
          modalDiv.querySelector('.modal-body').insertAdjacentHTML('afterbegin',
            `<div class="alert alert-danger">${errHtml}</div>`);
        }
      });
    });
  }
}

function initHandlers() {
    handleAllergySearch();
}

document.addEventListener('DOMContentLoaded', function() {
    initHandlers();
    handleSidebar();
});

handleSidebar();

window.addEventListener('resize', handleSidebar);