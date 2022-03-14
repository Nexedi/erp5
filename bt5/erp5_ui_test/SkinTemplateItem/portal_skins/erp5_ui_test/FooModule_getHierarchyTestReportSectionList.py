from Products.ERP5Form.Report import ReportSection

return [
  ReportSection(title='1. First', level=1),
  ReportSection(title='1.1 First / First', level=2),
  ReportSection(title='1.2 First / Second', level=2),
  ReportSection(title='1.2.1 First / Second / First', level=3),
  ReportSection(title='2. Second', level=1),
]
