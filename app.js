/*=====================================
CLICK2PAY APP
Version : 1.0
=====================================*/

"use strict";

/*=====================================
AOS
=====================================*/

AOS.init({

    duration:1000,

    once:true,

    easing:"ease-in-out"

});

/*=====================================
COPYRIGHT YEAR
=====================================*/

const year = document.getElementById("year");

if(year){

    year.textContent = new Date().getFullYear();

}

/*=====================================
NAVBAR SCROLL
=====================================*/

const navbar = document.querySelector(".glass-navbar");

window.addEventListener("scroll",()=>{

    if(window.scrollY > 80){

        navbar.style.background="rgba(255,255,255,.95)";

        navbar.style.boxShadow="0 15px 40px rgba(0,0,0,.08)";

        navbar.style.padding="10px 0";

    }else{

        navbar.style.background="rgba(255,255,255,.75)";

        navbar.style.boxShadow="0 8px 30px rgba(0,0,0,.08)";

        navbar.style.padding="18px 0";

    }

});

/*=====================================
COUNTER
=====================================*/

const counters=document.querySelectorAll(".counter");

const speed=200;

counters.forEach(counter=>{

    const update=()=>{

        const target=+counter.dataset.target;

        const count=+counter.innerText.replace(/,/g,"");

        const inc=target/speed;

        if(count<target){

            counter.innerText=Math.ceil(count+inc).toLocaleString();

            requestAnimationFrame(update);

        }else{

            counter.innerText=target.toLocaleString();

        }

    };

    update();

});

/*=====================================
BUTTON RIPPLE
=====================================*/

document.querySelectorAll(".btn").forEach(button=>{

button.addEventListener("mouseenter",()=>{

button.style.transition=".3s";

});

});

/*=====================================
SMOOTH SCROLL
=====================================*/

document.querySelectorAll("a[href^='#']").forEach(anchor=>{

anchor.addEventListener("click",function(e){

e.preventDefault();

document.querySelector(this.getAttribute("href"))

.scrollIntoView({

behavior:"smooth"

});

});

});

/*=====================================
FLOATING CARDS
=====================================*/

document.querySelectorAll(
".dashboard-card,.stat-card,.step-card,.feature-card,.security-card"
).forEach(card=>{

let x=0;
let y=0;

card.addEventListener("mousemove",(e)=>{

const rect=card.getBoundingClientRect();

x=e.clientX-rect.left;
y=e.clientY-rect.top;

card.style.transform=
`perspective(1000px)
rotateX(${-(y-rect.height/2)/18}deg)
rotateY(${(x-rect.width/2)/18}deg)
translateY(-8px)`;

});

card.addEventListener("mouseleave",()=>{

card.style.transform="";

});

});

/*=====================================
STAR GENERATOR
=====================================*/

const stars=document.querySelector(".stars-container");

if(stars){

for(let i=0;i<120;i++){

const star=document.createElement("span");

star.style.position="absolute";

star.style.width="3px";

star.style.height="3px";

star.style.borderRadius="50%";

star.style.background="#ffffff";

star.style.left=Math.random()*100+"%";

star.style.top=Math.random()*100+"%";

star.style.opacity=Math.random();

star.style.animation=
`twinkle ${2+Math.random()*5}s infinite`;

stars.appendChild(star);

}

}

/*=====================================
SNOW GENERATOR
=====================================*/

const snow=document.querySelector(".snow-container");

if(snow){

for(let i=0;i<150;i++){

const item=document.createElement("div");

const size=Math.random()*6+2;

item.style.position="absolute";

item.style.width=size+"px";

item.style.height=size+"px";

item.style.borderRadius="50%";

item.style.background="#ffffff";

item.style.opacity=Math.random();

item.style.left=Math.random()*100+"vw";

item.style.top="-20px";

item.style.filter="blur(.5px)";

item.style.animation=
`snow ${8+Math.random()*12}s linear infinite`;

item.style.animationDelay=
`${Math.random()*10}s`;

snow.appendChild(item);

}

}

/*=====================================
PROGRESS ANIMATION
=====================================*/

document.querySelectorAll(".progress-bar")

.forEach(bar=>{

const width=bar.style.width;

bar.style.width="0";

setTimeout(()=>{

bar.style.width=width;

},400);

});

/*=====================================
NUMBER PULSE
=====================================*/

setInterval(()=>{

document.querySelectorAll(".counter")

.forEach(el=>{

el.animate(

[
{transform:"scale(1)"},
{transform:"scale(1.06)"},
{transform:"scale(1)"}
],

{

duration:800

}

);

});

},4000);

/*=====================================
PARALLAX BACKGROUND
=====================================*/

document.addEventListener("mousemove",(e)=>{

const bg=document.querySelector(".animated-bg");

if(!bg) return;

const x=(e.clientX/window.innerWidth)*20;

const y=(e.clientY/window.innerHeight)*20;

bg.style.transform=`translate(${x}px,${y}px)`;

});

/*=====================================
MARQUEE SPEED
=====================================*/

const marquee=document.querySelector(".marquee-content");

if(marquee){

const wrap=document.querySelector(".marquee");

wrap.addEventListener("mouseenter",()=>{

marquee.style.animationPlayState="paused";

});

wrap.addEventListener("mouseleave",()=>{

marquee.style.animationPlayState="running";

});

}

/*=====================================
BUTTON GLOW
=====================================*/

document.querySelectorAll(".btn-primary")

.forEach(btn=>{

btn.addEventListener("mouseenter",()=>{

btn.animate(

[
{
boxShadow:"0 0 0 rgba(33,150,243,.2)"
},
{
boxShadow:"0 0 35px rgba(33,150,243,.6)"
},
{
boxShadow:"0 0 0 rgba(33,150,243,.2)"
}
],

{
duration:1200
}

);

});

});

/*=====================================
FLOAT ICON
=====================================*/

document.querySelectorAll(

".stat-icon,.step-icon"

).forEach(icon=>{

setInterval(()=>{

icon.animate(

[
{
transform:"translateY(0)"
},
{
transform:"translateY(-8px)"
},
{
transform:"translateY(0)"
}
],

{

duration:2500,

iterations:1

}

);

},3000);

});

/*=====================================
SCROLL REVEAL
=====================================*/

const revealItems=document.querySelectorAll(

".feature-item,.dashboard-item"

);

const revealObserver=new IntersectionObserver(entries=>{

entries.forEach(entry=>{

if(entry.isIntersecting){

entry.target.style.opacity="1";

entry.target.style.transform="translateY(0)";

}

});

});

revealItems.forEach(item=>{

item.style.opacity="0";

item.style.transform="translateY(30px)";

item.style.transition=".7s";

revealObserver.observe(item);

});

/*=====================================
LOADING
=====================================*/

window.addEventListener("load",()=>{

document.body.classList.add("loaded");

});

/*=====================================
END
=====================================*/

console.log(
"🚀 Click2Pay Loaded Successfully"
);
