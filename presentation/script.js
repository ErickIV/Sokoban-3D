document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const currentSlideSpan = document.getElementById('currentSlide');
    const totalSlidesSpan = document.getElementById('totalSlides');
    const progressBar = document.getElementById('progressBar');

    let currentSlideIndex = 0;
    const totalSlides = slides.length;

    // Set total slides count dynamically
    if (totalSlidesSpan) {
        totalSlidesSpan.textContent = totalSlides;
    }

    // Navigation functions
    function goToSlide(index, updateHash = true) {
        if (index >= 0 && index < totalSlides) {
            slides[currentSlideIndex].classList.remove('active');
            currentSlideIndex = index;
            slides[currentSlideIndex].classList.add('active');
            updateUI();
            if (updateHash) {
                // Use replaceState to avoid cluttering browser history for normal navigation
                history.replaceState({ slide: index }, `Slide ${index + 1}`, `#slide=${index + 1}`);
            }
        }
    }

    function nextSlide() {
        if (currentSlideIndex < totalSlides - 1) {
            goToSlide(currentSlideIndex + 1);
        }
    }

    function prevSlide() {
        if (currentSlideIndex > 0) {
            goToSlide(currentSlideIndex - 1);
        }
    }

    function updateUI() {
        // Update counter
        currentSlideSpan.textContent = currentSlideIndex + 1;

        // Update progress bar
        const progress = ((currentSlideIndex + 1) / totalSlides) * 100;
        progressBar.style.width = `${progress}%`;

        // Button states
        prevBtn.style.opacity = currentSlideIndex === 0 ? '0.5' : '1';
        nextBtn.style.opacity = currentSlideIndex === totalSlides - 1 ? '0.5' : '1';
        prevBtn.style.cursor = currentSlideIndex === 0 ? 'default' : 'pointer';
        nextBtn.style.cursor = currentSlideIndex === totalSlides - 1 ? 'default' : 'pointer';
    }

    function handleHashChange() {
        const hash = window.location.hash;
        let slideNumber = parseInt(hash.replace('#slide=', ''), 10);
        if (!isNaN(slideNumber) && slideNumber > 0 && slideNumber <= totalSlides) {
            // Do not update hash again as we are responding to a hash change
            goToSlide(slideNumber - 1, false);
        } else {
            goToSlide(0, true);
        }
    }

    // --- INITIALIZATION ---

    // Set total slides number
    totalSlidesSpan.textContent = totalSlides;

    // Set initial slide based on hash
    handleHashChange();

    // --- EVENT LISTENERS ---

    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    // Listen for hash changes (browser back/forward buttons)
    window.addEventListener('hashchange', handleHashChange);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === 'Space' || e.key === 'Enter') {
            e.preventDefault(); // Prevent space from scrolling the page
            nextSlide();
        } else if (e.key === 'ArrowLeft') {
            prevSlide();
        }
    });

    // Optional: Mouse wheel navigation (debounced)
    let isScrolling = false;
    document.addEventListener('wheel', (e) => {
        if (isScrolling) return;

        if (e.deltaY > 0) {
            nextSlide();
        } else if (e.deltaY < 0) {
            prevSlide();
        }

        isScrolling = true;
        setTimeout(() => {
            isScrolling = false;
        }, 800); // 800ms delay between scrolls
    });
});
