"""Build Samuel Scheit's recruiter-focused CV in English and German.

The English copy and its German translation live together in this file.  The
portfolio is deliberately curated rather than generated from every repository:
each listed project is validated against the local GitHub metadata as owned by
Samuel Scheit and not a fork before either PDF is rendered.
"""

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Literal
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

Language = Literal["en", "de"]

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS: dict[Language, Path] = {
    "en": ROOT / "output/pdf/samuel-scheit-cv-en.pdf",
    "de": ROOT / "output/pdf/samuel-scheit-cv-de.pdf",
}

PAGE_WIDTH, _ = A4
LEFT_MARGIN = 15 * mm
RIGHT_MARGIN = 15 * mm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

INK = HexColor("#17212B")
MUTED = HexColor("#4B5563")
ACCENT_HEX = "#0B5D6B"
ACCENT = HexColor(ACCENT_HEX)
RULE = HexColor("#AAB7BC")


@dataclass(frozen=True)
class Localized:
    """English source text paired with its German translation."""

    en: str
    de: str

    def for_language(self, language: Language) -> str:
        return getattr(self, language)


def loc(en: str, de: str) -> Localized:
    return Localized(en=en, de=de)


def tr(value: Localized, language: Language) -> str:
    return value.for_language(language)


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
    return f'<link href="{escape(url)}"><font color="{ACCENT_HEX}">{escape(label)}</font></link>'


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


def entry(title: str, date: str, items: list[str], *, space_after: float = 2.6) -> KeepTogether:
    content = [heading(title, date), *bullets(items), Spacer(1, space_after)]
    return KeepTogether(content)


_GITHUB_DATA: dict | None = None


def github_repositories() -> dict:
    """Load the downloaded GitHub metadata once for project ownership checks."""
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
    """Return a user-created, non-fork repository or fail loudly."""
    repository = next(
        (
            value
            for value in github_repositories().values()
            if (value.get("details") or {}).get("name", "").casefold() == name.casefold()
            and ((value.get("details") or {}).get("owner") or {}).get("login", "").casefold() == "samuelscheit"
        ),
        None,
    )
    if repository is None:
        raise RuntimeError(f"Repository {name!r} is not owned by Samuel Scheit in the GitHub project data")
    details = repository["details"]
    if details.get("isFork"):
        raise RuntimeError(f"Repository {name!r} is a fork and cannot be presented as a created project")
    return details


@dataclass(frozen=True)
class PortfolioProject:
    """A curated, bilingual project validated against owned GitHub metadata."""

    repository: str
    title: Localized
    role: Localized
    date: Localized
    sort_date: datetime
    summaries: tuple[Localized, ...]
    url_override: str | None = None


