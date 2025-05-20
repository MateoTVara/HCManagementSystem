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

// Initial call
handleSidebar();

// Handle window resize
window.addEventListener('resize', handleSidebar);