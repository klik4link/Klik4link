/* ==========================================
   CLICK2PAY SERVICE WORKER
========================================== */

const CACHE_NAME = "click2pay-v2";

const FILES = [
    "/",
    "/index.html",
    "/assets/css/style.css",
    "/assets/js/app.js",
    "/manifest.json"
];

/* =========================
   INSTALL
========================= */

self.addEventListener("install", event => {

    self.skipWaiting();

    event.waitUntil(

        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(FILES))

    );

});

/* =========================
   ACTIVATE
========================= */

self.addEventListener("activate", event => {

    event.waitUntil(

        caches.keys().then(keys => {

            return Promise.all(

                keys.map(key => {

                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }

                })

            );

        }).then(() => self.clients.claim())

    );

});

/* =========================
   FETCH
========================= */

self.addEventListener("fetch", event => {

    if (event.request.method !== "GET") return;

    event.respondWith(

        fetch(event.request)

            .then(response => {

                const clone = response.clone();

                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, clone);
                });

                return response;

            })

            .catch(() => {

                return caches.match(event.request);

            })

    );

});
