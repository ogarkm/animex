const CACHE_NAME = 'animex-v1';
const PRECACHE_URLS = [
  '/', // index.html
  '/index.html',
  '/Resources/styles.css',
  '/Resources/series.css',
  '/Resources/manifest.json',
  '/Resources/favicon.png',
  '/Resources/Images/image 1.png',
  '/Resources/Images/Launch.png',
  '/Resources/Images/app-icon.png',
  '/Resources/Svgs/item-list-1.svg',
  '/Resources/Svgs/item-list-2.svg',
  '/Resources/Svgs/item-list-arrow.svg',
  '/Resources/Svgs/Tabbar/Anime.svg',
  '/anime.html',
  '/manga.html',
  '/search.html',
  '/settings.html',
  '/library.html',
  '/video_player.html',
  '/test.htm',
  '/series-info.html',
  '/view.html',
  '/pdf.html',
  '/Launch.html'
];

// Install: cache critical assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Activate: clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch: network first, fallback to cache, then offline page
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then(networkRes => {
        // update cache in background
        const clone = networkRes.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return networkRes;
      })
      .catch(() => caches.match(event.request))
      .then(cachedRes => {
        if (cachedRes) return cachedRes;
        // if page navigation and nothing cached, show offline page
        if (event.request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
      })
  );
});
