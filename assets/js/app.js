/* =========================================
   CLICK2PAY PREMIUM APP
   PART 1
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================
       LOADING SCREEN
    ========================================= */

    window.addEventListener("load", () => {
        setTimeout(() => document.body.classList.add("loaded"), 500);
    });

    /* =========================================
       ELEMENTS
    ========================================= */

    const progressBar = document.querySelector(".scroll-progress");
    const navbar = document.querySelector(".glass-navbar");
    const backToTop = document.querySelector(".back-to-top");

    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");

    /* =========================================
       SCROLL UI
    ========================================= */

    function updateScrollUI() {

        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;

        if (progressBar && docHeight > 0) {
            progressBar.style.width =
                `${(scrollTop / docHeight) * 100}%`;
        }

        navbar?.classList.toggle("scrolled", scrollTop > 50);
        backToTop?.classList.toggle("show", scrollTop > 400);

        let current = "";

        sections.forEach(section => {

            const top = section.offsetTop - 120;
            const bottom = top + section.offsetHeight;

            if (scrollTop >= top && scrollTop < bottom) {
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

    updateScrollUI();

    window.addEventListener("scroll", updateScrollUI, {
        passive: true
    });

    /* =========================================
       BACK TO TOP
    ========================================= */

    backToTop?.addEventListener("click", () => {

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    });

    /* =========================================
       SMOOTH SCROLL
    ========================================= */

    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.addEventListener("click", e => {

            const target = document.querySelector(link.getAttribute("href"));

            if (!target) return;

            e.preventDefault();

            window.scrollTo({
                top: target.offsetTop - 80,
                behavior: "smooth"
            });

            const collapse =
                document.querySelector(".navbar-collapse");

            if (collapse?.classList.contains("show")) {

                bootstrap.Collapse
                    .getOrCreateInstance(collapse)
                    .hide();

            }

        });

    });

    /* =========================================
       COUNTER
    ========================================= */

    const counters = document.querySelectorAll("[data-target]");

    const animateCounter = counter => {

        const target = Number(counter.dataset.target);

        let value = 0;

        const speed = target / 120;

        function update() {

            value += speed;

            if (value < target) {

                counter.textContent =
                    Math.floor(value).toLocaleString("id-ID");

                requestAnimationFrame(update);

            } else {

                counter.textContent =
                    target.toLocaleString("id-ID");

            }

        }

        update();

    };

    if (counters.length) {

        const observer = new IntersectionObserver(entries => {

            entries.forEach(entry => {

                if (!entry.isIntersecting) return;

                animateCounter(entry.target);

                observer.unobserve(entry.target);

            });

        }, {
            threshold: .4
        });

        counters.forEach(counter =>
            observer.observe(counter)
        );

    }

});

/* =========================================
   CLICK2PAY PREMIUM APP
   PART 2
   SNOW • STARS • LIVE USERS
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    const snowContainer = document.querySelector(".snow-container");
    const starsContainer = document.querySelector(".stars-container");
    const liveUsers = document.getElementById("live-users");
    const dashboard = document.querySelector(".dashboard-card");
    const animatedBg = document.querySelector(".animated-bg");

    /* =========================================
       CREATE PARTICLES
    ========================================= */

    function createParticles(container, total, className, callback) {

        if (!container) return;

        const fragment = document.createDocumentFragment();

        for (let i = 0; i < total; i++) {

            const item = document.createElement("span");

            item.className = className;

            callback(item);

            fragment.appendChild(item);

        }

        container.appendChild(fragment);

    }

    /* =========================================
       SNOW
    ========================================= */

    createParticles(snowContainer, 60, "snow", snow => {

        const size = Math.random() * 5 + 2;

        snow.style.left = `${Math.random() * 100}%`;
        snow.style.width = `${size}px`;
        snow.style.height = `${size}px`;
        snow.style.opacity = Math.random();

        snow.style.animationDuration =
            `${8 + Math.random() * 12}s`;

        snow.style.animationDelay =
            `${Math.random() * 10}s`;

    });

    /* =========================================
       STARS
    ========================================= */

    createParticles(starsContainer, 120, "star", star => {

        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;

        star.style.opacity = Math.random();

        star.style.animationDuration =
            `${2 + Math.random() * 4}s`;

        star.style.animationDelay =
            `${Math.random() * 5}s`;

    });

    /* =========================================
       LIVE USERS
    ========================================= */

    if (liveUsers) {

        let users = 1825;

        const updateUsers = () => {

            users += Math.floor(Math.random() * 9) - 4;

            users = Math.min(1910, Math.max(1760, users));

            liveUsers.textContent =
                users.toLocaleString("id-ID");

        };

        updateUsers();

        setInterval(updateUsers, 2500);

    }

    /* =========================================
       FLOATING DASHBOARD
    ========================================= */

    if (dashboard) {

        dashboard.style.animation =
            "float 5s ease-in-out infinite";

    }

    /* =========================================
       HERO PARALLAX
    ========================================= */

    if (animatedBg) {

        let mouseX = 0;
        let mouseY = 0;
        let ticking = false;

        const updateParallax = () => {

            animatedBg.style.transform =
                `translate(${mouseX}px, ${mouseY}px)`;

            ticking = false;

        };

        window.addEventListener("mousemove", e => {

            mouseX =
                (e.clientX / window.innerWidth - 0.5) * 20;

            mouseY =
                (e.clientY / window.innerHeight - 0.5) * 20;

            if (!ticking) {

                requestAnimationFrame(updateParallax);

                ticking = true;

            }

        });

    }

});

