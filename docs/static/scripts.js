/* Loading management */
// Config: tempo mínimo (ms) que o overlay fica visível antes de iniciar a navegação
const MIN_LOADING_TIME = 1500; // 1.5 segundos
document.addEventListener('DOMContentLoaded', function() {
    // Add loading component to body if it doesn't exist
    if (!document.getElementById('loading-screen')) {
        // Create overlay container
        const overlay = document.createElement('div');
        overlay.id = 'loading-screen';
        overlay.className = 'loading-container';

        const img = document.createElement('img');
        img.src = '/static/loading.apng';
        img.alt = 'Loading...';
        img.className = 'loading-gif';
        // fallback se erro (ex.: APNG não suportado ou arquivo faltando)
        img.addEventListener('error', function handler(){
            img.removeEventListener('error', handler);
            img.src = '/static/loading.gif';
        });
        overlay.appendChild(img);

        // Create style element to keep CSS together
        const style = document.createElement('style');
    style.textContent = '\n.loading-container {\n  position: fixed;\n  top: 0;\n  left: 0;\n  width: 100%;\n  height: 100%;\n  background-color: rgba(255, 255, 255, 0.9);\n  pointer-events: auto;\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  z-index: 9999;\n  display: none;\n}\nbody.loading-active {\n  overflow: hidden !important;\n  touch-action: none !important;\n}\n.loading-gif {\n  width: 400px;\n  height: 400px;\n}\n';

        document.body.appendChild(overlay);
        document.head.appendChild(style);

        // Hide overlay initially
        overlay.style.display = 'none';
    }
});

// Global loading functions
window.showLoading = function() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
    // add class to body to stop scrolling and interactions
    document.body.classList.add('loading-active');
    loadingScreen.style.display = 'flex';
    }
};

window.hideLoading = function() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
    loadingScreen.style.display = 'none';
    document.body.classList.remove('loading-active');
    }
};

// Handle page transitions with loading screen
document.addEventListener('click', function(e) {
    const link = e.target.closest('a');
    if (!link || !link.href || link.target || e.ctrlKey || e.shiftKey) return;

    // Ignore links that are UI toggles (Bootstrap dropdowns/toggles, buttons, anchors without navigation)
    const hrefAttr = link.getAttribute('href') || '';
    if (hrefAttr === '#' || hrefAttr.trim() === '') return;
    if (hrefAttr.startsWith('javascript:')) return;
    if (link.hasAttribute('data-bs-toggle') || link.hasAttribute('data-bs-target') || link.hasAttribute('data-toggle')) return;
    if (link.classList.contains('dropdown-toggle')) return; // only ignore the toggle itself
    if (link.getAttribute('role') === 'button') return;

    // If this is a hash-only link to the same page (anchor), allow default behaviour
    try {
        const targetUrl = new URL(link.href, location.href);
        const isSameOrigin = targetUrl.origin === location.origin;
        const isSamePath = targetUrl.pathname === location.pathname;
        const isSameSearch = targetUrl.search === location.search;
        const isHashOnly = isSameOrigin && isSamePath && isSameSearch && targetUrl.hash && targetUrl.hash !== '';
        if (isHashOnly) return; // let browser handle anchor navigation
    } catch (err) {
        // If URL parsing fails, continue with default behavior below
    }

    e.preventDefault();
    showLoading();

    // safety: if navigation doesn't happen (e.g. blocked), hide overlay after 8s
    const safetyTimer = setTimeout(() => { hideLoading(); }, 8000);

    // Mantém o loader visível por pelo menos MIN_LOADING_TIME antes de navegar
    setTimeout(() => {
        clearTimeout(safetyTimer);
        window.location.href = link.href;
    }, MIN_LOADING_TIME);
});

// Hide loader when the page is being unloaded/hidden so it doesn't stay stuck
['visibilitychange','pagehide','beforeunload','unload'].forEach(ev => {
    window.addEventListener(ev, () => {
        try { hideLoading(); } catch (e) { /* ignore */ }
    }, { passive: true });
});

// Ensure loading screen is hidden when page loads
window.addEventListener('load', function() {
    hideLoading();
});

/* Small helper: staggered reveal on scroll + subtle tilt effect on hover.
	 Designed to work with .member-card-animate and data-delay attr set in the templates.
*/
document.addEventListener('DOMContentLoaded', function () {
	// Reveal on intersection with staggered delays
	const observer = new IntersectionObserver((entries) => {
		entries.forEach(entry => {
			if (entry.isIntersecting) {
				const el = entry.target;
				const delay = parseInt(el.getAttribute('data-delay') || '0', 10);
				el.style.transitionDelay = (delay * 80) + 'ms';
				el.classList.add('revealed');
				observer.unobserve(el);
			}
		});
	}, { threshold: 0.12 });

	document.querySelectorAll('.member-card-animate').forEach(el => observer.observe(el));

	// Simple mouse tilt effect
	function bindTilt(container) {
		const card = container.querySelector('.card');
		const rect = () => card.getBoundingClientRect();
		function onMove(e) {
			const r = rect();
			const x = (e.clientX - r.left) / r.width; // 0..1
			const y = (e.clientY - r.top) / r.height;
			const rotateY = (x - 0.5) * 8; // degrees
			const rotateX = -(y - 0.5) * 6; // degrees
			card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(6px)`;
		}
		function onLeave() {
			card.style.transform = '';
		}
		container.addEventListener('mousemove', onMove);
		container.addEventListener('mouseleave', onLeave);
		// touch: slight scale feedback
		container.addEventListener('touchstart', () => { card.style.transform = 'scale(1.01) translateZ(2px)'; });
		container.addEventListener('touchend', () => { card.style.transform = ''; });
	}

	document.querySelectorAll('[data-tilt]').forEach(bindTilt);
});
