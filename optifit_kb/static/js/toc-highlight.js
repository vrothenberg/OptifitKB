// static/js/toc-highlight.js

document.addEventListener('DOMContentLoaded', function() {
    const headings = document.querySelectorAll('.article-body h2');
    const tocLinks = document.querySelectorAll('.sidebar .toc-item a');
    const headerHeight = document.querySelector('.header-content').offsetHeight;

    function highlightTocLink() {
        let fromTop = window.scrollY;

        // Adjust fromTop to account for the fixed header
        fromTop += headerHeight; 

        // Find the nearest heading
        let nearestHeading = null;
        let minDistance = Infinity;

        for (let i = 0; i < headings.length; i++) {
            const heading = headings[i];
            const distance = Math.abs(heading.offsetTop - fromTop);

            if (distance < minDistance) {
                minDistance = distance;
                nearestHeading = heading;
            }
        }

        // Highlight the corresponding TOC link
        tocLinks.forEach(link => link.classList.remove('active')); // Remove from all

        if (nearestHeading) {
            const section = nearestHeading.id;
            const tocLink = document.querySelector(`.sidebar .toc-item a[href="#${section}"]`);
            if (tocLink) {
                tocLink.classList.add('active');
            }
        }
    }

    window.addEventListener('scroll', highlightTocLink);
    highlightTocLink();
});