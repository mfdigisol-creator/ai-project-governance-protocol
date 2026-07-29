from pathlib import Path
import re
import mistune
from bs4 import BeautifulSoup
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "PROTOCOL.md"
PDF_NAME = "AI_Project_Governance_Protocol_v2.0.pdf"
PDF_PATH = ROOT / PDF_NAME

text = SRC.read_text(encoding="utf-8")
parts = re.split(r"\n---\n", text, maxsplit=1)
body_md = parts[1] if len(parts) == 2 else text
md = mistune.create_markdown(plugins=["table", "strikethrough"])
soup = BeautifulSoup(md(body_md), "html.parser")

used = set()
def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "section"
    base = slug
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug

headings = []
for heading in soup.find_all(["h1", "h2"]):
    title = heading.get_text(" ", strip=True)
    hid = slugify(title)
    heading["id"] = hid
    if heading.name == "h1":
        headings.append((title, hid))

for blockquote in soup.find_all("blockquote"):
    blockquote["class"] = ["callout"]

for h1 in list(soup.find_all("h1")):
    section = soup.new_tag("section")
    section["class"] = ["protocol-section"]
    section["aria-labelledby"] = h1.get("id")
    h1.insert_before(section)
    node = h1
    while node is not None:
        next_node = node.next_sibling
        if node is not h1 and getattr(node, "name", None) == "h1":
            break
        section.append(node.extract())
        node = next_node

toc_items = "\n".join(
    f'<li><a href="#{hid}"><span>{title}</span></a></li>'
    for title, hid in headings
)

css = r'''
@page {
  size: A4;
  margin: 20mm 18mm 19mm 18mm;
  @top-left { content: "AI-Assisted Project Governance Protocol v2.0"; font-family: Arial, sans-serif; font-size: 8pt; color: #64748b; }
  @top-right { content: "Public Reference Edition"; font-family: Arial, sans-serif; font-size: 8pt; color: #64748b; }
  @bottom-left { content: "Prepared by MF - July 29, 2026"; font-family: Arial, sans-serif; font-size: 8pt; color: #64748b; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font-family: Arial, sans-serif; font-size: 8pt; color: #64748b; }
}
@page cover { margin: 0; @top-left { content: none; } @top-right { content: none; } @bottom-left { content: none; } @bottom-right { content: none; } }
@page toc { @top-left { content: "AI-Assisted Project Governance Protocol v2.0"; } }
* { box-sizing: border-box; }
html { font-family: Arial, Helvetica, sans-serif; color: #172033; font-size: 10.25pt; line-height: 1.5; }
body { margin: 0; }
.cover { page: cover; height: 297mm; position: relative; overflow: hidden; background: linear-gradient(145deg, #071b34 0%, #0d3154 58%, #176b78 100%); color: white; padding: 26mm 24mm 22mm; display: flex; flex-direction: column; justify-content: space-between; }
.cover:before { content: ""; position: absolute; width: 155mm; height: 155mm; border: 1.2mm solid rgba(255,255,255,.10); transform: rotate(28deg); right: -74mm; top: -50mm; }
.cover:after { content: ""; position: absolute; width: 95mm; height: 95mm; border: 1mm solid rgba(255,255,255,.12); transform: rotate(28deg); left: -50mm; bottom: -36mm; }
.kicker { font-size: 9.5pt; letter-spacing: 2.3px; text-transform: uppercase; color: #b8ebee; font-weight: 700; }
.cover h1 { color: white; border: 0; padding: 0; font-size: 30pt; line-height: 1.08; margin: 18mm 0 7mm; max-width: 156mm; letter-spacing: -.4px; }
.cover h2 { font-size: 15pt; line-height: 1.3; margin: 0; max-width: 140mm; color: #d8f5f6; font-weight: 400; }
.cover-rule { width: 38mm; height: 1.3mm; background: #6ed4d7; margin: 9mm 0; }
.cover-principles { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm 8mm; max-width: 160mm; margin-top: 11mm; }
.cover-principles div { font-weight: 700; font-size: 10pt; padding: 3.2mm 0; border-top: .35mm solid rgba(255,255,255,.28); }
.cover-meta { position: relative; z-index: 2; display: grid; grid-template-columns: 1fr auto; gap: 10mm; align-items: end; color: #d8f5f6; font-size: 9.5pt; }
.cover-version { text-align: right; font-weight: 700; color: white; }
.frontmatter { break-before: page; }
.frontmatter h1, .toc h1 { font-size: 23pt; margin-top: 0; color: #0d3154; }
.summary-box { background: #eef7f8; border-left: 1.4mm solid #17808a; padding: 5mm 6mm; margin: 8mm 0; }
.summary-box p { margin: 0; }
.toc { page: toc; break-before: page; }
.toc ol { list-style: none; padding: 0; margin: 0; columns: 2; column-gap: 12mm; }
.toc li { break-inside: avoid; margin: 0 0 2.5mm; border-bottom: .2mm dotted #cbd5e1; padding-bottom: 1.2mm; }
.toc a { color: #23374d; text-decoration: none; font-size: 9.2pt; }
.protocol-body { break-before: page; }
h1 { font-size: 20pt; line-height: 1.18; color: #0d3154; margin: 9mm 0 4mm; padding-bottom: 2.5mm; border-bottom: .45mm solid #b7dadd; break-after: avoid; }
h2 { font-size: 13.2pt; line-height: 1.25; color: #176b78; margin: 6mm 0 2.5mm; break-after: avoid; }
h3 { font-size: 11.2pt; color: #0d3154; margin: 5mm 0 2mm; break-after: avoid; }
p { margin: 0 0 3.2mm; orphans: 3; widows: 3; }
ul, ol { margin: 1.5mm 0 4mm 6mm; padding-left: 5mm; }
li { margin: 0 0 1.2mm; }
li::marker { color: #17808a; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.8pt; color: #0a4851; background: #eef7f8; padding: .4mm 1mm; border-radius: 1mm; }
.callout { margin: 5mm 0; padding: 4.5mm 5.5mm; background: #f1f7fb; border-left: 1.3mm solid #176b78; color: #17324a; break-inside: avoid; }
.callout p { margin: 0; }
table { width: 100%; border-collapse: collapse; margin: 5mm 0; font-size: 8.7pt; break-inside: auto; }
thead { display: table-header-group; }
th { background: #0d3154; color: white; text-align: left; padding: 2.4mm 2.2mm; }
td { border-bottom: .25mm solid #d6e1e7; padding: 2.2mm; vertical-align: top; }
tr:nth-child(even) td { background: #f7fafb; }
.protocol-section { break-inside: auto; }
.protocol-section > h1:first-child { margin-top: 0; }
.protocol-section + .protocol-section { margin-top: 5mm; }
hr { border: 0; border-top: .3mm solid #cbd5e1; margin: 8mm 0; }
strong { color: #102a43; }
@media print { a { color: inherit; } }
'''

