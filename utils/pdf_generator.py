"""
PDF Generator for Fantasy Football Recaps
Converts AI-generated summaries into beautifully formatted PDF documents
"""

import io
from datetime import datetime
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
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
    Generate a PDF document from fantasy football summary content
    
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
    
    # Create HTML content with embedded CSS
    html_content = create_html_template(
        summary_content, character, league_name, week_number, summary_format, trash_talk_level
    )
    
    # Generate PDF from HTML
    font_config = FontConfiguration()
    html_doc = HTML(string=html_content)
    css_styles = CSS(string=get_pdf_styles())
    
    pdf_buffer = io.BytesIO()
    html_doc.write_pdf(pdf_buffer, stylesheets=[css_styles], font_config=font_config)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()

def create_html_template(
    summary_content: str, 
    character: str, 
    league_name: str,
    week_number: str,
    summary_format: str,
    trash_talk_level: int
) -> str:
    """Create the HTML template for the PDF"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    format_badge = "📝 Classic Recap" if summary_format == "Classic" else "📊 Detailed Analysis"
    trash_talk_emoji = "🔥" if trash_talk_level >= 8 else "💬" if trash_talk_level >= 5 else "😊"
    
    # Split summary into paragraphs for better formatting
    paragraphs = summary_content.split('\\n\\n') if '\\n\\n' in summary_content else [summary_content]
    formatted_content = ""
    
    for paragraph in paragraphs:
        if paragraph.strip():
            formatted_content += f"<p>{paragraph.strip()}</p>\\n"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{league_name} - {week_number} Recap</title>
    </head>
    <body>
        <div class="document">
            <!-- Header Section -->
            <header class="header">
                <div class="header-content">
                    <div class="logo-section">
                        <h1 class="league-title">🏈 {league_name}</h1>
                        <div class="week-info">
                            <span class="week-number">{week_number}</span>
                            <span class="date">{current_date}</span>
                        </div>
                    </div>
                    <div class="meta-info">
                        <div class="format-badge">{format_badge}</div>
                        <div class="character-info">
                            <span class="character-label">Narrated by:</span>
                            <span class="character-name">{character}</span>
                        </div>
                        <div class="trash-talk-level">
                            <span class="trash-label">Intensity:</span>
                            <span class="trash-value">{trash_talk_emoji} Level {trash_talk_level}</span>
                        </div>
                    </div>
                </div>
                <div class="header-divider"></div>
            </header>

            <!-- Main Content -->
            <main class="content">
                <div class="summary-section">
                    <div class="content-wrapper">
                        {formatted_content}
                    </div>
                </div>
            </main>

            <!-- Footer -->
            <footer class="footer">
                <div class="footer-content">
                    <div class="generated-info">
                        <span>🤖 Generated with AI • Commish.ai</span>
                    </div>
                    <div class="timestamp">
                        <span>Generated on {current_date}</span>
                    </div>
                </div>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html_template

def get_pdf_styles() -> str:
    """Return CSS styles for PDF formatting"""
    
    return """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto+Slab:wght@400;500;600;700&display=swap');

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.6;
        color: #2c3e50;
        background: #ffffff;
    }

    .document {
        max-width: 8.5in;
        margin: 0 auto;
        background: white;
        min-height: 11in;
        display: flex;
        flex-direction: column;
    }

    /* Header Styles */
    .header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem 2.5rem 1.5rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }

    .league-title {
        font-family: 'Roboto Slab', serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .week-info {
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .week-number {
        font-size: 1.2rem;
        font-weight: 600;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }

    .date {
        font-size: 1rem;
        opacity: 0.9;
    }

    .meta-info {
        text-align: right;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .format-badge {
        background: #e74c3c;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
    }

    .character-info, .trash-talk-level {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }

    .character-label, .trash-label {
        font-size: 0.8rem;
        opacity: 0.8;
        margin-bottom: 0.2rem;
    }

    .character-name {
        font-size: 1.1rem;
        font-weight: 600;
    }

    .trash-value {
        font-size: 1rem;
        font-weight: 500;
    }

    .header-divider {
        height: 3px;
        background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60);
        border-radius: 2px;
        margin-top: 1rem;
    }

    /* Content Styles */
    .content {
        flex: 1;
        padding: 2.5rem;
    }

    .summary-section {
        background: white;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        overflow: hidden;
    }

    .content-wrapper {
        padding: 2rem;
    }

    .content-wrapper p {
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
        line-height: 1.8;
        text-align: justify;
    }

    .content-wrapper p:first-child {
        font-size: 1.2rem;
        font-weight: 500;
        color: #1e3c72;
        border-left: 4px solid #e74c3c;
        padding-left: 1rem;
        margin-bottom: 2rem;
    }

    .content-wrapper p:last-child {
        margin-bottom: 0;
    }

    /* Footer Styles */
    .footer {
        background: #f8f9fa;
        padding: 1.5rem 2.5rem;
        border-top: 1px solid #e9ecef;
        margin-top: auto;
    }

    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        color: #6c757d;
    }

    .generated-info {
        font-weight: 500;
    }

    .timestamp {
        font-style: italic;
    }

    /* Print Specific Styles */
    @media print {
        body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .document {
            box-shadow: none;
        }
    }

    @page {
        size: letter;
        margin: 0.5in;
    }
    """

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