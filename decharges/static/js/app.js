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
  if (toggleHistory) {
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
  }

  const dechargeProrataInput = document.getElementById("id_decharge_applicable_uniquement_sur_une_partie_de_lannee")
  const toggleDates = function (visible) {
    const date1 = document.getElementById("id_date_fin_decharge")
    const date2 = document.getElementById("id_date_debut_decharge")
    date1.parentNode.parentNode.style["display"] = visible ? "block" : "none"
    date2.parentNode.parentNode.style["display"] = visible ? "block" : "none"
  }
  if (dechargeProrataInput) {
    toggleDates(dechargeProrataInput.checked)
    dechargeProrataInput.onchange = function (value) {
      toggleDates(value.target.checked)
    }
  }
});
