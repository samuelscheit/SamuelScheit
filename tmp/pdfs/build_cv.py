"""Build Samuel Scheit's complete, recruiter-focused CV.

The website CV (``CV.md``) is intentionally detailed.  The old PDF builder
selected only two open-source projects and replaced the rest with a generic
``50+`` link, which made the PDF materially less useful than the source CV.
Project data now lives in this module as explicit entries so every project that
is named in the CV is visible in the generated PDF.  Dates use month precision
whenever the source material provides it; client engagements whose notes only
contain a year keep that year rather than inventing a month.
"""

from datetime import datetime
import json
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output/pdf/samuel-scheit-cv.pdf"

PAGE_WIDTH, _ = A4
LEFT_MARGIN = 15 * mm
RIGHT_MARGIN = 15 * mm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

INK = HexColor("#17212B")
MUTED = HexColor("#4B5563")
ACCENT_HEX = "#0B5D6B"
ACCENT = HexColor(ACCENT_HEX)
RULE = HexColor("#AAB7BC")


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=26,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=2.0,
        ),
        "headline": ParagraphStyle(
            "Headline",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=13.0,
            alignment=TA_CENTER,
            textColor=ACCENT,
            spaceAfter=2.4,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.1,
            leading=11.0,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceAfter=0,
        ),
        "summary": ParagraphStyle(
            "Summary",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.2,
            leading=12.6,
            alignment=TA_LEFT,
            textColor=INK,
            spaceAfter=0,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.3,
            leading=12.0,
            textColor=ACCENT,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "entry_title": ParagraphStyle(
            "EntryTitle",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.1,
            leading=11.8,
            textColor=INK,
            spaceAfter=0,
        ),
        "date": ParagraphStyle(
            "Date",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.1,
            leading=11.8,
            alignment=TA_RIGHT,
            textColor=ACCENT,
            spaceAfter=0,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9.0,
            leading=10.6,
            textColor=MUTED,
            spaceAfter=1.1,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.0,
            leading=12.3,
            leftIndent=10,
            firstLineIndent=-8.5,
            bulletIndent=0,
            textColor=INK,
            spaceAfter=2.3,
            allowWidows=0,
            allowOrphans=0,
        ),
        "compact": ParagraphStyle(
            "Compact",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.7,
            leading=11.7,
            textColor=INK,
            spaceAfter=0,
        ),
    }


STYLES = make_styles()


def normalize(text: str) -> str:
    """Keep punctuation portable without disturbing ReportLab markup."""
    return (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2011", "-")
        .replace("\u2212", "-")
        .replace("\u00a0", " ")
        .replace("\u00d7", "x")
    )


def link(label: str, url: str) -> str:
    return (
        f'<link href="{escape(url)}">'
        f'<font color="{ACCENT_HEX}">{escape(label)}</font>'
        "</link>"
    )


def paragraph(text: str, style: str = "compact") -> Paragraph:
    return Paragraph(normalize(text), STYLES[style])


def section(title: str) -> KeepTogether:
    return KeepTogether(
        [
            Spacer(1, 6.2),
            paragraph(escape(title.upper()), "section"),
            HRFlowable(
                width="100%",
                thickness=0.55,
                color=RULE,
                spaceBefore=0.6,
                spaceAfter=3.8,
            ),
        ]
    )


