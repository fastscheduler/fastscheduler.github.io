## 1. Introduction

This Privacy Policy explains how Maxim Mkrtchyan, an individual operator based in Armenia ("**we**", "**us**", or "**our**"), collects, uses, discloses, and protects personal data when you ("**you**" or "**the User**") use:

- **Fast Scheduler** — a Telegram bot for scheduling and automating messages to Telegram channels and groups, with companion payment, reporting, and data-management features (the "**Main Service**"); and
- **SetDate** — a companion Telegram bot that helps you build posting schedules and import them into the Main Service (the "**SetDate Service**").
- **Fast Support** — a companion Telegram bot for support conversations, help, feedback intake, and ratings (the "**Support Service**"); and
- **Our website** at https://fastscheduler.github.io/ — landing pages, help center, blog, and legal pages in English and Russian (the "**Website**", and together with the Main Service, the SetDate Service, and the Support Service, the "**Services**").

This policy applies to all personal data processed through the Services, including data collected via:
- The Main Service directly;
- Connected **Sender Bots** (Telegram bots whose tokens you provide so the Services can post on your behalf);
- The SetDate Service (when you choose to import a schedule);
- The Support Service (when you contact support or submit feedback and ratings);
- The Website (as described in Section 4(m) — essentially on-device preferences only); and
- Payment processing interactions with our third-party payment providers.

If you do not agree with this policy, please do not use the Services.

---

## 2. Definitions

- **Personal Data** means any information relating to an identified or identifiable natural person.
- **Processing** means any operation performed on Personal Data (collection, storage, use, disclosure, deletion, etc.).
- **Controller** means the entity that determines the purposes and means of Processing.
- **Processor** means an entity that Processes Personal Data on our behalf.
- **Telegram** means Telegram LLC / Telegram Messenger Inc. and its affiliated services.
- **Sender Bot** means a Telegram bot account whose token you provide to the Main Service so that the Service can post on your behalf to a channel you administer.
- **Premium** means a paid subscription tier (monthly or annual) provided by the Services.
- **SetDate** means a separate Telegram bot operated by us that helps you design posting schedules for import into the Main Service.
- **Support Service** means **Fast Support**, a separate Telegram bot operated by us for support conversations, help, feedback intake, and ratings.
- **Website** means our public informational website at https://fastscheduler.github.io/ (landing, help center, blog, legal pages), hosted as static files on GitHub Pages. The Website has no user accounts and no server-side processing of visitor data.

**Brand-name clarification:** **Fast Support** and **Fast Community** are names in the Fast Scheduler brand family. In these names, **“Fast” is a brand element**, not a promise or description that support responses, moderation, or community activity are instantaneous or faster than another service.

---

## 3. Who We Are (Data Controller)

The data controller responsible for your Personal Data is:

