# Website security and reliability audit

**Date:** 2026-10-06  
**Scope:** `website/` static site and the `src/web_server.py` HTTP service that can serve the dashboard/webhook host.  
**Method:** read-only source review of generated HTML, JavaScript, deployment files, response-header configuration, public data files, and dashboard middleware. No application code was changed.

## Executive summary

The public website is predominantly static and does not contain an obvious Telegram token, payment secret, database credential, or third-party script. Search and rendering code generally escapes user-entered search text, and external links consistently use `rel="noopener noreferrer"`.

There are two findings that should be treated as release blockers for a security-sensitive deployment:

1. The dashboard origin check raises `NameError` for requests that include an `Origin` header, so authenticated browser requests can fail with HTTP 500 (`src/web_server.py:200-214`).
2. The site is canonicalized and published on GitHub Pages, while `website/_headers` explicitly says GitHub Pages ignores that file. The deployed site therefore cannot be assumed to receive the HSTS, CSP, clickjacking, MIME, and cross-origin headers listed there.

The remaining findings are hardening and operational issues: the CSP allows `unsafe-inline`, dashboard and webhook traffic share the public listener, CORS preflight is not implemented, and the consent cookie should be marked `Secure`.

## Findings

### W-01 — Response security headers are not guaranteed on the actual host (High)

**Evidence:** `website/_headers:1-4` says the file is for Cloudflare Pages/Netlify and that GitHub Pages ignores it. The canonical URLs and sitemap point to `https://fastscheduler.github.io/` (for example `website/index.html:12` and `website/sitemap.xml`). The header rules are only declared in `website/_headers:10-18`.

