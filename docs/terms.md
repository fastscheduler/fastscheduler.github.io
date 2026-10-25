## 1. Acceptance of Terms

By accessing or using **Fast Scheduler** ("Main Service"), **SetDate** ("SetDate Service"), **Fast Support** ("Support Service"), and our public website at https://fastscheduler.github.io/ ("Website" — landing, help center, blog, and legal pages, and together the "**Services**") operated by Maxim Mkrtchyan, an individual operator based in Armenia ("**we**", "**us**", "**our**"), you agree to be bound by these Terms of Service ("**Terms**"). If you do not agree, do not use the Services.

These Terms incorporate our **Privacy Policy** and, where you purchase a subscription, the refund terms in our **Refund Policy**.

**Brand-name clarification:** **Fast Support** and **Fast Community** are names in the Fast Scheduler brand family. In these names, **“Fast” is a brand element**, not a promise or description that support responses, moderation, or community activity are instantaneous or faster than another service.

When you first interact with the Services, you will be presented with these Terms and asked to accept them. You will not be able to use the Services until you have accepted. The commands `/legal`, `/help`, `/language`, `/cancel`, and `/start` remain accessible even before acceptance so you can review these documents.

---

## 2. Definitions

- **User / you** — any person using the Services.
- **Channel** — a Telegram channel, group, or supergroup you connect to the Main Service.
- **Sender Bot** — a Telegram bot whose token you provide so the Services can post messages to your Channels on your behalf.
- **Premium** — a paid subscription tier (monthly or annual) unlocking higher usage limits and priority features.
- **Free Tier** — the no-cost usage level with standard limits.
- **SetDate** — a companion Telegram bot operated by us that helps you design posting schedules for import into the Main Service.
- **Support Service** — **Fast Support**, a companion Telegram bot operated by us for support conversations, help, feedback intake, and ratings.
- **Website** — our public informational website (landing, help center, blog, legal pages, in English and Russian), hosted as static files with no user accounts. Browsing the Website requires no acceptance step, but the Acceptable Use (Section 8), Intellectual Property (Section 9), Disclaimers (15), and Liability (16) provisions apply to it.
- **Scheduled Message** — a one-time message (text, media, poll, quiz, or rich content) configured to be delivered at a specific date and time.
- **Recurring Message** — a message configured to repeat on a schedule (using CRON expressions, e.g., daily, weekly, on specific days).
- **Signature** — a saved text/media template automatically appended to or prepended to your scheduled messages.
- **Promo Code** — a promotional discount code applied to reduce the price of a Premium subscription.
- **Referral Program** — our program that rewards users with Premium days for inviting new users to the Services.
- **Data Export** — a downloadable file (`.fsback` or `.fspback`) containing your data from the Services.
- **Freeze / Grace Period** — the period after Premium expiry during which excess channels, bots, and schedules are temporarily preserved but inaccessible, giving you time to renew or choose what to keep.

---

## 3. Eligibility

You represent and warrant that you:

- Are at least **13 years old** (or the minimum age of digital consent in your country of residence, whichever is higher);
- Have a valid Telegram account in good standing;
- Are not located in a country or region subject to trade sanctions or embargoes that would prohibit use of the Services;
- Are not on any trade-restriction list maintained by your country or the United Nations;
- Will comply with Telegram's Terms of Service (https://telegram.org/tos) and Telegram Bot Platform Policy.

We reserve the right to refuse, suspend, or terminate access to the Services for any violation of these Terms, including but not limited to the Acceptable Use provisions in Section 8.

---

## 4. Description of the Services

The Services provide a comprehensive message-automation platform for Telegram. The full feature set includes:

1. **Message scheduling**: Schedule one-time messages (text, photos, videos, documents, polls, quizzes, checklists, rich content) to be delivered to your Telegram channels/groups at a specific date and time. Supports timezone-aware scheduling per channel.

2. **Recurring messages**: Configure messages that repeat on a schedule (CRON-based: daily, weekly, monthly, on specific weekdays, or custom intervals). Recurring messages can expire after a set number of repetitions or on a specific date.

