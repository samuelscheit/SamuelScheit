---
title: Samuel Scheit — Curriculum Vitae
description: Samuel Scheit — software engineer, open-source founder, and technical researcher.
---

# Samuel Scheit

**Software Engineer · Open-Source Founder · TypeScript / React Native / Systems**

[contact@samuelscheit.com](mailto:contact@samuelscheit.com) · [Portfolio](https://samuelscheit.com) · [GitHub](https://github.com/samuelscheit) · [LinkedIn](https://www.linkedin.com/in/samuel-scheit-343436247/)

**Address:** Keplerstraße 23, 85609 Aschheim, Germany · **Phone:** [+49 160 97788689](tel:+491609778869)<br />
**Date/place of birth:** 28 November 2003 · Munich, Germany

## Profile

Open-source software engineer, founder, and self-employed contractor focused on real-time communication platforms, cross-platform mobile performance, developer tooling, browser automation, and reverse-engineering-adjacent research. Founder of [Spacebar](https://spacebar.chat) (formerly Fosscord) and [Respond](https://github.com/respondchat); creator and maintainer of public TypeScript packages including [`puppeteer-stream`](https://github.com/samuelscheit/puppeteer-stream) and [`react-native-skia-list`](https://github.com/samuelscheit/react-native-skia-list). Combines product ownership with hands-on systems work across TypeScript, React Native, Rust/JSI, WebRTC-oriented communication systems, and data-intensive tooling.

## Experience

### Self-Employed Software Contractor

**2025–2026 · client engagements**

#### [PHONT](https://phont.ai) — WebGL Video Export Engine

**2025**

- Built and integrated a WebGL video-export engine into PHONT Studio’s frontend/UI for pixel-accurate subtitle and video rendering.
- Reworked the export pipeline from real-time recording to frame-by-frame rendering, including FFmpeg subtitle compositing in a serverless function.
- Optimized rendering/export performance; local project documentation records optimization of up to **50×**, while the signed project specification defined benchmark tiers up to **10× real-time export** on the validation hardware.

#### [Exodus](https://www.exodus.com) — React Native Mobile Product Work

**2025**

- Implemented and tuned high-performance gestures, animations, and UI interactions across Exodus Mobile and the Grateful mobile application.
- Delivered custom swap-keyboard and exchange-flow interactions, portfolio glow and gradient-mesh effects, card/perspective animations, splash and onboarding transitions, passkey animations, modal-dismiss gestures, hidden-balance transitions, and activity/rewards motion systems.
- Worked across React Native, Reanimated, Skia-oriented rendering, and native iOS/Android integration with attention to reduced-motion behavior, frame stability, and interaction polish.

#### [MyroDex](https://myrodex.gg) — Software Development Engagement

**2026**

- Designed and implemented the MyroDex platform end-to-end as a full-stack SaaS and operations workspace, from application architecture and data model through authenticated product surfaces, backoffice tooling, workers, and deployment configuration.
- Built a Bun workspace monorepo with a main Next.js application and a separate Next.js Backoffice application sharing authentication, entity, database, and business modules.
- Delivered organization-aware workspaces covering configurable dashboards, user/role/permission management, teams and departments, project planning, task dependencies, templates, approvals/QAS workflows, activity logs, support/helpdesk, and internal documentation.
- Implemented domain modules for competitive gaming operations (leagues, teams, players, matches, statistics, templates and access rules), inventory (warehouses, products, items and stock movements), calendars (drag-and-drop scheduling, attendees, reminders, conflicts and system events), sponsors (contacts, activities, assets, deals and deliverables), and creator operations (content plans, social content and platform insights).
- Built the commercial and platform foundation: Better Auth with email verification, password reset, two-factor authentication and organization permissions; PostgreSQL with Drizzle ORM, generated migrations and schema/entity definitions; GraphQL Yoga APIs; Zod validation; signed S3-compatible uploads and organization exports; Stripe Checkout, Billing Portal, subscriptions, entitlements, refunds and idempotent webhooks.
- Added an AI and observability layer using OpenAI/LangChain, Langfuse, OpenTelemetry and Sentry, plus WebSocket/SSE-style realtime updates, push notifications, transactional email, cron jobs, and dedicated background workers.
- Implemented polished, responsive product UI with React, Tailwind CSS, Radix primitives, React Hook Form, FullCalendar/React Big Calendar, `react-grid-layout`, TanStack Table/Virtual, Recharts, Framer Motion, drag-and-drop utilities, MDX/Fumadocs documentation, and Playwright end-to-end coverage.
- Established a production workflow using Docker, Docker Compose, Dokploy, compile-mode Next.js builds, migration-on-startup, separate web/cron/export-worker services, and automated typecheck, lint, unit, integration, E2E, metadata, documentation, and billing test commands.
- **Technology:** TypeScript, React, Next.js, Bun, PostgreSQL, Drizzle ORM, GraphQL Yoga, Better Auth, Zod, Stripe, S3, OpenAI, LangChain, Langfuse, WebSockets, SSE, Docker, Dokploy, Playwright, Vitest/Bun Test, Tailwind CSS, Radix UI, FullCalendar, React Big Calendar, Recharts, Framer Motion, TanStack, and AWS SDK.
- Project source: [`myrodex/myrodex`](https://github.com/myrodex/myrodex). The repository is private; no credentials, secrets, customer data, or private operational details are included in this CV.

### Founder — [Spacebar Chat](https://spacebar.chat) _(formerly Fosscord)_

**Founded January 2021**

- Founded an open-source, self-hostable, Discord-compatible communication-platform ecosystem for chat, voice, and video.
- Helped establish a public project spanning API schemas, an HTTP API, WebSocket gateway, CDN, WebRTC, database models, administration tooling, client applications, and documentation.
- The flagship [Spacebar repository](https://github.com/spacebarchat/spacebarchat) had **6.7k+ GitHub stars and 220+ forks** as of 25 August 2026; this is project/community impact, not a personal star count.
- Built in and for an open-source community with Discord compatibility, self-hosting, extensibility, and user control as core product constraints.

### Founder — [Respond](https://github.com/respondchat)

**Founded January 2022**

- Founded a multi-platform messaging initiative intended to bring contacts and conversations across WhatsApp, Telegram, Discord, and Fosscord/Spacebar into one client experience.
- Developed supporting mobile/runtime infrastructure across TypeScript, React Native, performance-oriented state management, and Rust–React Native JSI interoperability.
- Contributed to the technical direction of a cross-platform messenger with public open-source components.

### Open-Source Contributor / Maintainer — [Trant Labs projects](https://github.com/trantlabs)

**2021–2024 · public repository history; formal employment title not asserted**

- Contributed feature work, releases, documentation, and CI/CD to [`missing-native-js-functions`](https://github.com/trantlabs/missing-native-js-functions), a zero-dependency JavaScript utility library for browser and Node.js applications.
- Worked across TypeScript/JavaScript library design, package publishing, documentation, and automated delivery workflows.

### Independent Software Developer

**From 2018 · project and commissioned work**

- Built a collaboration platform for a tablet-class cohort, then evolved it into the GyKi school mobile app for timetables, substitution plans, and appointments.
- Developed Discord bots for commissioned work and created [Discord Bot Client](https://github.com/samuelscheit/discord-bot-client), a historical/archived Discord tooling project with **695 GitHub stars and 390 forks** as of 25 August 2026.
- Built an early technical foundation in C, Linux, self-hosted game servers, HTML/CSS, PHP, and SQL, including a database-backed server-management application.

## Selected Open-Source Projects

### [Puppeteer Stream](https://github.com/samuelscheit/puppeteer-stream) — Creator & Maintainer

**2020–present**

**TypeScript · Node.js · Puppeteer · Browser media capture**

- Created the library and continue to maintain it as an MIT-licensed TypeScript package for retrieving audio and video streams from web pages through Puppeteer.
- Supports programmatic media capture for browser-automation workflows, browser-extension integration, headless execution, media constraints, and Node.js streams.
- Public impact: **459 GitHub stars / 131 forks** as of 25 August 2026, plus **[222,841 npm downloads](https://api.npmjs.org/downloads/point/2025-08-25:2026-08-24/puppeteer-stream)** from 25 August 2025 to 24 August 2026.

### [React Native Skia List](https://github.com/samuelscheit/react-native-skia-list) — Creator

**2024–present**

**React Native · TypeScript · Skia · C++ · iOS · Android**

- Developed and released an MIT-licensed, high-performance list-rendering component built on [Shopify React Native Skia](https://shopify.github.io/react-native-skia/).
- Built public documentation, demos, package release automation, TypeScript APIs, and native iOS/Android/C++ integration.
- Published a detailed [rendering architecture and benchmark article](https://samuelscheit.com/blog/2024/react-native-skia-list); reported measurements are project benchmarks rather than an independently verified ranking.
- Project had **243 GitHub stars** as of 25 August 2026.

### [Phishing Support](https://phishing.support) — Creator

**2026**

**TypeScript · Threat-analysis automation · Web tooling**

- Built an open-source tool for automated analysis, reporting, and tracking of phishing emails and malicious websites.
- Designed workflow-oriented tooling for indicator extraction, automated checks, abuse/takedown reporting, and a web interface.

### [Bundestagswahl 2025](https://github.com/samuelscheit/bundestagswahl2025) — Independent Data Analysis

**2025**

**TypeScript · Bun · Data acquisition · Normalization · Visualization**

- Built and published a data pipeline and [interactive map](https://bundestagswahl.samuelscheit.com/) covering all **299 German federal-election constituencies** in 2025.
- Collected constituency-level sources, implemented provider-specific download and normalization scripts, and compared source data with official results.
- Documented the methodology and results in the public article [“Fehlende Stimmen bei der Bundestagswahl 2025?”](https://samuelscheit.com/blog/2025/bundestagswahl).

### [Browser Fingerprinting Technical Analysis](https://github.com/samuelscheit/fingerprinting) — Co-author

**2024**

**JavaScript · Browser privacy · Data collection · Technical research**

- Co-authored, with James Bergfeld, a technical analysis of browser-fingerprinting techniques based on FingerprintJS.
- Developed a custom fingerprinting library and dataset to evaluate identification methods, practical limitations, and potential countermeasures.

### [WPlace World Archive](https://github.com/samuelscheit/wplace-archive) — Creator

**2025–present**

**C++ · Image/tile processing · Linux infrastructure · Visualization**

- Built a public system to scrape, archive, process, and visualize the entire `wplace.live` map.
- Implemented tiled archival workflows, PNG storage, lower-zoom generation with VIPS, and full-world jobs on self-hosted Linux infrastructure.

### [Spotify DRM Report](https://github.com/samuelscheit/spotify-drm-report) — Independent Technical Research

**2023 report · published 2025**

- Published a proof-of-concept report on a **reported** missing-DRM-enforcement issue in Spotify’s Accesspoint API.
- Demonstrates reverse-engineering-adjacent investigation and technical documentation; no CVE, bounty, or vendor outcome is claimed here.

## Open-Source Contributions & Technical Writing

- **React Native Skia:** Contributed the merged [iOS ProMotion 120 Hz fix](https://github.com/Shopify/react-native-skia/pull/2690) and originated the approach for [macOS Catalyst support](https://github.com/Shopify/react-native-skia/pull/3296), later completed upstream and released in React Native Skia v2.3.0.
- **Rust / React Native interoperability:** Authored the merged [iOS support contribution to `jsi-rs`](https://github.com/laptou/jsi-rs/pull/3), supporting native Rust integrations in React Native.
- **Technical writing:**
    - [Using Rust in React Native with `jsi-rs`](https://samuelscheit.com/blog/2023/react-native-rust) — Rust, libsignal, Hermes, and JSI interoperability (5 July 2023).
    - [Implementing the fastest list renderer for React Native](https://samuelscheit.com/blog/2024/react-native-skia-list) — Skia rendering, virtualization, worklets, and performance measurement (25 October 2024).
    - [Fehlende Stimmen bei der Bundestagswahl 2025?](https://samuelscheit.com/blog/2025/bundestagswahl) — public data collection and constituency-level election analysis (26 February 2025).
- **Systems challenge:** Co-built [Team Checkmate’s](https://github.com/samuelscheit/hackatum-2024) high-concurrency Go REST backend for the Check24 Hackatum car-rental challenge, using SQL optimization, in-memory bitmap filtering, B-trees, and `fasthttp`.

## Education

### Technical University of Munich (TUM)

**Bachelor of Science in Computer Science / Informatics · 2022–2024**

### Gymnasium Kirchheim

**Allgemeine Hochschulreife (Abitur) · 2014–2022 · Final grade: 1.9**

## Technical Skills

| Area                               | Technologies and demonstrated domains                                                                                                                           |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Languages**                      | TypeScript, JavaScript, Rust, Go, C++, C, PHP, SQL                                                                                                              |
| **Application development**        | React, React Native, Next.js, Node.js, React Native Skia, Expo                                                                                                  |
| **Systems & infrastructure**       | Linux, Docker, Nginx, WebSocket, WebRTC-oriented systems, CDN/media workflows, self-hosting                                                                     |
| **Native/mobile interoperability** | React Native JSI, Hermes, Rust bindings, iOS, Android, C++ integration                                                                                          |
| **Performance engineering**        | Rendering/virtualization, mobile UI benchmarking, concurrent REST APIs, in-memory filtering, B-trees                                                            |
| **Developer & browser tooling**    | Puppeteer, browser automation, browser extensions/instrumentation, npm package publishing and maintenance                                                       |
| **Technical domains**              | Real-time communication systems, messaging, reverse engineering, browser privacy/fingerprinting, phishing-analysis automation, data pipelines and visualization |

## Public Profile & Project Links

[Portfolio](https://samuelscheit.com) · [GitHub](https://github.com/samuelscheit) · [LinkedIn](https://www.linkedin.com/in/samuel-scheit-343436247/) · [Spacebar](https://spacebar.chat) · [Respond](https://github.com/respondchat) · [PHONT](https://phont.ai) · [Exodus](https://www.exodus.com) · [MyroDex](https://myrodex.gg) · [npm](https://www.npmjs.com/~samuelscheit)

<details>
<summary>Research and verification notes</summary>

- The primary identity chain is consistent across Samuel’s first-party portfolio, GitHub profile, npm publisher metadata, linked social profiles, and the public Spacebar/Respond organization pages.
- Founder dates and the early career timeline are first-person public portfolio claims. Organization membership and project documentation corroborate the projects, but do not establish legal ownership or employment status.
- GitHub star/fork figures above are public snapshots observed on 25 August 2026; npm downloads include the reporting interval. They are not timeless metrics.
- Public LinkedIn metadata lists **Trant Labs** as experience and Technical University of Munich education. The accessible profile does not expose a reliable title or role dates, so the Trant Labs entry above is intentionally limited to public repository history rather than a formal employment claim.
- The address, phone number, birth details, degree wording, study dates, and Abitur grade above come from the workspace CV notes supplied for this task. Public profile metadata corroborates TUM but displays a different study end year (2025); confirm the exact degree title, award status, and dates before sending this CV for an application.
- This version is application-ready and includes the supplied personal contact details. Remove the street address, phone number, and birth details before publishing the page publicly if you prefer a privacy-minimized CV.
- The 2025–2026 contractor entries are corroborated by local work artifacts and repository history where available. Contract, invoice, source-code, and financial details are intentionally summarized rather than reproduced.
- MyroDex is represented only by the user-provided project name and public site; its source repository is private, and no credentials or access details are included.

</details>
