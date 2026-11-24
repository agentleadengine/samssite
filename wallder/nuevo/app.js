const menu = document.querySelector('.mobile-nav');
menu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => { menu.open = false; });
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu.open) {
    menu.open = false;
    menu.querySelector('summary').focus();
  }
});
document.querySelectorAll('[data-demo]').forEach(form => {
  form.addEventListener('submit', event => {
    event.preventDefault();
    form.querySelector('.status').textContent = form.dataset.demo;
  });
});
