"""Build Samuel Scheit's complete, recruiter-focused CV.

The project portfolio is deliberately curated rather than generated from every
repository.  Its entries are validated against the local GitHub metadata so
only projects Samuel created, not contribution-only repositories or forks, can
appear in the CV.
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
    PageBreak,
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


@dataclass(frozen=True)
class PortfolioProject:
    """A recruiter-relevant project validated against owned GitHub metadata."""

    repository: str
    title: str
    role: str
    date: str
    sort_date: datetime
    summaries: tuple[str, ...]
    url_override: str | None = None


# This is a curated recruiter portfolio rather than a repository listing. Each
# record maps to a project owned by Samuel Scheit and not marked as a fork in
# GitHub metadata.  Entries are rendered newest-first, the standard CV order.
PORTFOLIO_PROJECTS: tuple[PortfolioProject, ...] = (
    PortfolioProject(
        "npm-malicious-check",
        "npm-malicious-check",
        "Creator",
        "May 2026",
        datetime(2026, 5, 15),
        (
            "Built a Python triage utility that downloads npm malware advisories, normalizes them to CSV, and scans local npm, Bun, and Yarn caches for package/version matches.",
            "Designed the workflow to give developers and incident responders a fast, auditable first check after a supply-chain incident.",
        ),
    ),
    PortfolioProject(
        "phishing.support",
        "Phishing Support",
        "Creator",
        "Jan 2026",
        datetime(2026, 1, 9),
        (
            "Built an open-source tool for automated analysis, reporting, and tracking of phishing emails and malicious websites, including indicator extraction, automated checks, and abuse/takedown workflows.",
        ),
        url_override="https://phishing.support",
    ),
    PortfolioProject(
        "prediction_arbitrage",
        "Prediction Market Data Platform",
        "Creator",
        "Sep 2025",
        datetime(2025, 9, 20),
        (
            "Built a private real-time prediction-market data platform integrating Polymarket and Kalshi HTTP and WebSocket feeds.",
            "Designed reconnection and subscription logic, a TimescaleDB ingestion pipeline, Docker delivery, and a web application for exploring live orders and event data.",
        ),
    ),
    PortfolioProject(
        "wplace-archive",
        "WPlace World Archive",
        "Creator",
        "Aug 2025",
        datetime(2025, 8, 23),
        (
            "Built a C++/Linux system to scrape, archive, process, and visualize the entire wplace.live map with tiled storage, VIPS lower-zoom generation, and full-world jobs.",
        ),
    ),
    PortfolioProject(
        "react-native-skia-yoga",
        "React Native Skia Yoga",
        "Creator",
        "Jul 2025",
        datetime(2025, 7, 30),
        (
            "Developed a C++/TypeScript library combining Yoga layout with React Native Skia for declarative, interactive UI rendering.",
        ),
    ),
    PortfolioProject(
        "holistische",
        "Holistische",
        "Founder - AI-assisted news platform",
        "Jun 2025",
        datetime(2025, 6, 5),
        (
            "Built an AI-assisted news aggregation product covering German and international reporting.",
            "Designed the product and publishing workflow around source-based aggregation, structured editorial review, and clear positioning.",
        ),
        url_override="https://holistische.de",
    ),
    PortfolioProject(
        "spotify-drm-report",
        "Spotify DRM Report",
        "Independent Technical Research",
        "May 2025",
        datetime(2025, 5, 20),
        (
            "Published a proof-of-concept report on a reported missing-DRM-enforcement issue in Spotify's Accesspoint API.",
        ),
    ),
    PortfolioProject(
        "bundestagswahl2025",
        "Bundestagswahl 2025",
        "Independent Data Analysis",
        "Feb 2025",
        datetime(2025, 2, 26),
        (
            "Built and published a TypeScript/Bun data pipeline and interactive map covering all 299 German federal-election constituencies; documented the methodology in a public article.",
        ),
    ),
    PortfolioProject(
        "react-native-skia-list",
        "React Native Skia List",
        "Creator",
        "Oct 2024",
        datetime(2024, 10, 15),
        (
            "Built a Skia/C++ virtualized list that rendered 1,000 items up to 10x faster than existing React Native list-rendering solutions with about 70% fewer dropped frames; 240+ GitHub stars.",
        ),
    ),
    PortfolioProject(
        "fingerprinting",
        "Browser Fingerprinting Technical Analysis",
        "Author",
        "May 2024",
        datetime(2024, 5, 8),
        (
            "Authored a FingerprintJS-based technical analysis; developed a custom fingerprinting library and dataset to evaluate identification methods, limitations, and countermeasures.",
        ),
    ),
    PortfolioProject(
        "Baileys",
        "Baileys & WhatsApp Messaging Stack",
        "Creator",
        "Apr 2023",
        datetime(2023, 4, 20),
        (
            "Extended a private WhatsApp-compatible messaging stack with native-mobile API support, TCP transport, registration flows, media mappings, and device/session events.",
            "Built the associated operations backend and dashboard with account authentication, APNs integration, proxy handling, API-key management, BullMQ jobs, structured logging, and performance-focused data flows.",
        ),
    ),
    PortfolioProject(
        "missing-native-js-syntax",
        "Missing Native JS Syntax",
        "Creator & Maintainer",
        "Jul 2023",
        datetime(2023, 7, 28),
        (
            "Created a TypeScript transformer and Babel plugin that adds missing JavaScript syntax patterns to existing codebases.",
            "Packaged the tool for npm with documentation, examples, and automated CI, demonstrating compiler-tooling and developer-experience work.",
        ),
    ),
    PortfolioProject(
        "PokemonGame",
        "Pokémon-inspired 2D Game",
        "Creator",
        "Feb 2021",
        datetime(2021, 2, 24),
        (
            "Built a complete 2D game in Java with the LITIengine framework, including game mechanics, assets, and a distributable release.",
            "Applied object-oriented design and game-engine development in an independently shipped personal project.",
        ),
    ),
    PortfolioProject(
        "puppeteer-stream",
        "Puppeteer Stream",
        "Creator & Maintainer",
        "Dec 2020",
        datetime(2020, 12, 22),
        (
            "Created and maintains a TypeScript browser audio/video capture library for Puppeteer with 222k+ npm downloads in the 12 months ending August 2026, 459+ GitHub stars, and 131 forks.",
        ),
    ),
    PortfolioProject(
        "carcassonne-ai",
        "Carcassonne AI",
        "Creator",
        "Nov 2020",
        datetime(2020, 11, 16),
        (
            "Designed and implemented an AI for the board game Carcassonne as a school seminar project, supported by a technical paper and playable implementation.",
            "Explored search and decision-making techniques alongside Python game logic and a visual game interface.",
        ),
    ),
    PortfolioProject(
        "discord-bot-client",
        "Discord Bot Client",
        "Creator",
        "May 2020",
        datetime(2020, 5, 15),
        (
            "Created a Discord client fork with bot-login support, exposing a bot-oriented client experience that the official application did not provide.",
            "Built and maintained a widely adopted open-source project with 695 GitHub stars, 390 forks, and 908,716 downloads.",
        ),
    ),
    PortfolioProject(
        "gyki-app",
        "GyKi Mobile App",
        "Creator",
        "Feb 2019",
        datetime(2019, 2, 1),
        (
            "Developed GYKI, a school app for Gymnasium Kirchheim students, reaching 1,753 users.",
        ),
    ),
)


def portfolio_project_title(project: PortfolioProject) -> str:
    details = github_project(project.repository)
    if project.url_override:
        return f"{link(project.title, project.url_override)} | {escape(project.role)}"
    if details.get("isPrivate"):
        return f"{escape(project.title)} | {escape(project.role)}"
    return f"{link(project.title, details['url'])} | {escape(project.role)}"


def portfolio_project_url(project: PortfolioProject) -> str | None:
    """Return the recruiter-facing URL while keeping private projects private."""
    if project.url_override:
        return project.url_override
    details = github_project(project.repository)
    return None if details.get("isPrivate") else str(details["url"])


def portfolio_project_entries() -> list[KeepTogether]:
    """Render one continuous, newest-first portfolio section.

    The page break is purely typographic: it keeps the Projects section
    unified while giving the final projects, skills, languages, and education
    enough room to render as a balanced final page.
    """
    entries: list = []
    for project in sorted(PORTFOLIO_PROJECTS, key=lambda project: project.sort_date, reverse=True):
        entries.append(
            project_entry(
                portfolio_project_title(project),
                project.date,
                list(project.summaries),
                space_after=1.6,
            )
        )
        if project.repository == "PokemonGame":
            entries.append(PageBreak())
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
            "Jan 2021-Jan 2022",
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
            "Jan 2022-Dec 2024",
            [
                "Founded Respond, a multi-platform messaging app uniting WhatsApp, Telegram, "
                "Discord, and Fosscord/Spacebar in one client experience; built supporting "
                "React Native, Rust, and JSI runtime infrastructure.",
            ],
            space_after=1.0,
        ),
        section("Projects"),
        paragraph(
            f"<b>GitHub overview of all work:</b> {link('samuelscheit.com/github', 'https://samuelscheit.com/github')}",
            "subtitle",
        ),
        *portfolio_project_entries(),
        section("Technical Skills"),
        paragraph(
            "<b>Primary:</b> TypeScript, JavaScript, React, Next.js, React Native, Node.js/Bun<br/>"
            "<b>Backend &amp; delivery:</b> PostgreSQL, GraphQL, WebSocket/WebRTC, Docker, Linux, Playwright, CI/CD, Go<br/>"
            "<b>Mobile &amp; performance:</b> Skia, Reanimated, JSI/Hermes, iOS/Android, C++, Rust, WebGL/FFmpeg",
            "compact",
        ),
        section("Languages"),
        paragraph(
            "<b>German:</b> Native speaker &nbsp;|&nbsp; <b>English:</b> B2 (upper-intermediate)",
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
        "Jan 2021-Jan 2022",
        "Mar 2025",
        "Jul-Sep 2025",
        "Oct-Nov 2025",
        "Dec 2020",
        "Oct 2024",
        "Feb 2025",
        "German:",
        "Native speaker",
        "English:",
        "B2 (upper-intermediate)",
        "Technical University of Munich",
    ]
    required_text.extend(project.title for project in PORTFOLIO_PROJECTS)
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
        "Spotify Playback SDK for Node.js",
        "WhatsApp Operations Backend",
        "Minecraft Server Admin Panel",
        "cccb-servicepoint-browser",
        "jura",
        "gpia",
        "GykiSpace",
        "Lambert-server",
        "Lambert-orm",
        "Database-Browser",
        "CAPTCHA",
        "(private)",
    ]
    unexpected_text = [item for item in removed_text if item in flat_text]
    if unexpected_text:
        raise RuntimeError(f"Removed content is still present in the recruiter-facing CV: {unexpected_text}")

    projects_start = flat_text.index("PROJECTS")
    skills_start = flat_text.index("TECHNICAL SKILLS")
    projects_text = flat_text[projects_start:skills_start]
    if "present" in projects_text:
        raise RuntimeError("Projects must use completion dates rather than open-ended date ranges")
    ordered_titles = [project.title for project in sorted(PORTFOLIO_PROJECTS, key=lambda project: project.sort_date, reverse=True)]
    positions = [projects_text.index(title) for title in ordered_titles]
    if positions != sorted(positions):
        raise RuntimeError("Projects are not ordered chronologically, newest first")

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
        "https://samuelscheit.com/github",
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
        url
        for project in PORTFOLIO_PROJECTS
        if (url := portfolio_project_url(project)) is not None
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