3. **Batch scheduling**: Send multiple date+message pairs in sequence to create multiple scheduled messages in one conversation.

4. **Sender Bots**: Connect your own Telegram bot by providing its token. The Services can then post scheduled messages through your bot instead of through the main bot. You can have multiple Sender Bots (limits depend on your subscription tier). Sender Bots can be linked to specific channels and can optionally take over primary management of those channels.

5. **Manage multiple channels**: Connect multiple Telegram channels/groups to the Services (limits depend on your subscription tier). Each channel can have its own timezone and default settings.

6. **Message signatures**: Create and save signature templates (text with formatting, inline buttons, optional attachment) that are automatically added above or below your scheduled messages. Signatures can be assigned to specific channels for automatic inclusion.

7. **Poll, quiz, and checklist creation**: Create polls (anonymous/quiz mode), multi-question quizzes, and checklists as scheduled messages. Note that polls in channels must be set to anonymous mode.

8. **Search**: Search within your own scheduled and recurring messages by keyword, channel, or date range.

9. **Import and export**: Export your full data as a `.fsback` (Fast Scheduler Backup) or `.fspback` (Fast Scheduler Protected Backup, password-encrypted) file. Import previously exported data to restore schedules, channels, signatures, and settings. Supports import from TXT, RTF, ODT, CSV, JSON, `.fsback`, and `.fspback` formats.

10. **SetDate companion bot**: Use SetDate to visually design a posting calendar (dates and times) and import the resulting schedule directly into the Main Service via an in-bot link.

11. **Premium subscriptions**: Subscribe to Premium (monthly or yearly) for higher limits, priority processing, and exclusive features (see Section 11).

12. **Referral program**: Earn Premium days by inviting other users to the Services (see Section 14).

13. **Promo codes**: Apply promotional discount codes to reduce Premium subscription prices.

14. **Feedback and ratings**: Submit feedback, rate the Services (1–5 stars), and leave written reviews visible to other users.

15. **Statistics and leaderboards**: View per-channel message delivery statistics and paginated leaderboards (top posts by views, comments, or reactions — up to 50 entries per page — plus a top-commentators ranking) for Premium subscribers. All statistics cover only messages sent through the Services.

16. **Automated reports**: Generate and receive periodic (every 3/6/12 hours, daily, weekly, monthly, quarterly, yearly) statistics reports via Telegram, delivered in the recipient's own timezone, for Premium subscribers.

17. **Backup and restore**: The Services maintain internal backups of your data. You can trigger manual exports at any time.

18. **Support conversations**: Contact support, get help, and submit feedback or ratings through the Support Service.

19. **Public website**: Browse landing, help-center, blog, and legal pages in English or Russian with no account required. The Website stores display preferences (theme, language, accessibility options) only in your own browser, shows a cookie banner recording a first-party consent choice, and links into the Telegram bots with source tags used for aggregate arrival analytics (see Privacy Policy). The Website contains no analytics, trackers, or third-party scripts.

The Services are provided "as is" and "as available" (see Section 15). Features may be added, modified, or removed with reasonable notice.

---

## 5. Sender Bots (Your Connected Bots)

When you connect a Sender Bot to the Services by providing its Telegram bot token:

