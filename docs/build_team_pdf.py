from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "NEXUS_TEAM_CONTRIBUTION_GUIDE.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleNexus", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=28, textColor=colors.HexColor("#123b68"), alignment=TA_CENTER, spaceAfter=4))
styles.add(ParagraphStyle(name="SubtitleNexus", parent=styles["Normal"], fontSize=11, leading=14, textColor=colors.HexColor("#52657d"), alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="HeadingNexus", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=colors.HexColor("#123b68"), spaceBefore=13, spaceAfter=7))
styles.add(ParagraphStyle(name="BodyNexus", parent=styles["BodyText"], fontSize=9.2, leading=12, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallNexus", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#52657d")))
styles.add(ParagraphStyle(name="BranchNexus", parent=styles["Code"], fontName="Courier", fontSize=7.7, leading=9, textColor=colors.HexColor("#7b3f00")))
styles.add(ParagraphStyle(name="CodeNexus", parent=styles["Code"], fontName="Courier", fontSize=7.5, leading=9, backColor=colors.HexColor("#f3f6f9"), borderColor=colors.HexColor("#d7e0e8"), borderWidth=0.5, borderPadding=6, spaceAfter=6))


def p(text, style="BodyNexus"):
    return Paragraph(text, styles[style])


def member(title, branch, description, folders):
    body = [p(f"<b>{title}</b>"), p(branch, "BranchNexus"), p(description), p(folders, "SmallNexus")]
    table = Table([[body]], colWidths=[88 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f9fd")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#c9d8e6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def build():
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    story = [p("NEXUS Team Contribution Guide", "TitleNexus"), p("Evidence-First Investigative Intelligence | Six-member GitHub workflow", "SubtitleNexus")]
    banner = Table([[p("<b>Repository:</b> github.com/Aryansh077/NEXUS-Investigative-Intelligence<br/>Use synthetic data only. Never treat an anomaly as proof of criminality.")]], colWidths=[178 * mm])
    banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eaf4fc")), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#2b80c5")), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story += [banner, p("Team Assignments", "HeadingNexus")]
    cards = [
        member("Member 1: Data Ingestion and Backend", "feature/ingestion-backend", "Upload APIs, parsing, normalization, validation, database storage, and evidence registration.", "Folders: backend/app/services/ingestion/, backend/app/api/ingestion.py, backend/app/database/, scripts/seed_database.py"),
        member("Member 2: NLP and Entity Resolution", "feature/nlp-resolution", "Entity extraction, aliases, fuzzy matching, confidence scores, and relationship extraction.", "Folders: backend/app/services/nlp/, entity_resolution/, relationship_extraction/"),
        member("Member 3: Knowledge Graph", "feature/knowledge-graph", "Graph construction, paths, centrality, communities, and Cypher artifacts.", "Folders: backend/app/services/graph/, neo4j/"),
        member("Member 4: ML and Anomaly Detection", "feature/ml-anomaly", "Feature engineering, Isolation Forest, anomaly explanations, evaluation, and ML tests.", "Folders: ml/, backend/app/services/anomaly/"),
        member("Member 5: Frontend and Visualization", "feature/frontend-visualization", "Dashboard, entities, graph, timeline, evidence, anomalies, Copilot UI, and API states.", "Folder: frontend/"),
        member("Member 6: Copilot, Security, and Integration", "feature/copilot-security", "Grounded Copilot, authentication, RBAC, audit, Docker, CI, and integration checks.", "Folders: backend/app/services/copilot/, backend/app/security/, Dockerfile, .github/"),
    ]
    grid = Table([[cards[0], cards[1]], [cards[2], cards[3]], [cards[4], cards[5]]], colWidths=[91 * mm, 91 * mm], hAlign="LEFT")
    grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.append(grid)
    story += [p("First-time Setup", "HeadingNexus"), p("git clone https://github.com/Aryansh077/NEXUS-Investigative-Intelligence.git<br/>Set-Location NEXUS-Investigative-Intelligence<br/>git switch YOUR_ASSIGNED_BRANCH<br/>git pull origin YOUR_ASSIGNED_BRANCH", "CodeNexus"), p("Run and Test", "HeadingNexus"), p("Backend terminal:<br/>Set-Location backend<br/>python -m venv .venv<br/>.\\.venv\\Scripts\\Activate.ps1<br/>python -m pip install -r requirements.txt<br/>python ..\\scripts\\generate_data.py<br/>python ..\\scripts\\seed_database.py<br/>python -m uvicorn app.main:app --reload --port 8000", "CodeNexus"), p("Frontend terminal:<br/>Set-Location frontend<br/>npm install<br/>npm run dev -- --host 0.0.0.0 --port 5173", "CodeNexus"), p("Open http://localhost:5173. API docs: http://localhost:8000/docs. Demo login: investigator / nexus-demo.")]
    story += [p("Before a Pull Request", "HeadingNexus"), p("Set-Location backend<br/>.\\.venv\\Scripts\\python.exe -m pytest -q<br/>Set-Location ..\\frontend<br/>npm run build<br/>Set-Location ..<br/>git add .<br/>git commit -m \"Describe the focused change\"<br/>git push -u origin YOUR_ASSIGNED_BRANCH", "CodeNexus"), p("Open a Pull Request with base branch main. Another member should review it before merge."), p("Team Rules", "HeadingNexus")]
    for rule in ["Do not develop directly on main.", "Do not commit .env, .venv, node_modules, database files, credentials, or private data.", "Use synthetic demonstration data only.", "Update tests when backend behavior changes.", "Do not claim model accuracy or training results that were not measured.", "Anomaly results are investigative leads requiring human verification."]:
        story.append(p(f"• {rule}"))
    story += [Spacer(1, 8), p("NEXUS | From fragmented data to connected intelligence | Local SIH prototype", "SmallNexus")]
    document.build(story)


if __name__ == "__main__":
    build()
    print(OUTPUT)
