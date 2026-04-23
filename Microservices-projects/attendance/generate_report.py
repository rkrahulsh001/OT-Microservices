from fpdf import FPDF
import xml.etree.ElementTree as ET
import datetime
import os


class ReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'Attendance Service - Test Report', 0, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10,
            f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | Page {self.page_no()}',
            0, 0, 'C')


def parse_xml(xml_file):
    abs_path = os.path.abspath(xml_file)
    print(f"Looking for XML: {abs_path}")
    if not os.path.exists(abs_path):
        print(f"WARNING: File not found: {abs_path}")
        return None
    print(f"Found XML: {abs_path} ({os.path.getsize(abs_path)} bytes)")
    tree  = ET.parse(abs_path)
    root  = tree.getroot()
    suite = root if root.tag == 'testsuite' else root.find('testsuite')
    if suite is None:
        print(f"WARNING: No testsuite element in {abs_path}")
        return None
    tests    = int(suite.get('tests',    0))
    failures = int(suite.get('failures', 0))
    errors   = int(suite.get('errors',   0))
    skipped  = int(suite.get('skipped',  0))
    return {
        'tests'   : tests,
        'failures': failures,
        'errors'  : errors,
        'skipped' : skipped,
        'passed'  : tests - failures - errors,
        'time'    : float(suite.get('time', 0))
    }


def get_coverage(cov_file):
    abs_path = os.path.abspath(cov_file)
    print(f"Looking for coverage: {abs_path}")
    if not os.path.exists(abs_path):
        print(f"WARNING: Coverage file not found: {abs_path}")
        return None
    print(f"Found coverage: {abs_path} ({os.path.getsize(abs_path)} bytes)")
    root = ET.parse(abs_path).getroot()
    return round(float(root.get('line-rate', 0)) * 100, 2)


def generate():
    # Fix: script ki apni directory mein chale jao
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Debug info

    cwd = os.getcwd()
    print(f"Working directory: {cwd}")
    print(f"Files present: {sorted(os.listdir(cwd))}")

    pdf = ReportPDF()
    pdf.add_page()

    # Build Info
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(236, 240, 241)
    pdf.cell(0, 10, 'Build Information', 0, 1, 'L', True)
    pdf.set_font('Arial', '', 10)
    for label, value in [
        ('Service',      'attendance'),
        ('Version',      os.getenv('VERSION',      '1.0.0')),
        ('Environment',  os.getenv('ENVIRONMENT',  'staging')),
        ('Branch',       os.getenv('GIT_BRANCH',   'master').replace('origin/', '')),
        ('Build Number', os.getenv('BUILD_NUMBER', 'N/A')),
        ('Date',         datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    ]:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(50, 8, f'{label}:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, str(value), 0, 1)
    pdf.ln(5)

    # Test Results Table
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(236, 240, 241)
    pdf.cell(0, 10, 'Test Results', 0, 1, 'L', True)
    pdf.ln(2)

    cols   = ['Suite', 'Total', 'Passed', 'Failed', 'Skipped', 'Time(s)', 'Status']
    widths = [55, 20, 22, 20, 22, 22, 20]

    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    for c, w in zip(cols, widths):
        pdf.cell(w, 8, c, 1, 0, 'C', True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)

    total_t = total_p = total_f = 0
    for xml_file, name in [
        ('unit-results.xml',        'Unit Tests'),
        ('integration-results.xml', 'Integration Tests'),
    ]:
        d = parse_xml(xml_file)
        pdf.set_font('Arial', '', 9)
        pdf.set_fill_color(245, 245, 245)
        if d:
            ok     = d['failures'] == 0 and d['errors'] == 0
            status = 'PASS' if ok else 'FAIL'
            color  = (39, 174, 96) if ok else (231, 76, 60)
            vals   = [name, d['tests'], d['passed'],
                      d['failures'], d['skipped'],
                      f"{d['time']:.2f}", status]
            for i, (v, w) in enumerate(zip(vals, widths)):
                if i == 6:
                    pdf.set_text_color(*color)
                pdf.cell(w, 7, str(v), 1, 0, 'C' if i > 0 else 'L', True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln()
            total_t += d['tests']
            total_p += d['passed']
            total_f += d['failures']
        else:
            for v, w in zip([name, '-', '-', '-', '-', '-', 'N/A'], widths):
                pdf.cell(w, 7, v, 1, 0, 'C', True)
            pdf.ln()
    pdf.ln(5)

    # Coverage
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(236, 240, 241)
    pdf.cell(0, 10, 'Code Coverage', 0, 1, 'L', True)
    cov = get_coverage('coverage.xml')
    if cov is not None:
        color = (39, 174, 96) if cov >= 50 else (231, 76, 60)
        pdf.set_font('Arial', 'B', 28)
        pdf.set_text_color(*color)
        pdf.cell(0, 15, f'{cov}%', 0, 1, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8,
            f'Threshold: 50% | Status: {"PASSED" if cov >= 50 else "FAILED"}',
            0, 1, 'C')
    else:
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 10, 'Coverage data not available', 0, 1, 'C')
    pdf.ln(5)

    # Overall Summary
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(236, 240, 241)
    pdf.cell(0, 10, 'Overall Summary', 0, 1, 'L', True)
    ok    = total_f == 0
    color = (39, 174, 96) if ok else (231, 76, 60)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(*color)
    pdf.cell(0, 12,
        'ALL TESTS PASSED' if ok else 'SOME TESTS FAILED',
        0, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8,
        f'Total: {total_t} | Passed: {total_p} | Failed: {total_f}',
        0, 1, 'C')

    out = 'test-report.pdf'
    pdf.output(out)
    size = os.path.getsize(out)
    print(f'PDF generated: {out} ({size} bytes)')
    if size < 5000:
        print('WARNING: PDF is very small — XML/coverage files may be missing!')


if __name__ == '__main__':
    generate()
