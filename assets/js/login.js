/* ==========================================
   CLICK2PAY LOGIN
========================================== */


const SUPABASE_URL = "https://lprwxtzqrfyicmknxeau.supabase.co/rest/v1/";

const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxwcnd4dHpxcmZ5aWNta254ZWF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1MjYyNjQsImV4cCI6MjA5OTEwMjI2NH0.oCK3RT6v0sXHo-bK9u-YbFkJOZi2Q7qmJABkZe1omgg";


const supabaseClient = supabase.createClient(
    SUPABASE_URL,
    SUPABASE_KEY
);



document.addEventListener("DOMContentLoaded",()=>{


document.body.classList.add("loaded");



/* =========================
   SHOW / HIDE PASSWORD
========================= */


const toggle=document.getElementById("togglePassword");
const passwordInput=document.getElementById("password");


if(toggle && passwordInput){

toggle.addEventListener("click",()=>{


const icon=toggle.querySelector("i");


if(passwordInput.type==="password"){

passwordInput.type="text";

icon.classList.replace(
"bi-eye",
"bi-eye-slash"
);


}else{

passwordInput.type="password";

icon.classList.replace(
"bi-eye-slash",
"bi-eye"
);

}


});

}




/* =========================
   LOGIN EMAIL
========================= */


const form=document.getElementById("loginForm");


if(form){


form.addEventListener("submit",async(e)=>{


e.preventDefault();



const token=document.querySelector(
'input[name="cf-turnstile-response"]'
)?.value;



if(!token){

showToast(
"Silakan selesaikan verifikasi."
);

return;

}




const email=document.getElementById("email").value.trim();

const password=document.getElementById("password").value;



if(!email || !password){

showToast(
"Email dan password wajib diisi."
);

return;

}




const btn=form.querySelector(
"button[type='submit']"
);



btn.disabled=true;


btn.innerHTML=`

<span class="spinner-border spinner-border-sm me-2"></span>

Memproses...

`;





/* CEK AKUN */


const {data:userCheck,error:userError}=

await supabaseClient
.from("users")
.select("id,email")
.eq("email",email)
.maybeSingle();




if(!userCheck){


showToast(
"Akun belum terdaftar."
);


resetButton();

return;

}





/* LOGIN SUPABASE */


const {data,error}=

await supabaseClient.auth.signInWithPassword({

email:email,

password:password

});





if(error){


showToast(
"Password salah."
);


resetButton();

return;

}





showToast(
"Login berhasil."
);



setTimeout(()=>{


window.location.href="dashboard.html";


},1000);





function resetButton(){


btn.disabled=false;


btn.innerHTML=`

<i class="bi bi-box-arrow-in-right"></i>

Masuk

`;


}



});


}






/* =========================
   GOOGLE LOGIN
========================= */


const googleBtn=document.getElementById(
"googleLogin"
);



if(googleBtn){


googleBtn.addEventListener("click",async()=>{


const {error}=

await supabaseClient.auth.signInWithOAuth({

provider:"google",

options:{

redirectTo:
"https://klik-bv1.pages.dev/dashboard.html"

}

});



if(error){

showToast(error.message);

}



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
