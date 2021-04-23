document.addEventListener('DOMContentLoaded', () => {
  /* Menu */
  // https://bulma.io/documentation/components/navbar/#navbarJsExample
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


  /* Notification */
  const removeNotificationButtons = document.getElementsByClassName('remove-notification')
  for (const button of removeNotificationButtons) {
    button.onclick = function () {
      const notification = button.parentNode
      notification.parentNode.removeChild(notification)
      return false
    }
  }

  /* Historique */
  const toggleHistory = document.getElementById("toggle-history")
  const history = document.getElementById("history-table")
  toggleHistory.onclick = function () {
    if (history.classList.contains('is-hidden')) {
      toggleHistory.innerHTML = `<span class="fa fa-eye-slash mr-2"></span> Cacher l'historique`
    } else {
      toggleHistory.innerHTML = `<span class="fa fa-eye mr-2"></span> Voir l'historique`
    }
    history.classList.toggle('is-hidden')
    return false
  }
});
