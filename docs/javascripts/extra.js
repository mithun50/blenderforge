/**
 * BlenderForge - Enhanced Interactivity
 * Custom JavaScript for stunning UI effects
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all enhancements
  initParticles();
  initScrollAnimations();
  initCardEffects();
  initTypingEffect();
  initCounterAnimation();
  initCursorGlow();
});

/**
 * Floating Particles Background
 */
function initParticles() {
  // Check if particles container already exists
  if (document.querySelector('.particle-container')) return;

  const container = document.createElement('div');
  container.className = 'particle-container';

  // Create particles
  for (let i = 0; i < 15; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 20 + 's';
    particle.style.animationDuration = (15 + Math.random() * 15) + 's';

    // Random colors
    const colors = ['#a855f7', '#f59e0b', '#ec4899', '#06b6d4', '#10b981'];
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    particle.style.width = (4 + Math.random() * 6) + 'px';
    particle.style.height = particle.style.width;

    container.appendChild(particle);
  }

  document.body.appendChild(container);
}

/**
 * Scroll-triggered Animations
 */
function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe cards and sections
  document.querySelectorAll('.card, .stat-card, .admonition, table').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });

  // Add animation class
  const style = document.createElement('style');
  style.textContent = `
    .animate-in {
      opacity: 1 !important;
      transform: translateY(0) !important;
    }
  `;
  document.head.appendChild(style);
}

/**
 * 3D Card Tilt Effect
 */
function initCardEffects() {
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = (y - centerY) / 20;
      const rotateY = (centerX - x) / 20;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
      card.style.transition = 'transform 0.5s ease';
    });

    card.addEventListener('mouseenter', () => {
      card.style.transition = 'transform 0.1s ease';
    });
  });
}

/**
 * Typing Effect for Hero Text
 */
function initTypingEffect() {
  const heroGradient = document.querySelector('.hero-gradient');
  if (!heroGradient || heroGradient.dataset.typed) return;

  heroGradient.dataset.typed = 'true';
  const originalText = heroGradient.innerHTML;

  // Skip typing effect for accessibility or if user prefers reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
}

/**
 * Animated Counter for Stats
 */
function initCounterAnimation() {
  const counters = document.querySelectorAll('.stat-number');

  const observerOptions = {
    threshold: 0.5
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = 'true';
        animateCounter(entry.target);
      }
    });
  }, observerOptions);

  counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
  const text = element.textContent;
  const hasPlus = text.includes('+');
  const hasPercent = text.includes('%');
  const numericValue = parseInt(text.replace(/[^0-9]/g, ''));

  if (isNaN(numericValue)) return;

  const duration = 2000;
  const startTime = performance.now();

  function updateCounter(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Easing function for smooth animation
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    const currentValue = Math.floor(easeOutQuart * numericValue);

    element.textContent = currentValue + (hasPlus ? '+' : '') + (hasPercent ? '%' : '');

    if (progress < 1) {
      requestAnimationFrame(updateCounter);
    }
  }

  requestAnimationFrame(updateCounter);
}

/**
 * Cursor Glow Effect
 */
function initCursorGlow() {
  // Skip on mobile
  if (window.matchMedia('(max-width: 768px)').matches) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const glow = document.createElement('div');
  glow.className = 'cursor-glow';
  glow.style.cssText = `
    position: fixed;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(124, 58, 237, 0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: -1;
    transform: translate(-50%, -50%);
    transition: opacity 0.3s ease;
    opacity: 0;
  `;
  document.body.appendChild(glow);

  let mouseX = 0, mouseY = 0;
  let glowX = 0, glowY = 0;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    glow.style.opacity = '1';
  });

  document.addEventListener('mouseleave', () => {
    glow.style.opacity = '0';
  });

  // Smooth follow animation
  function updateGlow() {
    glowX += (mouseX - glowX) * 0.1;
    glowY += (mouseY - glowY) * 0.1;
    glow.style.left = glowX + 'px';
    glow.style.top = glowY + 'px';
    requestAnimationFrame(updateGlow);
  }
  updateGlow();
}

/**
 * Copy Code with Feedback
 */
document.addEventListener('click', (e) => {
  if (e.target.closest('.md-clipboard')) {
    const button = e.target.closest('.md-clipboard');
    const originalIcon = button.innerHTML;

    button.innerHTML = '<span style="color: #10b981;">✓</span>';
    button.style.transform = 'scale(1.2)';

    setTimeout(() => {
      button.innerHTML = originalIcon;
      button.style.transform = 'scale(1)';
    }, 2000);
  }
});

/**
 * Smooth Scroll Enhancement
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const targetId = this.getAttribute('href');
    if (targetId === '#') return;

    const target = document.querySelector(targetId);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

/**
 * Add Version Badge
 */
function addVersionBadge() {
  if (document.querySelector('.version-badge')) return;

  const badge = document.createElement('a');
  badge.className = 'version-badge';
  badge.href = 'https://github.com/mithun50/blenderforge/releases';
  badge.target = '_blank';
  badge.textContent = 'v1.0.5';
  badge.title = 'View releases on GitHub';
  document.body.appendChild(badge);
}

// Initialize version badge after DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addVersionBadge);
} else {
  addVersionBadge();
}

/**
 * Easter Egg: Konami Code
 */
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
  konamiCode.push(e.key);
  konamiCode = konamiCode.slice(-10);

  if (konamiCode.join(',') === konamiSequence.join(',')) {
    document.body.style.animation = 'rainbow-bg 2s ease';
    setTimeout(() => {
      document.body.style.animation = '';
    }, 2000);
  }
});

// Add rainbow animation style
const rainbowStyle = document.createElement('style');
rainbowStyle.textContent = `
  @keyframes rainbow-bg {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(360deg); }
  }
`;
document.head.appendChild(rainbowStyle);
