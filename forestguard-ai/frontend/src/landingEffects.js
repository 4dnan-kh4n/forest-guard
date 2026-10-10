export function startForestScroll() {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const coarse = window.matchMedia('(pointer: coarse)');
  if (reduced.matches || coarse.matches) return;
  const root = document.documentElement;
  const original = root.style.scrollBehavior;
  root.style.scrollBehavior = 'auto';
  let target = window.scrollY, frame = 0, animating = false;
  const clamp = value => Math.min(Math.max(value, 0), Math.max(0, root.scrollHeight - innerHeight));
  const animate = () => {
    target = clamp(target);
    const difference = target - scrollY;
    if (Math.abs(difference) < .5) { scrollTo(0, target); animating = false; return; }
    scrollTo(0, scrollY + difference * .1);
    frame = requestAnimationFrame(animate);
  };
  const begin = () => { if (!animating) { animating = true; frame = requestAnimationFrame(animate); } };
  const cancel = () => { cancelAnimationFrame(frame); animating = false; target = scrollY; };
  const wheel = event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || !event.deltaY || reduced.matches || coarse.matches || event.target.closest?.('dialog')) return;
    event.preventDefault();
    const lineHeight = parseFloat(getComputedStyle(document.body).lineHeight) || 16;
    const unit = event.deltaMode === 1 ? lineHeight : event.deltaMode === 2 ? innerHeight : 1;
    target = clamp(target + event.deltaY * unit);
    begin();
  };
  const scroll = () => { if (!animating) target = scrollY; };
  const click = event => {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || reduced.matches || coarse.matches) return;
    const link = event.target.closest?.('a[href^="#"]');
    if (!link || link.classList.contains('skip-link')) return;
    const destination = document.getElementById(link.getAttribute('href').slice(1));
    if (!destination) return;
    event.preventDefault();
    target = clamp(scrollY + destination.getBoundingClientRect().top - (document.querySelector('.landing-nav')?.getBoundingClientRect().height ?? 0) - 16);
    history.pushState(null, '', link.getAttribute('href'));
    begin();
  };
  const key = event => { if (['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(event.key)) cancel(); };
  addEventListener('wheel', wheel, {passive:false}); addEventListener('scroll', scroll, {passive:true});
  addEventListener('keydown', key); addEventListener('pointerdown', cancel);
  reduced.addEventListener('change', cancel); coarse.addEventListener('change', cancel); document.addEventListener('click', click);
  return () => {
    cancel(); removeEventListener('wheel', wheel); removeEventListener('scroll', scroll); removeEventListener('keydown', key);
    removeEventListener('pointerdown', cancel); reduced.removeEventListener('change', cancel); coarse.removeEventListener('change', cancel);
    document.removeEventListener('click', click); root.style.scrollBehavior = original;
  };
}

export function startForestCursor(cursor) {
  const root = document.documentElement;
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const cursors = () => [cursor, ...document.querySelectorAll('.modal-cursor')];
  const hide = () => { cursors().forEach(node => { node.style.opacity = '0'; }); root.classList.remove('custom-cursor-active'); };
  const move = event => {
    if (event.pointerType === 'touch' || !fine.matches || reduced.matches) { hide(); return; }
    cursors().forEach(node => {
      node.style.transform = `translate(${event.clientX}px, ${event.clientY}px) translate(-50%, -50%)`;
      node.style.opacity = '1';
    });
    root.classList.add('custom-cursor-active');
  };
  document.addEventListener('pointermove', move); document.addEventListener('pointerleave', hide); addEventListener('blur', hide);
  fine.addEventListener('change', hide); reduced.addEventListener('change', hide);
  return () => {
    hide(); document.removeEventListener('pointermove', move); document.removeEventListener('pointerleave', hide); removeEventListener('blur', hide);
    fine.removeEventListener('change', hide); reduced.removeEventListener('change', hide);
  };
}
