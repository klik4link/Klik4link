const CACHE_NAME =
"click2pay-v1";


const FILES = [

"/",

"/assets/css/style.css",

"/assets/js/app.js",

"/manifest.json"

];



self.addEventListener(
"install",
event=>{


event.waitUntil(

caches.open(CACHE_NAME)
.then(cache=>{

return cache.addAll(FILES);

})

);


});





self.addEventListener(
"fetch",
event=>{


event.respondWith(


caches.match(event.request)
.then(response=>{


return response ||
fetch(event.request);


})


);


});
