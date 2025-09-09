"""
PDF Generator for Fantasy Football Recaps
Converts AI-generated summaries into beautifully formatted PDF documents using ReportLab
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
import streamlit as st

def generate_pdf_from_summary(
    summary_content: str, 
    character: str, 
    league_name: str = "Fantasy Football League",
    week_number: str = "Current Week",
    summary_format: str = "Classic",
    trash_talk_level: int = 5
) -> bytes:
    """
    Generate a PDF document from fantasy football summary content using ReportLab
    
    Args:
        summary_content: The AI-generated summary text
        character: Character persona used for the summary
        league_name: Name of the fantasy league
        week_number: Week being summarized
        summary_format: Classic or Detailed format
        trash_talk_level: Intensity level of trash talk (1-10)
    
    Returns:
        bytes: PDF document as bytes
    """
    
    # Create PDF buffer
    pdf_buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Build the PDF content
    story = []
    styles = get_custom_styles()
    
    # Add header section
    story.extend(create_header_content(
        league_name, week_number, character, summary_format, trash_talk_level, styles
    ))
    
    # Add main content
    story.extend(create_main_content(summary_content, styles))
    
    # Add footer
    story.extend(create_footer_content(styles, league_name, week_number))
    
    # Build the PDF
    doc.build(story)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()

def get_custom_styles():
    """Create custom ReportLab styles for the PDF"""
    styles = getSampleStyleSheet()
    
    # Custom title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3c72'),
        fontName='Helvetica-Bold'
    ))
    
    # Custom subtitle style
    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2a5298'),
        fontName='Helvetica'
    ))
    
    # Custom header info style
    styles.add(ParagraphStyle(
        name='HeaderInfo',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica'
    ))
    
    # Custom body style with better spacing
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Helvetica'
    ))
    
    # Custom intro paragraph style
    styles.add(ParagraphStyle(
        name='IntroBody',
        parent=styles['CustomBody'],
        fontSize=12,
        spaceAfter=18,
        textColor=colors.HexColor('#1e3c72'),
        fontName='Helvetica-Bold'
    ))
    
    # Footer style
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#888888'),
        fontName='Helvetica-Oblique'
    ))
    
    return styles

def create_header_content(league_name, week_number, character, summary_format, trash_talk_level, styles):
    """Create the header content for the PDF"""
    story = []
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Main title with football emoji
    title_text = f"🏈 {league_name}"
    story.append(Paragraph(title_text, styles['CustomTitle']))
    story.append(Spacer(1, 12))
    
    # Week and date info
    week_text = f"{week_number} • {current_date}"
    story.append(Paragraph(week_text, styles['CustomSubtitle']))
    story.append(Spacer(1, 8))
    
    # Format badge
    format_badge = "📝 Classic Recap" if summary_format == "Classic" else "📊 Detailed Analysis"
    story.append(Paragraph(format_badge, styles['HeaderInfo']))
    
    # Character and intensity info
    trash_talk_emoji = "🔥" if trash_talk_level >= 8 else "💬" if trash_talk_level >= 5 else "😊"
    character_text = f"Narrated by: <b>{character}</b> | Intensity: {trash_talk_emoji} Level {trash_talk_level}"
    story.append(Paragraph(character_text, styles['HeaderInfo']))
    story.append(Spacer(1, 24))
    
    # Add a decorative line
    story.append(create_decorative_line())
    story.append(Spacer(1, 18))
    
    return story

def create_main_content(summary_content, styles):
    """Create the main content section"""
    story = []
    
    # Split content into paragraphs
    paragraphs = summary_content.split('\n\n') if '\n\n' in summary_content else [summary_content]
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            # Clean up the paragraph text
            clean_paragraph = paragraph.strip()
            
            # Use special style for first paragraph
            if i == 0:
                story.append(Paragraph(clean_paragraph, styles['IntroBody']))
            else:
                story.append(Paragraph(clean_paragraph, styles['CustomBody']))
    
    return story

def create_footer_content(styles, league_name="Fantasy Football League", week_number="Week Recap"):
    """Create the footer content"""
    story = []
    current_year = datetime.now().year
    
    story.append(Spacer(1, 36))
    
    # Add decorative line
    story.append(create_decorative_line())
    story.append(Spacer(1, 12))
    
    # Footer text with league name and week
    footer_text = f"{league_name} | {week_number}, {current_year}"
    story.append(Paragraph(footer_text, styles['Footer']))
    
    return story

def create_decorative_line():
    """Create a decorative colored line"""
    # Create a simple table to act as a colored line
    line_data = [['', '', '']]
    line_table = Table(line_data, colWidths=[2*inch, 2*inch, 2*inch])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e74c3c')),  # Red
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f39c12')),  # Orange
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#27ae60')),  # Green
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#e74c3c')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    return line_table

def get_filename(league_name: str, week_number: str, character: str) -> str:
    """Generate a formatted filename for the PDF"""
    # Clean up names for filename
    clean_league = "".join(c for c in league_name if c.isalnum() or c in (' ', '-', '_')).strip()
    clean_week = "".join(c for c in week_number if c.isalnum() or c in (' ', '-', '_')).strip()
    clean_character = "".join(c for c in character if c.isalnum() or c in (' ', '-', '_')).strip()
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{clean_league}_{clean_week}_{clean_character}_{timestamp}.pdf"
    
    # Replace spaces with underscores and limit length
    filename = filename.replace(" ", "_")[:100]
    
    return filename