def heading(title: str, date: str) -> Table:
    # Keep the date column wide enough for month-qualified ranges such as
    # ``2023 report; May 2025 publication`` without squeezing project names.
    date_width = 43 * mm
    table = Table(
        [[paragraph(title, "entry_title"), paragraph(escape(date), "date")]],
        colWidths=[CONTENT_WIDTH - date_width, date_width],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def bullets(items: list[str]) -> list[Paragraph]:
    return [paragraph(f"- {item}", "bullet") for item in items]


def entry(
    title: str,
    date: str,
    items: list[str],
    subtitle: str | None = None,
    space_after: float = 2.6,
) -> KeepTogether:
    content = [heading(title, date)]
    if subtitle:
        content.append(paragraph(subtitle, "subtitle"))
    content.extend(bullets(items))
    content.append(Spacer(1, space_after))
    return KeepTogether(content)


def project_entry(
    title: str,
    date: str,
    items: list[str],
    *,
    subtitle: str | None = None,
    space_after: float = 2.0,
) -> KeepTogether:
    """Create a project entry with the same layout as an experience entry."""
    return entry(title, date, items, subtitle=subtitle, space_after=space_after)


_GITHUB_DATA: dict | None = None


def github_repositories() -> dict:
    """Load the downloaded GitHub metadata once for curated project dates."""
    global _GITHUB_DATA
    if _GITHUB_DATA is not None:
        return _GITHUB_DATA

    source = ROOT / "github/commits.json"
    try:
        _GITHUB_DATA = json.loads(source.read_text(encoding="utf-8"))["repositories"]
    except FileNotFoundError as error:
        raise RuntimeError(f"GitHub project source is missing: {source}") from error
    except (json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"GitHub project source is invalid: {source}") from error
    return _GITHUB_DATA


def github_project(name: str) -> dict:
    """Return a user-created, non-fork repository or fail loudly.

    ``commits.json`` contains both repositories created by Samuel and places
    where he contributed.  This guard prevents the CV from accidentally
    presenting upstream contributions as projects he created.
    """
    repositories = github_repositories()
    repository = next(
        (
            value
            for value in repositories.values()
            if (value.get("details") or {}).get("name", "").casefold() == name.casefold()
            and ((value.get("details") or {}).get("owner") or {}).get("login", "").casefold() == "samuelscheit"
        ),
        None,
    )
    if repository is None:
        raise RuntimeError(f"Repository {name!r} is not present in commits.json as Samuel's repository")
    details = repository["details"]
    if details.get("isFork"):
        raise RuntimeError(f"Repository {name!r} is a fork and cannot be presented as a created project")
    return details


def github_created_month(name: str) -> str:
    created_at = github_project(name).get("createdAt")
    if not created_at:
        raise RuntimeError(f"Repository {name!r} has no creation date in commits.json")
    try:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%b %Y")
    except ValueError as error:
        raise RuntimeError(f"Invalid creation date for repository {name!r}: {created_at!r}") from error


def github_project_title(name: str, role: str) -> str:
    details = github_project(name)
    # Private repositories are deliberately not linked; their summaries still
    # communicate the work without exposing an inaccessible destination.
    if details.get("isPrivate"):
        return f"{escape(name)} (private) | {escape(role)}"
    return f"{link(name, details['url'])} | {escape(role)}"


CURATED_PROJECTS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "npm-malicious-check",
        "Creator - supply-chain security tooling",
        (
            "Built a Python triage utility that downloads npm malware advisories, normalizes them to CSV, and scans local npm, Bun, and Yarn caches for package/version matches.",
            "Designed the workflow to give developers and incident responders a fast, auditable first check after a supply-chain incident.",
        ),
    ),
    (
        "react-native-skia-yoga",
        "Creator - React Native rendering prototype",
        (
            "Developed a C++/TypeScript library combining Yoga layout with React Native Skia for declarative, interactive UI rendering.",
            "Built the JSX intrinsic-node surface and example integration for complex layouts, while documenting the project as an early-stage prototype rather than production software.",
        ),
    ),
    (
        "holistische",
        "Founder - AI-assisted news platform",
        (
            "Built a private AI-assisted news aggregation product covering German and international reporting.",
            "Designed the product and publishing workflow around source-based aggregation, structured editorial review, and clear positioning.",
        ),
    ),
    (
        "cccb-servicepoint-browser",
        "Creator - browser media integration",
        (
            "Built a TypeScript/Bun service that sends text, images, and live Puppeteer browser video to the CCC Berlin Service Point display.",
            "Connected browser automation and media transport into a small operational display system with explicit commands for each content type.",
        ),
    ),
    (
        "missing-native-js-syntax",
        "Creator and maintainer - TypeScript tooling",
        (
            "Created a TypeScript transformer and Babel plugin that adds missing JavaScript syntax patterns to existing codebases.",
            "Packaged the tool for npm with documentation, examples, and automated CI, demonstrating compiler-tooling and developer-experience work.",
        ),
    ),
    (
        "gpia",
        "Creator - Android integrity research prototype",
        (
            "Investigated Google Play Integrity, SafetyNet, and DroidGuard request flows through a focused protobuf client prototype.",
            "Applied protocol analysis and binary/API research to document how Android anti-abuse services can be queried from native tooling.",
        ),
    ),
    (
        "whatsapp",
        "Creator - private messaging backend",
        (
            "Built a private WhatsApp operations backend and dashboard with account authentication, APNs integration, proxy handling, API-key management, and account-event processing.",
            "Added BullMQ-backed jobs, structured logging, lazy-loaded data tables, and performance-focused API flows for a multi-account service.",
        ),
    ),
    (
        "Baileys",
        "Creator - messaging protocol infrastructure",
        (
            "Extended a private WhatsApp-compatible messaging stack with native-mobile API support, TCP transport, registration flows, media mappings, CAPTCHA handling, and device/session events.",
            "Worked across protocol integration, asynchronous connection state, and mobile-specific behavior in a TypeScript runtime.",
        ),
    ),
    (
        "jura",
        "Creator - legal text analysis prototype",
        (
            "Developed a private legal-text analysis prototype with a parser for German statutes and references, MongoDB-backed data models, and a Next.js interface.",
            "Added AI-assisted checks for legal content and iterated on grammar, extraction, and judgment-analysis workflows.",
        ),
    ),
    (
        "GykiSpace",
        "Creator - school collaboration platform",
        (
            "Built a real-time school collaboration and chat project for the GyKi community, extending the earlier school-app work into a shared communication surface.",
            "Used the project to explore product design, messaging flows, and self-hosted application development.",
        ),
    ),
    (
        "Lambert-server",
        "Creator - Node.js server framework",
        (
            "Created an Express-based route handler with convention-driven route registration, JSON error handling, and schema-style request validation.",
            "Published a reusable npm-oriented server foundation designed to reduce boilerplate across small Node.js services.",
        ),
    ),
    (
        "Lambert-orm",
        "Creator - database abstraction library",
        (
            "Designed a database abstraction layer that exposes path-based data access while allowing the underlying database engine to change independently.",
            "Implemented a MongoDB adapter and a proxy-style API that fetches only the data needed for each operation.",
        ),
    ),
    (
        "Database-Browser",
        "Creator - web administration tool",
        (
            "Built a browser-based PHP/JavaScript/MySQL administration tool for inspecting and editing database contents.",
            "Delivered an early end-to-end application spanning the LAMP stack, server deployment, tabular data views, and write operations.",
        ),
    ),
)


