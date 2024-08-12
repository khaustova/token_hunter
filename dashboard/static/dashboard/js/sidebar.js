'use strict'; 

// Сворачивание/разворачивание боковой панели.

const toggleSidebar = document.getElementById('toggle-sidebar');

if (toggleSidebar !== null) {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementsByClassName('wrapper')[0];
    let sidebarIsOpen = localStorage.getItem('sidebarIsOpen');
    
    if (sidebarIsOpen === null) {
        sidebarIsOpen = 'true';
    }
    
    main.classList.toggle('shifted', sidebarIsOpen === 'true');
    sidebar.setAttribute('aria-expanded', sidebarIsOpen);

    toggleSidebar.addEventListener('click', function() {
        toggleSidebar.classList.toggle('rotate');
        if (sidebarIsOpen === 'true') {
            sidebarIsOpen = 'false';
        } else {
            sidebarIsOpen = 'true';
        }
        localStorage.setItem('sidebarIsOpen', sidebarIsOpen);
        main.classList.toggle('shifted');
        sidebar.setAttribute('aria-expanded', sidebarIsOpen);
    });
}
