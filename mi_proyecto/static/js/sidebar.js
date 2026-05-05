document.addEventListener('DOMContentLoaded', function () {
    var sidebar = document.getElementById('sidebar');
    var sidebarToggle = document.getElementById('sidebarToggle');
    var mobileToggle = document.getElementById('mobileToggle');
    var sectionToggles = document.querySelectorAll('.nav-section-toggle');

    if (!sidebar) {
        return;
    }

    function setExpanded(button, expanded) {
        if (button) {
            button.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        }
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            var isCollapsed = sidebar.classList.toggle('collapsed');
            setExpanded(sidebarToggle, !isCollapsed);
        });
    }

    sectionToggles.forEach(function (toggle) {
        toggle.addEventListener('click', function () {
            var section = toggle.closest('.nav-section');

            if (!section) {
                return;
            }

            var isOpen = section.classList.toggle('open');
            setExpanded(toggle, isOpen);
        });
    });

    if (mobileToggle) {
        mobileToggle.addEventListener('click', function () {
            var isOpen = sidebar.classList.toggle('open');
            setExpanded(mobileToggle, isOpen);
        });
    }

    sidebar.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
                setExpanded(mobileToggle, false);
            }
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            setExpanded(mobileToggle, false);
        }
    });
});
