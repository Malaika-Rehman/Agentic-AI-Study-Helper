"""
Notification Manager for Agentic AI Study Helper.
Handles Web Push subscriptions, Service Worker registration,
dispatching browser notifications via pywebpush, and optional SMTP email fallback.
"""
import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import streamlit.components.v1 as components

from data.database import (
    get_or_create_vapid_keys,
    save_push_subscription,
    get_user_push_subscriptions,
    delete_push_subscription,
    record_notification_sent,
)

logger = logging.getLogger(__name__)


def render_push_notification_client(user_email: str):
    """
    Render JavaScript client for Web Push:
    1. Registers Service Worker (sw.js)
    2. Checks Notification.permission
    3. Handles subscription to pushManager with the VAPID Public Key
    4. Syncs subscription back to the server.
    """
    if not user_email:
        return

    vapid_pub, _, _ = get_or_create_vapid_keys()
    if not vapid_pub:
        return

    # Check if a subscription or dismissal was submitted via query params or session state
    query_params = st.query_params
    if "dismiss_notif" in query_params:
        st.session_state.is_first_login = False
        del st.query_params["dismiss_notif"]

    if "push_sub_payload" in query_params:
        try:
            payload_str = query_params["push_sub_payload"]
            payload = json.loads(payload_str)
            endpoint = payload.get("endpoint", "")
            keys = payload.get("keys", {})
            p256dh = keys.get("p256dh", "")
            auth = keys.get("auth", "")
            if endpoint and p256dh and auth:
                save_push_subscription(user_email, endpoint, p256dh, auth)
            del st.query_params["push_sub_payload"]
        except Exception as e:
            logger.warning(f"Failed to process push subscription: {e}")

    js_code = f"""
    <script>
    (function() {{
        const vapidPublicKey = "{vapid_pub}";
        const userEmail = "{user_email}";

        function urlBase64ToUint8Array(base64String) {{
            const padding = '='.repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                .replace(/\\-/g, '+')
                .replace(/_/g, '/');
            const rawData = window.atob(base64);
            const outputArray = new Uint8Array(rawData.length);
            for (let i = 0; i < rawData.length; ++i) {{
                outputArray[i] = rawData.charCodeAt(i);
            }}
            return outputArray;
        }}

        async function registerAndSubscribe() {{
            if (!('serviceWorker' in navigator) || !('PushManager' in window)) {{
                return;
            }}

            try {{
                // Service worker registration
                const swCode = `
                self.addEventListener('push', function(event) {{
                    let data = {{
                        title: '🎓 Agentic AI Study Helper',
                        body: 'You have some work remaining for this week. Open Study Helper and continue your progress.',
                        url: '/'
                    }};
                    if (event.data) {{
                        try {{ data = Object.assign(data, event.data.json()); }}
                        catch(e) {{ data.body = event.data.text() || data.body; }}
                    }}
                    event.waitUntil(
                        self.registration.showNotification(data.title, {{
                            body: data.body,
                            icon: 'https://cdn-icons-png.flaticon.com/512/3135/3135755.png',
                            data: {{ url: data.url || '/' }},
                            requireInteraction: true
                        }})
                    );
                }});
                self.addEventListener('notificationclick', function(event) {{
                    event.notification.close();
                    const targetUrl = (event.notification.data && event.notification.data.url) ? event.notification.data.url : '/';
                    event.waitUntil(
                        clients.matchAll({{ type: 'window', includeUncontrolled: true }}).then(function(clientList) {{
                            for (let i = 0; i < clientList.length; i++) {{
                                if ('focus' in clientList[i]) return clientList[i].focus();
                            }}
                            if (clients.openWindow) return clients.openWindow(targetUrl);
                        }})
                    );
                }});
                `;
                const blob = new Blob([swCode], {{ type: 'application/javascript' }});
                const swUrl = URL.createObjectURL(blob);
                const reg = await navigator.serviceWorker.register(swUrl);

                if (Notification.permission === 'granted') {{
                    let sub = await reg.pushManager.getSubscription();
                    if (!sub) {{
                        const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);
                        sub = await reg.pushManager.subscribe({{
                            userVisibleOnly: true,
                            applicationServerKey: convertedVapidKey
                        }});
                    }}
                    if (sub) {{
                        const subJson = sub.toJSON();
                        const keyFlag = "study_helper_sub_synced_" + btoa(subJson.endpoint).substring(0, 16);
                        if (!localStorage.getItem(keyFlag)) {{
                            localStorage.setItem(keyFlag, "true");
                            // Send subscription back to streamlit via query param
                            const currentUrl = new URL(window.parent.location.href);
                            currentUrl.searchParams.set("push_sub_payload", JSON.stringify(subJson));
                            window.parent.history.replaceState(null, "", currentUrl.toString());
                        }}
                    }}
                }}
            }} catch (err) {{
                console.warn("Push registration note:", err);
            }}
        }}

        registerAndSubscribe();
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)


def render_notification_permission_button(user_email: str):
    """
    Render an interactive card to request or confirm push notification permissions.
    """
    vapid_pub, _, _ = get_or_create_vapid_keys()

    btn_html = f"""
    <div style="background:#FDF7F8; border:1px solid #EADCE0; border-radius:12px; padding:12px; margin: 10px 0;">
        <div style="font-size:12px; font-weight:700; color:#802B45; margin-bottom:4px;">
            🔔 Study Reminders & Inactivity Alerts
        </div>
        <div style="font-size:11px; color:#7A5864; line-height:1.4; margin-bottom:8px;">
            Receive background study reminders on your device if you haven't visited for 7+ days.
        </div>
        <button id="enable-notif-btn" onclick="requestNotificationPermission()"
                style="background:#802B45; color:white; border:none; border-radius:8px;
                       padding:6px 12px; font-size:11.5px; font-weight:600; cursor:pointer; width:100%;">
            🔔 Enable Background Reminders
        </button>
        <div id="notif-status" style="font-size:10px; color:#15803D; margin-top:6px; display:none;">
            ✓ Notifications enabled for this device!
        </div>
    </div>

    <script>
    function urlBase64ToUint8Array(base64String) {{
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/\\-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {{
            outputArray[i] = rawData.charCodeAt(i);
        }}
        return outputArray;
    }}

    async function requestNotificationPermission() {{
        const btn = document.getElementById("enable-notif-btn");
        const status = document.getElementById("notif-status");
        if (!('Notification' in window)) {{
            alert("This browser does not support desktop notifications.");
            return;
        }}

        const permission = await Notification.requestPermission();
        if (permission === 'granted') {{
            btn.style.display = "none";
            status.style.display = "block";

            try {{
                const swCode = `
                self.addEventListener('push', function(event) {{
                    let data = {{
                        title: '🎓 Agentic AI Study Helper',
                        body: 'You have some work remaining for this week. Open Study Helper and continue your progress.',
                        url: '/'
                    }};
                    if (event.data) {{
                        try {{ data = Object.assign(data, event.data.json()); }}
                        catch(e) {{ data.body = event.data.text() || data.body; }}
                    }}
                    event.waitUntil(
                        self.registration.showNotification(data.title, {{
                            body: data.body,
                            icon: 'https://cdn-icons-png.flaticon.com/512/3135/3135755.png',
                            data: {{ url: data.url || '/' }},
                            requireInteraction: true
                        }})
                    );
                }});
                self.addEventListener('notificationclick', function(event) {{
                    event.notification.close();
                    const targetUrl = (event.notification.data && event.notification.data.url) ? event.notification.data.url : '/';
                    event.waitUntil(
                        clients.matchAll({{ type: 'window', includeUncontrolled: true }}).then(function(clientList) {{
                            for (let i = 0; i < clientList.length; i++) {{
                                if ('focus' in clientList[i]) return clientList[i].focus();
                            }}
                            if (clients.openWindow) return clients.openWindow(targetUrl);
                        }})
                    );
                }});
                `;
                const blob = new Blob([swCode], {{ type: 'application/javascript' }});
                const reg = await navigator.serviceWorker.register(URL.createObjectURL(blob));
                const convertedVapidKey = urlBase64ToUint8Array("{vapid_pub}");
                const sub = await reg.pushManager.subscribe({{
                    userVisibleOnly: true,
                    applicationServerKey: convertedVapidKey
                }});
                if (sub) {{
                    const subJson = sub.toJSON();
                    const currentUrl = new URL(window.parent.location.href);
                    currentUrl.searchParams.set("push_sub_payload", JSON.stringify(subJson));
                    window.parent.location.href = currentUrl.toString();
                }}
            }} catch (e) {{
                console.error("Failed to subscribe push:", e);
            }}
        }} else {{
            alert("Notification permission was denied.");
        }}
    }}

    // Check existing state
    if (Notification.permission === 'granted') {{
        const btn = document.getElementById("enable-notif-btn");
        const status = document.getElementById("notif-status");
        if (btn && status) {{
            btn.style.display = "none";
            status.style.display = "block";
        }}
    }}
    </script>
    """
    components.html(btn_html, height=125)


def render_first_login_notification_prompt(user_email: str, user_name: str):
    """
    Render a full-screen overlay notification permission dialog on first login.
    Styled like native iOS/Android/browser permission prompts — centered card,
    blurred backdrop, allow / don't allow buttons.
    Dismissal is handled via a ?dismiss_notif=1 query param reload.
    """
    vapid_pub, _, _ = get_or_create_vapid_keys()

    # Handle dismissal / subscription from query params
    if "dismiss_notif" in st.query_params:
        st.session_state.is_first_login = False
        del st.query_params["dismiss_notif"]
        st.rerun()

    if "push_sub_payload" in st.query_params:
        try:
            payload_str = st.query_params["push_sub_payload"]
            payload = json.loads(payload_str)
            endpoint = payload.get("endpoint", "")
            keys = payload.get("keys", {})
            p256dh = keys.get("p256dh", "")
            auth = keys.get("auth", "")
            if endpoint and p256dh and auth:
                save_push_subscription(user_email, endpoint, p256dh, auth)
            del st.query_params["push_sub_payload"]
        except Exception as e:
            logger.warning(f"Failed to process push subscription (first-login): {e}")

    overlay_html = f"""
    <style>
    /* ── Backdrop ── */
    #notif-overlay {{
        position: fixed;
        inset: 0;
        z-index: 99999;
        background: rgba(15, 5, 10, 0.55);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'DM Sans', Roboto, sans-serif;
        animation: fadeInOverlay 0.25s ease;
    }}
    @keyframes fadeInOverlay {{
        from {{ opacity: 0; }}
        to   {{ opacity: 1; }}
    }}

    /* ── Dialog card ── */
    #notif-card {{
        background: #FFFFFF;
        border-radius: 22px;
        width: 360px;
        max-width: calc(100vw - 40px);
        box-shadow:
            0 32px 80px rgba(0,0,0,0.28),
            0 8px 24px rgba(0,0,0,0.12);
        overflow: hidden;
        animation: slideUpCard 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }}
    @keyframes slideUpCard {{
        from {{ opacity:0; transform: translateY(30px) scale(0.96); }}
        to   {{ opacity:1; transform: translateY(0)   scale(1);    }}
    }}

    /* ── Top brand strip ── */
    #notif-brand {{
        background: linear-gradient(135deg, #802B45 0%, #4E1828 100%);
        padding: 28px 24px 22px;
        text-align: center;
        position: relative;
    }}
    #notif-brand-ring {{
        position: absolute;
        width: 160px; height: 160px;
        border-radius: 50%;
        border: 1.5px solid rgba(255,255,255,0.10);
        top: -60px; right: -40px;
        pointer-events: none;
    }}
    #notif-app-icon {{
        width: 64px; height: 64px;
        border-radius: 18px;
        background: rgba(255,255,255,0.15);
        display: flex; align-items: center; justify-content: center;
        font-size: 32px;
        margin: 0 auto 12px;
        border: 2px solid rgba(255,255,255,0.25);
        box-shadow: 0 4px 14px rgba(0,0,0,0.20);
    }}
    #notif-app-name {{
        font-size: 12px;
        font-weight: 700;
        color: rgba(255,255,255,0.75);
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }}

    /* ── Body content ── */
    #notif-body {{
        padding: 22px 24px 8px;
        text-align: center;
    }}
    #notif-headline {{
        font-size: 18px;
        font-weight: 700;
        color: #1A0A0F;
        margin: 0 0 8px;
        line-height: 1.3;
    }}
    #notif-subtext {{
        font-size: 13px;
        color: #7A5864;
        line-height: 1.6;
        margin: 0 0 18px;
    }}

    /* ── Feature list ── */
    #notif-features {{
        background: #FDF7F8;
        border: 1px solid #EADCE0;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 20px;
        text-align: left;
    }}
    .notif-feature-row {{
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 5px 0;
    }}
    .notif-feature-row:not(:last-child) {{
        border-bottom: 1px solid #F0E4E8;
        padding-bottom: 8px;
        margin-bottom: 5px;
    }}
    .notif-feature-ico {{
        font-size: 16px;
        flex-shrink: 0;
        margin-top: 1px;
    }}
    .notif-feature-text {{
        font-size: 12px;
        color: #4A3A40;
        line-height: 1.45;
    }}
    .notif-feature-text b {{
        color: #1A0A0F;
        font-weight: 700;
    }}

    /* ── Buttons ── */
    #notif-actions {{
        padding: 0 24px 24px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    #btn-notif-allow {{
        width: 100%;
        background: linear-gradient(135deg, #802B45 0%, #5C1E31 100%);
        color: white;
        border: none;
        border-radius: 13px;
        padding: 14px;
        font-size: 15px;
        font-weight: 700;
        cursor: pointer;
        letter-spacing: 0.01em;
        box-shadow: 0 4px 16px rgba(128, 43, 69, 0.35);
        transition: all 0.18s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }}
    #btn-notif-allow:hover {{
        background: linear-gradient(135deg, #6B2339 0%, #4A1828 100%);
        box-shadow: 0 6px 22px rgba(128, 43, 69, 0.45);
        transform: translateY(-1px);
    }}
    #btn-notif-allow:active {{ transform: translateY(0); }}

    #btn-notif-skip {{
        width: 100%;
        background: transparent;
        color: #9E828D;
        border: none;
        border-radius: 13px;
        padding: 10px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: color 0.15s ease;
    }}
    #btn-notif-skip:hover {{ color: #1A0A0F; }}

    /* ── Success state ── */
    #notif-success {{
        display: none;
        padding: 16px 24px 24px;
        text-align: center;
    }}
    #notif-success-ico {{
        font-size: 42px;
        margin-bottom: 10px;
    }}
    #notif-success-title {{
        font-size: 16px;
        font-weight: 700;
        color: #166534;
        margin-bottom: 6px;
    }}
    #notif-success-msg {{
        font-size: 13px;
        color: #7A5864;
    }}

    /* ── Loading spinner ── */
    .notif-spinner {{
        display: inline-block;
        width: 16px; height: 16px;
        border: 2px solid rgba(255,255,255,0.4);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.7s linear infinite;
        margin-right: 8px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    </style>

    <div id="notif-overlay">
      <div id="notif-card">

        <!-- Brand header -->
        <div id="notif-brand">
          <div id="notif-brand-ring"></div>
          <div id="notif-app-icon">🎓</div>
          <div id="notif-app-name">Agentic AI Study Helper</div>
        </div>

        <!-- Body -->
        <div id="notif-body">
          <div id="notif-headline">"Study Helper" Would Like<br>to Send You Notifications</div>
          <div id="notif-subtext">
            Stay on track with your learning goals.<br>
            We'll only notify you when it matters.
          </div>

          <div id="notif-features">
            <div class="notif-feature-row">
              <span class="notif-feature-ico">📅</span>
              <span class="notif-feature-text"><b>Study reminders</b> — get nudged when you have pending study plans or unread materials.</span>
            </div>
            <div class="notif-feature-row">
              <span class="notif-feature-ico">⏰</span>
              <span class="notif-feature-text"><b>Inactivity alerts</b> — a gentle ping if you haven't studied for 7+ days before an exam.</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div id="notif-actions">
          <button id="btn-notif-allow" onclick="handleNotifAllow()">
            🔔 Allow Notifications
          </button>
          <button id="btn-notif-skip" onclick="handleNotifSkip()">
            Don't Allow
          </button>
        </div>

        <!-- Success state (shown after grant) -->
        <div id="notif-success">
          <div id="notif-success-ico">✅</div>
          <div id="notif-success-title">Notifications Enabled!</div>
          <div id="notif-success-msg">You'll receive helpful study reminders on this device.</div>
        </div>

      </div>
    </div>

    <script>
    function urlB64ToUint8Array(b64) {{
        const pad = '='.repeat((4 - b64.length % 4) % 4);
        const b64s = (b64 + pad).replace(/\\-/g,'+'). replace(/_/g,'/');
        const raw = window.atob(b64s);
        const arr = new Uint8Array(raw.length);
        for (let i=0;i<raw.length;i++) arr[i]=raw.charCodeAt(i);
        return arr;
    }}

    function handleNotifSkip() {{
        const url = new URL(window.parent.location.href);
        url.searchParams.set('dismiss_notif','1');
        window.parent.location.href = url.toString();
    }}

    async function handleNotifAllow() {{
        const btn = document.getElementById('btn-notif-allow');
        btn.innerHTML = '<span class="notif-spinner"></span> Requesting…';
        btn.disabled = true;

        if (!('Notification' in window)) {{
            handleNotifSkip(); return;
        }}

        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {{
            handleNotifSkip(); return;
        }}

        // Show success UI immediately
        document.getElementById('notif-actions').style.display = 'none';
        document.getElementById('notif-success').style.display = 'block';

        // Register SW & subscribe
        try {{
            const swCode = `
            self.addEventListener('push', e => {{
                let d = {{ title:'🎓 Agentic AI Study Helper', body:'You have pending study material. Open Study Helper to continue.', url:'/' }};
                if (e.data) {{ try {{ d = Object.assign(d, e.data.json()); }} catch(_) {{}} }}
                e.waitUntil(self.registration.showNotification(d.title, {{
                    body: d.body,
                    icon: 'https://cdn-icons-png.flaticon.com/512/3135/3135755.png',
                    data: {{ url: d.url || '/' }},
                    requireInteraction: true
                }}));
            }});
            self.addEventListener('notificationclick', e => {{
                e.notification.close();
                const u = (e.notification.data && e.notification.data.url) ? e.notification.data.url : '/';
                e.waitUntil(clients.matchAll({{type:'window',includeUncontrolled:true}}).then(l => {{
                    for (let c of l) if ('focus' in c) return c.focus();
                    if (clients.openWindow) return clients.openWindow(u);
                }}));
            }});
            `;
            const blob = new Blob([swCode], {{type:'application/javascript'}});
            const reg  = await navigator.serviceWorker.register(URL.createObjectURL(blob));
            const key  = urlB64ToUint8Array('{vapid_pub}');
            const sub  = await reg.pushManager.subscribe({{ userVisibleOnly:true, applicationServerKey:key }});
            if (sub) {{
                const sj = sub.toJSON();
                const url = new URL(window.parent.location.href);
                url.searchParams.set('push_sub_payload', JSON.stringify(sj));
                url.searchParams.set('dismiss_notif', '1');
                setTimeout(() => {{ window.parent.location.href = url.toString(); }}, 1200);
                return;
            }}
        }} catch(err) {{
            console.warn('Push subscribe failed:', err);
        }}
        // Fallback dismiss if subscribe failed
        setTimeout(handleNotifSkip, 1200);
    }}
    </script>
    """
    # Render as full-viewport iframe so the overlay truly covers the page
    components.html(overlay_html, height=0, scrolling=False)



# ─────────────────────────────────────────────
# BACKEND NOTIFICATION DISPATCHERS
# ─────────────────────────────────────────────
def send_browser_web_push(subscription: dict, title: str, body: str, target_url: str = "/") -> bool:
    """
    Send a Web Push notification to a single browser subscription using pywebpush.
    """
    try:
        from pywebpush import webpush, WebPushException

        _, priv_pem, claim_email = get_or_create_vapid_keys()
        if not priv_pem:
            logger.error("Cannot send web push: Private VAPID key is missing.")
            return False

        subscription_info = {
            "endpoint": subscription["endpoint"],
            "keys": {
                "p256dh": subscription["p256dh"],
                "auth": subscription["auth"]
            }
        }

        payload = json.dumps({
            "title": title,
            "body": body,
            "url": target_url
        })

        # Send via pywebpush
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=priv_pem,
            vapid_claims={"sub": claim_email},
            ttl=86400
        )
        return True

    except WebPushException as ex:
        logger.warning(f"WebPush failed: {ex}")
        # If subscription has expired or unsubscribed (HTTP 404 or 410 Gone), remove it
        if ex.response and ex.response.status_code in (404, 410):
            delete_push_subscription(subscription["endpoint"])
        return False
    except Exception as e:
        logger.error(f"Unexpected error in send_browser_web_push: {e}")
        return False


def send_email_reminder(to_email: str, user_name: str, subject: str, body_text: str) -> bool:
    """
    Send an email reminder via standard SMTP if configured in .env.
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "notifications@studyhelper.ai")

    if not smtp_host or not smtp_user or not smtp_pass:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Agentic AI Study Helper <{smtp_from}>"
        msg["To"] = to_email

        html_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width:560px; margin:0 auto; padding:24px; border:1px solid #EADCE0; border-radius:14px; background:#FFFFFF;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:16px;">
                <span style="font-size:24px;">🎓</span>
                <span style="font-size:18px; font-weight:700; color:#802B45;">Agentic AI Study Helper</span>
            </div>
            <h2 style="color:#1A0A0F; margin-top:0; font-size:20px;">Hello {user_name}!</h2>
            <p style="color:#7A5864; font-size:14px; line-height:1.6;">
                {body_text}
            </p>
            <div style="background:#FDF7F8; border:1px solid #EADCE0; border-radius:10px; padding:14px; margin:20px 0;">
                <p style="margin:0; font-size:13px; color:#802B45; font-weight:600;">
                    💡 Consistent study sessions lead to better exam retention.
                </p>
            </div>
            <p style="font-size:12px; color:#9E828D; margin-top:24px;">
                Agentic AI Study Helper — AI Assistant
            </p>
        </div>
        """

        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return True
    except Exception as e:
        logger.error(f"Email reminder failed: {e}")
        return False


def dispatch_inactivity_notification(user: dict) -> bool:
    """
    Dispatch an inactivity reminder to a user across all configured channels
    (Web Push notifications, email fallback).
    """
    email = user["email"]
    name = user.get("name", "Student")

    title = "🎓 Agentic AI Study Helper"
    body = "You have some work remaining for this week. Open Study Helper and continue your progress."

    sent_any = False

    # 1. Try Browser Web Push subscriptions
    subscriptions = get_user_push_subscriptions(email)
    for sub in subscriptions:
        success = send_browser_web_push(sub, title=title, body=body)
        if success:
            sent_any = True
            record_notification_sent(
                email=email,
                notification_type="inactivity_reminder_7d",
                channel="webpush",
                status="sent",
                details=f"Endpoint: {sub['endpoint'][:35]}..."
            )

    # 2. Try Email fallback if configured
    email_success = send_email_reminder(
        to_email=email,
        user_name=name,
        subject="🎓 Study Helper — Continue Your Learning Progress",
        body_text=body
    )
    if email_success:
        sent_any = True
        record_notification_sent(
            email=email,
            notification_type="inactivity_reminder_7d",
            channel="email",
            status="sent",
            details=f"To: {email}"
        )

    # 3. If neither push nor email could be physically delivered (e.g. In local development without push permissions or SMTP),
    # log simulated dispatch to notification_logs and update last_reminder_sent so the state machine progresses accurately.
    if not sent_any:
        record_notification_sent(
            email=email,
            notification_type="inactivity_reminder_7d",
            channel="system_log",
            status="sent",
            details="Dispatched inactivity reminder log (no active push subscriptions / SMTP credentials)."
        )
        sent_any = True

    return sent_any
