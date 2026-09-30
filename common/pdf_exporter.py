import re
from pathlib import Path
from fpdf import FPDF

class PresentationPDF(FPDF):
    def __init__(self, total_slides=1):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.total_slides = total_slides

    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "CUSTOMER & GROWTH AI LAB - RESTITUTION STRATEGIQUE", new_x="LMARGIN", new_y="NEXT", align="R")
        self.set_draw_color(226, 232, 240)
        self.line(12, 11, 285, 11)
        self.set_y(13)

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, f"Slide {self.page_no()} / {self.total_slides}", align="C")


def render_table_cells(pdf: PresentationPDF, lines: list[str]):
    """Rendu structuré des tableaux Markdown sous forme de grille compacte et esthétique."""
    table_rows = []
    for line in lines:
        if "---" in line or "|---" in line:
            continue
        cells = [c.strip().replace("**", "").replace("*", "").replace("`", "") for c in line.split("|")[1:-1]]
        if cells:
            table_rows.append(cells)

    if not table_rows:
        return

    num_cols = max(len(r) for r in table_rows)
    page_width = 271.0
    
    # Largeurs adaptatives selon le nombre de colonnes
    if num_cols == 5:
        col_widths = [32.0, 95.0, 30.0, 74.0, 40.0]
    elif num_cols == 4:
        col_widths = [45.0, 116.0, 40.0, 70.0]
    else:
        col_widths = [page_width / num_cols] * num_cols

    for row_idx, row in enumerate(table_rows):
        is_header = (row_idx == 0)
        pdf.set_font("Helvetica", "B" if is_header else "", 7.5)
        
        # Calcul préventif du nombre de lignes pour chaque cellule
        max_lines = 1
        for i, cell_text in enumerate(row):
            w = col_widths[i] if i < len(col_widths) else 30.0
            # Estimation manuelle de la hauteur pour éviter le déclenchement de page break par multi_cell
            approx_chars_per_line = max(1, int((w - 3) / 1.6))
            lines_count = max(1, len(cell_text) // approx_chars_per_line + (1 if len(cell_text) % approx_chars_per_line > 0 else 0))
            if "\n" in cell_text:
                lines_count = max(lines_count, len(cell_text.split("\n")))
            max_lines = max(max_lines, lines_count)

        row_h = max_lines * 3.4 + 2.5

        x_start = 12.0
        y_start = pdf.get_y()

        # Si la ligne dépasse le bas de page disponible (195mm), on resserre row_h
        if y_start + row_h > 195:
            row_h = max(4.0, 195 - y_start)

        for i, cell_text in enumerate(row):
            w = col_widths[i] if i < len(col_widths) else 30.0
            x_pos = x_start + sum(col_widths[:i])
            
            # Styles d'en-tête et de rangées
            if is_header:
                pdf.set_fill_color(239, 246, 255) # Light Navy Tint
                pdf.set_draw_color(191, 219, 254)
                pdf.set_text_color(30, 58, 138)
            else:
                bg_color = (255, 255, 255) if row_idx % 2 == 1 else (248, 250, 252)
                pdf.set_fill_color(*bg_color)
                pdf.set_draw_color(226, 232, 240)
                pdf.set_text_color(30, 41, 59)

            pdf.rect(x_pos, y_start, w, row_h, style="FD")
            
            # Écriture du texte dans la cellule
            pdf.set_xy(x_pos + 1.5, y_start + 1.2)
            pdf.multi_cell(w=w - 3, h=3.2, text=cell_text, border=0, align="L")

        pdf.set_xy(x_start, y_start + row_h)


def export_markdown_slides_to_pdf(md_path: Path) -> bytes:
    if not md_path.exists():
        return b""

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Nettoyage des caractères spéciaux et emojis non supportés par la police standard Latin-1
    replacements = {
        "—": "-", "–": "-", "’": "'", "“": '"', "”": '"', "…": "...",
        "★": "*", "🎯": "", "🚨": "", "💡": "", "📦": "", "📈": "", "•": "-"
    }
    for old, new in replacements.items():
        content = content.replace(old, new)

    content = re.sub(r'[\U00010000-\U0010FFFF]', '', content)

    # Découpage des slides par le séparateur --- sur sa propre ligne (évite les tableaux |---|)
    blocks = [b.strip() for b in re.split(r'\n\s*---\s*\n', content) if b.strip()]
    if not blocks:
        return b""

    # Si le premier bloc est un titre global (# Restitution Stratégique), on le fusionne avec la Slide 1
    slides_content = []
    global_title = ""
    
    for b in blocks:
        lines = [l.strip() for l in b.split("\n") if l.strip()]
        if not lines:
            continue
        # Si le bloc contient uniquement le titre global (# H1) sans Slide (## H2)
        if lines[0].startswith("# ") and not any(l.startswith("## ") for l in lines):
            global_title = lines[0].replace("# ", "")
        else:
            slides_content.append((global_title, b))
            global_title = "" # consommé

    pdf = PresentationPDF(total_slides=len(slides_content))
    pdf.set_auto_page_break(auto=False, margin=10)
    pdf.set_margins(12, 12, 12)

    for slide_idx, (g_title, slide_text) in enumerate(slides_content):
        pdf.add_page()
        lines = [l.strip() for l in slide_text.split("\n") if l.strip()]
        
        # Titre global du document si présent sur la première slide
        if g_title:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(71, 85, 105)
            pdf.cell(0, 5, g_title.upper(), new_x="LMARGIN", new_y="NEXT", align="L")
            pdf.ln(1)

        in_table = False
        table_lines = []

        for line_str in lines:
            if line_str.startswith("|"):
                in_table = True
                table_lines.append(line_str)
                continue
            elif in_table:
                render_table_cells(pdf, table_lines)
                table_lines = []
                in_table = False
                pdf.ln(1.5)

            # Titre principal (# H1)
            if line_str.startswith("# "):
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(30, 58, 138)
                clean_txt = line_str.replace("# ", "").replace("**", "").replace("*", "")
                pdf.multi_cell(w=271, h=6, text=clean_txt)
                pdf.ln(1.5)

            # Titre de la slide (## H2)
            elif line_str.startswith("## "):
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(30, 58, 138)
                clean_txt = line_str.replace("## ", "").replace("**", "").replace("*", "")
                pdf.multi_cell(w=271, h=5.5, text=clean_txt)
                pdf.ln(1)

            # Phrase de conclusion (### H3)
            elif line_str.startswith("### "):
                pdf.set_font("Helvetica", "B", 9.5)
                pdf.set_text_color(185, 28, 28) # Crimson Red
                clean_txt = line_str.replace("### ", "").replace("**", "").replace("*", "")
                pdf.multi_cell(w=271, h=4.5, text=clean_txt)
                pdf.ln(1)

            # Synthèse / Accroche (> Quote)
            elif line_str.startswith("> "):
                pdf.set_font("Helvetica", "I", 8.5)
                pdf.set_text_color(51, 65, 85)
                clean_txt = line_str.replace("> ", "").replace("**", "").replace("*", "")
                pdf.multi_cell(w=271, h=4, text=clean_txt)
                pdf.ln(1)

            # Puces (- ou *)
            elif line_str.startswith("* ") or line_str.startswith("- "):
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_text_color(30, 41, 59)
                clean_txt = "  *  " + line_str[2:].replace("**", "").replace("*", "")
                pdf.multi_cell(w=271, h=4, text=clean_txt)
                pdf.ln(0.5)

            # Sous-puces (ex: 1. 2. 3.)
            elif re.match(r'^\d+\.', line_str):
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_text_color(30, 41, 59)
                clean_txt = "     " + line_str.replace("**", "").replace("*", "")
                pdf.multi_cell(w=271, h=4, text=clean_txt)
                pdf.ln(0.5)

            # Texte normal
            else:
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_text_color(30, 41, 59)
                clean_txt = line_str.replace("**", "").replace("*", "")
                pdf.multi_cell(w=271, h=4, text=clean_txt)
                pdf.ln(0.5)

        if in_table and table_lines:
            render_table_cells(pdf, table_lines)

    return bytes(pdf.output())


