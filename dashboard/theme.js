(function () {
  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
  });
})();
