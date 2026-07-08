/* =========================================================
   CLICK2PAY
   PREMIUM JAVASCRIPT
========================================================= */

"use strict";

/* =========================================================
   DOM READY
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    document.body.classList.add("loaded");

    initNavbar();

    initSmoothScroll();

    initReveal();

    initCounter();

    initRipple();

    initParallax();

});



/* =========================================================
   NAVBAR SCROLL
========================================================= */

function initNavbar(){

    const navbar=document.querySelector(".glass-navbar");

    if(!navbar) return;

    const updateNavbar=()=>{

        if(window.scrollY>50){

            navbar.classList.add("scrolled");

        }else{

            navbar.classList.remove("scrolled");

        }

    };

    updateNavbar();

    window.addEventListener("scroll",updateNavbar,{
        passive:true
    });

}



/* =========================================================
   SMOOTH SCROLL
========================================================= */

function initSmoothScroll(){

    document
    .querySelectorAll('a[href^="#"]')
    .forEach(link=>{

        link.addEventListener("click",e=>{

            const id=link.getAttribute("href");

            if(id==="#" || id.length<2) return;

            const target=document.querySelector(id);

            if(!target) return;

            e.preventDefault();

            target.scrollIntoView({

                behavior:"smooth",

                block:"start"

            });

        });

    });

}



/* =========================================================
   REVEAL ANIMATION
========================================================= */

function initReveal(){

    const items=document.querySelectorAll(".reveal");

    if(!items.length) return;

    const observer=new IntersectionObserver(entries=>{

        entries.forEach(entry=>{

            if(entry.isIntersecting){

                entry.target.classList.add("show");

            }

        });

    },{

        threshold:.15

    });

    items.forEach(item=>observer.observe(item));

}



/* =========================================================
   COUNTER ANIMATION
========================================================= */

function initCounter(){

    const counters=document.querySelectorAll("[data-count]");

    if(!counters.length) return;

    const observer=new IntersectionObserver(entries=>{

        entries.forEach(entry=>{

            if(!entry.isIntersecting) return;

            animateCounter(entry.target);

            observer.unobserve(entry.target);

        });

    },{

        threshold:.5

    });

    counters.forEach(counter=>observer.observe(counter));

}



function animateCounter(element){

    const target=parseInt(

        element.dataset.count

    );

    if(isNaN(target)) return;

    const duration=1800;

    const start=0;

    const startTime=performance.now();

    function update(now){

        const progress=Math.min(

            (now-startTime)/duration,

            1

        );

        const value=Math.floor(

            progress*(target-start)+start

        );

        element.textContent=value.toLocaleString();

        if(progress<1){

            requestAnimationFrame(update);

        }

    }

    requestAnimationFrame(update);

}



/* =========================================================
   RIPPLE EFFECT
========================================================= */

function initRipple(){

    document.querySelectorAll(".btn").forEach(btn=>{

        btn.addEventListener("click",function(e){

            const circle=document.createElement("span");

            const size=Math.max(

                this.offsetWidth,

                this.offsetHeight

            );

            const rect=this.getBoundingClientRect();

            circle.style.width=size+"px";

            circle.style.height=size+"px";

            circle.style.left=(

                e.clientX-rect.left-size/2

            )+"px";

            circle.style.top=(

                e.clientY-rect.top-size/2

            )+"px";

            circle.className="ripple";

            this.appendChild(circle);

            setTimeout(()=>{

                circle.remove();

            },600);

        });

    });

}
/* =========================================================
   BACK TO TOP
========================================================= */

function initBackToTop(){

    const button=document.querySelector(".back-to-top");

    if(!button) return;

    const toggleButton=()=>{

        if(window.scrollY>400){

            button.classList.add("show");

        }else{

            button.classList.remove("show");

        }

    };

    toggleButton();

    window.addEventListener("scroll",toggleButton,{
        passive:true
    });

    button.addEventListener("click",()=>{

        window.scrollTo({

            top:0,

            behavior:"smooth"

        });

    });

}