def curated_project_entries() -> list[KeepTogether]:
    entries: list[KeepTogether] = []
    projects = sorted(
        CURATED_PROJECTS,
        key=lambda item: datetime.strptime(github_created_month(item[0]), "%b %Y"),
        reverse=True,
    )
    for repository, role, summary in projects:
        entries.append(
            project_entry(
                github_project_title(repository, role),
                github_created_month(repository),
                list(summary),
                space_after=1.6,
            )
        )
    return entries


def build_story() -> list:
    return [
        paragraph("Samuel Scheit", "name"),
        paragraph(
            "Software Engineer | Full-Stack, React Native &amp; Performance Engineering",
            "headline",
        ),
        paragraph(
            "Munich, Germany"
            f" | {link('+49 160 97788689', 'tel:+491609778869')}"
            f" | {link('contact@samuelscheit.com', 'mailto:contact@samuelscheit.com')}"
            f" | {link('samuelscheit.com', 'https://samuelscheit.com')}"
            f" | {link('GitHub', 'https://github.com/samuelscheit')}"
            f" | {link('LinkedIn', 'https://www.linkedin.com/in/samuel-scheit-343436247/')}",
            "contact",
        ),
        section("Summary"),
        paragraph(
            "Software engineer with commercial delivery experience across high-performance "
            "mobile applications, WebGL video rendering, full-stack SaaS, and real-time systems. "
            "Delivered product engineering for PHONT, Exodus, and MyroDex; founded Spacebar "
            "(6.7k+ GitHub stars) and built developer tooling with 222k+ npm downloads in 12 months. "
            "The project history below includes every project named in the full CV.",
            "summary",
        ),
        section("Experience & Ventures"),
        entry(
            "Freelance Software Engineer",
            "2025-2026",
            [
                f"<b>{link('PHONT', 'https://phont.ai')} (2025; month not recorded):</b> Re-engineered a WebGL/FFmpeg "
                "video-export pipeline from real-time capture to deterministic frame-by-frame "
                "rendering, improving export speed by up to <b>50x in project benchmarks</b>.",
                f"<b>{link('Exodus', 'https://www.exodus.com')} (2025; month not recorded):</b> Delivered "
                "performance-sensitive gestures, animations, and product flows across Exodus "
                "Mobile and Grateful using React Native, Reanimated, Skia, and native iOS/Android "
                "integration.",
            ],
            subtitle="Selected client engagements",
        ),
        entry(
            f"Founder &amp; Engineer | {link('Spacebar Chat', 'https://spacebar.chat')}",
            "Jan 2021-present",
            [
                f"<b>{link('MyroDex', 'https://myrodex.gg')} (2026; month not recorded):</b> Founded and built "
                "a multi-tenant esports operations SaaS end to end across customer and back-office "
                "apps, organization RBAC, workflows, Stripe billing, background workers, automated "
                "tests, and a production deployment workflow.",
                "Founded a self-hostable, Discord-compatible chat, voice, and video "
                "platform whose flagship repository reached <b>6.7k+ stars and 220+ forks</b>; "
                "the ecosystem spans HTTP APIs, WebSocket/WebRTC, CDN/media delivery, data "
                "models, administration tooling, and clients.",
            ],
            space_after=1.0,
        ),
        entry(
            f"Founder &amp; Engineer | {link('Respond', 'https://github.com/respondchat')}",
            "Jan 2022-present",
            [
                "Founded a multi-platform messaging initiative uniting WhatsApp, Telegram, "
                "Discord, and Fosscord/Spacebar in one client experience; built supporting "
                "React Native, Rust, and JSI runtime infrastructure.",
            ],
            space_after=1.0,
        ),
        entry(
            f"Open-Source Contributor / Maintainer | {link('Trant Labs', 'https://github.com/trantlabs')}",
            "Jan 2021-Nov 2024",
            [
                f"Contributed features, releases, documentation, and CI/CD to {link('missing-native-js-functions', 'https://github.com/trantlabs/missing-native-js-functions')}, "
                "a zero-dependency JavaScript utility library.",
            ],
            space_after=1.0,
        ),
        entry(
            "Independent Software Developer",
            "From Jan 2018",
            [
                f"Built the {link('GyKi', 'https://github.com/samuelscheit/gyki-app')} school app for timetables, substitution plans, and appointments; "
                f"created the historical {link('Discord Bot Client', 'https://github.com/samuelscheit/discord-bot-client')} (695 stars / 390 forks) "
                "and Discord bots for commissioned work.",
                "Built an early database-backed server-management application and developed a foundation in C, Linux, HTML/CSS, PHP, and SQL.",
            ],
            space_after=1.0,
        ),
        section("Projects"),
        project_entry(
            f"{link('Puppeteer Stream', 'https://github.com/samuelscheit/puppeteer-stream')} | Creator &amp; Maintainer",
            "Dec 2020-present",
            [
                "Created and maintains a TypeScript browser audio/video capture library for "
                f"Puppeteer with {link('222k+ npm downloads', 'https://api.npmjs.org/downloads/point/2025-08-25:2026-08-24/puppeteer-stream')} "
                "in the 12 months ending August 2026, <b>459+ GitHub stars and 131 forks</b>.",
            ],
            space_after=1.0,
        ),
        project_entry(
            f"{link('React Native Skia List', 'https://github.com/samuelscheit/react-native-skia-list')} | Creator",
            "Oct 2024-present",
            [
                "Built a Skia/C++ virtualized list that rendered 1,000 items <b>up to 10x faster</b> "
                "than existing react-native list rendering solutions with "
                f"{link('about 70% fewer dropped frames', 'https://samuelscheit.com/blog/2024/react-native-skia-list')}"
                "; 240+ GitHub stars.",
            ],
            space_after=1.0,
        ),
        project_entry(
            f"{link('Phishing Support', 'https://phishing.support')} | Creator",
            "Jan 2026-present",
            [
                "Built an open-source tool for automated analysis, reporting, and tracking of phishing emails and malicious websites, including indicator extraction, automated checks, and abuse/takedown workflows.",
            ],
        ),
        project_entry(
            f"{link('Bundestagswahl 2025', 'https://github.com/samuelscheit/bundestagswahl2025')} | Independent Data Analysis",
            "Feb 2025",
            [
                "Built and published a TypeScript/Bun data pipeline and interactive map covering all 299 German federal-election constituencies; documented the methodology in a public article.",
            ],
        ),
        project_entry(
            f"{link('Browser Fingerprinting Technical Analysis', 'https://github.com/samuelscheit/fingerprinting')} | Co-author",
            "May 2024-present",
            [
                "Co-authored a FingerprintJS-based technical analysis; developed a custom fingerprinting library and dataset to evaluate identification methods, limitations, and countermeasures.",
            ],
        ),
        project_entry(
            f"{link('WPlace World Archive', 'https://github.com/samuelscheit/wplace-archive')} | Creator",
            "Aug 2025-present",
            [
                "Built a C++/Linux system to scrape, archive, process, and visualize the entire wplace.live map with tiled storage, VIPS lower-zoom generation, and full-world jobs.",
            ],
        ),
        project_entry(
            f"{link('Spotify DRM Report', 'https://github.com/samuelscheit/spotify-drm-report')} | Independent Technical Research",
            "May 2025 (report 2023)",
            [
                "Published a proof-of-concept report on a reported missing-DRM-enforcement issue in Spotify's Accesspoint API; no CVE, bounty, or vendor outcome is claimed.",
            ],
        ),
        project_entry(
            f"{link('Team Checkmate / Hackatum 2024', 'https://github.com/samuelscheit/hackatum-2024')} | Systems Challenge",
            "Nov 2024",
            [
                "Co-built a high-concurrency Go REST backend for Check24's car-rental challenge using SQL optimization, in-memory bitmap filtering, B-trees, and fasthttp.",
            ],
        ),
        project_entry(
            "Upstream Mobile &amp; Native Contributions",
            "Sep-Oct 2024",
            [
                f"Landed {link('React Native Skia iOS ProMotion 120 Hz', 'https://github.com/Shopify/react-native-skia/pull/2690')} support, originated its {link('macOS Catalyst approach', 'https://github.com/Shopify/react-native-skia/pull/3296')}, and added {link('iOS support to jsi-rs', 'https://github.com/laptou/jsi-rs/pull/3')} for Rust/JSI interoperability.",
            ],
        ),
        section("Technical Writing"),
        paragraph(
            f"{link('Jul 2023', 'https://samuelscheit.com/blog/2023/react-native-rust')} - Using Rust in React Native with jsi-rs; "
            f"{link('Oct 2024', 'https://samuelscheit.com/blog/2024/react-native-skia-list')} - Implementing the fastest list renderer for React Native; "
            f"{link('Feb 2025', 'https://samuelscheit.com/blog/2025/bundestagswahl')} - Fehlende Stimmen bei der Bundestagswahl 2025?",
            "compact",
        ),
        section("Selected Additional Projects"),
        paragraph(
            "Curated from my own repository history and limited to projects that demonstrate meaningful engineering work. "
            "Dates use each repository's creation month; summaries focus on recruiter-relevant engineering scope.",
            "subtitle",
        ),
        *curated_project_entries(),
        section("Technical Skills"),
        paragraph(
            "<b>Primary:</b> TypeScript, JavaScript, React, Next.js, React Native, Node.js/Bun<br/>"
            "<b>Backend &amp; delivery:</b> PostgreSQL, GraphQL, WebSocket/WebRTC, Docker, Linux, Playwright, CI/CD, Go<br/>"
            "<b>Mobile &amp; performance:</b> Skia, Reanimated, JSI/Hermes, iOS/Android, C++, Rust, WebGL/FFmpeg",
            "compact",
        ),
        section("Education"),
        paragraph(
            "<b>Technical University of Munich (TUM)</b> | Informatics studies (no degree) | 2022-2024",
            "compact",
        ),
        Spacer(1, 1.2),
        paragraph(
            "<b>Gymnasium Kirchheim</b> | Allgemeine Hochschulreife (Abitur), grade 1.9 | 2022",
            "compact",
        ),
    ]


