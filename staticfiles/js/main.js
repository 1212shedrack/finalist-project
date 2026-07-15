'use strict';

/* 
   1. DARK MODE TOGGLE
 */
(function initDarkMode() {
  const html    = document.documentElement;
  const toggle  = document.getElementById('darkModeToggle');
  const icon    = document.getElementById('darkModeIcon');
  const stored  = localStorage.getItem('theme') || 'light';

  html.setAttribute('data-theme', stored);
  updateIcon(stored);

  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      const next    = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateIcon(next);
    });
  }

  function updateIcon(theme) {
    if (!icon) return;
    icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
  }
})();


/* 
   1b. LANGUAGE SWITCHER DROPDOWN
 */
(function initLangSwitcher() {
  const dropdown = document.getElementById('langDropdown');
  const toggleBtn = document.getElementById('langToggleBtn');
  const menu      = document.getElementById('langMenu');
  if (!dropdown || !toggleBtn || !menu) return;

  toggleBtn.addEventListener('click', e => {
    e.stopPropagation();
    const isOpen = dropdown.classList.toggle('open');
    toggleBtn.setAttribute('aria-expanded', isOpen);
  });

  // Close when clicking outside
  document.addEventListener('click', e => {
    if (!dropdown.contains(e.target)) {
      dropdown.classList.remove('open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      dropdown.classList.remove('open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    }
  });
})();


/* 
   2. NAVBAR SCROLL EFFECT
 */
(function initNavbar() {
  const navbar = document.getElementById('mainNavbar');
  if (!navbar) return;

  const onScroll = () => {
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // run on load

  // Close mobile menu on nav-link click
  document.querySelectorAll('#navbarNav .nav-link').forEach(link => {
    link.addEventListener('click', () => {
      const collapse = document.getElementById('navbarNav');
      if (collapse && collapse.classList.contains('show')) {
        const toggler = document.querySelector('.navbar-toggler');
        if (toggler) toggler.click();
      }
    });
  });
})();


/* 
   3. TOAST NOTIFICATION SYSTEM
 */
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById('toastContainer');
    // Auto-show any server-rendered toasts
    if (this.container) {
      this.container.querySelectorAll('.toast-custom[data-auto-show]').forEach(t => {
        this._show(t);
      });
    }
  },

  show(message, type = 'info') {
    if (!this.container) return;
    const icons = {
      success: 'bi-check-circle-fill',
      error:   'bi-exclamation-triangle-fill',
      danger:  'bi-exclamation-triangle-fill',
      warning: 'bi-exclamation-circle-fill',
      info:    'bi-info-circle-fill',
    };
    const toast = document.createElement('div');
    toast.className = `toast-custom toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <div class="toast-icon"><i class="bi ${icons[type] || icons.info}"></i></div>
      <div class="toast-body-text">${message}</div>
      <button type="button" class="toast-close" aria-label="Close">
        <i class="bi bi-x"></i>
      </button>`;
    this.container.appendChild(toast);
    this._show(toast);
  },

  _show(toast) {
    toast.style.animation = 'slideInRight 0.35s ease forwards';
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) closeBtn.addEventListener('click', () => this._dismiss(toast));
    setTimeout(() => this._dismiss(toast), 5000);
  },

  _dismiss(toast) {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(60px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 320);
  }
};
document.addEventListener('DOMContentLoaded', () => Toast.init());


/* 
   4. IMAGE UPLOAD — DRAG & DROP + PREVIEW + VALIDATION
 */
(function initUpload() {
  const dropZone      = document.getElementById('dropZone');
  const fileInput     = document.getElementById('image-input');
  const previewSection= document.getElementById('previewSection');
  const previewImage  = document.getElementById('previewImage');
  const previewName   = document.getElementById('previewName');
  const previewSize   = document.getElementById('previewSize');
  const submitSection = document.getElementById('submitSection');
  const changeBtn     = document.getElementById('changeImageBtn');
  const uploadForm    = document.getElementById('uploadForm');

  if (!dropZone || !fileInput) return;

  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];
  const MAX_SIZE      = 10 * 1024 * 1024; // 10MB

  // Drag events
  ['dragenter', 'dragover'].forEach(evt => {
    dropZone.addEventListener(evt, e => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });
  });
  ['dragleave', 'dragend', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, e => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
    });
  });
  dropZone.addEventListener('drop', e => {
    const file = e.dataTransfer?.files?.[0];
    if (file) handleFile(file);
  });

  // Click to browse
  dropZone.addEventListener('click', e => {
    if (e.target.closest('.btn-browse') || e.target === fileInput) return;
    fileInput.click();
  });

  // File input change 
  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    if (file) handleFile(file);
  });

  // Change image button
  if (changeBtn) {
    changeBtn.addEventListener('click', () => {
      fileInput.value = '';
      previewSection.style.display = 'none';
      submitSection.style.display  = 'none';
      dropZone.style.display       = 'block';
    });
  }

  // Handle file
  function handleFile(file) {
    // Validate type
    if (!ALLOWED_TYPES.includes(file.type)) {
      Toast.show(`Invalid file type: ${file.type}. Please upload JPG or PNG.`, 'error');
      fileInput.value = '';
      return;
    }
    // Validate size
    if (file.size > MAX_SIZE) {
      Toast.show(`File too large (${formatBytes(file.size)}). Maximum allowed is 10 MB.`, 'error');
      fileInput.value = '';
      return;
    }

    // Set file on input (for drag-drop)
    if (fileInput.files.length === 0) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = e => {
      if (previewImage)  previewImage.src  = e.target.result;
      if (previewName)   previewName.textContent  = file.name;
      if (previewSize)   previewSize.textContent  = formatBytes(file.size);
      if (previewSection) previewSection.style.display = 'block';
      if (submitSection)  submitSection.style.display  = 'block';
      if (dropZone)       dropZone.style.display       = 'none';
      Toast.show('Image ready! Click "Analyze Disease" to proceed.', 'success');
    };
    reader.readAsDataURL(file);
  }

  // Form submit — show loading
  if (uploadForm) {
    uploadForm.addEventListener('submit', e => {
      if (!fileInput.files?.length) {
        e.preventDefault();
        Toast.show('Please select an image first.', 'warning');
        return;
      }
      showLoading();
    });
  }

  function formatBytes(bytes) {
    if (bytes < 1024)             return bytes + ' B';
    if (bytes < 1024 * 1024)     return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  }
})();


