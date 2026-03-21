(function () {
  var stored = localStorage.getItem('theme');
  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.setAttribute('data-theme', (stored ? stored === 'dark' : prefersDark) ? 'dark' : 'light');
})();

document.addEventListener('DOMContentLoaded', function () {
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');

  function apply(dark) {
    root.setAttribute('data-theme', dark ? 'dark' : 'light');
    btn.textContent = dark ? '☀️ Light' : '🌙 Dark';
    btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
  }

  apply(root.getAttribute('data-theme') === 'dark');

  btn.addEventListener('click', function () {
    var isDark = root.getAttribute('data-theme') !== 'dark';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    apply(isDark);
  });
});
