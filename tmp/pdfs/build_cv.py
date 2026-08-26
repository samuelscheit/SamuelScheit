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
from dataclasses import dataclass
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
        raise RuntimeError(f"Repository {name!r} is not present in the GitHub project data as Samuel's repository")
    details = repository["details"]
    if details.get("isFork"):
        raise RuntimeError(f"Repository {name!r} is a fork and cannot be presented as a created project")
    return details


def github_created_month(name: str) -> str:
    created_at = github_project(name).get("createdAt")
    if not created_at:
        raise RuntimeError(f"Repository {name!r} has no creation date in the GitHub project data")
    try:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%b %Y")
    except ValueError as error:
        raise RuntimeError(f"Invalid creation date for repository {name!r}: {created_at!r}") from error


def github_project_title(name: str, role: str, display_name: str | None = None) -> str:
    details = github_project(name)
    label = display_name or name
    # Private repositories are deliberately not linked; their summaries still
    # communicate the work without exposing an inaccessible destination.
    if details.get("isPrivate"):
        return f"{escape(label)} (private) | {escape(role)}"
    return f"{link(label, details['url'])} | {escape(role)}"


@dataclass(frozen=True)
class CuratedProject:
    """A recruiter-relevant project validated against the local GitHub export."""

    repository: str
    title: str
    role: str
    summaries: tuple[str, ...]
    date: str | None = None


# This deliberately represents a curated portfolio, not a raw GitHub dump.
# Every entry is validated as a repository owned by Samuel Scheit and not a
# fork; private entries remain unlinked in the rendered CV.
CURATED_PROJECTS: tuple[CuratedProject, ...] = (
    CuratedProject(
        "npm-malicious-check",
        "npm-malicious-check",
        "Creator - supply-chain security tooling",
        (
            "Built a Python triage utility that downloads npm malware advisories, normalizes them to CSV, and scans local npm, Bun, and Yarn caches for package/version matches.",
            "Designed the workflow to give developers and incident responders a fast, auditable first check after a supply-chain incident.",
        ),
    ),
    CuratedProject(
        "prediction_arbitrage",
        "Prediction Market Data Platform",
        "Creator - real-time market-data platform",
        (
            "Built a private real-time prediction-market data platform integrating Polymarket and Kalshi HTTP and WebSocket feeds.",
            "Designed reconnection and subscription logic, a TimescaleDB ingestion pipeline, Docker delivery, and a web application for exploring live orders and event data.",
        ),
    ),
    CuratedProject(
        "react-native-skia-yoga",
        "React Native Skia Yoga",
        "Creator - React Native rendering prototype",
        (
            "Developed a C++/TypeScript library combining Yoga layout with React Native Skia for declarative, interactive UI rendering.",
            "Built the JSX intrinsic-node surface and example integration for complex layouts, while clearly documenting the project as an early-stage prototype.",
        ),
    ),
    CuratedProject(
        "holistische",
        "Holistische",
        "Founder - AI-assisted news platform",
        (
            "Built a private AI-assisted news aggregation product covering German and international reporting.",
            "Designed the product and publishing workflow around source-based aggregation, structured editorial review, and clear positioning.",
        ),
    ),
    CuratedProject(
        "Baileys",
        "Baileys Mobile Protocol Stack",
        "Creator - messaging protocol infrastructure",
        (
            "Extended a private WhatsApp-compatible messaging stack with native-mobile API support, TCP transport, registration flows, media mappings, CAPTCHA handling, and device/session events.",
            "Worked across protocol integration, asynchronous connection state, and mobile-specific behavior in a TypeScript runtime.",
        ),
    ),
    CuratedProject(
        "whatsapp",
        "WhatsApp Operations Backend",
        "Creator - private messaging backend",
        (
            "Built a private WhatsApp operations backend and dashboard with account authentication, APNs integration, proxy handling, API-key management, and account-event processing.",
            "Added BullMQ-backed jobs, structured logging, lazy-loaded data tables, and performance-focused API flows for a multi-account service.",
        ),
    ),
    CuratedProject(
        "missing-native-js-syntax",
        "Missing Native JS Syntax",
        "Creator and maintainer - TypeScript tooling",
        (
            "Created a TypeScript transformer and Babel plugin that adds missing JavaScript syntax patterns to existing codebases.",
            "Packaged the tool for npm with documentation, examples, and automated CI, demonstrating compiler-tooling and developer-experience work.",
        ),
    ),
    CuratedProject(
        "PokemonGame",
        "Pokémon-inspired 2D Game",
        "Creator - Java game development",
        (
            "Built a complete 2D game in Java with the LITIengine framework, including game mechanics, assets, and a distributable release.",
            "Applied object-oriented design and game-engine development in an independently shipped personal project.",
        ),
    ),
    CuratedProject(
        "spotify-playback-sdk-node",
        "Spotify Playback SDK for Node.js",
        "Creator - developer library",
        (
            "Created a Node.js wrapper around Spotify's Web Playback SDK to make browser playback capabilities accessible from JavaScript applications.",
            "Published the library as a reusable developer integration and maintained supporting documentation and example environments.",
        ),
    ),
    CuratedProject(
        "carcassonne-ai",
        "Carcassonne AI",
        "Creator - AI and game-systems project",
        (
            "Designed and implemented an AI for the board game Carcassonne as a school seminar project, supported by a technical paper and playable implementation.",
            "Explored search and decision-making techniques alongside Python game logic and a visual game interface.",
        ),
    ),
    CuratedProject(
        "gyki-app",
        "GyKi Mobile App",
        "Creator - iOS school companion",
        (
            "Built a native iOS app for the Gymnasium Kirchheim community, giving students mobile access to timetables and substitution plans.",
            "Developed the app as part of a broader school-product effort that later included collaboration and communication tools.",
        ),
        date="2018; repository archived Apr 2022",
    ),
    CuratedProject(
        "minecraft-server-admin-panel",
        "Minecraft Server Admin Panel",
        "Creator - self-hosted infrastructure tooling",
        (
            "Built a web dashboard for creating and administering self-hosted Minecraft servers, covering operational workflows and server configuration.",
            "Established an early foundation in Linux-hosted services, PHP, SQL, and browser-based administration interfaces.",
        ),
        date="2017; repository created Jun 2021",
    ),
)


