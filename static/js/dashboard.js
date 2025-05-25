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