from datetime import datetime
import io
import os
import zipfile
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='CenterTitle', parent=self.styles['Heading1'], alignment=1))
        self.styles.add(ParagraphStyle(name='CenterSubtitle', parent=self.styles['Heading2'], alignment=1))

    def _create_header(self, elements: List, title: str, subtitle: str = ""):
        # Add Logo if exists (assuming public/logo.png or similar path, skipping for now or using placeholder)
        # elements.append(Image('path/to/logo.png', width=50, height=50))
        elements.append(Paragraph("E-BODHA INSTITUTE OF TECHNOLOGY", self.styles['CenterTitle']))
        elements.append(Paragraph(title, self.styles['CenterSubtitle']))
        if subtitle:
            elements.append(Paragraph(subtitle, self.styles['Normal']))
        elements.append(Spacer(1, 0.25 * inch))

    def generate_grade_card(self, student_data: Dict[str, Any], semester_data: Dict[str, Any], courses: List[Dict[str, Any]]) -> bytes:
        """
        Generates a PDF Grade Card for a single student for a specific semester.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # Header
        self._create_header(elements, "SEMESTER GRADE CARD", f"Semester: {semester_data['name']}")

        # Student Details
        details_data = [
            ["Name:", student_data['name'], "Roll No:", student_data['id']],
            ["Discipline:", student_data['discipline_name'] or "N/A", "Month/Year:", datetime.now().strftime("%B %Y")]
        ]
        t = Table(details_data, colWidths=[1.5*inch, 3*inch, 1*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))

        # Course Table
        headers = ["Course Code", "Course Name", "Category", "Credits", "Grade"]
        table_data = [headers]
        
        for course in courses:
            table_data.append([
                course['code'],
                course['name'],
                "Core", # Assuming category is Core for now as not in simple schema, or fetch if available
                str(course['credits']),
                course['grade'] or "N/A"
            ])

        t = Table(table_data, colWidths=[1*inch, 3*inch, 1*inch, 1*inch, 1*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'), # Align course names left
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))

        # Footer (SGPA/CGPA)
        footer_data = [
            [f"SGPA: {student_data.get('sgpa', 'N/A')}", f"CGPA: {student_data.get('cgpa', 'N/A')}"]
        ]
        t = Table(footer_data, colWidths=[3.5*inch, 3.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()

    def generate_transcript(self, student_data: Dict[str, Any], semester_history: List[Dict[str, Any]]) -> bytes:
        """
        Generates a Transcript PDF containing all semesters.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        self._create_header(elements, "OFFICIAL TRANSCRIPT")

        # Student Details
        details_data = [
            ["Name:", student_data['name']],
            ["Roll No:", student_data['id']],
            ["Discipline:", student_data['discipline_name'] or "N/A"]
        ]
        t = Table(details_data, colWidths=[1.5*inch, 5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))

        # Iterate Semesters
        for sem in semester_history:
            elements.append(Paragraph(f"{sem['name']} (SGPA: {sem.get('sgpa', 'N/A')})", self.styles['Heading3']))
            
            headers = ["Code", "Course Name", "Credits", "Grade"]
            table_data = [headers]
            for course in sem['courses']:
                table_data.append([
                    course['code'],
                    course['name'],
                    str(course['credits']),
                    course['grade'] or "N/A"
                ])
            
            t = Table(table_data, colWidths=[1*inch, 3.5*inch, 1*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.15*inch))
            
        # Final CGPA
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"Final CGPA: {student_data.get('cgpa', 'N/A')}", self.styles['Heading2']))

        doc.build(elements)
        buffer.seek(0)
        return buffer.read()

    def create_zip(self, files: Dict[str, bytes]) -> bytes:
        """
        Creates a ZIP file from a dictionary of filenames and content bytes.
        """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files.items():
                zip_file.writestr(filename, content)
        buffer.seek(0)
        return buffer.read()

pdf_generator = PDFGenerator()
