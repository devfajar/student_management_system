import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from student_management_app.models import StudentResult, AttendanceReport

def calculate_grade(total_marks):
    if total_marks >= 90:
        return 'A+', 4.0, 'Distinction'
    elif total_marks >= 80:
        return 'A', 3.75, 'Excellent'
    elif total_marks >= 70:
        return 'B', 3.0, 'Good'
    elif total_marks >= 60:
        return 'C', 2.0, 'Average'
    elif total_marks >= 50:
        return 'D', 1.0, 'Pass'
    else:
        return 'F', 0.0, 'Fail'

def generate_student_report_card_pdf(student):
    """
    Generates a PDF academic transcript report card for a student.
    Returns bytes of the generated PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1, # Centered
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        fontName='Helvetica'
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e40af'),
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=6
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b')
    )

    cell_normal = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        fontName='Helvetica',
        textColor=colors.HexColor('#334155')
    )

    # 1. Header & Branding
    story.append(Paragraph("STUDENT MANAGEMENT SYSTEM", title_style))
    story.append(Paragraph("OFFICIAL ACADEMIC TRANSCRIPT & PERFORMANCE REPORT", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceBefore=2, spaceAfter=12))

    # 2. Student & Institutional Info
    course_name = student.course_id.course_name if student.course_id else "N/A"
    session_str = f"{student.session_year_id.session_start_year} - {student.session_year_id.session_end_year}" if student.session_year_id else "N/A"
    full_name = f"{student.admin.first_name} {student.admin.last_name}".strip() or student.admin.username

    info_data = [
        [
            Paragraph("<b>Student Name:</b>", cell_bold), Paragraph(full_name, cell_normal),
            Paragraph("<b>Student ID:</b>", cell_bold), Paragraph(f"#{student.id}", cell_normal),
        ],
        [
            Paragraph("<b>Username / Reg No:</b>", cell_bold), Paragraph(student.admin.username, cell_normal),
            Paragraph("<b>Gender:</b>", cell_bold), Paragraph(student.gender or "N/A", cell_normal),
        ],
        [
            Paragraph("<b>Enrolled Course:</b>", cell_bold), Paragraph(course_name, cell_normal),
            Paragraph("<b>Academic Session:</b>", cell_bold), Paragraph(session_str, cell_normal),
        ],
        [
            Paragraph("<b>Email:</b>", cell_bold), Paragraph(student.admin.email, cell_normal),
            Paragraph("<b>Date of Issue:</b>", cell_bold), Paragraph(datetime.now().strftime("%B %d, %Y"), cell_normal),
        ],
    ]

    info_table = Table(info_data, colWidths=[120, 160, 110, 150])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    # 3. Attendance Overview
    att_reports = AttendanceReport.objects.filter(student_id=student)
    total_classes = att_reports.count()
    present_classes = att_reports.filter(status=True).count()
    attendance_pct = (present_classes / total_classes * 100) if total_classes > 0 else 0.0

    att_summary_data = [
        [
            Paragraph(f"<b>Classes Conducted:</b> {total_classes}", cell_normal),
            Paragraph(f"<b>Present Days:</b> {present_classes}", cell_normal),
            Paragraph(f"<b>Attendance Rate:</b> {attendance_pct:.1f}%", cell_bold)
        ]
    ]
    att_table = Table(att_summary_data, colWidths=[180, 180, 180])
    att_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(att_table)
    story.append(Spacer(1, 12))

    # 4. Examination Results Table
    story.append(Paragraph("Coursework & Examination Performance", section_header))

    results = StudentResult.objects.filter(student_id=student).select_related('subject_id')
    marks_table_data = [
        [
            Paragraph("<b>Subject / Course Module</b>", cell_bold),
            Paragraph("<b>Exam (50)</b>", cell_bold),
            Paragraph("<b>Assign (50)</b>", cell_bold),
            Paragraph("<b>Total (100)</b>", cell_bold),
            Paragraph("<b>Grade</b>", cell_bold),
            Paragraph("<b>GPA</b>", cell_bold),
            Paragraph("<b>Status</b>", cell_bold)
        ]
    ]

    total_gpa_points = 0.0
    subject_count = 0

    if results.exists():
        for res in results:
            exam = res.subject_exam_marks or 0.0
            assign = res.subject_assignment_marks or 0.0
            total = exam + assign
            letter_grade, gpa_point, remark = calculate_grade(total)

            total_gpa_points += gpa_point
            subject_count += 1

            status_color = '#15803d' if total >= 50 else '#b91c1c'
            status_text = f"<font color='{status_color}'><b>{'PASS' if total >= 50 else 'FAIL'}</b></font>"

            marks_table_data.append([
                Paragraph(res.subject_id.subject_name if res.subject_id else "N/A", cell_normal),
                Paragraph(f"{exam:.1f}", cell_normal),
                Paragraph(f"{assign:.1f}", cell_normal),
                Paragraph(f"{total:.1f}", cell_bold),
                Paragraph(letter_grade, cell_bold),
                Paragraph(f"{gpa_point:.2f}", cell_normal),
                Paragraph(status_text, cell_normal)
            ])
    else:
        marks_table_data.append([
            Paragraph("<i>No examination results recorded for this period</i>", cell_normal),
            "", "", "", "", "", ""
        ])

    marks_table = Table(marks_table_data, colWidths=[190, 60, 60, 65, 50, 50, 65])
    marks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(marks_table)
    story.append(Spacer(1, 14))

    # 5. CGPA & Academic Summary Card
    cgpa = (total_gpa_points / subject_count) if subject_count > 0 else 0.0
    cgpa_letter, _, cgpa_remark = calculate_grade(cgpa * 25) # Scale to 100 for remark

    summary_data = [
        [
            Paragraph(f"<b>Subjects Evaluated:</b> {subject_count}", cell_normal),
            Paragraph(f"<b>Cumulative GPA:</b> <font size='11' color='#1e3a8a'><b>{cgpa:.2f} / 4.00</b></font>", cell_normal),
            Paragraph(f"<b>Standing:</b> <b>{cgpa_remark} ({cgpa_letter})</b>", cell_normal)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[180, 180, 180])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 30))

    # 6. Signatures & Verification Stamp
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Registrar / Academic Dean</b>", cell_normal),
            Paragraph("____________________________<br/><b>Controller of Examinations</b>", cell_normal),
            Paragraph("<b>Official Digital Seal</b><br/><i>Verified System Document</i>", cell_normal)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[180, 180, 180])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
