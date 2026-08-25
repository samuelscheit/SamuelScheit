"""Build Samuel Scheit's recruiter-focused, one-page CV."""

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
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=11.4,
            textColor=ACCENT,
            alignment=TA_CENTER,
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
        f'<u><font color="{ACCENT_HEX}">{escape(label)}</font></u>'
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
    date_width = 31 * mm
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


def project_callout() -> Paragraph:
    return paragraph(
        "<b>Additional projects and open-source contributions (50+):</b> "
        f"{link('samuelscheit.com/github', 'https://samuelscheit.com/github')}",
        "callout",
    )


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
            "Delivered product engineering for Exodus, PHONT, and MyroDex; founded Spacebar "
            "(6.7k+ GitHub stars) and built developer tooling with 222k+ npm downloads in 12 months.",
            "summary",
        ),
        section("Experience"),
        entry(
            "Freelance Software Engineer",
            "2025-2026",
            [
                f"<b>{link('MyroDex', 'https://myrodex.gg')} (2026):</b> Built and delivered "
                "MyroDex, a multi-tenant esports operations SaaS, end to end across customer and "
                "back-office apps, organization RBAC, workflows, Stripe billing, background "
                "workers, automated tests, and a production deployment workflow.",
                f"<b>{link('PHONT', 'https://phont.ai')} (2025):</b> Re-engineered a WebGL/FFmpeg "
                "video-export pipeline from real-time capture to deterministic frame-by-frame "
                "rendering, improving export speed by up to <b>50x in project benchmarks</b>.",
                f"<b>{link('Exodus', 'https://www.exodus.com')} (2025):</b> Delivered "
                "performance-sensitive gestures, animations, and product flows across Exodus "
                "Mobile and Grateful using React Native, Reanimated, Skia, and native iOS/Android "
                "integration, tuning frame stability and reduced-motion behavior.",
            ],
            subtitle="Selected client engagements",
        ),
        entry(
            f"Founder &amp; Engineer | {link('Spacebar Chat', 'https://spacebar.chat')}",
            "Founded 2021",
            [
                "Founded Spacebar, a self-hostable, Discord-compatible chat, voice, and video "
                "platform whose flagship repository reached <b>6.7k+ stars and 220+ forks</b>; "
                "the ecosystem spans HTTP APIs, WebSocket/WebRTC, CDN/media delivery, data "
                "models, administration tooling, and clients.",
            ],
            space_after=0.5,
        ),
        section("Selected Open-Source Impact"),
        entry(
            f"{link('Puppeteer Stream', 'https://github.com/samuelscheit/puppeteer-stream')} | Creator &amp; Maintainer",
            "2020-present",
            [
                "Created and maintains a TypeScript browser audio/video capture library for "
                f"Puppeteer with {link('222k+ npm downloads', 'https://api.npmjs.org/downloads/point/2025-08-25:2026-08-24/puppeteer-stream')} "
                "in the 12 months ending August 2026, <b>459+ GitHub stars and 131 forks</b>.",
            ],
            space_after=0.7,
        ),
        entry(
            f"{link('React Native Skia List', 'https://github.com/samuelscheit/react-native-skia-list')} | Creator",
            "2024-present",
            [
                "Built a Skia/C++ virtualized list that rendered 1,000 items <b>up to 10x faster</b> "
                "than FlashList/FlatList with <b>about 70% fewer dropped frames</b> in a "
                f"{link('published iPhone 13 Pro Max benchmark', 'https://samuelscheit.com/blog/2024/react-native-skia-list')} "
                "on React Native 0.75 New Architecture; 240+ GitHub stars.",
            ],
            space_after=0.7,
        ),
        entry(
            "Upstream Mobile &amp; Native Contributions",
            "",
            [
                f"Landed {link('React Native Skia iOS ProMotion 120 Hz', 'https://github.com/Shopify/react-native-skia/pull/2690')} "
                f"support, originated its {link('macOS Catalyst approach', 'https://github.com/Shopify/react-native-skia/pull/3296')}, "
                f"and added {link('iOS support to jsi-rs', 'https://github.com/laptou/jsi-rs/pull/3')} for Rust/JSI interoperability.",
            ],
            space_after=0.8,
        ),
        Spacer(1, 1.0),
        project_callout(),
        section("Technical Skills"),
        paragraph(
            "<b>Primary:</b> TypeScript, JavaScript, React, Next.js, React Native, Node.js/Bun<br/>"
            "<b>Backend &amp; delivery:</b> PostgreSQL, GraphQL, WebSocket/WebRTC, Docker, Linux, Playwright, CI/CD, Go<br/>"
            "<b>Mobile &amp; performance:</b> Skia, Reanimated, JSI/Hermes, iOS/Android, C++, Rust, WebGL/FFmpeg",
            "compact",
        ),
        section("Education"),
        paragraph(
            "<b>Technical University of Munich (TUM)</b> | Informatics studies | 2022-2024",
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
    if len(reader.pages) != 1:
        raise RuntimeError(f"Expected exactly one page, generated {len(reader.pages)} pages")

    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    if abs(width - A4[0]) > 0.5 or abs(height - A4[1]) > 0.5:
        raise RuntimeError(f"Expected A4, generated {width:.1f} x {height:.1f} points")

    text = page.extract_text() or ""
    required_text = [
        "Samuel Scheit",
        "Freelance Software Engineer",
        "Spacebar Chat",
        "Puppeteer Stream",
        "Additional projects and open-source contributions (50+)",
        "Technical University of Munich",
    ]
    missing_text = [item for item in required_text if item not in text]
    if missing_text:
        raise RuntimeError(f"Missing required text in generated PDF: {missing_text}")

    uris = set()
    for annotation_ref in page.get("/Annots", []):
        annotation = annotation_ref.get_object()
        action = annotation.get("/A")
        if action and action.get("/URI"):
            uris.add(str(action["/URI"]))
    required_uris = {
        "mailto:contact@samuelscheit.com",
        "https://samuelscheit.com/github",
        "https://github.com/samuelscheit",
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
        title="Samuel Scheit - One-Page Curriculum Vitae",
        author="Samuel Scheit",
        subject="Software engineering curriculum vitae",
    )
    document.build(build_story())
    verify_pdf(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
