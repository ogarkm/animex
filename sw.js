const CACHE_NAME = 'animex-v2';
const PRECACHE_URLS = [
  '/', // index.html
  '/Launch.html',
  '/README.md',
  '/Resources/Images/Launch.png',
  '/Resources/Images/app-icon.png',
  '/Resources/Images/image%201.png',
  '/Resources/Images/image.png',
  '/Resources/Svgs/Tabbar/Anime.svg',
  '/Resources/Svgs/item-list-1.svg',
  '/Resources/Svgs/item-list-2.svg',
  '/Resources/Svgs/item-list-arrow.svg',
  '/Resources/favicon.png',
  '/Resources/manifest.json',
  '/Resources/old/Manga.html',
  '/Resources/old/styles.css',
  '/Resources/series.css',
  '/Resources/styles.css',
  '/anime.html',
  '/cdn.py',
  '/down.html',
  '/in.py',
  '/index.html',
  '/kwik_page.html',
  '/library.html',
  '/make.py',
  '/manga.html',
  '/output.html',
  '/pdf.html',
  '/search.html',
  '/series-info.html',
  '/settings.html',
  '/test.htm',
  '/video_player.html', // Make sure this is included
  '/view.html',
  '/offline.html',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
];

// Install: cache critical assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return Promise.allSettled(
          PRECACHE_URLS.map(url =>
            cache.add(url).catch(err => {
              console.warn('SW cache add failed:', url, err);
              return null; // Don't fail the entire install
            })
          )
        );
      })
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

// Fetch: Cache first for app resources, network first for external APIs
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  
  // Cache-first strategy for app resources and CDN assets
  if (url.origin === location.origin || 
      url.hostname.includes('fonts.googleapis.com') ||
      url.hostname.includes('fonts.gstatic.com') ||
      url.hostname.includes('cdnjs.cloudflare.com') ||
      url.hostname.includes('unpkg.com')) {
    
    event.respondWith(
      caches.match(event.request)
        .then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          return fetch(event.request)
            .then(networkResponse => {
              // Cache successful responses
              if (networkResponse.status === 200) {
                const responseClone = networkResponse.clone();
                caches.open(CACHE_NAME)
                  .then(cache => cache.put(event.request, responseClone));
              }
              return networkResponse;
            })
            .catch(() => {
              // FIXED: Only show offline page for main navigation, not for video player
              if (event.request.mode === 'navigate' && 
                  !url.pathname.includes('video_player.html')) {
                return caches.match('/offline.html');
              }
              // For video player or other resources, just throw the error
              throw new Error('Network failed and no cache available');
            });
        })
    );
  } else {
    // Network-first for external APIs and video content
    event.respondWith(
      fetch(event.request)
        .then(networkResponse => {
          // Cache successful responses for later
          if (networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME)
              .then(cache => cache.put(event.request, responseClone));
          }
          return networkResponse;
        })
        .catch(() => caches.match(event.request))
    );
  }
});