PORTFOLIO_PROJECTS: tuple[PortfolioProject, ...] = (
    PortfolioProject(
        "npm-malicious-check",
        loc("npm-malicious-check", "npm-malicious-check"),
        loc("Creator", "Ersteller"),
        loc("May 2026", "Mai 2026"),
        datetime(2026, 5, 15),
        (
            loc(
                "Built a Python triage utility that downloads npm malware advisories, normalizes them to CSV, and scans local npm, Bun, and Yarn caches for package/version matches.",
                "Entwickelte ein Python-Triage-Tool, das npm-Malware-Hinweise herunterlädt, als CSV normalisiert und lokale npm-, Bun- und Yarn-Caches auf passende Paket-/Versionskombinationen prüft.",
            ),
            loc(
                "Designed the workflow to give developers and incident responders a fast, auditable first check after a supply-chain incident.",
                "Konzipierte den Ablauf als schnelle, nachvollziehbare Erstprüfung für Entwickler und Incident-Response-Teams nach einem Supply-Chain-Vorfall.",
            ),
        ),
    ),
    PortfolioProject(
        "phishing.support",
        loc("Phishing Support", "Phishing Support"),
        loc("Creator", "Ersteller"),
        loc("Jan 2026", "Jan. 2026"),
        datetime(2026, 1, 9),
        (
            loc(
                "Built an open-source tool for automated analysis, reporting, and tracking of phishing emails and malicious websites, including indicator extraction, automated checks, and abuse/takedown workflows.",
                "Entwickelte ein Open-Source-Tool zur automatisierten Analyse, Meldung und Nachverfolgung von Phishing-E-Mails und schädlichen Websites, einschließlich Indikator-Extraktion, automatisierter Prüfungen sowie Abuse-/Takedown-Workflows.",
            ),
        ),
        url_override="https://phishing.support",
    ),
    PortfolioProject(
        "prediction_arbitrage",
        loc("Prediction Market Data Platform", "Datenplattform für Prognosemärkte"),
        loc("Creator", "Ersteller"),
        loc("Sep 2025", "Sept. 2025"),
        datetime(2025, 9, 20),
        (
            loc(
                "Built a private real-time prediction-market data platform integrating Polymarket and Kalshi HTTP and WebSocket feeds.",
                "Entwickelte eine private Echtzeit-Datenplattform für Prognosemärkte mit Polymarket- und Kalshi-Feeds über HTTP und WebSockets.",
            ),
            loc(
                "Designed reconnection and subscription logic, a TimescaleDB ingestion pipeline, Docker delivery, and a web application for exploring live orders and event data.",
                "Konzipierte Reconnect- und Subscription-Logik, eine TimescaleDB-Ingestion-Pipeline, Docker-Deployment und eine Webanwendung zur Analyse von Live-Orders und Ereignisdaten.",
            ),
        ),
    ),
    PortfolioProject(
        "wplace-archive",
        loc("WPlace World Archive", "WPlace World Archive"),
        loc("Creator", "Ersteller"),
        loc("Aug 2025", "Aug. 2025"),
        datetime(2025, 8, 23),
        (
            loc(
                "Built a C++/Linux system to scrape, archive, process, and visualize the entire wplace.live map with tiled storage, VIPS lower-zoom generation, and full-world jobs.",
                "Entwickelte ein C++/Linux-System zum Scrapen, Archivieren, Verarbeiten und Visualisieren der gesamten wplace.live-Karte mit gekachelter Speicherung, VIPS-generierten Zoomstufen und Full-World-Jobs.",
            ),
        ),
    ),
    PortfolioProject(
        "react-native-skia-yoga",
        loc("React Native Skia Yoga", "React Native Skia Yoga"),
        loc("Creator", "Ersteller"),
        loc("Jul 2025", "Juli 2025"),
        datetime(2025, 7, 30),
        (
            loc(
                "Developed a C++/TypeScript library combining Yoga layout with React Native Skia for declarative, interactive UI rendering.",
                "Entwickelte eine C++/TypeScript-Bibliothek, die das Yoga-Layoutsystem mit React Native Skia für deklaratives, interaktives UI-Rendering verbindet.",
            ),
        ),
    ),
    PortfolioProject(
        "holistische",
        loc("Holistische", "Holistische"),
        loc("Founder", "Gründer"),
        loc("Jun 2025", "Juni 2025"),
        datetime(2025, 6, 5),
        (
            loc(
                "Built an AI-assisted news aggregation product covering German and international reporting.",
                "Entwickelte ein KI-gestütztes News-Aggregationsprodukt für deutsche und internationale Berichterstattung.",
            ),
            loc(
                "Designed the product and publishing workflow around source-based aggregation, structured editorial review, and clear positioning.",
                "Gestaltete Produkt- und Publishing-Workflow rund um quellenbasierte Aggregation, strukturierte redaktionelle Prüfung und klare Positionierung.",
            ),
        ),
        url_override="https://holistische.de",
    ),
    PortfolioProject(
        "spotify-drm-report",
        loc("Spotify DRM Report", "Spotify-DRM-Report"),
        loc("Independent Technical Research", "Unabhängige technische Recherche"),
        loc("May 2025", "Mai 2025"),
        datetime(2025, 5, 20),
        (
            loc(
                "Published a proof-of-concept report on a reported missing-DRM-enforcement issue in Spotify's Accesspoint API.",
                "Veröffentlichte einen Proof-of-Concept-Report über ein gemeldetes Problem bei der DRM-Durchsetzung in Spotifys Accesspoint-API.",
            ),
        ),
    ),
    PortfolioProject(
        "bundestagswahl2025",
        loc("Bundestagswahl 2025", "Bundestagswahl 2025"),
        loc("Independent Data Analysis", "Unabhängige Datenanalyse"),
        loc("Feb 2025", "Feb. 2025"),
        datetime(2025, 2, 26),
        (
            loc(
                "Built and published a TypeScript/Bun data pipeline and interactive map covering all 299 German federal-election constituencies; documented the methodology in a public article.",
                "Entwickelte und veröffentlichte eine TypeScript/Bun-Datenpipeline sowie eine interaktive Karte für alle 299 deutschen Bundestagswahlkreise; dokumentierte die Methodik in einem öffentlichen Artikel.",
            ),
        ),
    ),
    PortfolioProject(
        "react-native-skia-list",
        loc("React Native Skia List", "React Native Skia List"),
        loc("Creator", "Ersteller"),
        loc("Oct 2024", "Okt. 2024"),
        datetime(2024, 10, 15),
        (
            loc(
                "Built a Skia/C++ virtualized list that rendered 1,000 items up to 10x faster than existing React Native list-rendering solutions with about 70% fewer dropped frames; 240+ GitHub stars.",
                "Entwickelte eine virtualisierte Skia/C++-Liste, die 1.000 Elemente bis zu 10x schneller als bestehende React-Native-Listen renderte und dabei rund 70 % weniger Frame-Drops erreichte; 240+ GitHub Stars.",
            ),
        ),
    ),
    PortfolioProject(
        "fingerprinting",
        loc("Browser Fingerprinting Technical Analysis", "Technische Analyse des Browser-Fingerprintings"),
        loc("Author", "Autor"),
        loc("May 2024", "Mai 2024"),
        datetime(2024, 5, 8),
        (
            loc(
                "Authored a FingerprintJS-based technical analysis; developed a custom fingerprinting library and dataset to evaluate identification methods, limitations, and countermeasures.",
                "Verfasste eine technische Analyse auf Basis von FingerprintJS und entwickelte eine eigene Fingerprinting-Bibliothek sowie einen Datensatz zur Bewertung von Identifikationsmethoden, Grenzen und Gegenmaßnahmen.",
            ),
        ),
    ),
    PortfolioProject(
        "missing-native-js-syntax",
        loc("Missing Native JS Syntax", "Missing Native JS Syntax"),
        loc("Creator & Maintainer", "Ersteller"),
        loc("Jul 2023", "Juli 2023"),
        datetime(2023, 7, 28),
        (
            loc(
                "Created a TypeScript transformer and Babel plugin that adds missing JavaScript syntax patterns to existing codebases.",
                "Entwickelte einen TypeScript-Transformer und ein Babel-Plugin, die fehlende JavaScript-Syntaxmuster in bestehende Codebasen einbringen.",
            ),
            loc(
                "Packaged the tool for npm with documentation, examples, and automated CI, demonstrating compiler-tooling and developer-experience work.",
                "Paketierte das Tool für npm mit Dokumentation, Beispielen und automatisierter CI und zeigte damit Erfahrung in Compiler-Tooling und Developer Experience.",
            ),
        ),
    ),
    PortfolioProject(
        "Baileys",
        loc("Baileys & WhatsApp Messaging Stack", "Baileys & WhatsApp Messaging Stack"),
        loc("Creator", "Ersteller"),
        loc("Apr 2023", "Apr. 2023"),
        datetime(2023, 4, 20),
        (
            loc(
                "Extended a private WhatsApp-compatible messaging stack with native-mobile API support, TCP transport, registration flows, media mappings, and device/session events.",
                "Erweiterte einen privaten WhatsApp-kompatiblen Messaging-Stack um Native-Mobile-API-Support, TCP-Transport, Registrierungsabläufe, Media-Mappings sowie Geräte-/Session-Events.",
            ),
            loc(
                "Built the associated operations backend and dashboard with account authentication, APNs integration, proxy handling, API-key management, BullMQ jobs, structured logging, and performance-focused data flows.",
                "Entwickelte das zugehörige Operations-Backend und Dashboard mit Account-Authentifizierung, APNs-Integration, Proxy-Handling, API-Key-Verwaltung, BullMQ-Jobs, strukturiertem Logging und performanceorientierten Datenflüssen.",
            ),
        ),
    ),
    PortfolioProject(
        "PokemonGame",
        loc("Pokémon-inspired 2D Game", "Pokémon-inspiriertes 2D-Spiel"),
        loc("Creator", "Ersteller"),
        loc("Feb 2021", "Feb. 2021"),
        datetime(2021, 2, 24),
        (
            loc(
                "Built a complete 2D game in Java with the LITIengine framework, including game mechanics, assets, and a distributable release.",
                "Entwickelte ein vollständiges 2D-Spiel in Java mit dem LITIengine-Framework, einschließlich Spielmechanik, Assets und distributierbarem Release.",
            ),
            loc(
                "Applied object-oriented design and game-engine development in an independently shipped personal project.",
                "Setzte objektorientiertes Design und Game-Engine-Entwicklung in einem eigenständig veröffentlichten Projekt ein.",
            ),
        ),
    ),
    PortfolioProject(
        "puppeteer-stream",
        loc("Puppeteer Stream", "Puppeteer Stream"),
        loc("Creator & Maintainer", "Ersteller"),
        loc("Dec 2020", "Dez. 2020"),
        datetime(2020, 12, 22),
        (
            loc(
                "Created and maintains a TypeScript browser audio/video capture library for Puppeteer with 222k+ npm downloads in the 12 months ending August 2026, 459+ GitHub stars, and 131 forks.",
                "Entwickelte und betreut eine TypeScript-Bibliothek zur Audio-/Video-Aufzeichnung aus dem Browser mit Puppeteer; 222k+ npm-Downloads in den zwölf Monaten bis August 2026, 459+ GitHub Stars und 131 Forks.",
            ),
        ),
    ),
    PortfolioProject(
        "carcassonne-ai",
        loc("Carcassonne AI", "Carcassonne-KI"),
        loc("Creator", "Ersteller"),
        loc("Nov 2020", "Nov. 2020"),
        datetime(2020, 11, 16),
        (
            loc(
                "Designed and implemented an AI for the board game Carcassonne as a school seminar project, supported by a technical paper and playable implementation.",
                "Konzipierte und implementierte eine KI für das Brettspiel Carcassonne als schulisches Seminarprojekt, ergänzt durch eine technische Ausarbeitung und spielbare Implementierung.",
            ),
            loc(
                "Explored search and decision-making techniques alongside Python game logic and a visual game interface.",
                "Erprobte Such- und Entscheidungsverfahren zusammen mit Python-Spiellogik und einer visuellen Spieloberfläche.",
            ),
        ),
    ),
    PortfolioProject(
        "discord-bot-client",
        loc("Discord Bot Client", "Discord Bot Client"),
        loc("Creator", "Ersteller"),
        loc("May 2020", "Mai 2020"),
        datetime(2020, 5, 15),
        (
            loc(
                "Created a Discord client fork with bot-login support, exposing a bot-oriented client experience that the official application did not provide.",
                "Entwickelte einen Discord-Client-Fork mit Bot-Login-Support und ermöglichte damit eine botorientierte Client-Erfahrung, die die offizielle Anwendung nicht bot.",
            ),
            loc(
                "Built and maintained a widely adopted open-source project with 695 GitHub stars, 390 forks, and 908,716 downloads.",
                "Entwickelte und betreute ein weit verbreitetes Open-Source-Projekt mit 695 GitHub Stars, 390 Forks und 908.716 Downloads.",
            ),
        ),
    ),
    PortfolioProject(
        "gyki-app",
        loc("GyKi Mobile App", "GyKi Mobile App"),
        loc("Creator", "Ersteller"),
        loc("Feb 2019", "Feb. 2019"),
        datetime(2019, 2, 1),
        (
            loc(
                "Developed GYKI, a school app for Gymnasium Kirchheim students, reaching 1,753 users.",
                "Entwickelte GYKI, eine Schul-App für Schülerinnen und Schüler des Gymnasium Kirchheim, die 1.753 Nutzer erreichte.",
            ),
        ),
    ),
)


