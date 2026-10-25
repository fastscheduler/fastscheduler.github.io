// Theme: toggle + persist across pages (localStorage). No-flash read is inline in <head>.
(function () {
  function applyTheme(next) {
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
  }
  var btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', function () {
      var cur = document.documentElement.getAttribute('data-theme') || 'light';
      var next = cur === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      btn.classList.add('spin');
      setTimeout(function () { btn.classList.remove('spin'); }, 400);
    });
  }
  // Keep theme in sync across open tabs/pages.
  window.addEventListener('storage', function (e) {
    if (e.key === 'theme' && e.newValue) {
      document.documentElement.setAttribute('data-theme', e.newValue);
    }
  });
})();