cover = '''
<section class="cover">
  <div>
    <div class="kicker">Public Governance Framework</div>
    <h1>Project Interaction, Scope, Governance, and Change-Control Protocol</h1>
    <div class="cover-rule"></div>
    <h2>AI-Assisted Project Execution Standard</h2>
    <div class="cover-principles">
      <div>Discussion is not Approval</div><div>Approval is not Execution</div>
      <div>Implementation is not Verification</div><div>External Content is not Authority</div>
      <div>Memory is not Source of Truth</div><div>Evidence Before Completion</div>
    </div>
  </div>
  <div class="cover-meta"><div>Prepared by MF<br>Public Reference Edition<br>July 29, 2026</div><div class="cover-version">VERSION 2.0</div></div>
</section>
'''

frontmatter = '''
<section class="frontmatter">
  <h1>About This Protocol</h1>
  <div class="summary-box"><p><strong>Purpose:</strong> Prevent AI-assisted project drift by separating information, proposals, decisions, execution, verification, acceptance, and closure within a traceable governance model.</p></div>
  <p>AI-assisted projects can drift when questions are mistaken for decisions, recommendations are treated as approvals, or approved ideas are executed beyond their intended scope. This protocol establishes a disciplined operating framework for project interaction, scope protection, decision control, change authorisation, execution safety, traceability, verification, and continuity across long or multi-session work.</p>
  <p>The framework is designed for project owners, programme and project managers, product teams, engineers, analysts, consultants, reviewers, and people using AI systems to support substantial project work.</p>
  <blockquote class="callout"><p><strong>Core rule:</strong> Discussion is not approval. Approval is not execution. Implementation is not verification. Verification is not acceptance.</p></blockquote>
  <h2>How to Use It</h2>
  <ol><li>Place the protocol at the beginning of a substantial AI-assisted project session.</li><li>Complete the Project Control Header with the current project identity and baseline versions.</li><li>Use the command vocabulary to separate questions, proposals, approvals, execution, and verification.</li><li>Apply formal change control to material changes and the simplified path only to genuinely low-risk work.</li><li>Create checkpoints at controlled milestones and before moving work to another session.</li></ol>
  <p><strong>Document status:</strong> Public governance reference. Adapt it to the project's authority model, security requirements, regulatory context, and technical risk.</p>
</section>
'''

toc = f'<section class="toc"><h1>Contents</h1><ol>{toc_items}</ol></section>'
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AI Project Governance Protocol v2.0</title><style>{css}</style></head><body>{cover}{frontmatter}{toc}<main class="protocol-body">{str(soup)}</main></body></html>'''
HTML(string=html, base_url=str(ROOT)).write_pdf(str(PDF_PATH))
print(PDF_PATH)
