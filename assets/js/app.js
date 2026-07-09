/* =========================================
   CLICK2PAY PREMIUM APP
   PART 1
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================
       LOADING SCREEN
    ========================================= */

    setTimeout(() => {
        document.body.classList.add("loaded");
    }, 600);

    /* =========================================
       SCROLL PROGRESS BAR
    ========================================= */

    const progressBar = document.querySelector(".scroll-progress");

    window.addEventListener("scroll", () => {

        const scrollTop = window.scrollY;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        const progress = (scrollTop / docHeight) * 100;

        if(progressBar){
            progressBar.style.width = progress + "%";
        }

    });

    /* =========================================
       NAVBAR SCROLL EFFECT
    ========================================= */

    const navbar = document.querySelector(".glass-navbar");

    function updateNavbar(){
        if(window.scrollY > 50){
            navbar.classList.add("scrolled");
        }else{
            navbar.classList.remove("scrolled");
        }
    }

    updateNavbar();
    window.addEventListener("scroll", updateNavbar);

    /* =========================================
       BACK TO TOP
    ========================================= */

    const backToTop = document.querySelector(".back-to-top");

    function toggleBackToTop(){
        if(window.scrollY > 400){
            backToTop.classList.add("show");
        }else{
            backToTop.classList.remove("show");
        }
    }

    toggleBackToTop();
    window.addEventListener("scroll", toggleBackToTop);

    if(backToTop){
        backToTop.addEventListener("click", () => {
            window.scrollTo({
                top:0,
                behavior:"smooth"
            });
        });
    }

    /* =========================================
       SMOOTH SCROLL NAVIGATION
    ========================================= */

    document.querySelectorAll("a[href^='#']").forEach(link => {

        link.addEventListener("click", function(e){

            const targetId = this.getAttribute("href");
            const target = document.querySelector(targetId);

            if(target){
                e.preventDefault();

                const offset = 80;
                const top = target.offsetTop - offset;

                window.scrollTo({
                    top:top,
                    behavior:"smooth"
                });

                // tutup navbar mobile
                const navbarCollapse = document.querySelector(".navbar-collapse");
                if(navbarCollapse.classList.contains("show")){
                    bootstrap.Collapse.getInstance(navbarCollapse).hide();
                }
            }
        });
    });

    /* =========================================
       COUNTER ANIMATION
    ========================================= */

    const counters = document.querySelectorAll(".counter");

    const animateCounter = (counter) => {

        const target = +counter.getAttribute("data-target");
        const duration = 2000;
        const step = target / (duration / 16);

        let current = 0;

        const update = () => {

            current += step;

            if(current < target){
                counter.textContent = Math.floor(current).toLocaleString("id-ID");
                requestAnimationFrame(update);
            }else{
                counter.textContent = target.toLocaleString("id-ID");
            }
        };

        update();
    };

    const counterObserver = new IntersectionObserver((entries, observer) => {

        entries.forEach(entry => {
            if(entry.isIntersecting){
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });

    }, { threshold:0.4 });

    counters.forEach(counter => {
        counterObserver.observe(counter);
    });

    /* =========================================
       ACTIVE NAV LINK ON SCROLL
    ========================================= */

    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");

    function setActiveNav(){

        let current = "";

        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            const sectionHeight = section.offsetHeight;

            if(window.scrollY >= sectionTop &&
               window.scrollY < sectionTop + sectionHeight){
                current = section.getAttribute("id");
            }
        });

        navLinks.forEach(link => {
            link.classList.remove("active");

            if(link.getAttribute("href") === `#${current}`){
                link.classList.add("active");
            }
        });
    }

    setActiveNav();
    window.addEventListener("scroll", setActiveNav);

});

/* ==========================================
   CLICK2PAY
   PART 2
   SNOW + STARS + LIVE USERS
========================================== */

