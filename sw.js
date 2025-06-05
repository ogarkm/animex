self.addEventListener("install", event => {
    event.waitUntil(
        caches.open("v1").then(cache => {
            return cache.addAll([
                "/",
                "/Launch.html",
                "/index.html",
                "/anime.html",
                "/manga.html",
                "/search.html",
                "/settings.html",
                "/library.html",
                "/video_player.html",
                "/test.htm",
                "/series-info.html",
                "/README.md",
                "/sw.js",
                "/list.py",
                "/Resources/favicon.png",
                "/Resources/styles.css",
                "/Resources/series.css",
                "/Resources/manifest.json",
                "/Resources/Images/image 1.png",
                "/Resources/Images/Launch.png",
                "/Resources/Svgs/item-list-1.svg",
                "/Resources/Svgs/item-list-2.svg",
                "/Resources/Svgs/item-list-arrow.svg",
                "/Resources/Svgs/Tabbar/Anime.svg",
                "/Resources/old/styles.css",
                "/Resources/old/Manga.html",
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
                "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
            ]);
        })
    );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
