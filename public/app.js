// Melhorias progressivas. Todas as validações definitivas também existem no servidor.
document.querySelectorAll('[data-demo-email]').forEach(button => button.addEventListener('click', () => {
  document.querySelector('[name=email]').value = button.dataset.demoEmail;
  document.querySelector('[name=password]').value = 'Clinica2026!';
  document.querySelector('[name=password]').focus();
}));
const mobileMenu = document.querySelector('[data-menu]');
mobileMenu?.addEventListener('click', () => {
  const open = document.querySelector('.sidebar').classList.toggle('open');
  mobileMenu.setAttribute('aria-expanded', String(open));
});
const supportMenu = document.querySelector('.nav-details');
const supportPanel = supportMenu?.querySelector('.subnav');
function positionSupportMenu() {
  if (!supportMenu || !supportPanel) return;
  if (!supportMenu.open || window.innerWidth <= 720) {
    if (supportPanel.parentElement !== supportMenu) supportMenu.appendChild(supportPanel);
    return;
  }
  // Fora do details, o painel não é recortado pelo conteúdo rolável do menu.
  if (supportPanel.parentElement !== document.body) document.body.appendChild(supportPanel);
  const summary = supportMenu.querySelector('summary').getBoundingClientRect();
  supportPanel.style.top = Math.max(91, Math.min(summary.top, window.innerHeight - supportPanel.offsetHeight - 14)) + 'px';
}
supportMenu?.addEventListener('toggle', positionSupportMenu);
window.addEventListener('resize', positionSupportMenu);
document.querySelector('.sidebar nav')?.addEventListener('scroll', positionSupportMenu);
document.addEventListener('click', event => {
  if (supportMenu?.open && !supportMenu.contains(event.target) && !supportPanel?.contains(event.target)) supportMenu.open = false;
  if (window.innerWidth <= 720 && !event.target.closest('.sidebar, [data-menu]')) {
    document.querySelector('.sidebar')?.classList.remove('open');
    mobileMenu?.setAttribute('aria-expanded', 'false');
  }
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    if (supportMenu) supportMenu.open = false;
    document.querySelector('.sidebar')?.classList.remove('open');
    mobileMenu?.setAttribute('aria-expanded', 'false');
  }
});
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
// Máscaras dos cadastros: só aceitam dígitos e limitam ao tamanho do documento.
const masks = {
  cpf: d => d.slice(0, 11).replace(/^(\d{3})(\d)/, '$1.$2').replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3').replace(/\.(\d{3})(\d{1,2})$/, '.$1-$2'),
  phone: d => {
    d = d.slice(0, 11);
    if (d.length <= 2) return d ? `(${d}` : '';
    const tail = d.length === 11 ? 5 : 4;
    return `(${d.slice(0, 2)}) ${d.slice(2, 2 + tail)}${d.length > 2 + tail ? '-' + d.slice(2 + tail) : ''}`;
  },
};
document.querySelectorAll('[data-mask]').forEach(input => {
  const apply = event => {
    if (input.dataset.mask === 'house-number') {
      const v = input.value.toUpperCase();
      const deleting = event?.inputType?.startsWith('delete');
      input.value = /^S/.test(v) ? (deleting ? '' : 'S/N') : v.replace(/\D/g, '').slice(0, 6);
      return;
    }
    input.value = masks[input.dataset.mask](input.value.replace(/\D/g, ''));
  };
  input.addEventListener('input', apply);
  apply();
});
// Confirmação antes de ações destrutivas. Roda na captura para impedir o bloqueio do botão se o usuário cancelar.
document.querySelectorAll('form[data-confirm]').forEach(form => form.addEventListener('submit', event => {
  if (!window.confirm(form.dataset.confirm)) { event.preventDefault(); event.stopImmediatePropagation(); }
}, true));
