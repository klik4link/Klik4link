/* =========================================================
   CLICK2PAY
   PREMIUM APP JS
========================================================= */


document.addEventListener("DOMContentLoaded",()=>{


/* =========================================================
   PAGE LOADED
========================================================= */

document.body.classList.add("loaded");




/* =========================================================
   YEAR FOOTER
========================================================= */

const year = document.getElementById("year");

if(year){

    year.textContent =
    new Date().getFullYear();

}





/* =========================================================
   NAVBAR SCROLL EFFECT
========================================================= */


const navbar =
document.querySelector(".glass-navbar");


window.addEventListener("scroll",()=>{


    if(!navbar) return;


    if(window.scrollY > 50){

        navbar.classList.add("scrolled");

    }

    else{

        navbar.classList.remove("scrolled");

    }


});






/* =========================================================
   SMOOTH SCROLL
========================================================= */


document.querySelectorAll('a[href^="#"]').forEach(link=>{


    link.addEventListener("click",e=>{


        const target =
        document.querySelector(
            link.getAttribute("href")
        );


        if(target){

            e.preventDefault();


            target.scrollIntoView({

                behavior:"smooth",

                block:"start"

            });


        }


    });


});






/* =========================================================
   COUNTER ANIMATION
========================================================= */


const counters =
document.querySelectorAll(".counter");


const formatter =
new Intl.NumberFormat("id-ID");



const startCounter=(counter)=>{


    const target =
    Number(counter.dataset.target);


    let current=0;


    const speed =
    Math.max(
        target / 120,
        1
    );



    const update=()=>{


        current += speed;



        if(current < target){


            counter.textContent =
            formatter.format(
                Math.floor(current)
            );


            requestAnimationFrame(update);


        }


        else{


            counter.textContent =
            formatter.format(target);


        }


    };


    update();


};





const observerCounter =
new IntersectionObserver(entries=>{


    entries.forEach(entry=>{


        if(entry.isIntersecting){


            startCounter(
                entry.target
            );


            observerCounter.unobserve(
                entry.target
            );


        }


    });


},{
    threshold:.5
});



counters.forEach(counter=>{


    observerCounter.observe(counter);


});







/* =========================================================
   LIVE ONLINE USERS
========================================================= */


const liveUsers =
document.getElementById("live-users");


if(liveUsers){


    let users =
    Number(
        liveUsers.textContent.replace(",","")
    );


    setInterval(()=>{


        const change =
        Math.floor(
            Math.random()*15
        ) - 7;



        users += change;



        if(users < 1000){

            users = 1000;

        }



        liveUsers.textContent =
        formatter.format(users);



    },4000);


}






/* =========================================================
   ACTIVE MENU ON SCROLL
========================================================= */


const sections =
document.querySelectorAll("section[id]");


const navLinks =
document.querySelectorAll(".nav-link");



window.addEventListener("scroll",()=>{


    let current="";


    sections.forEach(section=>{


        const top =
        section.offsetTop - 150;


        const height =
        section.offsetHeight;


        if(
            window.scrollY >= top &&
            window.scrollY < top+height
        ){

            current =
            section.getAttribute("id");

        }


    });



    navLinks.forEach(link=>{


        link.classList.remove("active");


        if(
            link.getAttribute("href")
            === "#"+current
        ){

            link.classList.add("active");

        }


    });



});






/* =========================================================
   SCROLL REVEAL
========================================================= */


const revealElements =
document.querySelectorAll(
`
.feature-card,
.stat-card,
.payment-card,
.security-card,
.step-card,
.glass-card
`
);



const revealObserver =
new IntersectionObserver(entries=>{


    entries.forEach(entry=>{


        if(entry.isIntersecting){


            entry.target.classList.add(
                "show"
            );


        }


    });


},{
    threshold:.15
});



revealElements.forEach(el=>{


    el.classList.add("reveal");

    revealObserver.observe(el);


});







/* =========================================================
   SNOW EFFECT
========================================================= */


const snowContainer =
document.querySelector(
".snow-container"
);



if(snowContainer){


    for(let i=0;i<80;i++){


        const snow =
        document.createElement("span");


        snow.className="snow";


        snow.style.left =
        Math.random()*100+"%";


        snow.style.animationDuration =
        (5+
        Math.random()*10)
        +"s";



        snow.style.animationDelay =
        Math.random()*10+"s";



        snow.style.opacity =
        Math.random();



        snowContainer.appendChild(
            snow
        );


    }


}






/* =========================================================
   PARALLAX BACKGROUND
========================================================= */


const bg =
document.querySelector(".animated-bg");


window.addEventListener("mousemove",e=>{


    if(!bg)return;


    const x =
    (e.clientX/window.innerWidth-.5)
    *30;


    const y =
    (e.clientY/window.innerHeight-.5)
    *30;



    bg.style.transform =
    `
    translate(${x}px,${y}px)
    `;


});






/* =========================================================
   DASHBOARD FLOAT RANDOM
========================================================= */


const dashboard =
document.querySelector(
".dashboard-card"
);



if(dashboard){


    let angle=0;


    setInterval(()=>{


        angle += .02;


        dashboard.style.transform =
        `
        translateY(${Math.sin(angle)*8}px)
        `;


    },50);


}






/* =========================================================
   TYPING EFFECT OPTIONAL
========================================================= */


const typing =
document.querySelector(
".typing"
);



if(typing){


    const text =
    typing.dataset.text ||
    typing.textContent;


    typing.textContent="";


    let i=0;



    function type(){


        if(i < text.length){


            typing.textContent +=
            text.charAt(i);


            i++;


            setTimeout(type,70);


        }


    }


    type();


}




});

