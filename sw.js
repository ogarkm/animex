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
  '/Launch.html',
  // External links (deduplicated)
  'https://fonts.googleapis.com',
  'https://fonts.gstatic.com',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
  'https://arkm20-authapi.hf.space',
  'https://cdn.myanimelist.net/images/anime/1463/145502l.jpg',
  'https://cdn.myanimelist.net/images/anime/1448/147351.jpg',
  'https://cdn.myanimelist.net/images/anime/1770/97704l.jpg',
  'https://cdn.myanimelist.net/images/manga/2/253146.jpg',
  'https://placehold.co/60x80/555/fff?text=N/A',
  'https://placehold.co/60x80/444/fff?text=N/A',
  'https://placehold.co/140x200/444/fff?text=N/A',
  'https://cdn.i.haymarketmedia.asia/?n=campaign-asia%2Fcontent%2F20240719041444_Untitled+design+(12).png&h=570&w=855&q=100&v=20250320&c=1',
  'https://placehold.co/80/cccccc/fff?text=?',
  'https://placehold.co/80/cc0000/fff?text=${initial}',
  'https://placehold.co/60x80/444/fff?text=${encodeURIComponent(seriesName.substring(0,3))}',
  'https://unpkg.com/@ffmpeg/ffmpeg@0.12.10/dist/umd/ffmpeg.js',
  'https://unpkg.com/@ffmpeg/util@0.12.1/dist/umd/index.js',
  'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd/ffmpeg-core.js',
  'https://arkm20-authapi.hf.space/users/me/watch-history?${params.toString()}',
  'https://placehold.co/1200x700/1A2B3C/FFF?text=No+Image+Available',
  'https://arkm20-animex-player-api.hf.space',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'
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
