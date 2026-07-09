/* =========================================
   CLICK2PAY PREMIUM APP
   PART 1
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================
       LOADING SCREEN
    ========================================= */

    window.addEventListener("load", () => {
        setTimeout(() => {
            document.body.classList.add("loaded");
        }, 500);
    });

    /* =========================================
       ELEMENTS
    ========================================= */

    const progressBar = document.querySelector(".scroll-progress");
    const navbar = document.querySelector(".glass-navbar");
    const backToTop = document.querySelector(".back-to-top");

    /* =========================================
       UPDATE UI ON SCROLL
    ========================================= */

    function updateScrollUI() {

        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;

        /* Progress Bar */

        if (progressBar && docHeight > 0) {
            progressBar.style.width = `${(scrollTop / docHeight) * 100}%`;
        }

        /* Navbar */

        if (navbar) {
            navbar.classList.toggle("scrolled", scrollTop > 50);
        }

        /* Back To Top */

        if (backToTop) {
            backToTop.classList.toggle("show", scrollTop > 400);
        }

    }

    updateScrollUI();
    window.addEventListener("scroll", updateScrollUI, {
        passive: true
    });

    /* =========================================
       BACK TO TOP BUTTON
    ========================================= */

    if (backToTop) {

        backToTop.addEventListener("click", () => {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        });

    }

    /* =========================================
       SMOOTH SCROLL NAVIGATION
    ========================================= */

    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.addEventListener("click", function (e) {

            const targetId = this.getAttribute("href");

            if (targetId === "#") return;

            const target = document.querySelector(targetId);

            if (!target) return;

            e.preventDefault();

            const offset = 80;

            window.scrollTo({
                top: target.offsetTop - offset,
                behavior: "smooth"
            });

            /* Tutup Navbar Mobile */

            const navbarCollapse = document.querySelector(".navbar-collapse");

            if (navbarCollapse && navbarCollapse.classList.contains("show")) {

                const bsCollapse =
                    bootstrap.Collapse.getOrCreateInstance(navbarCollapse);

                bsCollapse.hide();

            }

        });

    });

    /* =========================================
       COUNTER ANIMATION
    ========================================= */

    const counters = document.querySelectorAll("[data-target]");

    const animateCounter = (counter) => {

        const target = Number(counter.dataset.target);

        let current = 0;

        const duration = 2000;

        const increment = target / (duration / 16);

        const update = () => {

            current += increment;

            if (current < target) {

                counter.textContent =
                    Math.floor(current).toLocaleString("id-ID");

                requestAnimationFrame(update);

            } else {

                counter.textContent =
                    target.toLocaleString("id-ID");

            }

        };

        update();

    };

    if (counters.length) {

        const counterObserver = new IntersectionObserver((entries, observer) => {

            entries.forEach(entry => {

                if (!entry.isIntersecting) return;

                animateCounter(entry.target);

                observer.unobserve(entry.target);

            });

        }, {
            threshold: 0.4
        });

        counters.forEach(counter => {

            counterObserver.observe(counter);

        });

    }

    /* =========================================
       ACTIVE NAVIGATION
    ========================================= */

    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");

    function setActiveNav() {

        let current = "";

        sections.forEach(section => {

            const top = section.offsetTop - 120;
            const bottom = top + section.offsetHeight;

            if (window.scrollY >= top &&
                window.scrollY < bottom) {

                current = section.id;

            }

        });

        navLinks.forEach(link => {

            link.classList.toggle(
                "active",
                link.getAttribute("href") === `#${current}`
            );

        });

    }

    setActiveNav();

    window.addEventListener("scroll", setActiveNav, {
        passive: true
    });

});

/* ==========================================
   CLICK2PAY
   PART 2
   SNOW • STARS • LIVE USERS
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       ELEMENTS
    ========================= */

    const snowContainer = document.querySelector(".snow-container");
    const starsContainer = document.querySelector(".stars-container");
    const liveUsers = document.getElementById("live-users");
    const dashboard = document.querySelector(".dashboard-card");
    const animatedBg = document.querySelector(".animated-bg");

    /* =========================
       SNOW EFFECT
    ========================= */

    if (snowContainer) {

        const fragment = document.createDocumentFragment();

        for (let i = 0; i < 60; i++) {

            const snow = document.createElement("span");

            snow.className = "snow";
            snow.style.left = `${Math.random() * 100}%`;
            snow.style.opacity = Math.random();
            snow.style.width = `${Math.random() * 5 + 2}px`;
            snow.style.height = snow.style.width;
            snow.style.animationDuration = `${8 + Math.random() * 12}s`;
            snow.style.animationDelay = `${Math.random() * 10}s`;

            fragment.appendChild(snow);

        }

        snowContainer.appendChild(fragment);

    }

    /* =========================
       STARS
    ========================= */

    if (starsContainer) {

        const fragment = document.createDocumentFragment();

        for (let i = 0; i < 120; i++) {

            const star = document.createElement("span");

            star.className = "star";
            star.style.left = `${Math.random() * 100}%`;
            star.style.top = `${Math.random() * 100}%`;
            star.style.opacity = Math.random();
            star.style.animationDelay = `${Math.random() * 5}s`;
            star.style.animationDuration = `${2 + Math.random() * 4}s`;

            fragment.appendChild(star);

        }

        starsContainer.appendChild(fragment);

    }

    /* =========================
       LIVE USER COUNTER
    ========================= */

    if (liveUsers) {

        let current = 1825;

        setInterval(() => {

            current += Math.floor(Math.random() * 9) - 4;

            if (current < 1750) current = 1760;
            if (current > 1950) current = 1910;

            liveUsers.textContent = current.toLocaleString("id-ID");

        }, 2500);

    }

    /* =========================
       FLOATING DASHBOARD
    ========================= */

    if (dashboard) {

        dashboard.style.animation = "float 5s ease-in-out infinite";

    }

    /* =========================
       HERO PARALLAX
    ========================= */

    if (animatedBg) {

        let mouseX = 0;
        let mouseY = 0;
        let ticking = false;

        window.addEventListener("mousemove", (e) => {

            mouseX = (e.clientX / window.innerWidth - 0.5) * 20;
            mouseY = (e.clientY / window.innerHeight - 0.5) * 20;

            if (!ticking) {

                requestAnimationFrame(() => {

                    animatedBg.style.transform =
                        `translate(${mouseX}px, ${mouseY}px)`;

                    ticking = false;

                });

                ticking = true;

            }

        });

    }

});

