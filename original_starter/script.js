/* ================================
   SIDEBAR TOGGLE
================================ */

function toggleSidebar() {

    const sidebar = document.getElementById("sidebar");

    sidebar.classList.toggle("open");

}


/* ================================
   DROPDOWN MENU
================================ */

function toggleDropdown(menuId) {

    const menu = document.getElementById(menuId);

    menu.classList.toggle("show");

}