- **You remain the sole controller and responsible party** for that bot's activity, including all messages it posts. The Services act as a processor acting on your instructions.
- You must own, have created, or be expressly authorized to administer any Channel the Sender Bot posts to.
- The bot token is stored **encrypted at rest** (AES-256-GCM) and is used solely to authenticate and operate the Sender Bot to send messages on your instruction.
- You are responsible for keeping your bot token confidential. If your token is compromised, you should revoke it immediately via Telegram's BotFather and disconnect the bot within the Services.
- Disconnecting a Sender Bot permanently removes its token from our encrypted token database. No copy of the token is retained.
- The Services are not liable for any actions taken by your Sender Bot, including but not limited to messages posted under your instruction, messages posted due to misconfiguration (wrong time, wrong channel, wrong content), or unauthorized access to your bot token by third parties.
- Sender Bots may be created and connected through the in-bot `/addbot` and `/bots` interfaces:
  - **Via token submission**: You provide a bot token, and we verify it with Telegram and check that the bot is an administrator of the target channel.
  - **Via Managed Bot creation (Telegram's Managed Bots flow)**: You tap a creation link, confirm the new bot in Telegram, and we receive its token automatically via Telegram's API — no copy-paste needed.

---

## 6. SetDate Integration

SetDate is a companion bot operated by us that helps you design a posting schedule (dates and times) visually.

- When you use the **import feature** in SetDate, the following data is transmitted from SetDate to the Main Service via a local shared file on the same server:
  - Your Telegram user ID;
  - Your selected language in SetDate;
  - The schedule data (list of date/time pairs you selected).
- This data is used **solely** to create the corresponding scheduled messages in the Main Service.
- The SetDate Service does **not** have access to your existing scheduled messages, channel connections, or any other data stored in the Main Service beyond what you explicitly choose to import.
- No unrelated Personal Data is shared between the two bots beyond what is necessary for the import.

---

## 7. Accounts and Responsibilities

- **Account ownership**: Your account is tied to your Telegram user ID. You are responsible for all activity that occurs under your Telegram account. If you lose access to your Telegram account, we may not be able to restore your data.
- **Content responsibility**: You are solely responsible for all content you schedule, post, or transmit through the Services. You represent and warrant that your content complies with applicable law and does not infringe the rights of any third party.
- **Configuration accuracy**: You are responsible for configuring correct timezones, target channels, schedule times, and message content. We are not liable for messages sent at the wrong time, to the wrong channel, or with incorrect content resulting from your configuration errors.
- **Marketing attribution**: When you arrive at the bot from a link on our Website (including pricing buttons that preselect a plan, e.g. `premium_monthly__pricing`), an advertising campaign, or a referral link, we may record the source of that arrival for aggregate marketing analytics, as further described in our Privacy Policy.
- **Multiple bots and channels**: If you connect multiple Sender Bots or channels, you are responsible for managing them correctly and understanding which bot posts to which channel.
- **Service modifications**: We reserve the right to modify, suspend, or discontinue any aspect of the Services with reasonable notice (except in urgent cases such as security emergencies or legal requirements).

---

## 8. Acceptable Use

You agree **not** to:

1. **Post prohibited content**: Use the Services to post or distribute content that is unlawful, defamatory, harassing, abusive, fraudulent, obscene, hateful, incites violence, contains sexually explicit material, or infringes any third-party intellectual property or other rights.

2. **Spam and abuse**: Use the Services to send unsolicited bulk messages, spam, or any content that violates Telegram's Terms of Service or Telegram's Bot Platform Policy.

3. **Reverse engineering**: Attempt to reverse engineer, decompile, disassemble, or derive the source code of the Services.

4. **Disruption**: Intentionally disrupt, overload, or impair the Services, including by submitting an excessive number of requests, exploiting bugs, or interfering with other users' access.

5. **Abuse of financial systems**: Abuse promo codes (e.g., generating unlimited codes, reselling codes), the referral program (e.g., creating fake accounts, self-referrals), or payment systems (e.g., chargeback fraud, using stolen payment methods).

6. **Unauthorized access**: Attempt to access another user's account, channels, bots, schedules, or data.

7. **Security testing without authorization**: Scan, probe, or test the vulnerability of the Services or their infrastructure without prior written authorization from us.

8. **Circumventing restrictions**: Attempt to circumvent any technical restrictions, usage limits, or access controls implemented by the Services.

**Consequences of violation**: Violation of any of the above may result in:
- Immediate suspension or termination of your access to the Services;
- Blocking of your Telegram user ID from using the Services;
- Forfeiture of any Premium subscription fees paid (no refund for terms violations);
- Reporting to Telegram and/or appropriate law enforcement authorities where warranted.

**Temporary measures and records**: Minor disruptions trigger automatic temporary measures first — command rate-limit cooldowns (a few seconds) and freeze notices on expired-Premium sender bots. A block records your Telegram user ID, the timestamp, and the reason. **Appeal**: if you believe a block or termination was a mistake, contact the support bot (https://t.me/FastSchedulerSupport_bot) with your username and a description of what happened; appeals are reviewed within 7 business days.

---

## 9. Intellectual Property

- **Our IP**: The Services, including but not limited to their software code, design, user interface, branding, and original content created by us, are owned by the operator or his licensors and are protected by applicable intellectual property laws. You may not reproduce, modify, distribute, or create derivative works of the Services without our express written permission.

- **Your IP**: You retain full ownership of the content you create and schedule through the Services (message text, media, polls, signatures, schedules, and configurations). By using the Services, you grant us a **limited, non-exclusive, worldwide, royalty-free licence** to process, store, transmit, and display your content solely to the extent necessary to provide the Services to you (e.g., store your message until the scheduled time, deliver it to your chosen channel, display it back to you for review). This licence does not grant us any right to use your content for any purpose other than providing the Services to you.

- **Feedback licence**: If you provide us with feedback, suggestions, or feature requests, you grant us a perpetual, irrevocable, royalty-free licence to use that feedback for any purpose without compensation to you.

- **Resale prohibition**: You may not resell, sublicense, lease, rent, or commercially exploit the Services or any component thereof without our prior written permission.

- **Website content**: Our help articles, blog posts, documentation, and site design are our original content. You may share links to any public page freely. You may not republish our articles in full (including via scraping or automated copying) without permission; short quotations with attribution and a link are welcome.

---

## 10. Payments, Pricing, and Subscriptions

### Premium Pricing
Premium is offered at the prices displayed in the in-app premium menu — **the in-bot prices are authoritative** and override any figure quoted elsewhere (including this document and the Website, which may lag behind). Current standard prices are:

| Plan | Price (USD) |
| --- | --- |
| **Monthly** | $6.83/month |
| **3-month prepay** | $18.44 one-time (≈ $6.15/month — save 10% vs paying monthly) |
| **6-month prepay** | $35.65 one-time (≈ $5.94/month — save 13% vs paying monthly) |
| **Annual** | $68.03/year (≈ $5.67/month — save 17% vs paying monthly) |

Plans are billed in **Telegram Stars** at Telegram's Stars-to-currency rate at checkout; the USD figures above are reference equivalents. Prices may be adjusted from time to time (including via configuration without a Terms update for non-material rounding). Changes apply to new purchases and renewals after reasonable notice. Promotional and introductory pricing may differ.

### Payment Methods
Premium is paid exclusively with **Telegram Stars** — Telegram's in-app virtual-currency payment system. Payments are processed entirely within Telegram's infrastructure; no card details are ever handled by us.

### Auto-Renewal
Telegram Stars **monthly** plans renew automatically at the end of each billing period unless cancelled before the renewal date. You can cancel at any time; cancellation takes effect at the end of the current billing period, and you retain Premium access until that date. Telegram Stars **3-month, 6-month, and yearly** plans are one-time prepaid purchases and do not renew.

### Promo Codes
- Promotional discount codes may be offered from time to time.
- Each promo code has specific terms (discount percentage or fixed amount, applicable subscription duration, usage limits, and expiration date).
- Promo codes cannot be combined with other offers.
- Abuse of promo codes (e.g., systematic exploitation, resale) is grounds for immediate termination.

### Payment Retry and Freeze
- If an automatic renewal payment fails (e.g., insufficient Stars balance), the Services will automatically attempt to retry the payment for a limited period.
- If Premium lapses, your account enters a **staged freeze pipeline** (about 35 days, with in-bot notices around days 0, 3, 4, 14, 15 and 35):
  - **Days 0–3**: nothing is frozen — scheduled messages keep being sent. You choose which channels and settings to keep within Free Tier limits, and which single media storage to keep. Around day 3 an automatic backup file of your data is generated for you.
  - **Day 4**: scheduled sending stops for unkept excess items, and you are prompted to export your data.
  - **Media cleanup**: unkept media storages are removed and the kept storage is trimmed to 100 items. Messages that referenced deleted media are converted to plain text so no content is lost silently.
  - **Around day 35**: after a final 12-hour warning, excess channels are disconnected and their sender-bot tokens are permanently removed. Items within Free Tier limits keep working.
- Renewing at any point before final disconnection restores full service, including unfrozen items.

### Refunds
Refunds are governed by our **Refund Policy**, which is incorporated into these Terms by reference. See the `/legal` command or our Refund Policy page for details.

### Taxes
- Telegram Stars payments are generally tax-neutral at the point of sale; you remain responsible for any applicable tax obligations in your jurisdiction.

---

## 11. Free Tier vs. Premium

| Feature | Free Tier | Premium |
| --- | --- | --- |
| **Channels** | 1 | 3 |
| **Sender Bots** | 1 | 3 |
| **Scheduled messages** | Up to 100 pending at once | Unlimited |
| **Sent messages (per channel, per month)** | 100 | Unlimited |
| **Recurring messages** | 1 (expires after 365 days) | Unlimited (never expire) |
| **Message signatures** | 1 free trial, then Premium | Unlimited |
| **Media storages** | 1 (up to 100 items total) | 20 (up to 500 items total) |
| **Videos in messages** | Up to 25 MB per file | Up to 50 MB per file |
| **Videos in storage** | — | Up to 50 MB per file |
| **4K media** | — | Yes |
| **Statistics** | Basic | Full: paginated leaderboards (most viewed, most reacted, most commented, top commentators), averages, custom reports |
| **Automated reports** | — (Premium only) | Unlimited with custom schedules |
| **Search** | Included | Included |
| **Calendar** | Included | Included |
| **Import/Export** | — | Full backup and export (.fsback/.fspback) |
| **Broadcast priority** | Standard | Priority |
| **Support** | Standard | Priority |
| **Premium badge** | — | Yes |
| **Referral rewards** | Earn up to 45 Premium days | Earn up to 45 Premium days |

Limits may be adjusted from time to time; the in-app display is authoritative. Premium users' Sender Bots are processed with priority relative to Free Tier users in the global send queue.

---

## 12. Data Backups, Export, and Deletion

### Automatic Backups
The Services maintain internal backups of operational data. These backups are stored with our infrastructure providers and are used solely for disaster recovery. Backups are not guaranteed to be available on demand and are not a substitute for manual export.

### Manual Export
You can export your data at any time using the **`/export`** or **`/backup`** commands. Two export formats are available:

- **`.fsback`** — Fast Scheduler Backup. Contains all your data in JSON format with an HMAC integrity check. Not encrypted.
- **`.fspback`** — Fast Scheduler Protected Backup. Your data is **encrypted (AES-256-GCM) + integrity-protected (HMAC-SHA256)** using a password you provide.

A full export includes (where applicable): scheduled messages, recurring messages, channel connections and settings, user settings and preferences, message signatures, referral data, promo code usage, ratings given, feedback submitted, and usage statistics.

### Deletion
- **Individual messages and media**: Use the **`/delete`** command at any time to delete scheduled or recurring messages, stored media, or items by ID. This removes content, not your account.
- **Disconnecting channels or Sender Bots**: Removes the association. Disconnecting a Sender Bot permanently deletes its token from our systems. No copy is retained.
- **Full account erasure**: There is no self-serve wipe. To erase your entire account, contact us via the support bot (https://t.me/FastSchedulerSupport_bot) or fastschedulebot@gmail.com from your Telegram account so we can verify your identity. Erasure is processed within 7 business days across all per-user categories (schedules, channels, tokens, settings, signatures, media, ratings, feedback, referrals, statistics); only tax-required billing records are retained. A recovery snapshot is kept for 45 days in case the request was mistaken or unauthorized, then automatically and permanently purged. Contact us before then to cancel a pending erasure.

---

## 13. Referral Program (Beta)

The referral program (currently in **beta**) allows you to earn Premium days by inviting new users to the Main Service.

- Each user receives a unique referral link (accessible via the `/referral` command).
- When a genuinely new user arrives via your link **and proves real use** — connecting a channel and creating at least one scheduled/sent message — **both you and the newcomer earn 3 Premium days**.
- The newcomer's days activate as Premium immediately; **your** days are banked in an activate-later balance (usable from the referral menu, including after a paid period ends) — each referral pays exactly 3 days per side, never double.
- You can earn from at most **15 referees (45 Premium days total)**; one credit per newcomer.
- You cannot refer yourself (self-referral detection is enforced).
- Abuse of the referral program (creating fake accounts, using bots, farming, or any form of manipulation) is grounds for forfeiture of all referral rewards and account termination. Farmed balances may be removed.
- Beta status affects polish, never balances: earned days are recorded at qualification and honoured even if reward sizes, limits, or rules are tuned during beta. The program terms may be modified or discontinued at any time; accrued rewards at the time of discontinuation will be honoured.

---

## 14. Feedback and Ratings

- You may submit feedback and rate the Services (1–5 stars) through the `/feedback` command and the in-bot rating buttons.
- Ratings and written reviews may be displayed to other users within the Services.
- You represent that your feedback and ratings are your own honest opinion and do not violate any third-party rights.
- **No offensive content in feedback**: feedback, reviews, and support messages must not contain profanity, slurs, insults, threats, hate speech, sexually explicit language, or any other offensive content. A single mild expression may trigger a warning; heavily offensive messages are blocked automatically.
- **Moderation**: repeated offensive submissions lead to warnings; after 3 warnings, sending new feedback is temporarily blocked (currently 24 hours). If you believe a warning or block was a mistake, you may file a one-time review request from the bot; deliberately false review requests may lead to your feedback being ignored, loss of feedback access, or loss of access to the Services.
- We reserve the right to remove or not publish any feedback or rating that violates our Acceptable Use policy or is otherwise inappropriate.
- We may respond to your feedback publicly for transparency.

---

## 15. Disclaimers

- **"As is" and "as available"**: The Services are provided on an "as is" and "as available" basis without warranties of any kind, either express or implied, to the maximum extent permitted by applicable law. We expressly disclaim all implied warranties of merchantability, fitness for a particular purpose, title, and non-infringement.

- **No guarantee of delivery**: We do not guarantee that scheduled messages will be delivered at the exact scheduled time or at all. Message delivery depends on Telegram's API availability, your Sender Bot's connectivity, your channel's configuration, and other factors outside our control. We are not liable for delayed, misdelivered, or undelivered messages.

- **No guarantee of uninterrupted service**: We do not guarantee that the Services will be uninterrupted, error-free, secure, or free from viruses or other harmful components.

- **Telegram enforcement**: We are not responsible for any enforcement actions taken by Telegram against your account, channel, or bot, including but not limited to restrictions, suspensions, or bans, arising from your use of the Services or your content.

- **Third-party services**: We are not responsible for the availability, reliability, or security of any third-party services integrated with the Services (Telegram).

- **Beta features**: Features designated as "beta," "experimental," or "preview" may be changed or discontinued without notice.

---

## 16. Limitation of Liability

To the maximum extent permitted by applicable law:

- The operator shall **not** be liable for any indirect, incidental, special, consequential, exemplary, or punitive damages, including but not limited to loss of data, loss of profits, loss of business, loss of goodwill, or interruption of business, arising out of or in connection with these Terms or your use of the Services, whether based on contract, tort (including negligence), strict liability, or any other legal theory.

- Our **total aggregate liability** to you for all claims arising out of or relating to these Terms or the Services shall not exceed the greater of: (a) **the amounts you have paid us in the twelve (12) months immediately preceding the event giving rise to the liability**; or (b) **USD 100 (one hundred US dollars)** if you have not made any payments.

- The exclusions and limitations in this section apply even if we have been advised of the possibility of such damages and even if any limited remedy provided in these Terms fails of its essential purpose.

- Nothing in these Terms excludes or limits liability that cannot be excluded or limited under applicable law, including but not limited to liability for gross negligence, fraud, death, or personal injury caused by our negligence.

---

## 17. Indemnification

You agree to indemnify, defend, and hold harmless the operator from and against any and all claims, demands, losses, damages, liabilities, costs, and expenses (including reasonable attorneys' fees) arising out of or relating to:

1. Your use of the Services (including any actions taken by your Sender Bot);
2. Your content and messages scheduled or transmitted through the Services;
3. Your violation of these Terms;
4. Your violation of any applicable law or the rights of any third party;
5. Any unauthorized access to or use of your account, channels, or Sender Bot tokens.

We reserve the right, at our own expense, to assume the exclusive defence and control of any matter otherwise subject to indemnification by you, in which event you will cooperate with us in asserting any available defences.

---

## 18. Termination

- **By you**: You may stop using the Services at any time. You may request erasure of your data as described in Section 12. Deletion of data does not automatically entitle you to a refund of subscription fees already paid.

- **By us**: We may suspend or terminate your access to the Services, in whole or in part, at any time, with or without notice, if:
  - You violate these Terms (including the Acceptable Use policy);
  - Your use of the Services poses a security risk to us or other users;
  - We are required to do so by law or regulatory authority;
  - We decide to discontinue the Services (in which case we will provide reasonable notice).

- **Effect of termination**: Upon termination:
  - Your right to access and use the Services ceases immediately.
  - Your data will be handled per our Privacy Policy and data retention schedule.
  - Termination does not relieve you of any payment obligations accrued before termination.
  - **Banned with Premium**: if your access is terminated for violation of these Terms while you hold a paid Premium subscription, the already-paid period is **not refunded**, but your subscription is **cancelled automatically** and you will **not be charged again** (auto-renewal stops at termination).
  - Sections 9 (Intellectual Property), 16 (Limitation of Liability), 17 (Indemnification), and 19 (Governing Law) survive termination.

---

## 19. Governing Law and Disputes

These Terms and any disputes arising out of or relating to them (including non-contractual disputes) shall be governed by and construed in accordance with the laws of **Armenia**, without regard to its conflict-of-laws principles.

Any dispute arising out of or in connection with these Terms shall be resolved exclusively in the courts of **Yerevan, Armenia**.

**Consumer protection**: If you are a consumer resident in a jurisdiction where mandatory consumer-protection laws apply, those laws prevail over the governing law and venue specified above. Nothing in these Terms limits your statutory rights as a consumer.

**Informal resolution**: Before filing any claim, you agree to attempt to resolve the dispute informally by contacting https://t.me/FastSchedulerSupport_bot or fastschedulebot@gmail.com. We will attempt to resolve the dispute within 30 days. If the dispute cannot be resolved informally within that period, either party may pursue formal resolution.

---

## 20. Changes to These Terms

We may update these Terms from time to time. The process for changes depends on their nature:

- **Material changes** (e.g., changes to pricing, data processing, user rights): Will be announced via the Services (in-app notification or message). Continued use of the Services after the effective date of the changes constitutes your acceptance of the updated Terms.

- **Non-material changes** (e.g., clarifications, corrections, formatting): May be made without prior notice but will be reflected in the "Last updated" date.

- **If you do not agree** to a material change, you may stop using the Services and delete your data before the change takes effect.

---

## 21. Contact

For questions, concerns, or legal notices regarding these Terms:

> **Maxim Mkrtchyan** (individual operator, Armenia)
> Email: [fastschedulebot@gmail.com](mailto:fastschedulebot@gmail.com)
> Support bot: [FastSchedulerSupport_bot](https://t.me/FastSchedulerSupport_bot) (preferred contact — please do not spam personal chat)
> Personal Telegram: [@MaximalXP](https://t.me/MaximalXP)

---
