// Lightweight progressive enhancements; the experiment works without JavaScript.
window.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('[data-menu-toggle]');
  if (menu) {
    menu.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      const open = sidebar.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
    });
  }
  document.querySelectorAll('[data-copy-target]').forEach(button => {
    button.addEventListener('click', async () => {
      const source = document.getElementById(button.dataset.copyTarget);
      if (!source || !navigator.clipboard) return;
      try {
        await navigator.clipboard.writeText(source.textContent);
        const original = button.textContent;
        button.textContent = 'Copied ✓';
        setTimeout(() => button.textContent = original, 1700);
      } catch (_) { button.textContent = 'Select text to copy'; }
    });
  });
  // After a server-side POST, focus the results for a clear cause-and-effect demo.
  if (document.querySelector('.git-alert')) {
    document.getElementById('output')?.scrollIntoView({behavior:'smooth', block:'nearest'});
  }
});