> **Maxim Mkrtchyan** (individual operator, Armenia — no office)
> Data protection contact: [fastschedulebot@gmail.com](mailto:fastschedulebot@gmail.com)
> Support: [FastSchedulerSupport_bot](https://t.me/FastSchedulerSupport_bot) (preferred contact — please do not spam personal chat)
> Personal Telegram: [@MaximalXP](https://t.me/MaximalXP)

Our hosting and infrastructure are provided by secure third-party cloud and database providers, which Process Personal Data as our Processors on servers located in the European Union.

---

## 4. Categories of Personal Data We Process

We Process the following categories of Personal Data:

### (a) Telegram identity and profile
- Telegram user ID (a numeric identifier assigned by Telegram).
- Telegram username (if set), first name, last name (as provided by Telegram).
- Your chosen interface language and time zone within the Services.
- Account creation timestamp and last-seen timestamp.
- Terms-acceptance record (timestamp of acceptance, your username at that time, and whether the account was new or already existing).

### (b) Channel and group data
- Identifiers of the Telegram channels and groups you connect (numeric IDs, titles, usernames).
- Whether a channel is administered by you directly or by a Sender Bot on your behalf.
- Channel connection timestamps and disconnection history.
- Channel administrator records (Telegram user IDs of appointed channel admins, their roles/permissions, and ownership-transfer or permission requests).

### (c) Messaging content — scheduled and recurring posts
- The full text, captions, media file identifiers (Telegram file_ids), formatting, inline buttons, and signatures you create for scheduled or recurring posts. This includes locations and venues you choose to schedule as message content (coordinates, titles, addresses).
- If you send a live location or coordinates to auto-detect your time zone, the coordinates are processed in memory only to resolve the time-zone name and are never stored.
- Recurring/calendar schedule definitions (frequency in CRON format, times, timezone).
- Stored message templates, poll configurations, quiz/checklist data.
- Imported schedule content received from the SetDate Service.
- Unique job IDs assigned to each scheduled or recurring message, used for tracking and delivery.

### (d) Connected Sender Bot credentials
- The Telegram bot token you submit to connect a Sender Bot. Tokens are **encrypted at rest** (AES-GCM) in a dedicated SQLite database and are **redacted** in all operational logs. We do not use these tokens for any purpose other than operating the Sender Bot on your instruction.
- The bot username, bot ID, and the channel ID to which the bot is linked.
- Management transfer status (whether primary management has been handed over to the Sender Bot).

### (e) Feedback, ratings, and support communications
- Free-text feedback messages and attachments (screenshots, logs, documents) you voluntarily submit through the `/feedback` command or feedback menu (in the Main Service or the Support Service).
- Replies about our official channel: the Main Service occasionally invites you to join our official channel, thanks you once when you join, and — if you later leave — asks once what could be improved. Your reply is stored as standard feedback and forwarded to the administrator through the Support Service (no matter which of our bots you were talking to); afterwards you are never asked about the channel again. To enable this, the bot checks your membership of the official channel at most once a day when you use the bot (a standard Telegram membership lookup — no additional data is collected).
- Support tickets (complaints): your ticket messages, category, status, and any optional attachments.
- Star ratings (1–5) and optional written reviews you leave through the in-bot rating buttons.
- Each submitted rating generates an internal notification to the administrator containing your name, @username, Telegram user ID, star count, review text, submission date, and your current Free/Premium status, so reviews can be moderated and answered (administrators can reply to your rating inside the bot).
- Diagnostic information you voluntarily share when reporting an issue (e.g., via "show my actions" or "report an issue"), which may include metadata about your recent in-bot activity (commands used, timestamps) needed to resolve the issue.

### (f) SetDate session data
- The language you select in the SetDate Service.
- A one-time schedule-building session (dates and times you choose) that is transmitted to the Main Service when you use the import feature. This data is transient and used only to fulfil the import.

### (g) Usage statistics and operational data
- **Message delivery statistics**: For each message sent, we record the channel ID, channel username, timestamp, and message type. These are stored in a dedicated statistics SQLite database (`data/stats.db`) and are used for aggregate reporting.
- **Message reaction and view counts**: We periodically collect reaction counts and view counts for messages sent through the Services, stored per-channel for leaderboard and statistics features.
- **Comment authors**: If your channel has a linked discussion group and one of our bots is a member of it, we record the public Telegram identity of users who comment on your bot-sent channel posts (their Telegram user ID, @username, first name, and last name as shown in Telegram) together with per-post comment counts. This is used exclusively to build the "top commentators" leaderboard and to attribute comments in statistics reports. It covers only comments on messages sent through the Services, never private messages, and is never shared with other users outside the statistics you choose to view.
- **Feature usage counts**: Counts of scheduled messages created, messages sent daily, recurring messages configured, signatures created, searches performed, and similar operational metrics.
- **Login/access records** for administrative staff, protected by a separate secret credential.

### (h) Signature data
- Saved message signature templates (text, formatting, inline buttons, attachment file_id, attachment media type).
- Signature position preference (above or below the message).
- Automatic signature assignment settings (per-channel auto-add configuration).

### (i) Search data
- Search query terms you enter through the in-bot search feature. Search is performed against your own scheduled/recurring messages and is not shared.

### (j) Promotional codes and referral program data
- Promo codes you apply and their usage history (discount received, subscription ID).
- Referral code assigned to your account, the user who referred you (if any), referral rewards earned and claimed, and the list of users you have referred.
- Referral reward expiration and claiming status.

### (k) Billing and subscription data
- Subscription status (Free or Premium), subscription tier (monthly or annual), payment provider used, subscription start and end dates.
- Telegram payment confirmations for Stars purchases (amount, currency, Telegram and provider charge identifiers).
- Payment retry history and frozen asset state (channels/bots/schedules flagged for disconnection during premium expiry).
- Freeze/grace period state and expiration dates.
- Cancellation requests and their processing status.

### (l) Web server operational data
- When payments are processed, we temporarily process payment confirmation data (subscription ID, user ID, price, currency, transaction status) to grant or revoke Premium access. Data received from the payment provider is processed strictly for subscription management and is not used for any other purpose.

### (m) Website and marketing attribution
Our Website is a static site (no user accounts, no server-side code of ours). It collects **no personal data on our servers**. Everything below stays in your own browser unless you click a link that opens our Telegram bot:

**Preferences stored only in your browser (local storage, never transmitted to us):**
| Key | Purpose |
| --- | --- |
| `theme` | Light/dark theme choice |
| `fs-lang` | Website language (English/Russian) |
| `fs-motion`, `fs-fx`, `fs-hotkeys`, `fs-hotkey-custom`, `fs-rail` | Display and accessibility preferences (animations, effects, hotkeys, navigation rail) |
| `fs-help-recents` | Your last few help-center searches (up to 6), used only to show "recent searches" |
| `site_clicks` | Your last link clicks on the site (up to 200), used for nothing but your own history — never transmitted |
| `cookie_consent` | Whether you accepted or declined the cookie banner |

**One functional cookie:** when you answer the cookie banner, we store a `consent=accepted|declined` cookie (1-year expiry, first-party only) so the banner does not reappear. It contains no identifier and is never used for tracking. Choosing "decline" changes nothing else — the site has no trackers to disable and works identically either way.

**Feature-flag check:** the site fetches a tiny public file (`storage_state.json`, a few bytes) about once a minute to know which features to display. This is a plain anonymous download — no identifier, cookie, or personal data is sent with it.

**Help search assistant:** the on-page help assistant (`help-ai`) runs **entirely in your browser** — your query never leaves your device and is processed by no server.

**Opening the bot from the Website:** buttons and pricing links open Telegram with a source tag (for example `?start=start__website`, `?start=premium_monthly__pricing`). The same mechanism also powers marketing source links shared anywhere (for example `?start=threads`, `?start=threads__post_1`). When you do, we record the **source tag** together with a timestamp and your Telegram user ID in an internal rotation-limited analytics file (`data/tracking.json`, capped at 10,000 entries, oldest overwritten automatically). This is used only in aggregate to understand which pages bring users to the bot, and is viewable by our staff via an internal command (`/track`). Simply browsing the Website — without opening the bot — records nothing on our side.

**Hosting and third parties:** the Website's files are served by **GitHub Pages** (GitHub, Inc., USA). GitHub necessarily receives standard connection data (such as your IP address) to deliver the pages, under GitHub's own privacy statement — we have no server logs of our own. All scripts, styles, and fonts are served from the same site (no CDNs, no external dependencies). The Website contains **no analytics, no advertising networks, no social-media pixels, no cross-site tracking cookies, and no third-party SDKs of any kind**. Links to Telegram, GitHub, or search engines naturally leave our site and are governed by those services' policies.

**Public indexing:** the Website's public pages (landing, help, blog, legal) are intentionally indexable by search engines and AI assistants (see `robots.txt`, `sitemap.xml`, `llms.txt`, and the blog RSS feed). They contain no personal data — only our own documentation and articles.

We do **not** intentionally collect special categories of Personal Data (e.g., health, biometric, political, religious data, trade-union membership). Message content you choose to schedule is your responsibility; you should avoid scheduling sensitive personal data about yourself or others.

---

## 5. Sources of Personal Data

We collect Personal Data from the following sources:

- **Directly from you**, when you interact with the Services by:
  - Sending commands and messages to the bot;
  - Connecting channels by providing a Telegram channel or group identifier;
  - Submitting a Telegram bot token to connect a Sender Bot;
  - Composing and saving scheduled messages, recurring schedules, and signatures;
  - Submitting feedback, ratings, reviews, and support requests;
  - Applying promo codes;
  - Participating in the referral program;
  - Using the search feature;
  - Configuring language, timezone, and other preferences.

- **Automatically from Telegram**, as part of operating a Telegram bot:
  - Telegram provides basic user/profile fields (user ID, username, first name, last name) with every interaction.
  - Message metadata such as timestamps, chat IDs, and reply contexts are inherent to the Telegram Bot API protocol.

- **From the SetDate Service**, when you choose to import a schedule you built in SetDate into the Main Service:
  - Your language preference and the schedule data (dates/times) are transmitted via a shared data file.

- **From the payment provider** (Telegram Stars):
  - We receive payment confirmations confirming payment status, subscription identifiers, and user identifiers for the purpose of granting or revoking Premium access. Telegram handles all payment data per its own terms.

We do **not** purchase Personal Data from third-party data brokers.

---

## 6. Legal Bases for Processing (GDPR Art. 6)

| Purpose | Legal basis |
| --- | --- |
| Providing the Services under our Terms of Service (message scheduling, delivery, account management, Sender Bot operation, schedule import/export, signature management, search, ratings, feedback processing) | Performance of a contract (Art. 6(1)(b)) |
| Processing payments, managing subscriptions, handling cancellations, processing retries | Performance of a contract (Art. 6(1)(b)) |
| Securing the Services, detecting and preventing fraud, abuse, unauthorised access, and security incidents | Legitimate interests (Art. 6(1)(f)) |
| Debugging, troubleshooting, and improving the Services | Legitimate interests (Art. 6(1)(f)) |
| Complying with tax, accounting, and legal retention obligations (e.g., retained subscription records) | Legal obligation (Art. 6(1)(c)) |
| Complying with lawful requests from authorities (court orders, subpoenas) | Legal obligation (Art. 6(1)(c)) |
| Optional features requiring explicit choice (e.g., non-essential notifications you opt into, referral program participation) | Consent (Art. 6(1)(a)) |
| Remembering your Website cookie-banner choice (first-party `consent` cookie, no tracking) | Consent (Art. 6(1)(a)) — set only after you click accept/decline; declining disables nothing because there is nothing to disable |
| Delivering the static Website to visitors (hosting-level connection handling by GitHub Pages) | Legitimate interests (Art. 6(1)(f)) — operating a public informational website; no visitor profiling is performed |

Where we rely on legitimate interests, we have balanced those interests against your rights and freedoms and conclude that operating, securing, and improving the Services represents a compelling, proportionate interest. You have the right to object to any Processing based on legitimate interests (see Section 13).

---

## 7. How We Use Personal Data

We use Personal Data for the following specific purposes:

1. **Account management**: Create and maintain your user profile, preferences (language, timezone), and subscription status.
2. **Message scheduling and delivery**: Store your scheduled and recurring message content, deliver messages to your connected channels/groups at the specified times via the Main Service or your Sender Bot.
3. **Sender Bot operation**: Use your provided bot token exclusively to authenticate and operate the Sender Bot for posting on your behalf.
4. **SetDate import**: Receive and process one-time schedule imports from the SetDate companion bot.
5. **Signature management**: Store and apply your saved signatures to scheduled messages.
6. **Search**: Enable you to search within your own scheduled and recurring messages.
7. **Payment processing and subscription management**: Process payments via Telegram Stars, grant/revoke Premium access, handle payment retries, manage premium expiry (freeze/grace period, asset disconnection).
8. **Promo codes and referrals**: Process promotional discounts and manage the referral reward program.
9. **Customer support**: Receive, store, and respond to feedback, ratings, and support requests; investigate and resolve reported issues.
10. **Ratings and reviews**: Collect, display, and moderate star ratings and written reviews.
11. **Statistics and analytics**: Generate aggregate, non-identifying usage statistics (e.g., total messages sent, popular features) to improve the Services.
12. **Security and abuse prevention**: Monitor for and prevent fraudulent, abusive, or unauthorized use of the Services; maintain audit logs of administrative actions; enforce rate limits; scan for security threats (e.g., injection attacks, token leaks).
13. **Marketing attribution**: Record the source of user arrivals from website/marketing campaigns for aggregate analysis (non-identifying reporting only).
15. **Website operation**: Serve public informational pages (landing, help center, blog, legal) in English and Russian; remember purely on-device display preferences (theme, language, accessibility options); record the source tag only when you click through from the Website into our Telegram bot.
14. **Legal compliance**: Comply with applicable legal and regulatory obligations.

We do **not**:
- Sell your Personal Data to third parties.
- Use your Personal Data for automated individual decision-making or profiling with legal effects.
- Use your Sender Bot token for any purpose other than operating your Sender Bot on your instruction.

---

## 8. Sharing and Disclosure

We share Personal Data only as necessary to provide the Services:

- **Telegram** — All interactions pass through Telegram's servers. Telegram acts as an independent controller for data it Processes under its own Privacy Policy (https://telegram.org/privacy). We have no control over how Telegram handles data transmitted through its platform.

- **Telegram Stars** (for in-app payments via Telegram) — Payments are processed entirely within Telegram's infrastructure. Telegram handles all payment data per its own terms. We receive only a successful-payment confirmation from Telegram.

- **Infrastructure (hosting and database)** — All stored Personal Data is processed by secure third-party cloud and database providers acting as our Processors, with data hosted in the European Union. Their processing is covered by their data-processing terms.

- **GitHub Pages (Website hosting only)** — Our public Website's static files are served by GitHub, Inc. (USA). GitHub processes standard connection data (e.g., IP address) required to deliver the pages, under GitHub's own privacy statement. We operate no server-side code on the Website and keep no visitor logs of our own.

- **SetDate companion bot** — Shares a minimal data file (user language preference and an ephemeral schedule-building session) via a local file on the same server, only when you explicitly use the import feature.

- **Authorities and legal recipients** — We disclose Personal Data to authorities only where required by valid legal process (such as a court order or subpoena under Armenian law) or to protect our rights, users, or the public against imminent harm:
  - We disclose the **minimum data necessary** to comply — never bulk exports of user data;
  - We challenge overbroad or unclear requests where legally permitted;
  - We will notify you of the disclosure unless prohibited by law or court order (e.g., a gag order);
  - We do not voluntarily sell or hand over user data to any government outside such process.
- Note that Telegram may itself be compelled under its own jurisdiction and disclose data per its own policies — we have no control over those independent disclosures.

- **Service integrations**: We operate a local Node.js API server (if configured) for payment invoice generation. No user data is transmitted to external services beyond those listed above.

We require all Processors to be bound by contractual data protection terms that provide at least the same level of protection as this Privacy Policy.

---

## 9. International Data Transfers

Personal Data may be transferred to and Processed in countries outside your country of residence, including:

- **The European Union** — our cloud and database providers host data on servers in the EU.
- **The United States and other global locations** — Telegram operates globally; GitHub, Inc. (USA) serves our static Website files to visitors.

Where transfers are made from the EEA, UK, or Switzerland to third countries that have not received an adequacy decision from the European Commission, we rely on appropriate safeguards such as:

- The European Commission's **Standard Contractual Clauses (SCCs)** adopted under Article 46(2) of the GDPR;
- The **UK International Data Transfer Addendum** (where applicable);
- The safeguards maintained by our Processors.

You may request a copy of the relevant safeguards by contacting fastschedulebot@gmail.com (redacted as necessary to protect commercial confidentiality).

---

## 10. Data Retention

We retain Personal Data only for as long as necessary to fulfil the purposes described in this Policy, or as required by law.

| Data category | Retention period | Notes |
| --- | --- | --- |
| **Scheduled and recurring message content** | Until you delete the individual message or schedule, or until you delete your account | You can delete individual messages at any time via the in-app interface. |
| **Sender Bot tokens** | Until you disconnect the Sender Bot or delete your account | Tokens are permanently deleted upon disconnection; no soft-delete or backup copy is retained. |
| **Channel connection data** | Until you disconnect the channel or delete your account | |
| **User profile and preferences** | Until you delete your account | Language, timezone, subscription status. |
| **Usage statistics (stats.db)** | Individual delivery records: 365 days (rolling); aggregates indefinite | Individual message delivery records (including recorded comment authors) are pruned after 365 days; aggregated statistics are retained for service improvement. |
| **User action logs** | 30 days (rolling) | A log of recent in-bot actions (up to 60 per user) is retained for security and support. These are **encrypted at rest** (AES-GCM). A "privacy mode" toggle exists to disable collection of these logs entirely. |
| **Issue/diagnostic logs** | 30 days (rolling) | Logs of reported issues and diagnostic data are **encrypted at rest** (AES-GCM) and automatically purged. |
| **Feedback and ratings** | Indefinite, or until you request removal | Retained to operate support and improve the Services. You may request removal of specific feedback or ratings. |
| **Marketing attribution (tracking.json)** | Maximum 10,000 entries (rotation) | Capped file; oldest entries are overwritten automatically. |
| **Website on-device data (your browser only)** | Until you clear it | Theme, language, display preferences, recent help searches, on-device click history, and the `consent` cookie (1-year expiry) live exclusively in your browser. We cannot see, access, or delete them — clearing your browser data removes them. |
| **Website delivery (GitHub Pages)** | Per GitHub's retention | We keep no visitor logs; connection data handling is governed by GitHub's privacy statement. |
| **Referral program data** | Until you delete your account or until referral rewards expire | |
| **Promo code usage records** | Indefinite | Required for fraud prevention and financial record-keeping. |
| **Billing and subscription records** | As required by tax/accounting law (typically 5-7 years) | Payment processing is handled by Telegram. We retain only minimum subscription-status records. |
| **Recovery snapshots** | 45 days after account erasure | When your account is erased, a recovery snapshot is retained for up to 45 days in case the request was mistaken or unauthorized, after which it is automatically and permanently purged. |

### Account deletion process
There is no self-serve account wipe in the bot: the **`/delete`** command deletes scheduled/recurring messages and stored media only.
To erase your entire account, contact the support bot (https://t.me/FastSchedulerSupport_bot) or fastschedulebot@gmail.com from your Telegram account. The process works as follows:
1. You request erasure; we verify the request comes from the account owner.
2. Your data is deleted across all per-user categories within 7 business days (only tax-required billing records are retained).
3. A recovery snapshot is retained for 45 days, then automatically and permanently erased.

To cancel a pending erasure, contact us before the snapshot expires.

### Privacy Mode
The Services include a **Privacy Mode** feature (accessible to administrators) that, when enabled, pauses the collection of non-essential diagnostic action logs (`user_actions`). Essential operational data (scheduled messages, channel connections, tokens, subscription status) is never affected by Privacy Mode and is always retained according to the retention schedule above.

---

## 11. Security

We implement technical and organisational measures appropriate to the nature and risk of the Personal Data we Process:

### Encryption

| Data | Encryption method | Key management |
| --- | --- | --- |
| **Sender Bot tokens** (in SQLite database `bot.db`) | **AES-256-GCM** | Encryption key provided via environment variable (`TOKEN_ENCRYPTION_KEY`, 32-byte base64-encoded). |
| **User action logs** (file `user_actions.json`) | **AES-256-GCM** | Key is PBKDF2-derived from `TOKEN_ENCRYPTION_KEY` with a random salt. |
| **Issue/diagnostic logs** (file `issues.json`) | **AES-256-GCM** | Same key derivation as user action logs. |
| **Exported backup files** (`.fspback` — Fast Scheduler Protected Backup) | **AES-256-GCM + HMAC-SHA256** | Encrypted with a key derived from the user-supplied password combined with `FILE_ENCRYPTION_KEY`. |
| **Standard backup files** (`.fsback` — Fast Scheduler Backup) | **HMAC-SHA256** (integrity only, no encryption) | Key derived from `FILE_ENCRYPTION_KEY`. |
| **Bot data storage domains** (JSON files such as scheduled messages, channels, user settings) | **No encryption at rest** | These files contain operational data (message text, channel IDs, preferences) but no credentials. Encryption is not applied as the data needs to be read frequently for bot operation. The data is protected by filesystem-level access controls (see below). |

### Organisational and technical measures
- **Credential redaction**: All bot tokens and sensitive credentials are redacted (masked) in operational logs.
- **Administrative access control**: Administrative functions are protected by a separate secret credential (`ADMIN_PASSWORD`), which is not shared with end users. Administrative dashboards require an additional token (`ADMIN_DASHBOARD_TOKEN`).
- **Rate limiting**: The Services implement per-user rate limiting for actions such as channel connection, message scheduling, and bot creation to prevent abuse.
- **Security monitoring**: The Services include an automated security scanner that detects and logs potential threats including SQL injection attempts, shell injection attempts, cross-site scripting (XSS), token leaks in messages, and path-traversal attacks.
- **Webhook security**: CryptoBot payment webhooks, where enabled, are verified using **SHA-256** with an API key.
- **Deep-link signing**: Certain start parameters are signed with a `DEEP_LINK_SECRET` to prevent tampering.
- **IDOR protection**: Access to other users' data (ratings, channels, schedules) is prevented by explicit ownership checks (`_owns_channel`, `_owns_rating`) throughout the codebase.
- **Blocked users**: Users who violate the Terms of Service may be blocked. Blocked users cannot use the Services.
- **Regular backups**: Operational data is backed up periodically. Backup files are stored on the same server and are subject to the same access controls.

No method of transmission or storage is 100% secure. While we strive to protect your Personal Data using appropriate technical and organizational measures, we cannot guarantee absolute security.

---

## 12. Children

The Services are not directed to children under the age of 13 (or the applicable minimum age in your jurisdiction). Telegram requires users to be at least 13 years old to use its platform.

The Website itself is general-audience informational content (documentation, guides, legal pages) with no accounts, no age gate, and no data collection from visitors of any age. The 13+ requirement applies to using the Telegram bots (per Telegram's own age requirement). We do **not** knowingly collect Personal Data from children below the applicable minimum age. If you believe that a child has provided us with Personal Data without the requisite parental or guardian consent, please contact us immediately at fastschedulebot@gmail.com. If we become aware that we have inadvertently collected Personal Data from a child below the applicable minimum age, we will take steps to delete that information promptly.

---

## 13. Your Rights

Subject to applicable law (including the EU General Data Protection Regulation, the UK GDPR, the Brazilian Lei Geral de Proteção de Dados, and similar privacy regimes), you have the following rights regarding your Personal Data:

| Right | Description |
| --- | --- |
| **Access** | Request a copy of the Personal Data we hold about you. |
| **Rectification** | Request correction of inaccurate or incomplete Personal Data. |
| **Erasure** ("right to be forgotten") | Request deletion of your Personal Data, subject to legal retention obligations. |
| **Restriction** | Request restriction of Processing in certain circumstances (e.g., while a rectification request is pending). |
| **Objection** | Object to Processing based on legitimate interests, including Processing for direct marketing. |
| **Data portability** | Receive your Personal Data in a structured, commonly used, machine-readable format (JSON). |
| **Withdraw consent** | Withdraw consent at any time where Processing is based on consent. Withdrawal does not affect the lawfulness of Processing before withdrawal. |
| **Lodge a complaint** | Lodge a complaint with your local data protection supervisory authority. |

### Exercising your rights in-bot

You can exercise most of your rights directly through the Services:

- **`/delete`** — Delete scheduled or recurring messages and stored media (content-level deletion, not account erasure).
- **Account erasure** — There is no self-serve wipe; request it via the support bot or privacy email (see Section 10).
- **`/export`** / **`/backup`** — Download a full backup of your data (`.fsback` or `.fspback` format), including scheduled messages, recurring schedules, channel connections, settings, signatures, referral data, and more.
- **`/signature`** — Manage and delete your saved signatures.
- **Disconnect Sender Bots** — Removes their tokens and associated linkage from our systems.
- **Disconnect channels** — Removes channel associations and redirects scheduled messages.
- **`/cancel`** — Cancel any in-progress operation.
- **`/legal`** — Open the legal menu with links to the Privacy Policy, Terms of Service, and Refund Policy.
- **Contact support** — If you cannot use the in-bot tools above, message the support bot (https://t.me/FastSchedulerSupport_bot) and access, export, or deletion requests will be processed manually after verifying you through your Telegram account.

For requests that cannot be fulfilled through the in-bot interface (e.g., complex data-access requests, objection to Processing based on legitimate interests), please contact us at fastschedulebot@gmail.com. We will respond to your request within the timeframe required by applicable law (generally **one month** under the GDPR, extendable by two months for complex requests).

We may need to verify your identity before processing your request. We will not discriminate against you for exercising your privacy rights.

---

## 14. Cross-Bot Data Sharing

The Services consist of multiple cooperating Telegram bots. This section describes how data flows between them.

### Main Service and SetDate
- **What is shared**: When you use SetDate to build a posting schedule and choose to import it into the Main Service, the SetDate bot writes your Telegram user ID, selected language, and the schedule data (dates/times) to a local shared file on the same server.
- **How it is used**: The Main Service reads this file once to create the corresponding scheduled messages, then leaves the data in place (SetDate may overwrite it on subsequent sessions).
- **How long it is retained**: The shared file is not automatically deleted; however, it contains only the most recent session. No historical schedule data is accumulated.

### Main Service and Sender Bots
- **Sender Bots are separate Telegram bot applications**, each with their own token, running in the same process as the Main Service (managed by a `BotLifecycleManager`).
- **What is shared**: When management is transferred to a Sender Bot, the Main Service redirects certain user interactions to the Sender Bot via Telegram deep links. Scheduled messages are delivered through the Sender Bot (using its token) rather than through the Main Service's bot token. The Sender Bot reads the same shared data stores (scheduled messages, user settings, channels) from the same server.
- **Encryption**: The Sender Bot's token is stored encrypted at rest (AES-GCM) in the token database and is decrypted in memory only when the bot needs to operate.
- **User data separation**: A Sender Bot only processes data for the user who owns it. It does not have access to other users' data.

---

## 15. Logging and Monitoring

### Operational logs
The Services maintain several categories of logs:
- **Structured JSON logs** (`data/logs/bot_structured.json`): Rotated at 5 MB per file, with up to 3 backup copies retained. These logs record operational events (commands received, messages sent, errors encountered) and may contain user IDs and message metadata, but do **not** contain message content or bot tokens (tokens are redacted).
- **Standard log files** (`data/logs/app.log`): General application logs with similar content and rotation.

### Audit log
Administrative actions (e.g., granting Premium, blocking users, modifying settings) are recorded in a permanent **audit log** (`data/admin/audit_log.json`) with the admin's user ID, action description, and timestamp. This log is viewable only by authorized administrators.
### Error reports (what the administrator sees when something breaks)
When an error occurs in the bot, you only ever see a generic message ("An error occurred"). Behind the scenes the administrator receives a detailed error report containing: your Telegram user ID, the error type and technical details (tokens redacted), and your last actions before the error (e.g., which command you ran or button you pressed — never message content). Follow-up actions after the error may be appended. Reports are stored in the encrypted issue log with a unique issue ID so recurring errors can be tracked and fixed. This processing is necessary to operate and debug the Services.

### Security monitoring
The Services include an automated security scanner that inspects incoming messages and commands for patterns indicative of:
- SQL injection attempts
- Shell/command injection attempts
- Cross-site scripting (XSS) attempts
- Telegram bot token leaks
- Path-traversal attacks
- IP/hostname extraction patterns suggesting reconnaissance

When a potential threat is detected, the event is logged with the user's ID, the detected pattern type, and the offending input (redacted). The user may be blocked from using the Services if the activity is deemed malicious. No automated action is taken against a user based solely on a single detection.

---

## 16. Changes to This Policy

We may update this Privacy Policy from time to time to reflect changes in our data practices, legal requirements, or the Services themselves.

- Material changes will be announced through the Services (e.g., via a notice in the bot).
- The "Last updated" date at the top of this policy will reflect the date of the latest revision.
- We encourage you to review this Privacy Policy periodically.

Your continued use of the Services after changes take effect constitutes your acceptance of the updated policy.

---

## 17. Contact

Questions, concerns, or requests regarding this Privacy Policy or our data practices:

> **Maxim Mkrtchyan** (individual operator, Armenia — no office)
> Privacy contact: [fastschedulebot@gmail.com](mailto:fastschedulebot@gmail.com)
> Support: [FastSchedulerSupport_bot](https://t.me/FastSchedulerSupport_bot) (preferred contact — please do not spam personal chat)
> Personal Telegram: [@MaximalXP](https://t.me/MaximalXP)

For data-protection supervisory authority contact information in the European Economic Area, the UK, Switzerland, or other jurisdictions, please refer to your local data protection authority's website.

---