/* 
   5. LOADING OVERLAY
 */
function showLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (!overlay) return;

  overlay.style.display = 'flex';
  overlay.style.animation = 'fadeIn 0.3s ease forwards';

  // Animate loading steps
  const steps = ['loadStep1', 'loadStep2', 'loadStep3', 'loadStep4'];
  let current = 0;

  const advance = setInterval(() => {
    if (current < steps.length) {
      const prevEl = current > 0 ? document.getElementById(steps[current - 1]) : null;
      const currEl = document.getElementById(steps[current]);
      if (prevEl) { prevEl.classList.remove('active'); prevEl.classList.add('done'); }
      if (currEl) { currEl.classList.add('active'); }
      current++;
    } else {
      clearInterval(advance);
    }
  }, 700);
}


/* 
   6. ANIMATED PROGRESS BARS (result page)
 */
(function initProgressBars() {
  function animateBars() {
    document.querySelectorAll('[data-width]').forEach(bar => {
      const target = parseFloat(bar.getAttribute('data-width'));
      bar.style.transition = 'width 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
      setTimeout(() => {
        bar.style.width = Math.min(target, 100) + '%';
      }, 300);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', animateBars);
  } else {
    animateBars();
  }
})();


/* 
   7. COUNTER ANIMATION (home page stats)
 */
function animateCounter(el, target) {
  const duration = 1800;
  const start    = performance.now();
  const from     = 0;

  function step(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease     = 1 - Math.pow(1 - progress, 3); // cubic ease-out
    const current  = Math.round(from + (target - from) * ease);
    el.textContent = current.toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// Observe stats for counter animation trigger
document.addEventListener('DOMContentLoaded', () => {
  const statNums = document.querySelectorAll('[data-target]');
  if (!statNums.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.dataset.target, 10);
        animateCounter(entry.target, target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  statNums.forEach(el => observer.observe(el));
});


/* 
   8. SMOOTH SCROLL (for anchor links on home page)
 */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href').slice(1);
      if (!targetId) return;
      const target = document.getElementById(targetId);
      if (!target) return;
      e.preventDefault();
      const navH   = document.getElementById('mainNavbar')?.offsetHeight || 72;
      const top    = target.getBoundingClientRect().top + window.scrollY - navH - 16;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });
});


/* 
   9. HISTORY — DEBOUNCED SEARCH
 */
(function initHistorySearch() {
  const searchInput = document.getElementById('searchInput');
  const searchForm  = document.getElementById('searchForm');
  if (!searchInput || !searchForm) return;

  let timer;
  searchInput.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => searchForm.submit(), 600);
  });
})();


/* 
   10. DELETE CONFIRMATION
 */
function confirmDelete(e) {
  if (!confirm('Are you sure you want to delete this prediction record? This action cannot be undone.')) {
    e.preventDefault();
    return false;
  }
  return true;
}


/* 
   11. CARD ENTRANCE ANIMATIONS (Intersection Observer)
 */
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll(
    '.feature-card, .how-step, .prediction-card, .history-card, .disease-card, .tech-card'
  );

  if (!cards.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity    = '1';
          entry.target.style.transform  = 'translateY(0)';
          entry.target.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        }, i * 60);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  cards.forEach(card => {
    card.style.opacity   = '0';
    card.style.transform = 'translateY(20px)';
    observer.observe(card);
  });
});


/* 
   12. RESULT PAGE — TAB PERSISTENCE
 */
document.addEventListener('DOMContentLoaded', () => {
  const tabLinks = document.querySelectorAll('#recTabs .nav-link');
  if (!tabLinks.length) return;

  const saved = sessionStorage.getItem('activeRecTab');
  if (saved) {
    const tab = document.querySelector(`#recTabs [data-bs-target="${saved}"]`);
    if (tab) tab.click();
  }

  tabLinks.forEach(link => {
    link.addEventListener('shown.bs.tab', e => {
      sessionStorage.setItem('activeRecTab', e.target.dataset.bsTarget);
    });
  });
});


/* 
   13. ACTIVE NAV HIGHLIGHT (mobile)
 */
document.addEventListener('DOMContentLoaded', () => {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-custom .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });
});


/* 
   14. TIPS — LEARN MORE SMOOTH SCROLL
 */
document.addEventListener('DOMContentLoaded', () => {
  const learnMore = document.getElementById('learnMoreBtn');
  if (learnMore) {
    learnMore.addEventListener('click', e => {
      e.preventDefault();
      const target = document.getElementById('features');
      if (target) {
        const navH = 80;
        const top  = target.getBoundingClientRect().top + window.scrollY - navH;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  }
});