**Impact:** On the GitHub Pages deployment, the response-level `Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, COOP, and CORP headers may be absent. The HTML meta CSP cannot supply all of these protections, especially `frame-ancestors`. This weakens protection against clickjacking, MIME confusion, framing, and future script injection.

**Action:** Deploy behind a host that applies `_headers` (Cloudflare Pages/Netlify or a controlled reverse proxy), or configure equivalent response headers at the actual edge. Verify with an external `curl -I` check for the production URL. Keep HSTS only after every subdomain is HTTPS-only.

### W-02 — CSP depends on `unsafe-inline` (Medium)

**Evidence:** The page CSP in `website/index.html:7`, `website/help.html:7`, and `website/blog/index.html:24` allows `script-src 'self' 'unsafe-inline'` and `style-src 'self' 'unsafe-inline'`.

**Impact:** Any HTML injection in a generated page, future template, or compromised same-origin asset can execute inline JavaScript. This removes much of the XSS value of the CSP. The risk is amplified by the site’s large generated HTML and inline bootstrap scripts.

**Action:** Move inline JavaScript and CSS to versioned same-origin files. Where inline code is unavoidable, use per-response nonces or stable hashes and remove `unsafe-inline`. Add a report-only CSP during migration and test every localized/legal page.

### W-03 — Dashboard origin guard crashes on browser requests (High reliability / security)

**Evidence:** `src/web_server.py:200-214` defines `_origin_allowed()` and calls `urlparse(origin).netloc` at line 211, but `urlparse` is not imported in that function or at module scope. A separate import exists later inside `auth_middleware` at `src/web_server.py:242`, which does not make the name available to `_origin_allowed()`.

**Impact:** An authenticated request containing an `Origin` header reaches the guard and raises `NameError`. The error middleware converts it to HTTP 500. Normal same-origin browser calls can therefore break, and an attacker who can cause authenticated browser traffic can turn the dashboard into an availability target.

**Action:** Import `urlparse` at module scope (or inside `_origin_allowed`) and add a regression test for same-origin, allowed cross-origin, disallowed-origin, and malformed-origin requests.

### W-04 — CORS preflight is not supported (Medium reliability)

**Evidence:** Dashboard routes register only `GET` and `POST` handlers (`src/web_server.py:553-570`). The middleware requires bearer authentication for every non-webhook/non-health path (`src/web_server.py:216-230`), while the response code advertises `Access-Control-Allow-Methods: GET, POST, OPTIONS` (`src/web_server.py:238-250`). There is no `OPTIONS` route or preflight short-circuit.

**Impact:** A legitimate dashboard frontend hosted on an allowed origin will send an `OPTIONS` preflight for many JSON POST requests and receive `401 Unauthorized` instead of the advertised CORS response. This can look like a broken or intermittently unavailable dashboard.

**Action:** Either keep the dashboard strictly same-origin and remove CORS advertising, or implement an authenticated-safe `OPTIONS` handler that validates the requested origin and requested headers without performing a state-changing action.

### W-05 — Dashboard and webhook share a public listener (Medium)

**Evidence:** `start_web_server()` binds the webhook app to `0.0.0.0` on `WEBHOOK_PORT` (`src/web_server.py:609-610`). Dashboard routes are registered in the same app (`src/web_server.py:553-570`). A second dashboard listener is bound to `127.0.0.1` only when its port differs (`src/web_server.py:612-615`).

**Impact:** If the public webhook port is exposed directly, the dashboard API is also reachable from the Internet and relies entirely on the bearer token, rate limiting, and proxy configuration. A leaked or brute-forced dashboard token grants user-data and administrative mutation capabilities.

**Action:** Serve the dashboard only on a private listener or an authenticated reverse proxy/network allowlist. Do not publish the webhook listener as the dashboard origin. Ensure production TLS terminates before any bearer token is accepted and rotate `ADMIN_DASHBOARD_TOKEN` after suspected exposure.

### W-06 — Generated feature values are inserted with `innerHTML` (Low/Medium hardening)

**Evidence:** `website/scripts/main.js:45-60` escapes comparison-table values, but the feature list at `website/scripts/main.js:91-97` concatenates `r.label` and `value` into `innerHTML`. These values currently come from generated `website/scripts/site-config.js`, not from a visitor request.

**Impact:** This is not an observed reflected XSS in the current static data, but a compromised build input or future CMS/config value could inject markup or script into every page using the feature list. It also makes security review dependent on every generator input remaining trusted.

**Action:** Build the nodes with `textContent` and DOM APIs; keep only the fixed SVG markup as trusted static markup. Validate generated config fields at build time and fail the build on unexpected HTML.

### W-07 — Consent cookie is not marked `Secure` (Low)

**Evidence:** `website/scripts/main.js:173-177` writes `consent=...;path=/;max-age=31536000;samesite=lax` without the `Secure` attribute.

**Impact:** If a user reaches the site over plaintext HTTP before a redirect, the browser may send the cookie over HTTP. GitHub Pages normally redirects to HTTPS, but the property is safer when the cookie itself is constrained.

**Action:** Add `Secure` (and retain `SameSite=Lax`). A client-created cookie cannot be `HttpOnly`; keep it non-sensitive as it is today.

### W-08 — Public feature-state file reveals deployment timing and feature state (Informational)

**Evidence:** `website/storage_state.json` is publicly fetched every minute by `website/scripts/main.js:134-148` and contains `mediaStorageEnabled` and an exact `updatedAt` timestamp.

**Impact:** This is not sensitive by itself, but it exposes operational change timing and allows visitors to observe feature toggles. Any future addition of account, environment, or error data to this file would become public immediately.

**Action:** Keep the file limited to a boolean feature flag, avoid operational timestamps unless needed, and add a build/deployment check that rejects secrets, IDs, URLs containing credentials, or stack traces from public JSON assets.

## Checked areas with no issue found

- No Telegram bot token, payment credential, database password, or API key was found in the website assets reviewed. Public configuration contains pricing, usernames, contact addresses, and feature metadata only.
- Search terms are entity-encoded before being inserted into the help/blog result markup (`website/scripts/help-hub.js` and `website/scripts/blog-hub.js`).
- External links opened in a new tab were found with `rel="noopener noreferrer"` in the reviewed generated pages.
- The intended header policy includes `frame-ancestors 'none'`, `nosniff`, HSTS, and cross-origin isolation directives; the unresolved issue is whether the production host actually applies `website/_headers`.
- `robots.txt` intentionally allows crawling and publishes a sitemap. This is an information-disclosure/SEO decision, not an access-control boundary; no private route should be placed in the public website tree.

## Recommended verification before release

1. Run `curl -sSI https://fastscheduler.github.io/` and confirm the actual response headers, redirects, content types, and HSTS behavior.
2. Exercise dashboard requests with no `Origin`, same-origin `Origin`, allowed cross-origin `Origin`, disallowed `Origin`, malformed `Origin`, and an `OPTIONS` preflight.
3. Confirm the dashboard port is not publicly reachable in the cloud firewall/reverse-proxy configuration.
4. Add a static build scan that rejects secret-like values and unexpected HTML in generated JSON/config files.
5. Test CSP in report-only mode across English/Russian, help, blog, and legal/history pages before removing `unsafe-inline`.

## Limitations

This was a source-only review. I did not run a production HTTP scan, browser penetration test, dependency audit, or cloud firewall inspection. The local Python runtime was unavailable for executing the service, so runtime behavior should be verified in CI/staging after W-03 and W-04 are corrected.
