import tempfile
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from ..utils.timezone import format_datetime_in_organizer_timezone, get_current_time_in_organizer_timezone

def generate_pdf_report(meeting_data, participants_data, polls_data, scrutators_data=None):
    """Generate PDF report for the meeting"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#374151'),
        spaceAfter=20
    )
    
    # Add title
    story.append(Paragraph("RAPPORT DE VOTE SECRET", title_style))
    story.append(Spacer(1, 20))
    
    # Meeting info
    organizer_timezone = meeting_data.get('organizer_timezone')
    
    story.append(Paragraph(f"<b>Réunion:</b> {meeting_data['title']}", styles['Normal']))
    story.append(Paragraph(f"<b>Organisateur:</b> {meeting_data['organizer_name']}", styles['Normal']))
    story.append(Paragraph(f"<b>Code de réunion:</b> {meeting_data['meeting_code']}", styles['Normal']))
    
    # Format creation date in organizer's timezone
    if meeting_data.get('created_at'):
        if isinstance(meeting_data['created_at'], str):
            created_at = datetime.fromisoformat(meeting_data['created_at'].replace('Z', '+00:00'))
        else:
            created_at = meeting_data['created_at']
        formatted_created_at = format_datetime_in_organizer_timezone(created_at, organizer_timezone)
        story.append(Paragraph(f"<b>Date de création:</b> {formatted_created_at}", styles['Normal']))
    
    # Format generation date in organizer's timezone
    current_time = get_current_time_in_organizer_timezone(organizer_timezone)
    story.append(Paragraph(f"<b>Date de génération:</b> {current_time.strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Scrutators section (if any)
    if scrutators_data and len(scrutators_data) > 0:
        story.append(Paragraph("SCRUTATEURS", subtitle_style))
        
        # Create scrutators table
        scrutators_table_data = [['#', 'Nom du scrutateur', 'Ajouté le']]
        for i, scrutator in enumerate(scrutators_data, 1):
            # Handle both datetime objects and ISO strings, convert to organizer timezone
            if isinstance(scrutator['added_at'], str):
                added_datetime = datetime.fromisoformat(scrutator['added_at'].replace('Z', '+00:00'))
            else:
                added_datetime = scrutator['added_at']
            
            added_time = format_datetime_in_organizer_timezone(added_datetime, organizer_timezone)
            scrutators_table_data.append([str(i), scrutator['name'], added_time])
        
        scrutators_table = Table(scrutators_table_data, colWidths=[0.5*inch, 3*inch, 1.5*inch])
        scrutators_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(scrutators_table)
        story.append(Paragraph(f"<b>Total des scrutateurs:</b> {len(scrutators_data)}", styles['Normal']))
        story.append(Spacer(1, 30))
    
    # Participants section
    story.append(Paragraph("PARTICIPANTS APPROUVÉS", subtitle_style))
    
    # Create participants table
    approved_participants = [p for p in participants_data if p['approval_status'] == 'approved']
    
    if approved_participants:
        participants_table_data = [['#', 'Nom', 'Heure de participation']]
        for i, participant in enumerate(approved_participants, 1):
            # Handle both datetime objects and ISO strings, convert to organizer timezone
            if isinstance(participant['joined_at'], str):
                joined_datetime = datetime.fromisoformat(participant['joined_at'].replace('Z', '+00:00'))
            else:
                joined_datetime = participant['joined_at']
            
            joined_time = format_datetime_in_organizer_timezone(joined_datetime, organizer_timezone, '%H:%M')
            participants_table_data.append([str(i), participant['name'], joined_time])
        
        participants_table = Table(participants_table_data, colWidths=[0.5*inch, 3*inch, 1.5*inch])
        participants_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(participants_table)
        story.append(Paragraph(f"<b>Total des participants approuvés:</b> {len(approved_participants)}", styles['Normal']))
    else:
        story.append(Paragraph("Aucun participant approuvé", styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Polls section
    story.append(Paragraph("RÉSULTATS DES SONDAGES", subtitle_style))
    
    if polls_data:
        for i, poll in enumerate(polls_data, 1):
            # Poll question
            story.append(Paragraph(f"<b>Sondage {i}:</b> {poll['question']}", styles['Heading3']))
            story.append(Spacer(1, 10))
            
            # Calculate total votes
            total_votes = sum(opt['votes'] for opt in poll['options'])
            
            if total_votes > 0:
                # Create results table
                results_data = [['Option', 'Votes', 'Pourcentage']]
                for option in poll['options']:
                    percentage = (option['votes'] / total_votes * 100) if total_votes > 0 else 0
                    results_data.append([
                        option['text'],
                        str(option['votes']),
                        f"{percentage:.1f}%"
                    ])
                
                # Add total row
                results_data.append(['TOTAL', str(total_votes), '100.0%'])
                
                results_table = Table(results_data, colWidths=[3*inch, 1*inch, 1*inch])
                results_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e5e7eb')),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(results_table)
            else:
                story.append(Paragraph("Aucun vote enregistré pour ce sondage", styles['Normal']))
            
            story.append(Spacer(1, 20))
    else:
        story.append(Paragraph("Aucun sondage n'a été créé lors de cette réunion", styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 50))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Rapport généré par le système Vote Secret", footer_style))
    story.append(Paragraph("Toutes les données de cette réunion ont été supprimées après génération de ce rapport", footer_style))
    
    # Build PDF
    doc.build(story)
    
    return temp_path
