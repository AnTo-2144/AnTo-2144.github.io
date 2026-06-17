/* ============================================================
   PORTFOLIO.JS — Antonio Simoes Personal Portfolio
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ----------------------------------------------------------
     Page-exit transition — fade out before navigating away
     Only applies to same-site relative links (not anchors / mailto / external)
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
        e.preventDefault();
        document.body.classList.add('is-leaving');
        setTimeout(() => { window.location.href = href; }, 280);
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
