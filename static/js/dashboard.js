// Sidebar Toggle
document.getElementById('sidebarToggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('sidebar-collapsed');
});

// AJAX Content Loading
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

// Modified form handler (replace your existing attachFormHandlers)
function attachFormHandlers() {
    document.querySelectorAll('form').forEach(form => {
        // Ignora el formulario del modal de alergia
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

// CSRF Token Helper
function getCookie(name) {
    let cookie = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookie ? cookie.pop() : '';
}
// Only enable toggle for mobile
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

// Función para manejar el buscador de alergias
function handleAllergySearch() {
    document.addEventListener('input', function(e) {
        if(e.target && e.target.id === 'allergySearch') {
            const searchTerm = e.target.value.toLowerCase().trim();
            const container = document.getElementById('allergyList');
            
            if(!container) return; // Si no existe el contenedor, salir
            
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

// Función para crear y mostrar modal con contenido HTML
function showModal(contentHtml) {
  // Si ya hay modal, lo borramos para evitar duplicados
  let existingModal = document.getElementById('ajaxModal');
  if (existingModal) existingModal.remove();

  // Crear modal Bootstrap (usando clases Bootstrap 5)
  const modalDiv = document.createElement('div');
  modalDiv.id = 'ajaxModal';
  modalDiv.className = 'modal fade';
  modalDiv.tabIndex = -1;
  modalDiv.innerHTML = `
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-body">
          ${contentHtml}
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(modalDiv);

  // Inicializar modal con Bootstrap JS
  let modal = new bootstrap.Modal(modalDiv);
  modal.show();

  // Attach handler para el submit del formulario dentro del modal
  const form = modalDiv.querySelector('form');
  if (form) {
    form.id = 'addAllergyForm'; // para evitar conflictos con otros forms
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      // enviar formulario con AJAX
      fetch(form.action, {
        method: form.method,
        body: new FormData(form),
        headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken')}
      })
      .then(r => r.text())
      .then(html => {
        // Reemplaza el contenido del modal con la nueva respuesta
        modalDiv.querySelector('.modal-body').innerHTML = html;
        // Si quieres cerrar modal al guardar, detecta si hay formulario o mensaje de éxito
        // Por ejemplo, si no hay formulario, cierras el modal
        if (!modalDiv.querySelector('form')) {
          modal.hide();
        }
      });
    });
  }
}

// Evento click para abrir modal alergia
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
});


function initHandlers() {
    handleAllergySearch();
    // Agrega aquí otras inicializaciones necesarias
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    initHandlers();
    handleSidebar();
});

// Initial call
handleSidebar();

// Handle window resize
window.addEventListener('resize', handleSidebar);