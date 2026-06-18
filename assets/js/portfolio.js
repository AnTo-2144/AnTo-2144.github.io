/* ============================================================
   PORTFOLIO.JS — Antonio Simoes Personal Portfolio
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ----------------------------------------------------------
     Page-exit transition — fade out then navigate
     Uses inline styles so CSS specificity can never block it.
     Navigation is always guaranteed via the setTimeout fallback.
  ---------------------------------------------------------- */
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    const isInternal = href
      && !href.startsWith('#')
      && !href.startsWith('mailto:')
      && !href.startsWith('tel:')
      && !href.includes('://');

    if (isInternal) {
      link.addEventListener('click', e => {
        // Guard: don't double-fire if already navigating
        if (document._navigating) return;
        document._navigating = true;

        e.preventDefault();

        // Inline fade-out — avoids all CSS specificity issues
        document.body.style.transition = 'opacity 0.2s ease';
        document.body.style.opacity   = '0';

        // Navigate after the fade
        setTimeout(() => { window.location.href = href; }, 220);
      });
    }
  });


  /* ----------------------------------------------------------
     Mobile nav toggle
  ---------------------------------------------------------- */
  const navToggle = document.getElementById('navToggle');
  const navLinks  = document.getElementById('navLinks');

  navToggle?.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });

  // Close mobile menu when a link is clicked
  navLinks?.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => navLinks.classList.remove('open'));
  });


  /* ----------------------------------------------------------
     Active nav link highlighting based on scroll position
  ---------------------------------------------------------- */
  const sections = document.querySelectorAll('section[id], div[id="home"]');
  const navItems = document.querySelectorAll('.nav-links a');

  const highlightNav = () => {
    const scrollY = window.scrollY + 90; // offset for fixed nav height

    sections.forEach(section => {
      const top    = section.offsetTop;
      const height = section.offsetHeight;
      const id     = section.getAttribute('id');

      if (scrollY >= top && scrollY < top + height) {
        navItems.forEach(a => a.classList.remove('active'));
        const match = document.querySelector(`.nav-links a[href="#${id}"]`);
        if (match) match.classList.add('active');
      }
    });
  };

  window.addEventListener('scroll', highlightNav, { passive: true });
  highlightNav(); // run once on load


  /* ----------------------------------------------------------
     Scroll-triggered fade-in animations (IntersectionObserver)
  ---------------------------------------------------------- */
  const faders = document.querySelectorAll('.fade-in');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target); // animate once, then stop watching
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
  });

  faders.forEach(el => observer.observe(el));


  /* ----------------------------------------------------------
     Lightbox — triggered by .gallery-item elements
     Each item needs data-src (full image URL) and data-caption
  ---------------------------------------------------------- */
  const lightbox = document.getElementById('lightbox');

  if (lightbox) {
    const items   = Array.from(document.querySelectorAll('.gallery-item'));
    const lbImg   = lightbox.querySelector('.lightbox-img');
    const lbCap   = lightbox.querySelector('.lightbox-caption');
    let   current = 0;

    const show = (index) => {
      current = (index + items.length) % items.length;
      const item = items[current];
      lbImg.style.opacity = '0';
      lbImg.src         = item.dataset.src;
      lbImg.alt         = item.dataset.caption || '';
      lbCap.textContent = item.dataset.caption || '';
      lbImg.onload = () => { lbImg.style.opacity = '1'; };
    };

    const open = (index) => {
      show(index);
      lightbox.style.top = window.scrollY + 'px';
      lightbox.classList.add('open');
    };

    const close = () => {
      lightbox.classList.remove('open');
      lightbox.style.top = '';
    };

    items.forEach((item, i) => item.addEventListener('click', () => open(i)));

    lightbox.querySelector('.lightbox-backdrop').addEventListener('click', close);
    lightbox.querySelector('.lightbox-close').addEventListener('click', close);
    lightbox.querySelector('.lightbox-prev').addEventListener('click', () => show(current - 1));
    lightbox.querySelector('.lightbox-next').addEventListener('click', () => show(current + 1));

    document.addEventListener('keydown', e => {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape')     close();
      if (e.key === 'ArrowLeft')  show(current - 1);
      if (e.key === 'ArrowRight') show(current + 1);
    });
  }


  /* ----------------------------------------------------------
     Navbar shadow on scroll
  ---------------------------------------------------------- */
  const navbar = document.getElementById('navbar');

  const updateNavShadow = () => {
    if (window.scrollY > 10) {
      navbar.style.boxShadow = '0 2px 16px rgba(0,0,0,0.08)';
    } else {
      navbar.style.boxShadow = 'none';
    }
  };

  window.addEventListener('scroll', updateNavShadow, { passive: true });
  updateNavShadow();

});
