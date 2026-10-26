// Melhorias progressivas. Todas as validações definitivas também existem no servidor.
document.querySelectorAll('[data-demo-email]').forEach(button => button.addEventListener('click', () => {
  document.querySelector('[name=email]').value = button.dataset.demoEmail;
  document.querySelector('[name=password]').value = 'Clinica2026!';
  document.querySelector('[name=password]').focus();
}));
document.querySelector('[data-menu]')?.addEventListener('click', () => document.querySelector('.sidebar').classList.toggle('open'));
document.querySelectorAll('[data-open]').forEach(button => button.addEventListener('click', () => document.getElementById(button.dataset.open).showModal()));
document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
document.querySelector('[data-back]')?.addEventListener('click', () => window.history.length > 1 ? window.history.back() : window.location.assign('/'));
document.querySelector('[data-add-medication]')?.addEventListener('click', function () {
  const next = document.querySelector('.medication-item.hidden');
  if (next) next.classList.remove('hidden');
  if (!document.querySelector('.medication-item.hidden')) this.hidden = true;
});
document.querySelector('[data-procedure]')?.addEventListener('change', function () {
  const price = this.selectedOptions[0]?.dataset.price;
  if (price) this.closest('form').querySelector('[name=charged_price]').value = price;
});
document.querySelector('#doctor-select')?.addEventListener('change', function () {
  const selected = this.selectedOptions[0];
  for (const [target, key] of [['#specialty-select', 'specialties'], ['#unit-select', 'units']]) {
    const select = document.querySelector(target);
    const allowed = JSON.parse(selected?.dataset[key] || '[]');
    for (const option of select.options) option.disabled = !!option.value && allowed.length > 0 && !allowed.includes(Number(option.value));
    select.value = allowed.length === 1 ? String(allowed[0]) : '';
  }
});
// Evita clique duplicado na mesma operação; transações e constraints garantem integridade.
document.querySelectorAll('form[method=post]').forEach(form => form.addEventListener('submit', () => {
  const button = form.querySelector('button[type=submit], button:not([type])');
  if (button) { button.disabled = true; button.dataset.originalText = button.textContent; }
}));