def portfolio_project_title(project: PortfolioProject, language: Language) -> str:
    details = github_project(project.repository)
    title = tr(project.title, language)
    if project.url_override:
        return link(title, project.url_override)
    if details.get("isPrivate"):
        return escape(title)
    return link(title, details["url"])


def portfolio_project_url(project: PortfolioProject) -> str | None:
    """Return the recruiter-facing URL while keeping private repositories unlinked."""
    if project.url_override:
        return project.url_override
    details = github_project(project.repository)
    return None if details.get("isPrivate") else str(details["url"])


def portfolio_project_entries(language: Language) -> list[KeepTogether]:
    """Render a continuous, newest-first portfolio section."""
    return [
        entry(
            portfolio_project_title(project, language),
            tr(project.date, language),
            [tr(summary, language) for summary in project.summaries],
            space_after=1.6,
        )
        for project in sorted(PORTFOLIO_PROJECTS, key=lambda project: project.sort_date, reverse=True)
    ]


CONTACT = (
    "Munich, Germany"
    f" | {link('+49 160 97788689', 'tel:+491609778869')}"
    f" | {link('contact@samuelscheit.com', 'mailto:contact@samuelscheit.com')}"
    f" | {link('samuelscheit.com', 'https://samuelscheit.com')}"
    f" | {link('GitHub', 'https://github.com/samuelscheit')}"
    f" | {link('LinkedIn', 'https://www.linkedin.com/in/samuel-scheit-343436247/')}"
)
CONTACT_DE = CONTACT.replace("Munich, Germany", "München, Deutschland")