/* =========================================================
   PARTICLES BACKGROUND
========================================================= */


if(typeof particlesJS !== "undefined"){


    const particleLayer =
    document.createElement("div");


    particleLayer.id =
    "particles-js";


    particleLayer.style.position =
    "fixed";


    particleLayer.style.inset =
    "0";


    particleLayer.style.zIndex =
    "-2";


    particleLayer.style.pointerEvents =
    "none";


    document.body.prepend(
        particleLayer
    );



    particlesJS("particles-js",{


        particles:{


            number:{


                value:65,


                density:{


                    enable:true,


                    value_area:900


                }


            },


            color:{


                value:"#1e88ff"


            },


            shape:{


                type:"circle"


            },


            opacity:{


                value:.35,


                random:true


            },


            size:{


                value:3,


                random:true


            },


            line_linked:{


                enable:true,


                distance:140,


                color:"#6c63ff",


                opacity:.25,


                width:1


            },


            move:{


                enable:true,


                speed:1.5,


                direction:"none",


                random:true,


                straight:false,


                out_mode:"out",


                bounce:false


            }


        },



        interactivity:{


            detect_on:"canvas",


            events:{


                onhover:{


                    enable:true,


                    mode:"grab"


                },


                onclick:{


                    enable:true,


                    mode:"push"


                }


            },



            modes:{


                grab:{


                    distance:180,


                    line_linked:{


                        opacity:.6


                    }


                },


                push:{


                    particles_nb:4


                }


            }


        },



        retina_detect:true


    });


}
/* =========================================================
   3D CARD TILT
========================================================= */


if(window.innerWidth > 768){


const tiltCards =
document.querySelectorAll(
`
.feature-card,
.stat-card,
.payment-card,
.security-card
`
);



tiltCards.forEach(card=>{


    card.addEventListener(
    "mousemove",
    e=>{


        const rect =
        card.getBoundingClientRect();


        const x =
        e.clientX - rect.left;


        const y =
        e.clientY - rect.top;



        const rotateY =
        ((x / rect.width)-.5)*12;


        const rotateX =
        ((y / rect.height)-.5)*-12;



        card.style.transform =
        `
        perspective(900px)
        rotateX(${rotateX}deg)
        rotateY(${rotateY}deg)
        translateY(-8px)
        `;


    });



    card.addEventListener(
    "mouseleave",
    ()=>{


        card.style.transform="";


    });


});


}
/* =========================================================
   BUTTON RIPPLE EFFECT
========================================================= */


document.querySelectorAll(".btn")
.forEach(button=>{


button.addEventListener("click",function(e){


    const ripple =
    document.createElement("span");


    const rect =
    this.getBoundingClientRect();



    ripple.style.position="absolute";

    ripple.style.width="10px";

    ripple.style.height="10px";

    ripple.style.borderRadius="50%";

    ripple.style.background=
    "rgba(255,255,255,.5)";

    ripple.style.left=
    (e.clientX-rect.left)+"px";

    ripple.style.top=
    (e.clientY-rect.top)+"px";

    ripple.style.transform=
    "scale(0)";

    ripple.style.animation=
    "ripple .6s linear";



    this.style.position="relative";

    this.style.overflow="hidden";


    this.appendChild(ripple);



    setTimeout(()=>{


        ripple.remove();


    },600);



});


});
/* =========================================================
   PERFORMANCE OPTIMIZATION
   CLICK2PAY
========================================================= */


/* =========================
   DISABLE HEAVY EFFECT LOW DEVICE
========================= */


const isLowDevice =
navigator.hardwareConcurrency &&
navigator.hardwareConcurrency <= 4;



if(isLowDevice || window.innerWidth < 600){


    // Kurangi particle

    const particle =
    document.getElementById(
        "particles-js"
    );


    if(particle){

        particle.style.display="none";

    }



    // Disable tilt

    document
    .querySelectorAll(
    ".feature-card,.stat-card,.payment-card,.security-card"
    )
    .forEach(card=>{

        card.style.transition=".3s";

    });



}







/* =========================
   LAZY IMAGE LOADING
========================= */


document
.querySelectorAll("img")
.forEach(img=>{


    img.loading="lazy";


});







/* =========================
   OPTIMIZE SCROLL EVENT
========================= */


let ticking=false;



window.addEventListener(
"scroll",
()=>{


    if(!ticking){


        window.requestAnimationFrame(()=>{


            ticking=false;


        });


        ticking=true;


    }


},
{
    passive:true
});








/* =========================
   MOBILE NAV CLOSE
========================= */


const navLinksMobile =
document.querySelectorAll(
".navbar-nav .nav-link"
);



const navbarCollapse =
document.querySelector(
".navbar-collapse"
);



navLinksMobile.forEach(link=>{


link.addEventListener(
"click",
()=>{


    if(
    window.innerWidth < 992 &&
    navbarCollapse.classList.contains("show")
    ){


        document
        .querySelector(
        ".navbar-toggler"
        )
        .click();


    }


});


});








/* =========================
   AUTO YEAR
========================= */


const footerYear =
document.getElementById(
"year"
);



if(footerYear){

    footerYear.innerHTML =
    new Date().getFullYear();

}






/* =========================
   PREVENT HORIZONTAL BUG
========================= */


document.body.style.overflowX =
"hidden";






/* =========================
   NETWORK STATUS
========================= */


window.addEventListener(
"offline",
()=>{


    console.log(
    "Click2Pay offline mode"
    );


});



window.addEventListener(
"online",
()=>{


    console.log(
    "Click2Pay online"
    );


});