document.addEventListener("DOMContentLoaded",()=>{

/* =========================
   SNOW EFFECT
========================= */

const snowContainer=document.querySelector(".snow-container");

if(snowContainer){

for(let i=0;i<60;i++){

const snow=document.createElement("span");

snow.className="snow";

snow.style.left=Math.random()*100+"%";

snow.style.opacity=Math.random();

snow.style.width=(Math.random()*5+2)+"px";

snow.style.height=snow.style.width;

snow.style.animationDuration=
(8+Math.random()*12)+"s";

snow.style.animationDelay=
Math.random()*10+"s";

snowContainer.appendChild(snow);

}

}

/* =========================
   STARS
========================= */

const stars=document.querySelector(".stars-container");

if(stars){

for(let i=0;i<120;i++){

const star=document.createElement("span");

star.className="star";

star.style.left=Math.random()*100+"%";

star.style.top=Math.random()*100+"%";

star.style.opacity=Math.random();

star.style.animationDelay=
Math.random()*5+"s";

star.style.animationDuration=
(2+Math.random()*4)+"s";

stars.appendChild(star);

}

}

/* =========================
   LIVE USER COUNTER
========================= */

const live=document.getElementById("live-users");

if(live){

let current=1825;

setInterval(()=>{

const random=Math.floor(Math.random()*9)-4;

current+=random;

if(current<1750){

current=1760;

}

if(current>1950){

current=1910;

}

live.textContent=current.toLocaleString("id-ID");

},2500);

}

/* =========================
   FLOATING DASHBOARD
========================= */

const dashboard=document.querySelector(".dashboard-card");

if(dashboard){

dashboard.style.animation="float 5s ease-in-out infinite";

}

/* =========================
   HERO PARALLAX
========================= */

window.addEventListener("mousemove",(e)=>{

const bg=document.querySelector(".animated-bg");

if(!bg)return;

const x=(e.clientX/window.innerWidth-.5)*20;

const y=(e.clientY/window.innerHeight-.5)*20;

bg.style.transform=
`translate(${x}px,${y}px)`;

});

});

/* ==========================================
   CLICK2PAY
   PART 3
   BUTTONS • CARDS • EFFECTS
========================================== */

document.addEventListener("DOMContentLoaded",()=>{

/* =========================
   RIPPLE BUTTON
========================= */

document.querySelectorAll(".btn").forEach(btn=>{

btn.addEventListener("click",function(e){

const ripple=document.createElement("span");

const rect=this.getBoundingClientRect();

const size=Math.max(rect.width,rect.height);

ripple.style.width=size+"px";
ripple.style.height=size+"px";

ripple.style.left=
e.clientX-rect.left-size/2+"px";

ripple.style.top=
e.clientY-rect.top-size/2+"px";

ripple.style.position="absolute";
ripple.style.borderRadius="50%";
ripple.style.background="rgba(255,255,255,.35)";
ripple.style.transform="scale(0)";
ripple.style.pointerEvents="none";
ripple.style.animation="ripple .6s linear";

this.style.position="relative";
this.style.overflow="hidden";

this.appendChild(ripple);

setTimeout(()=>ripple.remove(),600);

});

});

/* =========================
   CARD HOVER TILT
========================= */

document.querySelectorAll(

".feature-card,.stat-card,.step-card,.payment-card,.security-card,.glass-card"

).forEach(card=>{

card.addEventListener("mousemove",e=>{

const rect=card.getBoundingClientRect();

const x=e.clientX-rect.left;

const y=e.clientY-rect.top;

const rotateY=(x/rect.width-.5)*10;

const rotateX=(.5-y/rect.height)*10;

card.style.transform=

`perspective(900px)
rotateX(${rotateX}deg)
rotateY(${rotateY}deg)
translateY(-8px)`;

});

card.addEventListener("mouseleave",()=>{

card.style.transform="";

});

});

/* =========================
   GLOW EFFECT
========================= */

document.querySelectorAll(

".feature-card,.stat-card"

).forEach(card=>{

card.addEventListener("mouseenter",()=>{

card.classList.add("glow");

});

card.addEventListener("mouseleave",()=>{

card.classList.remove("glow");

});

});

/* =========================
   HERO BADGE PULSE
========================= */

document.querySelectorAll(".hero-badge")

.forEach(el=>{

el.style.animation=

"pulse 2.5s infinite";

});

/* =========================
   ICON ROTATE
========================= */

document.querySelectorAll(

".feature-icon i"

).forEach(icon=>{

icon.addEventListener("mouseenter",()=>{

icon.style.animation=

"rotate .8s linear";

});

icon.addEventListener("mouseleave",()=>{

icon.style.animation="";

});

});

});