def build_story(language: Language) -> list:
    return [
        paragraph("Samuel Scheit", "name"),
        paragraph(
            tr(
                loc(
                    "Software Engineer | Full-Stack, React Native &amp; Performance Engineering",
                    "Softwareentwickler | Full-Stack, React Native &amp; Performance Engineering",
                ),
                language,
            ),
            "headline",
        ),
        paragraph(CONTACT if language == "en" else CONTACT_DE, "contact"),
        section(tr(loc("Summary", "Profil"), language)),
        paragraph(
            tr(
                loc(
                    "Software engineer with commercial delivery experience across high-performance mobile applications, WebGL video rendering, full-stack SaaS, and real-time systems. Founded and engineered Myrodex; delivered product engineering for PHONT and Exodus; founded Spacebar (6.7k+ GitHub stars); and built developer tooling with 222k+ npm downloads in 12 months. Selected projects below highlight product ownership, systems work, and developer tooling.",
                    "Softwareentwickler mit kommerzieller Umsetzungserfahrung in performanten Mobile-Anwendungen, WebGL-Video-Rendering, Full-Stack-SaaS und Echtzeitsystemen. Gründete und entwickelte Myrodex, lieferte Produktentwicklung für PHONT und Exodus, gründete Spacebar (6,7k+ GitHub Stars) und entwickelte Developer-Tooling mit 222k+ npm-Downloads in zwölf Monaten. Die ausgewählten Projekte zeigen Produktverantwortung, Systems Engineering und Developer Tooling.",
                ),
                language,
            ),
            "summary",
        ),
        section(tr(loc("Experience & Ventures", "Berufserfahrung & Gründungen"), language)),
        entry(
            tr(loc("Freelance Software Engineer", "Freiberuflicher Softwareentwickler"), language),
            "2025-2026",
            [
                tr(
                    loc(
                        f"<b>{link('PHONT', 'https://phont.ai')} (Jul-Sep 2025):</b> Re-engineered a WebGL/FFmpeg video-export pipeline from real-time capture to deterministic frame-by-frame rendering, improving export speed by up to <b>50x in project benchmarks</b>.",
                        f"<b>{link('PHONT', 'https://phont.ai')} (Juli-Sept. 2025):</b> Entwickelte eine WebGL/FFmpeg-Video-Export-Pipeline von Echtzeitaufzeichnung zu deterministischem Frame-by-Frame-Rendering um und beschleunigte den Export in Projektbenchmarks um bis zu <b>50x</b>.",
                    ),
                    language,
                ),
                tr(
                    loc(
                        f"<b>{link('Exodus', 'https://www.exodus.com')} (Oct-Nov 2025):</b> Delivered performance-sensitive gestures, animations, and product flows across Exodus Mobile and Grateful using React Native, Reanimated, Skia, and native iOS/Android integration.",
                        f"<b>{link('Exodus', 'https://www.exodus.com')} (Okt.-Nov. 2025):</b> Entwickelte performancekritische Gesten, Animationen und Produktabläufe für Exodus Mobile und Grateful mit React Native, Reanimated, Skia sowie nativer iOS-/Android-Integration.",
                    ),
                    language,
                ),
            ],
        ),
        entry(
            f"{tr(loc('Founder &amp; Engineer', 'Gründer &amp; Entwickler'), language)} | {link('Myrodex', 'https://myrodex.gg')}",
            tr(loc("Mar 2025-present", "März 2025-heute"), language),
            [
                tr(
                    loc(
                        "Founded and built a multi-tenant esports operations SaaS end to end across customer and back-office apps, organization RBAC, workflows, Stripe billing, background workers, automated tests, and a production deployment workflow.",
                        "Gründete und entwickelte eine Multi-Tenant-SaaS für Esports-Operations end-to-end: Kunden- und Backoffice-Anwendungen, organisationsweite RBAC, Workflows, Stripe-Abrechnung, Background Worker, automatisierte Tests und Produktions-Deployment.",
                    ),
                    language,
                ),
            ],
            space_after=1.0,
        ),
        entry(
            f"{tr(loc('Founder &amp; Engineer', 'Gründer &amp; Entwickler'), language)} | {link('Spacebar Chat', 'https://spacebar.chat')}",
            tr(loc("Jan 2021-Jan 2022", "Jan. 2021-Jan. 2022"), language),
            [
                tr(
                    loc(
                        "Founded a self-hostable, Discord-compatible chat, voice, and video platform whose flagship repository reached <b>6.7k+ stars and 220+ forks</b>; the ecosystem spans HTTP APIs, WebSocket/WebRTC, CDN/media delivery, data models, administration tooling, and clients.",
                        "Gründete eine selbst hostbare, Discord-kompatible Plattform für Chat, Sprache und Video. Das Haupt-Repository erreichte <b>6,7k+ Stars und 220+ Forks</b>; das Ökosystem umfasst HTTP-APIs, WebSocket/WebRTC, CDN-/Medienauslieferung, Datenmodelle, Administrationstools und Clients.",
                    ),
                    language,
                ),
            ],
            space_after=1.0,
        ),
        entry(
            f"{tr(loc('Founder &amp; Engineer', 'Gründer &amp; Entwickler'), language)} | {link('Respond', 'https://github.com/respondchat')}",
            tr(loc("Jan 2022-Dec 2024", "Jan. 2022-Dez. 2024"), language),
            [
                tr(
                    loc(
                        "Founded Respond, a multi-platform messaging app uniting WhatsApp, Telegram, Discord, and Fosscord/Spacebar in one client experience; built supporting React Native, Rust, and JSI runtime infrastructure.",
                        "Gründete Respond, eine plattformübergreifende Messaging-App, die WhatsApp, Telegram, Discord und Fosscord/Spacebar in einem Client vereint; entwickelte die zugrunde liegende React-Native-, Rust- und JSI-Runtime-Infrastruktur.",
                    ),
                    language,
                ),
            ],
            space_after=1.0,
        ),
        section(tr(loc("Projects", "Projekte"), language)),
        paragraph(
            link("samuelscheit.com/github", "https://samuelscheit.com/github"),
            "subtitle",
        ),
        *portfolio_project_entries(language),
        section(tr(loc("Technical Skills", "Technische Fähigkeiten"), language)),
        paragraph(
            tr(
                loc(
                    "<b>Primary:</b> TypeScript, JavaScript, React, Next.js, React Native, Node.js/Bun<br/><b>Backend &amp; delivery:</b> PostgreSQL, GraphQL, WebSocket/WebRTC, Docker, Linux, Playwright, CI/CD, Go<br/><b>Mobile &amp; performance:</b> Skia, Reanimated, JSI/Hermes, iOS/Android, C++, Rust, WebGL/FFmpeg",
                    "<b>Kernkompetenzen:</b> TypeScript, JavaScript, React, Next.js, React Native, Node.js/Bun<br/><b>Backend &amp; Delivery:</b> PostgreSQL, GraphQL, WebSocket/WebRTC, Docker, Linux, Playwright, CI/CD, Go<br/><b>Mobile &amp; Performance:</b> Skia, Reanimated, JSI/Hermes, iOS/Android, C++, Rust, WebGL/FFmpeg",
                ),
                language,
            ),
            "compact",
        ),
        section(tr(loc("Languages", "Sprachen"), language)),
        paragraph(
            tr(
                loc(
                    "<b>German:</b> Native speaker &nbsp;|&nbsp; <b>English:</b> B2",
                    "<b>Deutsch:</b> Muttersprache &nbsp;|&nbsp; <b>Englisch:</b> B2",
                ),
                language,
            ),
            "compact",
        ),
        section(tr(loc("Education", "Ausbildung"), language)),
        paragraph(
            tr(
                loc(
                    "<b>Technical University of Munich (TUM)</b> | Informatics studies (no degree) | 2022-2024",
                    "<b>Technische Universität München (TUM)</b> | Informatikstudium (ohne Abschluss) | 2022-2024",
                ),
                language,
            ),
            "compact",
        ),
        Spacer(1, 1.2),
        paragraph(
            tr(
                loc(
                    "<b>Gymnasium Kirchheim</b> | Allgemeine Hochschulreife (Abitur), grade 1.9 | 2022",
                    "<b>Gymnasium Kirchheim</b> | Allgemeine Hochschulreife (Abitur), Abschlussnote 1,9 | 2022",
                ),
                language,
            ),
            "compact",
        ),
    ]