def curated_project_entries() -> list[KeepTogether]:
    return [
        project_entry(
            github_project_title(project.repository, project.role, project.title),
            project.date or github_created_month(project.repository),
            list(project.summaries),
            space_after=1.6,
        )
        for project in CURATED_PROJECTS
    ]


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
            "Delivered product engineering for PHONT, Exodus, and Myrodex; founded Spacebar "
            "(6.7k+ GitHub stars) and built developer tooling with 222k+ npm downloads in 12 months. "
            "Selected projects below highlight product ownership, systems work, and developer tooling.",
            "summary",
        ),
        section("Experience & Ventures"),
        entry(
            "Freelance Software Engineer",
            "2025-2026",
            [
                f"<b>{link('PHONT', 'https://phont.ai')} (Jul-Sep 2025):</b> Re-engineered a WebGL/FFmpeg "
                "video-export pipeline from real-time capture to deterministic frame-by-frame "
                "rendering, improving export speed by up to <b>50x in project benchmarks</b>.",
                f"<b>{link('Exodus', 'https://www.exodus.com')} (Oct-Nov 2025):</b> Delivered "
                "performance-sensitive gestures, animations, and product flows across Exodus "
                "Mobile and Grateful using React Native, Reanimated, Skia, and native iOS/Android "
                "integration.",
            ],
            subtitle="Selected client engagements",
        ),
        entry(
            f"Founder &amp; Engineer | {link('Myrodex', 'https://myrodex.gg')}",
            "Mar 2025-present",
            [
                "Founded and built a multi-tenant esports operations SaaS end to end across customer and back-office "
                "apps, organization RBAC, workflows, Stripe billing, background workers, automated "
                "tests, and a production deployment workflow.",
            ],
            space_after=1.0,
        ),
        entry(
            f"Founder &amp; Engineer | {link('Spacebar Chat', 'https://spacebar.chat')}",
            "Jan 2021-present",
            [
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
                "Founded Respond, a multi-platform messaging app uniting WhatsApp, Telegram, "
                "Discord, and Fosscord/Spacebar in one client experience; built supporting "
                "React Native, Rust, and JSI runtime infrastructure.",
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
            f"{link('Browser Fingerprinting Technical Analysis', 'https://github.com/samuelscheit/fingerprinting')} | Author",
            "May 2024-present",
            [
                "Authored a FingerprintJS-based technical analysis; developed a custom fingerprinting library and dataset to evaluate identification methods, limitations, and countermeasures.",
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
                "Published a proof-of-concept report on a reported missing-DRM-enforcement issue in Spotify's Accesspoint API.",
            ],
        ),
        project_entry(
            f"{link('Discord Bot Client', 'https://github.com/samuelscheit/discord-bot-client')} | Creator",
            "May 2020",
            [
                "Created a Discord client fork with bot-login support, exposing a bot-oriented client experience that the official application did not provide.",
                "Built and maintained a widely adopted open-source project with <b>695 GitHub stars, 390 forks, and 908,716 GitHub release-asset downloads</b> across its ten published installers.",
            ],
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
        "Myrodex",
        "Spacebar Chat",
        "Respond",
        "Discord Bot Client",
        "Puppeteer Stream",
        "React Native Skia List",
        "Phishing Support",
        "Bundestagswahl 2025",
        "Browser Fingerprinting Technical Analysis",
        "WPlace World Archive",
        "Spotify DRM Report",
        "Prediction Market Data Platform",
        "GyKi Mobile App",
        "Jan 2021",
        "Mar 2025",
        "Jul-Sep 2025",
        "Oct-Nov 2025",
        "Dec 2020",
        "Oct 2024",
        "Feb 2025",
        "Technical University of Munich",
    ]
    required_text.extend(project.title for project in CURATED_PROJECTS)
    missing_text = [item for item in required_text if item not in flat_text]
    if missing_text:
        raise RuntimeError(f"Missing required text in generated PDF: {missing_text}")

    freelance_start = flat_text.index("Freelance Software Engineer")
    founder_start = flat_text.index("Founder & Engineer")
    if freelance_start >= founder_start:
        raise RuntimeError("Founder experience must follow freelance experience")
    if "Myrodex" in flat_text[freelance_start:founder_start]:
        raise RuntimeError("Myrodex must not be listed under freelance experience")
    if flat_text.find("Myrodex", founder_start) == -1:
        raise RuntimeError("Myrodex must be listed under founder experience")
    removed_text = [
        "Open-Source Contributor / Maintainer | Trant Labs",
        "Team Checkmate / Hackatum 2024",
        "Upstream Mobile & Native Contributions",
        "TECHNICAL WRITING",
        "SELECTED ADDITIONAL PROJECTS",
        "Curated from my own repository history",
        "More repository history",
        "commits.json",
    ]
    unexpected_text = [item for item in removed_text if item in flat_text]
    if unexpected_text:
        raise RuntimeError(f"Removed content is still present in the recruiter-facing CV: {unexpected_text}")

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
        "https://github.com/samuelscheit/discord-bot-client",
        "https://github.com/samuelscheit/puppeteer-stream",
        "https://github.com/samuelscheit/react-native-skia-list",
        "https://phishing.support",
        "https://github.com/samuelscheit/bundestagswahl2025",
        "https://github.com/samuelscheit/fingerprinting",
        "https://github.com/samuelscheit/wplace-archive",
        "https://github.com/samuelscheit/spotify-drm-report",
    }
    required_uris.update(
        details["url"]
        for project in CURATED_PROJECTS
        if not (details := github_project(project.repository)).get("isPrivate")
    )
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