/* =========================
   GLOW EFFECT
========================= */

document.querySelectorAll(
    ".feature-card,.stat-card,.security-card,.payment-card"
).forEach(card => {

    card.addEventListener("mouseenter", () => {
        card.classList.add("glow");
    });

    card.addEventListener("mouseleave", () => {
        card.classList.remove("glow");
    });

});

/* =========================
   HERO BADGE PULSE
========================= */

document.querySelectorAll(".hero-badge").forEach(badge => {
    badge.style.animation = "pulse 2.5s infinite";
});

/* =========================
   ICON ROTATE
========================= */

document.querySelectorAll(
    ".feature-icon i,.step-icon i,.stat-icon i"
).forEach(icon => {

    icon.addEventListener("mouseenter", () => {
        icon.style.animation = "rotate .8s linear";
    });

    icon.addEventListener("animationend", () => {
        icon.style.animation = "";
    });

});

/* =========================
   DASHBOARD ITEM HOVER
========================= */

document.querySelectorAll(".dashboard-item").forEach(item => {

    item.addEventListener("mouseenter", () => {
        item.style.transform = "translateY(-5px)";
    });

    item.addEventListener("mouseleave", () => {
        item.style.transform = "";
    });

});

/* =========================
   PAYMENT CARD EFFECT
========================= */

document.querySelectorAll(".payment-card").forEach(card => {

    card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-8px) scale(1.03)";
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "";
    });

});

/* =========================
   CTA BUTTON SHADOW
========================= */

document.querySelectorAll("#cta .btn").forEach(btn => {

    btn.addEventListener("mouseenter", () => {
        btn.style.boxShadow = "0 12px 30px rgba(30,136,255,.35)";
    });

    btn.addEventListener("mouseleave", () => {
        btn.style.boxShadow = "";
    });

});

});

/* =========================
   GLOW EFFECT
========================= */

document.querySelectorAll(
    ".feature-card,.stat-card,.payment-card,.security-card,.glass-card,.step-card"
).forEach(card => {

    card.addEventListener("mouseenter", () => {
        card.classList.add("glow");
    });

    card.addEventListener("mouseleave", () => {
        card.classList.remove("glow");
    });

});

/* =========================
   HERO BADGE PULSE
========================= */

document.querySelectorAll(".hero-badge").forEach(badge => {
    badge.style.animation = "pulse 2.5s infinite";
});

/* =========================
   ICON ROTATE
========================= */

document.querySelectorAll(
    ".feature-icon i,.step-icon i,.stat-icon i"
).forEach(icon => {

    icon.addEventListener("mouseenter", () => {
        icon.style.animation = "rotate .8s linear";
    });

    icon.addEventListener("animationend", () => {
        icon.style.animation = "";
    });

});

});

/* ==========================================
   CLICK2PAY
   PART 4
   FINAL
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       HERO TITLE ANIMATION
    ========================= */

    const heroTitle = document.querySelector(".hero-title");

    if (heroTitle) {
        heroTitle.classList.add("hero-show");
    }

    /* =========================
       REVEAL ANIMATION
    ========================= */

    const observer = new IntersectionObserver((entries) => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
                observer.unobserve(entry.target);
            }

        });

    }, {
        threshold: 0.15
    });

    document.querySelectorAll(
        ".feature-card,.stat-card,.glass-card,.payment-card,.security-card,.step-card,.dashboard-card"
    ).forEach(el => {

        el.style.opacity = "0";
        el.style.transform = "translateY(40px)";
        el.style.transition = "all .7s ease";

        observer.observe(el);

    });

    /* =========================
       RANDOM BALANCE
    ========================= */

    const balance = document.querySelector(".dashboard-item h3.text-primary");

    if (balance) {

        let value = 12580000;

        setInterval(() => {

            value += Math.floor(Math.random() * 5000);

            balance.textContent =
                "Rp " + value.toLocaleString("id-ID");

        }, 4000);

    }

    /* =========================
       RANDOM TODAY EARNING
    ========================= */

    const earning = document.querySelector(".dashboard-item h3.text-success");

    if (earning) {

        let income = 785000;

        setInterval(() => {

            income += Math.floor(Math.random() * 1200);

            earning.textContent =
                "+ Rp " + income.toLocaleString("id-ID");

        }, 2500);

    }

    /* =========================
       PAGE SHOW
    ========================= */

    window.addEventListener("pageshow", () => {
        document.body.classList.add("loaded");
    });

    console.log(
        "%cClick2Pay Loaded Successfully",
        "color:#1e88ff;font-size:16px;font-weight:bold;"
    );

});
