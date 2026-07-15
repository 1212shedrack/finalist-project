/**
 * Amaranthus AI — Service Worker
 * Enables offline support and PWA installability.
 *
 * Strategy:
 *   - Shell assets (CSS/JS/icons) → Cache First (fast, offline-safe)
 *   - HTML pages               → Network First (fresh content, falls back to cache)
 *   - API / predict POST       → Network Only  (never cache uploads)
 */

const CACHE_NAME    = 'amaranthus-ai-v1';
const OFFLINE_URL   = '/offline/';

// Assets to pre-cache on install (app shell)
const PRECACHE_URLS = [
  '/',
  '/predict/',
  '/history/',
  '/about/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// ── Install: cache the app shell ────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] Pre-caching app shell');
      // Use individual adds so one failure doesn't break everything
      return Promise.allSettled(
        PRECACHE_URLS.map(url => cache.add(url).catch(() => {
          console.warn('[SW] Failed to cache:', url);
        }))
      );
    }).then(() => self.skipWaiting())
  );
});

// ── Activate: delete old caches ──────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: respond with cache or network ─────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests (POST for predict/upload — never cache)
  if (request.method !== 'GET') return;

  // Skip cross-origin requests
  if (url.origin !== location.origin) return;

  // Skip admin URLs
  if (url.pathname.startsWith('/admin/')) return;

  // Skip media uploads
  if (url.pathname.startsWith('/media/')) return;

  // ── Static assets: Cache First ─────────────────────────────────────────────
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
          }
          return response;
        });
      })
    );
    return;
  }

  // ── HTML pages: Network First, fall back to cache ──────────────────────────
  event.respondWith(
    fetch(request)
      .then(response => {
        // Cache successful page loads
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        }
        return response;
      })
      .catch(() => {
        // Offline: serve from cache
        return caches.match(request).then(cached => {
          if (cached) return cached;
          // Nothing cached: show offline page
          return caches.match('/').then(home => home || offlinePage());
        });
      })
  );
});

// ── Background sync (future: queue failed predictions) ──────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'sync-predictions') {
    console.log('[SW] Background sync triggered');
  }
});

// ── Push notifications (future feature) ──────────────────────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  self.registration.showNotification(data.title || 'Amaranthus AI', {
    body:  data.body  || 'Your analysis is ready.',
    icon:  '/static/icons/icon-192.png',
    badge: '/static/icons/icon-192.png',
  });
});

// ── Helper: simple offline fallback page ─────────────────────────────────────
function offlinePage() {
  const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Offline — Amaranthus AI</title>
      <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
          font-family: 'Poppins', sans-serif;
          background: #1a4d2e;
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          text-align: center;
          padding: 2rem;
        }
        .card {
          background: rgba(255,255,255,0.1);
          backdrop-filter: blur(10px);
          border-radius: 20px;
          padding: 3rem 2rem;
          max-width: 400px;
        }
        .icon { font-size: 4rem; margin-bottom: 1rem; }
        h1 { font-size: 1.5rem; margin-bottom: 1rem; }
        p  { opacity: 0.8; margin-bottom: 1.5rem; line-height: 1.6; }
        button {
          background: #4CAF50;
          color: #fff;
          border: none;
          padding: 0.75rem 2rem;
          border-radius: 50px;
          font-size: 1rem;
          cursor: pointer;
        }
        button:hover { background: #45a049; }
      </style>
    </head>
    <body>
      <div class="card">
        <div class="icon">🌿</div>
        <h1>You're Offline</h1>
        <p>No internet connection detected.<br>
           Please check your connection and try again.</p>
        <button onclick="window.location.reload()">Try Again</button>
      </div>
    </body>
    </html>`;
  return new Response(html, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  });
}
