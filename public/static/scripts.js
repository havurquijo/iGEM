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