/* =========================================================
   TYPING EFFECT
========================================================= */

function initTyping(){

    const element=document.querySelector("[data-typing]");

    if(!element) return;

    const text=element.dataset.typing;

    let index=0;

    element.textContent="";

    function type(){

        if(index<text.length){

            element.textContent+=text.charAt(index);

            index++;

            setTimeout(type,40);

        }

    }

    type();

}



/* =========================================================
   LIVE COUNTER
========================================================= */

function initLiveCounter(){

    document.querySelectorAll("[data-live]").forEach(item=>{

        let value=parseInt(item.dataset.live)||0;

        item.textContent=value.toLocaleString();

        setInterval(()=>{

            value+=Math.floor(Math.random()*3);

            item.textContent=value.toLocaleString();

        },5000);

    });

}



/* =========================================================
   LOADING SCREEN
========================================================= */

function initLoading(){

    const loader=document.querySelector(".loading-screen");

    if(!loader) return;

    window.addEventListener("load",()=>{

        loader.classList.add("hide");

        setTimeout(()=>{

            loader.remove();

        },700);

    });

}



/* =========================================================
   SCROLL PROGRESS BAR
========================================================= */

function initScrollProgress(){

    const bar=document.querySelector(".scroll-progress");

    if(!bar) return;

    const update=()=>{

        const height=

            document.documentElement.scrollHeight-

            window.innerHeight;

        const progress=

            (window.scrollY/height)*100;

        bar.style.width=progress+"%";

    };

    update();

    window.addEventListener("scroll",update,{
        passive:true
    });

}



/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener("DOMContentLoaded",()=>{

    initBackToTop();

    initTyping();

    initLiveCounter();

    initLoading();

    initScrollProgress();

});
/* =========================================================
   PARALLAX EFFECT
========================================================= */

function initParallax(){

    const items=document.querySelectorAll(".parallax");

    if(!items.length) return;

    window.addEventListener("mousemove",(e)=>{

        const x=(e.clientX/window.innerWidth-.5)*20;
        const y=(e.clientY/window.innerHeight-.5)*20;

        items.forEach(item=>{

            const speed=item.dataset.speed||1;

            item.style.transform=
                `translate(${x*speed}px,${y*speed}px)`;

        });

    });

}




/* =========================================================
   FLOATING CARD
========================================================= */

