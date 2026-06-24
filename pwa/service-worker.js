// MessageCipher PWA Service Worker
// Cache-first strategy for offline support

const CACHE_NAME = 'messagecipher-pwa-v1.0.0';

const ASSETS = [
  './',
  './index.html',
  './style.css',
  './src/app.js',
  './src/cipher.js',
  './src/validator.js',
  './src/clipboard.js',
  './src/theme.js',
  './src/ui.js',
  './src/version-manager.js',
  './src/release-notes-dialog.js',
  './src/highlight-engine.js',
  './version.json',
  './release-notes.json',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

// Install event: pre-cache all static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate event: clean up old caches and claim clients
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => caches.delete(name))
        );
      })
      .then(() => self.clients.claim())
      .then(() => {
        // Notify all clients that a new version is active
        return self.clients.matchAll().then((clients) => {
          clients.forEach((client) => {
            client.postMessage({ type: 'SW_UPDATED' });
          });
        });
      })
  );
});

// Fetch event: cache-first strategy
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request);
      })
  );
});
