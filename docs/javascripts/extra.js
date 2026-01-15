/**
 * BlenderForge Documentation - Professional JavaScript
 * Minimal, accessible, and performance-focused
 */

(function() {
  'use strict';

  // Only initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    addVersionBadge();
    enhanceCopyButtons();
    smoothScrollAnchors();
  }

  /**
   * Add floating version badge
   */
  function addVersionBadge() {
    if (document.querySelector('.version-badge')) return;

    var badge = document.createElement('a');
    badge.className = 'version-badge';
    badge.href = 'https://github.com/mithun50/blenderforge/releases';
    badge.target = '_blank';
    badge.rel = 'noopener noreferrer';
    badge.textContent = 'v1.0.5';
    badge.title = 'View releases on GitHub';
    badge.setAttribute('aria-label', 'BlenderForge version 1.0.5 - View releases');
    document.body.appendChild(badge);
  }

  /**
   * Enhanced copy button feedback
   */
  function enhanceCopyButtons() {
    document.addEventListener('click', function(e) {
      var clipboard = e.target.closest('.md-clipboard');
      if (!clipboard) return;

      // Visual feedback
      clipboard.style.transform = 'scale(1.1)';
      setTimeout(function() {
        clipboard.style.transform = '';
      }, 200);
    });
  }

  /**
   * Smooth scroll for anchor links
   */
  function smoothScrollAnchors() {
    // Respect reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.addEventListener('click', function(e) {
      var anchor = e.target.closest('a[href^="#"]');
      if (!anchor) return;

      var targetId = anchor.getAttribute('href');
      if (targetId === '#') return;

      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        // Update URL without jumping
        history.pushState(null, null, targetId);
      }
    });
  }
})();
