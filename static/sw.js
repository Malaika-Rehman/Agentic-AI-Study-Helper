// Service Worker for Agentic AI Study Helper Push Notifications
// Runs in the browser background even when the Streamlit application is closed.

self.addEventListener('push', function(event) {
    let data = {
        title: '🎓 Agentic AI Study Helper',
        body: 'You have some work remaining for this week. Open Study Helper and continue your progress.',
        icon: '/app/static/logo.png',
        badge: '/app/static/logo.png',
        url: '/'
    };

    if (event.data) {
        try {
            const parsed = event.data.json();
            data = Object.assign(data, parsed);
        } catch (e) {
            data.body = event.data.text() || data.body;
        }
    }

    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        data: {
            url: data.url || '/'
        },
        vibrate: [100, 50, 100],
        actions: [
            { action: 'open', title: '📚 Open Study Helper' },
            { action: 'dismiss', title: 'Dismiss' }
        ],
        requireInteraction: true
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    const targetUrl = (event.notification.data && event.notification.data.url) ? event.notification.data.url : '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if ('focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