def verify_pdf(path: Path) -> None:
    reader = PdfReader(path)
    if len(reader.pages) < 2:
        raise RuntimeError(
            "The complete project history should span at least two pages; "
            f"generated {len(reader.pages)} page"
        )

    pages_text: list[str] = []
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - A4[0]) > 0.5 or abs(height - A4[1]) > 0.5:
            raise RuntimeError(f"Expected A4, generated {width:.1f} x {height:.1f} points")
        pages_text.append(page.extract_text() or "")

    text = "\n".join(pages_text)
    # ReportLab may insert line breaks in long headings while extracting text;
    # keep a whitespace-normalized copy for content assertions.
    flat_text = " ".join(text.split())
    required_text = [
        "Samuel Scheit",
        "Freelance Software Engineer",
        "Founder & Engineer",
        "MyroDex",
        "Spacebar Chat",
        "Respond",
        "Trant Labs",
        "GyKi",
        "Discord Bot Client",
        "Puppeteer Stream",
        "React Native Skia List",
        "Phishing Support",
        "Bundestagswahl 2025",
        "Browser Fingerprinting Technical Analysis",
        "WPlace World Archive",
        "Spotify DRM Report",
        "Team Checkmate / Hackatum 2024",
        "TECHNICAL WRITING",
        "Jan 2021",
        "Dec 2020",
        "Oct 2024",
        "Feb 2025",
        "Technical University of Munich",
    ]
    required_text.extend(repository for repository, _role, _summary in CURATED_PROJECTS)
    missing_text = [item for item in required_text if item not in flat_text]
    if missing_text:
        raise RuntimeError(f"Missing required text in generated PDF: {missing_text}")

    freelance_start = flat_text.index("Freelance Software Engineer")
    founder_start = flat_text.index("Founder & Engineer")
    if freelance_start >= founder_start:
        raise RuntimeError("Founder experience must follow freelance experience")
    if "MyroDex" in flat_text[freelance_start:founder_start]:
        raise RuntimeError("MyroDex must not be listed under freelance experience")
    if flat_text.find("MyroDex", founder_start) == -1:
        raise RuntimeError("MyroDex must be listed under founder experience")
    if "More repository history" in flat_text or "commits.json" in flat_text:
        raise RuntimeError("Internal source references must not appear in the recruiter-facing CV")

    uris = set()
    for page in reader.pages:
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                uris.add(str(action["/URI"]))
    required_uris = {
        "mailto:contact@samuelscheit.com",
        "https://github.com/samuelscheit",
        "https://spacebar.chat",
        "https://github.com/respondchat",
        "https://github.com/trantlabs",
        "https://github.com/trantlabs/missing-native-js-functions",
        "https://github.com/samuelscheit/gyki-app",
        "https://github.com/samuelscheit/discord-bot-client",
        "https://github.com/samuelscheit/puppeteer-stream",
        "https://github.com/samuelscheit/react-native-skia-list",
        "https://github.com/samuelscheit/react-native-skia-yoga",
        "https://phishing.support",
        "https://github.com/samuelscheit/cccb-servicepoint-browser",
        "https://github.com/samuelscheit/missing-native-js-syntax",
        "https://github.com/samuelscheit/GykiSpace",
        "https://github.com/samuelscheit/Lambert-server",
        "https://github.com/samuelscheit/Lambert-orm",
        "https://github.com/samuelscheit/Database-Browser",
        "https://github.com/samuelscheit/bundestagswahl2025",
        "https://github.com/samuelscheit/fingerprinting",
        "https://github.com/samuelscheit/wplace-archive",
        "https://github.com/samuelscheit/spotify-drm-report",
        "https://github.com/samuelscheit/hackatum-2024",
    }
    missing_uris = sorted(required_uris - uris)
    if missing_uris:
        raise RuntimeError(f"Missing required hyperlinks: {missing_uris}")


def build() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=15 * mm,
        bottomMargin=12 * mm,
        title="Samuel Scheit - Curriculum Vitae",
        author="Samuel Scheit",
        subject="Software engineering curriculum vitae",
    )
    def draw_footer(canvas, _document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(LEFT_MARGIN, 9 * mm, PAGE_WIDTH - RIGHT_MARGIN, 9 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT_MARGIN, 5.5 * mm, "Samuel Scheit - Curriculum Vitae")
        canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, 5.5 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    document.build(build_story(), onFirstPage=draw_footer, onLaterPages=draw_footer)
    verify_pdf(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