REMOVED_TEXT = (
    "Open-Source Contributor / Maintainer | Trant Labs",
    "Team Checkmate / Hackatum 2024",
    "Upstream Mobile & Native Contributions",
    "TECHNICAL WRITING",
    "SELECTED ADDITIONAL PROJECTS",
    "Spotify Playback SDK for Node.js",
    "WhatsApp Operations Backend",
    "Minecraft Server Admin Panel",
    "cccb-servicepoint-browser",
    "GykiSpace",
    "Lambert-server",
    "Lambert-orm",
    "Database-Browser",
    "CAPTCHA",
    "(private)",
    "PROJECTS (CONTINUED)",
    "GitHub release-asset",
    "across its ten published installers.",
    "JSX intrinsic-node surface",
    "All projects below were solely created and engineered by me.",
    "Alle unten aufgeführten Projekte wurden ausschließlich von mir konzipiert und entwickelt.",
)


def expected_text(language: Language) -> list[str]:
    shared = [
        "Samuel Scheit",
        "Myrodex",
        "Spacebar Chat",
        "Respond",
        "Discord Bot Client",
        "Puppeteer Stream",
        "Phishing Support",
        "WPlace World Archive",
        "React Native Skia Yoga",
        "Holistische",
        "908,716" if language == "en" else "908.716",
        "samuelscheit.com/github",
    ]
    language_specific = {
        "en": [
            "Freelance Software Engineer",
            "Founder & Engineer",
            "Jan 2021-Jan 2022",
            "Jan 2022-Dec 2024",
            "Jul-Sep 2025",
            "Oct-Nov 2025",
            "German:",
            "Native speaker",
            "English:",
            "B2",
            "Technical University of Munich",
        ],
        "de": [
            "Freiberuflicher Softwareentwickler",
            "Gründer & Entwickler",
            "Jan. 2021-Jan. 2022",
            "Jan. 2022-Dez. 2024",
            "Juli-Sept. 2025",
            "Okt.-Nov. 2025",
            "Deutsch:",
            "Muttersprache",
            "Englisch:",
            "B2",
            "Technische Universität München",
        ],
    }
    return shared + language_specific[language] + [tr(project.title, language) for project in PORTFOLIO_PROJECTS]


