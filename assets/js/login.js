/* ==========================================
   CLICK2PAY LOGIN
========================================== */

document.addEventListener("DOMContentLoaded",()=>{

document.body.classList.add("loaded");

/* =========================
   SHOW / HIDE PASSWORD
========================= */

const toggle=document.getElementById("togglePassword");
const password=document.getElementById("password");

if(toggle&&password){

toggle.addEventListener("click",()=>{

const icon=toggle.querySelector("i");

if(password.type==="password"){

password.type="text";
icon.classList.remove("bi-eye");
icon.classList.add("bi-eye-slash");

}else{

password.type="password";
icon.classList.remove("bi-eye-slash");
icon.classList.add("bi-eye");

}

});

}

/* =========================
   LOGIN
========================= */

const form=document.getElementById("loginForm");

if(form){

form.addEventListener("submit",(e)=>{

e.preventDefault();

const verify=document.getElementById("verifyCheck");

if(!verify.checked){

showToast("Silakan lakukan verifikasi terlebih dahulu.");

return;

}

const btn=form.querySelector("button[type='submit']");

btn.disabled=true;

btn.innerHTML='<span class="spinner-border spinner-border-sm me-2"></span>Memproses...';

setTimeout(()=>{

showToast("Login berhasil.");

btn.disabled=false;

btn.innerHTML='<i class="bi bi-box-arrow-in-right"></i> Masuk';

window.location.href="dashboard.html";

},1500);

});

}

/* =========================
   TOAST
========================= */

function showToast(text){

const toast=document.createElement("div");

toast.className="premium-toast";

toast.innerHTML=text;

document.body.appendChild(toast);

setTimeout(()=>{

toast.classList.add("show");

},50);

setTimeout(()=>{

toast.classList.remove("show");

setTimeout(()=>{

toast.remove();

},300);

},2500);

}

});
