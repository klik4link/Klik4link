/* ==========================================
   CLICK2PAY APP
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       LOADING
    ========================= */

    window.addEventListener("load", () => {
        const loading = document.querySelector(".loading-screen");

        setTimeout(() => {
            loading.style.opacity = "0";
            loading.style.visibility = "hidden";

            setTimeout(() => {
                loading.remove();
            }, 600);

        }, 700);
    });


    /* =========================
       SCROLL PROGRESS
    ========================= */

    const progress = document.querySelector(".scroll-progress");

    window.addEventListener("scroll", () => {

        const total =
            document.documentElement.scrollHeight -
            document.documentElement.clientHeight;

        const percent =
            window.scrollY / total * 100;

        progress.style.width = percent + "%";

    });


    /* =========================
       NAVBAR
    ========================= */

    const navbar = document.querySelector(".glass-navbar");

    window.addEventListener("scroll", () => {

        if (window.scrollY > 30) {

            navbar.classList.add("navbar-scrolled");

        } else {

            navbar.classList.remove("navbar-scrolled");

        }

    });


    /* =========================
       COUNTER
    ========================= */

    const counters = document.querySelectorAll(".counter");

    const observer = new IntersectionObserver((entries) => {

        entries.forEach(entry => {

            if (!entry.isIntersecting) return;

            const counter = entry.target;

            const target = +counter.dataset.target;

            let current = 0;

            const speed = target / 100;

            const update = () => {

                current += speed;

                if (current < target) {

                    counter.innerText =
                        Math.floor(current).toLocaleString();

                    requestAnimationFrame(update);

                } else {

                    counter.innerText =
                        target.toLocaleString();

                }

            };

            update();

            observer.unobserve(counter);

        });

    }, {

        threshold: .5

    });

    counters.forEach(counter => observer.observe(counter));


    /* =========================
       SMOOTH SCROLL
    ========================= */

    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.onclick = function (e) {

            const target =
                document.querySelector(this.getAttribute("href"));

            if (!target) return;

            e.preventDefault();

            target.scrollIntoView({

                behavior: "smooth"

            });

        };

    });


    /* =========================
       ACTIVE MENU
    ========================= */

    const sections = document.querySelectorAll("section");

    const navLinks =
        document.querySelectorAll(".navbar .nav-link");

    window.addEventListener("scroll", () => {

        let current = "";

        sections.forEach(sec => {

            const top =
                sec.offsetTop - 120;

            if (scrollY >= top) {

                current = sec.getAttribute("id");

            }

        });

        navLinks.forEach(link => {

            link.classList.remove("active");

            if (link.getAttribute("href") == "#" + current) {

                link.classList.add("active");

            }

        });

    });


    /* =========================
       BACK TO TOP
    ========================= */

    const topBtn =
        document.querySelector(".back-to-top");

    window.addEventListener("scroll", () => {

        if (window.scrollY > 500) {

            topBtn.classList.add("show");

        } else {

            topBtn.classList.remove("show");

        }

    });

    topBtn.onclick = () => {

        window.scrollTo({

            top: 0,

            behavior: "smooth"

        });

    };


    /* =========================
       LIVE USER
    ========================= */

    const live =
        document.getElementById("live-users");

    if (live) {

        let value = 1825;

        setInterval(() => {

            value += Math.floor(Math.random() * 15 - 7);

            if (value < 1700)
                value = 1700;

            if (value > 2100)
                value = 2100;

            live.innerText =
                value.toLocaleString();

        }, 3000);

    }


    /* =========================
       SNOW
    ========================= */

    const snow =
        document.querySelector(".snow-container");

    if (snow) {

        for (let i = 0; i < 60; i++) {

            const span =
                document.createElement("span");

            span.className = "snowflake";

            span.style.left =
                Math.random() * 100 + "%";

            span.style.animationDelay =
                Math.random() * 10 + "s";

            span.style.animationDuration =
                8 + Math.random() * 8 + "s";

            span.style.opacity =
                Math.random();

            snow.appendChild(span);

        }

    }


    /* =========================
       STARS
    ========================= */

    const stars =
        document.querySelector(".stars-container");

    if (stars) {

        for (let i = 0; i < 120; i++) {

            const s =
                document.createElement("span");

            s.className = "star";

            s.style.left =
                Math.random() * 100 + "%";

            s.style.top =
                Math.random() * 100 + "%";

            s.style.animationDelay =
                Math.random() * 5 + "s";

            stars.appendChild(s);

        }

    }


    /* =========================
       HERO PARALLAX
    ========================= */

    const hero =
        document.querySelector(".hero-section");

    window.addEventListener("mousemove", e => {

        if (!hero) return;

        const x =
            (window.innerWidth / 2 - e.clientX) / 50;

        const y =
            (window.innerHeight / 2 - e.clientY) / 50;

        hero.style.backgroundPosition =
            `${x}px ${y}px`;

    });


    /* =========================
       CARD HOVER
    ========================= */

    document.querySelectorAll(
        ".feature-card,.stat-card,.glass-card,.payment-card,.step-card,.security-card"
    ).forEach(card => {

        card.addEventListener("mousemove", e => {

            const rect =
                card.getBoundingClientRect();

            const x =
                e.clientX - rect.left;

            const y =
                e.clientY - rect.top;

            card.style.setProperty("--x", x + "px");

            card.style.setProperty("--y", y + "px");

        });

    });


    /* =========================
       MOBILE NAV CLOSE
    ========================= */

    const navCollapse =
        document.querySelector(".navbar-collapse");

    document.querySelectorAll(".nav-link")
        .forEach(link => {

            link.onclick = () => {

                if (navCollapse.classList.contains("show")) {

                    bootstrap.Collapse.getInstance(navCollapse).hide();

                }

            };

        });


    /* =========================
       BUTTON RIPPLE
    ========================= */

    document.querySelectorAll(".btn").forEach(btn => {

        btn.addEventListener("click", function (e) {

            const circle =
                document.createElement("span");

            circle.className = "ripple";

            const rect =
                this.getBoundingClientRect();

            circle.style.left =
                e.clientX - rect.left + "px";

            circle.style.top =
                e.clientY - rect.top + "px";

            this.appendChild(circle);

            setTimeout(() => {

                circle.remove();

            }, 600);

        });

    });

});
