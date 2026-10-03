"""
scratch/generate_pdf_slides.py - Script de génération du PDF des slides de cadrage Executive.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_pdf():
    pdf_path = Path(__file__).parent.parent / "slides" / "Projet4_Copilote_Agentique_Slides.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(letter),
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'SlideSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=10
    )
    
    story = []
    
    # Slide 1
    story.append(Paragraph("Projet 4 : Copilote Agentique Commercial", title_style))
    story.append(Paragraph("Slide 1 : Cas d'Usage & Gain de Temps Attendus", subtitle_style))
    story.append(Paragraph("• <b>Objectif</b> : Réduire le temps de préparation des rendez-vous clients et sécuriser les propositions tarifaires.", body_style))
    story.append(Paragraph("• <b>Tâche automatisée</b> : Synthèse du profil client (RFM), recommandations de pricing dynamique, vérification des remises et génération du projet d'e-mail.", body_style))
    story.append(Paragraph("• <b>Gain de temps estimé</b> : -60% de temps de préparation (passant de 25 min à 10 min par appel client).", body_style))
    story.append(Paragraph("• <i>Note : Ce gain de temps est une hypothèse à mesurer lors de la phase pilote.</i>", body_style))
    story.append(PageBreak())
    
    # Slide 2
    story.append(Paragraph("Projet 4 : Copilote Agentique Commercial", title_style))
    story.append(Paragraph("Slide 2 : Architecture & Garde-fous Anti-Hallucination", subtitle_style))
    story.append(Paragraph("• <b>Sécurité</b> : Aucun accès SQL direct par l'agent. Les chiffres proviennent à 100% de l'API REST FastAPI déterministe.", body_style))
    story.append(Paragraph("• <b>Outils REST</b> : Profil client, Historique achats, Recommandations de prix et Politique Commerciale (RAG).", body_style))
    story.append(Paragraph("• <b>Validation Humaine (Human-in-the-loop)</b> : Aucune proposition commerciale n'est envoyée au client sans l'approbation explicite d'un responsable.", body_style))
    story.append(Paragraph("• <b>Journal d'Audit</b> : Chaque demande, outil appelé et décision sont consignés déterministement.", body_style))
    story.append(PageBreak())
    
    # Slide 3
    story.append(Paragraph("Projet 4 : Copilote Agentique Commercial", title_style))
    story.append(Paragraph("Slide 3 : Déploiement Pilote & Gouvernance RGPD / AI Act", subtitle_style))
    story.append(Paragraph("• <b>Phase Pilote (4 semaines)</b> : Déploiement auprès d'une équipe de 5 commerciaux référents.", body_style))
    story.append(Paragraph("• <b>Indicateurs (KPIs)</b> : Taux d'acceptation des brouillons (>80%), temps de préparation, évolution des remises moyennes.", body_style))
    story.append(Paragraph("• <b>Gouvernance RGPD</b> : Minimisation des données (seuls des IDs anonymisés sont traités).", body_style))
    story.append(Paragraph("• <b>Transparence AI Act</b> : Notification claire de l'assistance IA et supervision humaine systématique.", body_style))
    
    doc.build(story)
    print(f"✅ PDF généré dans {pdf_path}")

if __name__ == "__main__":
    build_pdf()
