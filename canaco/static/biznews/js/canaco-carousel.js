(function () {
    const carousel = document.querySelector('.canaco-carousel');
    if (!carousel) return;

    const slides = Array.from(carousel.querySelectorAll('.canaco-slide'));
    const indicators = Array.from(carousel.querySelectorAll('.canaco-carousel-indicator'));
    if (slides.length < 2) return;

    let activeIndex = 0;
    let timer = null;

    function showSlide(index) {
        activeIndex = (index + slides.length) % slides.length;
        slides.forEach((slide, slideIndex) => {
            const active = slideIndex === activeIndex;
            slide.hidden = !active;
            slide.classList.toggle('is-active', active);
        });
        indicators.forEach((indicator, indicatorIndex) => {
            const active = indicatorIndex === activeIndex;
            indicator.classList.toggle('is-active', active);
            if (active) indicator.setAttribute('aria-current', 'true');
            else indicator.removeAttribute('aria-current');
        });
    }

    function stopTimer() {
        if (timer) window.clearInterval(timer);
        timer = null;
    }

    function startTimer() {
        stopTimer();
        if (carousel.dataset.autoplay === 'true' && !document.hidden) {
            timer = window.setInterval(() => showSlide(activeIndex + 1), 5000);
        }
    }

    carousel.querySelector('.canaco-carousel-prev')?.addEventListener('click', () => {
        showSlide(activeIndex - 1);
        startTimer();
    });
    carousel.querySelector('.canaco-carousel-next')?.addEventListener('click', () => {
        showSlide(activeIndex + 1);
        startTimer();
    });
    indicators.forEach((indicator) => {
        indicator.addEventListener('click', () => {
            showSlide(Number(indicator.dataset.slideTo));
            startTimer();
        });
    });
    document.addEventListener('visibilitychange', startTimer);
    startTimer();
})();