/* ==========================================
   CLICK2PAY
   PART 4
   FINAL
========================================== */

document.addEventListener("DOMContentLoaded",()=>{

/* =========================
   TYPING EFFECT
========================= */

const typing=document.querySelector(".hero-title");

if(typing){

const text=typing.innerHTML;

typing.innerHTML="";

let i=0;

const speed=18;

(function write(){

if(i<text.length){

typing.innerHTML+=text.charAt(i);

i++;

setTimeout(write,speed);

}

})();

}

/* =========================
   REVEAL ANIMATION
========================= */

const observer=new IntersectionObserver(entries=>{

entries.forEach(entry=>{

if(entry.isIntersecting){

entry.target.style.opacity="1";

entry.target.style.transform="translateY(0)";

}

});

},{
threshold:.15
});

document.querySelectorAll(

".feature-card,.stat-card,.glass-card,.payment-card,.security-card,.step-card"

).forEach(el=>{

el.style.opacity="0";

el.style.transform="translateY(40px)";

el.style.transition="all .7s ease";

observer.observe(el);

});

/* =========================
   RANDOM DASHBOARD VALUE
========================= */

const balance=document.querySelector(".dashboard-item h3.text-primary");

if(balance){

let value=12580000;

setInterval(()=>{

value+=Math.floor(Math.random()*5000);

balance.textContent=

"Rp "+value.toLocaleString("id-ID");

},4000);

}

/* =========================
   RANDOM TODAY EARNING
========================= */

const earn=document.querySelector(".dashboard-item h3.text-success");

if(earn){

let income=785000;

setInterval(()=>{

income+=Math.floor(Math.random()*1200);

earn.textContent=

"+ Rp "+income.toLocaleString("id-ID");

},2500);

}

/* =========================
   SCROLL ACTIVE NAV
========================= */

const sections=document.querySelectorAll("section");

const navLinks=document.querySelectorAll(".nav-link");

window.addEventListener("scroll",()=>{

let current="";

sections.forEach(sec=>{

const top=window.scrollY;

const offset=sec.offsetTop-180;

const height=sec.offsetHeight;

if(top>=offset && top<offset+height){

current=sec.id;

}

});

navLinks.forEach(link=>{

link.classList.remove("active");

if(link.getAttribute("href")==="#"+current){

link.classList.add("active");

}

});

});

/* =========================
   BACK TO TOP
========================= */

const topBtn=document.querySelector(".back-to-top");

if(topBtn){

topBtn.onclick=()=>{

window.scrollTo({

top:0,

behavior:"smooth"

});

};

}

/* =========================
   SCROLL PROGRESS
========================= */

const progress=document.querySelector(".scroll-progress");

window.addEventListener("scroll",()=>{

const total=

document.documentElement.scrollHeight-

window.innerHeight;

const percent=

(window.scrollY/total)*100;

if(progress){

progress.style.width=percent+"%";

}

});

/* =========================
   LOADING SCREEN
========================= */

window.addEventListener("load",()=>{

setTimeout(()=>{

document.body.classList.add("loaded");

},500);

});

/* =========================
   PERFORMANCE
========================= */

window.addEventListener("pageshow",()=>{

document.body.classList.add("loaded");

});

console.log(

"%cClick2Pay Loaded",

"color:#1e88ff;font-size:18px;font-weight:bold;"

);

});
