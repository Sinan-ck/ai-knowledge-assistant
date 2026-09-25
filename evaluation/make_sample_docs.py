from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

ss = getSampleStyleSheet()
H1, H2 = ss["Title"], ss["Heading2"]
B = ParagraphStyle("b", parent=ss["Normal"], fontSize=11, leading=16)
OUT = Path(__file__).resolve().parent.parent / "data" / "sample_docs"
OUT.mkdir(parents=True, exist_ok=True)


def P(t): return Paragraph(t, B)
def S(n=8): return Spacer(1, n)


def build(name, story):
    SimpleDocTemplate(str(OUT / name), pagesize=A4, title=name).build(story)
    print("created", name)


def table(rows, widths):
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2a6c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    return t


build("01_course_brochure.pdf", [
    Paragraph("Northbridge Institute of Technology", H1),
    Paragraph("Course Brochure 2027", H2),
    P("Northbridge Institute of Technology is a career-focused training institute located at Infopark, Kochi, Kerala. "
      "It offers three professional programs designed for graduates and working professionals."), S(),
    Paragraph("Full Stack Web Development", H2),
    P("Duration: 16 weeks. Next batch starts on 5 January 2027. Eligibility: any bachelor's degree; no prior coding experience is required. "
      "Topics covered: HTML, CSS, JavaScript, React, Node.js, Express and MongoDB. Each student builds two full projects and one capstone project."), S(),
    Paragraph("Data Science and AI", H2),
    P("Duration: 24 weeks. Next batch starts on 19 January 2027. Eligibility: BSc, BTech or BCA graduates with mathematics at the higher secondary level. "
      "Topics covered: Python, statistics, machine learning, deep learning, and an introduction to large language models. "
      "Students complete a 3-month internship after the classroom phase."), S(),
    Paragraph("Cloud and DevOps", H2),
    P("Duration: 12 weeks. Next batch starts on 2 February 2027. Eligibility: any degree with basic knowledge of Linux. "
      "Topics covered: AWS fundamentals, Docker, Kubernetes, CI/CD pipelines with GitHub Actions, and Terraform basics."),
    PageBreak(),
    Paragraph("Class Schedule and Format", H2),
    P("Weekday batches run Monday to Friday, either 9:30 AM to 1:30 PM (morning batch) or 2:00 PM to 6:00 PM (afternoon batch). "
      "The weekend batch runs on Saturdays from 10:00 AM to 4:00 PM. Classes are delivered in a hybrid format: in person at the Kochi campus, "
      "with live online access. All sessions are recorded."), S(),
    Paragraph("Certification", H2),
    P("Students who maintain at least 75 percent attendance and pass the final assessment receive a Certificate of Completion. "
      "Students who score above 90 percent in the final assessment receive a Certificate of Excellence."), S(),
    Paragraph("Batch Size and Mentoring", H2),
    P("Each batch is limited to 30 students. Every student is assigned a mentor who holds a weekly one-to-one review session."),
])

build("02_fee_structure.pdf", [
    Paragraph("Northbridge Institute of Technology", H1),
    Paragraph("Fee Structure 2027", H2),
    table([["Program", "Tuition Fee (INR)"],
           ["Full Stack Web Development", "65,000"],
           ["Data Science and AI", "95,000"],
           ["Cloud and DevOps", "55,000"]], [280, 160]),
    S(10),
    P("All tuition fees are exclusive of GST. GST at 18 percent is charged extra on the tuition fee. "
      "A one-time registration fee of INR 2,000 is payable at the time of application and is non-refundable."), S(),
    Paragraph("Payment Options", H2),
    P("Full payment: pay the entire tuition fee before 15 December 2026 to receive an early-bird discount of 10 percent on tuition. "
      "Installment plan: tuition can be paid in 3 installments. The first installment of 50 percent is due at admission, "
      "the second of 30 percent is due at week 6, and the third of 20 percent is due at week 12."),
    PageBreak(),
    Paragraph("Scholarships", H2),
    P("Merit scholarship: candidates with 85 percent or higher marks in their qualifying degree receive a 20 percent tuition scholarship. "
      "Only one scholarship or discount can be applied per student; the early-bird discount and the merit scholarship cannot be combined."), S(),
    Paragraph("Refund Policy", H2),
    P("Withdrawal within 7 days of the batch start date: 100 percent of the tuition fee is refunded. "
      "Withdrawal between day 8 and day 14: 50 percent of the tuition fee is refunded. "
      "No refund is given after 14 days. The registration fee is never refunded."), S(),
    Paragraph("Payment Methods", H2),
    P("Accepted payment methods are bank transfer, UPI, and debit or credit card. Cash payments are not accepted."),
])

build("03_internship_placement.pdf", [
    Paragraph("Northbridge Institute of Technology", H1),
    Paragraph("Internship and Placement Report 2025-26", H2),
    Paragraph("Internship Program", H2),
    P("The internship lasts 3 months and is compulsory for Data Science and AI students. It is optional for Full Stack Web Development "
      "and Cloud and DevOps students. The institute has internship partnerships with more than 40 companies. "
      "Interns who are rated in the top 20 percent by their supervisors receive a stipend of INR 8,000 per month."), S(),
    Paragraph("Placement Statistics 2025-26", H2),
    table([["Metric", "Value"],
           ["Students placed", "412"],
           ["Placement rate", "87 percent"],
           ["Highest package", "14.5 LPA"],
           ["Average package", "5.2 LPA"]], [220, 160]),
    S(10),
    P("Top recruiters included Zentek Systems, Brightwave Analytics and CloudNest Technologies."),
    PageBreak(),
    Paragraph("Placement Eligibility and Support", H2),
    P("To be eligible for placement assistance, a student must have at least 80 percent attendance and must complete the capstone project. "
      "Placement assistance remains valid for 12 months after course completion."), S(),
    P("Support includes resume workshops, three mock interviews per student, and access to the campus hiring drives held every quarter."), S(),
    Paragraph("Important Note", H2),
    P("Placement statistics reflect past batches and do not guarantee a job or a specific salary for future students."),
])

build("04_faq.pdf", [
    Paragraph("Northbridge Institute of Technology", H1),
    Paragraph("Frequently Asked Questions", H2),
    P("<b>Do I need coding experience to join Full Stack Web Development?</b><br/>No. The course starts from the basics, and no prior coding experience is required."), S(),
    P("<b>Are classes online or in person?</b><br/>Classes are hybrid. You can attend in person at the Kochi campus or join live online. "
      "Recordings of all sessions remain available for 6 months after the course ends."), S(),
    P("<b>Do I need my own laptop?</b><br/>Yes. Students must bring a laptop with at least 8 GB of RAM. The institute does not provide laptops."), S(),
    P("<b>Can I switch to another course after joining?</b><br/>Yes, within the first 10 days of the batch and subject to seat availability. A course-switch fee of INR 1,500 applies."), S(),
    P("<b>What happens if I miss classes?</b><br/>You can watch the recordings, but attendance is counted only for live or in-person sessions. "
      "Remember that certification needs 75 percent attendance."), S(),
    P("<b>How do I apply?</b><br/>Submit the online application on the institute website, pay the registration fee, and attend a short 20-minute counselling call."), S(),
    P("<b>How can I contact the admissions team?</b><br/>Email admissions@northbridge-demo.example or call +91 484 000 0000, Monday to Saturday, 9:00 AM to 5:00 PM."),
])
