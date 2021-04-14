/* Menu */

// https://bulma.io/documentation/components/navbar/#navbarJsExample
document.addEventListener('DOMContentLoaded', () => {
  const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  if ($navbarBurgers.length > 0) {
    $navbarBurgers.forEach( el => {
      el.addEventListener('click', () => {
        const target = el.dataset.target;
        const $target = document.getElementById(target);
        el.classList.toggle('is-active');
        $target.classList.toggle('is-active');
      });
    });
  }
});

/* Notification */

document.addEventListener('DOMContentLoaded', function (event) {
  const removeNotificationButtons = document.getElementsByClassName('remove-notification')
  for (const button of removeNotificationButtons) {
    button.onclick = function () {
      const notification = button.parentNode
      notification.parentNode.removeChild(notification)
      return false
    }
  }
})