def verify_pdf(path: Path, language: Language) -> None:
    reader = PdfReader(path)
    if len(reader.pages) < 2:
        raise RuntimeError(f"Expected a complete multi-page CV, generated {len(reader.pages)} page")

    pages_text: list[str] = []
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - A4[0]) > 0.5 or abs(height - A4[1]) > 0.5:
            raise RuntimeError(f"Expected A4, generated {width:.1f} x {height:.1f} points")
        pages_text.append(page.extract_text() or "")

    flat_text = " ".join("\n".join(pages_text).split())
    missing_text = [item for item in expected_text(language) if item not in flat_text]
    if missing_text:
        raise RuntimeError(f"Missing required {language} PDF text: {missing_text}")

    unexpected_text = [item for item in REMOVED_TEXT if item in flat_text]
    if unexpected_text:
        raise RuntimeError(f"Removed content is still present in the {language} CV: {unexpected_text}")

    projects_heading = "PROJECTS" if language == "en" else "PROJEKTE"
    skills_heading = "TECHNICAL SKILLS" if language == "en" else "TECHNISCHE FÄHIGKEITEN"
    projects_text = flat_text[flat_text.index(projects_heading) : flat_text.index(skills_heading)]
    open_ended_date = "present" if language == "en" else "heute"
    if open_ended_date in projects_text:
        raise RuntimeError(f"{language} project entries must not use open-ended date ranges")
    if "|" in projects_text:
        raise RuntimeError(f"{language} project headings must not include role separators")

    ordered_titles = [tr(project.title, language) for project in sorted(PORTFOLIO_PROJECTS, key=lambda project: project.sort_date, reverse=True)]
    positions = [projects_text.index(title) for title in ordered_titles]
    if positions != sorted(positions):
        raise RuntimeError(f"{language} projects are not ordered chronologically, newest first")

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
        "https://myrodex.gg",
        "https://phont.ai",
        "https://www.exodus.com",
    }
    required_uris.update(
        url
        for project in PORTFOLIO_PROJECTS
        if (url := portfolio_project_url(project)) is not None
    )
    missing_uris = sorted(required_uris - uris)
    if missing_uris:
        raise RuntimeError(f"Missing required {language} hyperlinks: {missing_uris}")