function initFloatingCards(){

    document.querySelectorAll(

        ".feature-card,.stat-card,.dashboard-card,.payment-card"

    ).forEach(card=>{

        card.addEventListener("mousemove",(e)=>{

            const rect=card.getBoundingClientRect();

            const x=e.clientX-rect.left;
            const y=e.clientY-rect.top;

            const rotateY=((x/rect.width)-0.5)*12;
            const rotateX=((y/rect.height)-0.5)*-12;

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

}




/* =========================================================
   LAZY IMAGE
========================================================= */

function initLazyImages(){

    const images=document.querySelectorAll("img[data-src]");

    if(!images.length) return;

    const observer=new IntersectionObserver(entries=>{

        entries.forEach(entry=>{

            if(!entry.isIntersecting) return;

            const img=entry.target;

            img.src=img.dataset.src;

            img.removeAttribute("data-src");

            observer.unobserve(img);

        });

    });

    images.forEach(img=>observer.observe(img));

}




/* =========================================================
   NUMBER FORMAT
========================================================= */

function formatNumber(number){

    return new Intl.NumberFormat("id-ID").format(number);

}




/* =========================================================
   RANDOM ONLINE USER
========================================================= */

function initOnlineUsers(){

    const el=document.querySelector("[data-online]");

    if(!el) return;

    let value=Number(el.dataset.online)||500;

    el.textContent=formatNumber(value);

    setInterval(()=>{

        value+=Math.floor(Math.random()*8)-3;

        if(value<100) value=100;

        el.textContent=formatNumber(value);

    },4000);

}




/* =========================================================
   BUTTON LOADING
========================================================= */

function initButtonLoading(){

    document.querySelectorAll(".btn-loading")

    .forEach(button=>{

        button.addEventListener("click",()=>{

            if(button.disabled) return;

            button.disabled=true;

            const text=button.innerHTML;

            button.innerHTML=

            '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';

            setTimeout(()=>{

                button.innerHTML=text;

                button.disabled=false;

            },1800);

        });

    });

}




/* =========================================================
   PERFORMANCE
========================================================= */

function initPerformance(){

    if(

        window.matchMedia(

            "(prefers-reduced-motion: reduce)"

        ).matches

    ){

        document.body.classList.add(

            "reduce-motion"

        );

    }

}




/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener(

    "DOMContentLoaded",

()=>{

    initFloatingCards();

    initLazyImages();

    initOnlineUsers();

    initButtonLoading();

    initPerformance();

});

/* =========================================================
   PREMIUM EFFECT
========================================================= */


/* =========================
   MOUSE SPOTLIGHT
========================= */

function initSpotlight(){

    const light=document.createElement("div");

    light.className="mouse-light";

    document.body.appendChild(light);

    document.addEventListener("mousemove",(e)=>{

        light.style.left=e.clientX+"px";
        light.style.top=e.clientY+"px";

    },{passive:true});

}




/* =========================
   COPY BUTTON
========================= */

function initCopyButton(){

    document.querySelectorAll("[data-copy]").forEach(btn=>{

        btn.addEventListener("click",async()=>{

            try{

                await navigator.clipboard.writeText(

                    btn.dataset.copy

                );

                showToast("Copied successfully");

            }

            catch(e){

                console.log(e);

            }

        });

    });

}




/* =========================
   TOAST
========================= */

function showToast(message){

    let toast=document.querySelector(".premium-toast");

    if(!toast){

        toast=document.createElement("div");

        toast.className="premium-toast";

        document.body.appendChild(toast);

    }

    toast.textContent=message;

    toast.classList.add("show");

    clearTimeout(toast.timer);

    toast.timer=setTimeout(()=>{

        toast.classList.remove("show");

    },2500);

}




/* =========================
   AUTO ACTIVE MENU
========================= */

function initActiveMenu(){

    const sections=document.querySelectorAll("section[id]");

    const links=document.querySelectorAll(".nav-link");

    if(!sections.length) return;

    window.addEventListener("scroll",()=>{

        let current="";

        sections.forEach(section=>{

            if(

                pageYOffset>=section.offsetTop-120

            ){

                current=section.id;

            }

        });

        links.forEach(link=>{

            link.classList.remove("active");

            if(

                link.getAttribute("href")==="#"+current

            ){

                link.classList.add("active");

            }

        });

    },{

        passive:true

    });

}




/* =========================
   AUTO YEAR
========================= */

function initYear(){

    const year=document.querySelector("[data-year]");

    if(year){

        year.textContent=

        new Date().getFullYear();

    }

}




/* =========================
   DEVICE DETECT
========================= */

function detectDevice(){

    const mobile=

    /Android|iPhone|iPad|iPod/i

    .test(navigator.userAgent);

    document.body.classList.add(

        mobile ?

        "device-mobile"

        :

        "device-desktop"

    );

}




/* =========================
   IMAGE FADE
========================= */

function initImageFade(){

    document.querySelectorAll("img").forEach(img=>{

        img.addEventListener("load",()=>{

            img.classList.add("loaded");

        });

    });

}




/* =========================
   INIT
========================= */

document.addEventListener(

    "DOMContentLoaded",

()=>{

    initSpotlight();

    initCopyButton();

    initActiveMenu();

    initYear();

    detectDevice();

    initImageFade();

});