/* =========================================
   CLICK2PAY PREMIUM APP
   PART 3
   UI EFFECTS
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================
       GLOW CARD
    ========================================= */

    const glowCards = document.querySelectorAll(
        ".feature-card,.stat-card,.payment-card,.security-card,.glass-card,.step-card"
    );

    glowCards.forEach(card => {

        card.addEventListener("mouseenter", () => {
            card.classList.add("glow");
        });

        card.addEventListener("mouseleave", () => {
            card.classList.remove("glow");
        });

    });

    /* =========================================
       HERO BADGE
    ========================================= */

    document.querySelectorAll(".hero-badge").forEach(badge => {
        badge.style.animation = "pulse 2.5s infinite";
    });

    /* =========================================
       ICON ROTATE
    ========================================= */

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

    /* =========================================
       DASHBOARD ITEM
    ========================================= */

    document.querySelectorAll(".dashboard-item").forEach(item => {

        item.addEventListener("mouseenter", () => {
            item.style.transform = "translateY(-5px)";
        });

        item.addEventListener("mouseleave", () => {
            item.style.transform = "";
        });

    });

    /* =========================================
       PAYMENT CARD
    ========================================= */

    document.querySelectorAll(".payment-card").forEach(card => {

        card.addEventListener("mouseenter", () => {
            card.style.transform =
                "translateY(-8px) scale(1.03)";
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });

    });

    /* =========================================
       CTA BUTTON
    ========================================= */

    document.querySelectorAll("#cta .btn").forEach(btn => {

        btn.addEventListener("mouseenter", () => {

            btn.style.boxShadow =
                "0 12px 30px rgba(30,136,255,.35)";

        });

        btn.addEventListener("mouseleave", () => {

            btn.style.boxShadow = "";

        });

    });

});

/* =========================================
   CLICK2PAY PREMIUM APP
   PART 4
   FINAL
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================
       HERO TITLE
    ========================================= */

    document.querySelector(".hero-title")
        ?.classList.add("hero-show");

    /* =========================================
       REVEAL ANIMATION
    ========================================= */

    const revealItems = document.querySelectorAll(
        ".feature-card,.stat-card,.glass-card,.payment-card,.security-card,.step-card,.dashboard-card"
    );

    const revealObserver = new IntersectionObserver((entries, observer) => {

        entries.forEach(entry => {

            if (!entry.isIntersecting) return;

            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";

            observer.unobserve(entry.target);

        });

    }, {
        threshold: 0.15
    });

    revealItems.forEach(item => {

        item.style.opacity = "0";
        item.style.transform = "translateY(40px)";
        item.style.transition = "all .7s ease";

        revealObserver.observe(item);

    });

    /* =========================================
       DASHBOARD BALANCE
    ========================================= */

    const balance =
        document.querySelector(".dashboard-item h3.text-primary");

    if (balance) {

        let value = 12580000;

        setInterval(() => {

            value += Math.floor(Math.random() * 5000);

            balance.textContent =
                `Rp ${value.toLocaleString("id-ID")}`;

        }, 4000);

    }

    /* =========================================
       TODAY EARNING
    ========================================= */

    const earning =
        document.querySelector(".dashboard-item h3.text-success");

    if (earning) {

        let income = 785000;

        setInterval(() => {

            income += Math.floor(Math.random() * 1200);

            earning.textContent =
                `+ Rp ${income.toLocaleString("id-ID")}`;

        }, 2500);

    }

    /* =========================================
       PAGE SHOW
    ========================================= */

    window.addEventListener("pageshow", () => {
        document.body.classList.add("loaded");
    });

    /* =========================================
       CONSOLE LOG
    ========================================= */

    console.log(
        "%cClick2Pay Loaded Successfully",
        "color:#1e88ff;font-size:16px;font-weight:bold;"
    );

});