def draw_footer(canvas, _document, language: Language) -> None:
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(LEFT_MARGIN, 9 * mm, PAGE_WIDTH - RIGHT_MARGIN, 9 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    footer_title = tr(loc("Samuel Scheit - Curriculum Vitae", "Samuel Scheit - Lebenslauf"), language)
    page_label = tr(loc("Page", "Seite"), language)
    canvas.drawString(LEFT_MARGIN, 5.5 * mm, footer_title)
    canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, 5.5 * mm, f"{page_label} {canvas.getPageNumber()}")
    canvas.restoreState()


def build(language: Language) -> Path:
    output = OUTPUTS[language]
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=15 * mm,
        bottomMargin=12 * mm,
        title=tr(loc("Samuel Scheit - Curriculum Vitae", "Samuel Scheit - Lebenslauf"), language),
        author="Samuel Scheit",
        subject=tr(loc("Software engineering curriculum vitae", "Lebenslauf Softwareentwicklung"), language),
    )

    def footer(canvas, document) -> None:
        draw_footer(canvas, document, language)

    document.build(build_story(language), onFirstPage=footer, onLaterPages=footer)
    verify_pdf(output, language)
    return output


def build_all() -> dict[Language, Path]:
    return {language: build(language) for language in ("en", "de")}


if __name__ == "__main__":
    for language, output in build_all().items():
        print(f"{language}: {output}")
