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
    handleAddonDownload();
  }

  /**
   * Force download for addon.py link
   */
  function handleAddonDownload() {
    document.addEventListener('click', function(e) {
      var link = e.target.closest('a[href*="addon.py"]');
      if (!link) return;

      e.preventDefault();

      var url = 'https://raw.githubusercontent.com/mithun50/Blender-Forge/main/addon.py';

      fetch(url)
        .then(function(response) {
          return response.blob();
        })
        .then(function(blob) {
          var downloadUrl = window.URL.createObjectURL(blob);
          var a = document.createElement('a');
          a.href = downloadUrl;
          a.download = 'addon.py';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(downloadUrl);
        })
        .catch(function(err) {
          // Fallback: open in new tab
          window.open(url, '_blank');
        });
    });
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
