// Minimal JavaScript for aux-analytics
console.log('Auxiliary Analytics loaded');

// Bulma navbar burger toggle
document.addEventListener('DOMContentLoaded', () => {
    // Get all "navbar-burger" elements
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    // Add a click event on each of them
    $navbarBurgers.forEach( el => {
        el.addEventListener('click', () => {
            // Get the target from the "data-target" attribute
            const target = el.dataset.target;
            const $target = document.getElementById(target);

            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            el.classList.toggle('is-active');
            $target.classList.toggle('is-active');
        });
    });

    // Close notification messages
    const $deleteButtons = Array.prototype.slice.call(document.querySelectorAll('.notification .delete'), 0);

    $deleteButtons.forEach( el => {
        el.addEventListener('click', () => {
            const notification = el.parentNode;
            notification.parentNode.removeChild(notification);
        });
    });
});
