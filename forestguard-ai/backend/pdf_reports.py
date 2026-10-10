"""Readable officer reports from verified saved observations; no online renderer."""
from io import BytesIO
from xml.sax.saxutils import escape
from datetime import datetime,timezone,timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak

STYLES=getSampleStyleSheet()
STYLES['Title'].textColor=colors.HexColor('#204f3c')
STYLES['BodyText'].leading=15

def paragraph(text,style='BodyText'):
    return Paragraph(escape(str(text)),STYLES[style])

def table(rows,widths):
    result=Table([[paragraph(value) for value in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    result.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eee5')),
        ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#c7d6c9')),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    return result

def build(title,contents):
    buffer=BytesIO()
    document=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=42,leftMargin=42,topMargin=44,bottomMargin=44,title=title,author='ForestGuard AI')
    def footer(canvas,doc):
        canvas.setFont('Helvetica',9);canvas.setFillColor(colors.HexColor('#53665a'))
        canvas.drawString(42,24,'ForestGuard AI | Saved observations');canvas.drawRightString(A4[0]-42,24,f'Page {doc.page}')
    document.build([paragraph('ForestGuard AI','Title'),paragraph(title,'Heading1'),Spacer(1,12),*contents],onFirstPage=footer,onLaterPages=footer)
    return buffer.getvalue()

def fire_pdf(report):
    stamp=datetime.fromisoformat(report['fetched_at']).astimezone(timezone(timedelta(hours=5,minutes=30))).strftime('%d %B %Y, %H:%M IST')
    contents=[paragraph('Joga - compartment 279 mapped area'),paragraph('Saved seven-day satellite fire feed. Retrieved: '+stamp),Spacer(1,14),
      table([['Inside mapped area','Nearby (within 2 km)'],[report['inside_count'],report['nearby_count']]], [255,255]),Spacer(1,14),
      paragraph('Satellite fire signals are inspection leads, not confirmed incidents. No detection does not prove that no fire occurred.')]
    if report['detections']:
        contents += [Spacer(1,12),paragraph('Recorded signals','Heading2'),table([['Time (IST)','Location','Position','Confidence'],
          *[[datetime.fromisoformat(e['observed_at']).astimezone(timezone(timedelta(hours=5,minutes=30))).strftime('%d %b %Y %H:%M'),
             f"{e['latitude']:.5f}, {e['longitude']:.5f}",'Inside mapped area' if e['scope']=='inside' else 'Nearby',e['confidence']] for e in report['detections']]], [140,145,135,90])]
    else:contents += [Spacer(1,12),paragraph('No fire signals were reported inside or near this mapped area in the saved feed.','Heading2')]
    contents += [Spacer(1,16),paragraph('Sources','Heading2'),paragraph(report['attribution']),paragraph('Feed status: '+report['status']),
      paragraph('Source: https://firms.modaps.eosdis.nasa.gov/active_fire/'),paragraph('Historical annual fire counts are not included in this seven-day report.')]
    return build('Satellite fire report',contents)

def annual_pdf(report,folder):
    contents=[paragraph('Joga - compartment 279 mapped area. This boundary does not cover the entire beat.'),
      paragraph('Estimated tree-covered share, not tree density. Percentages in this table use each image\'s clear area.'),Spacer(1,14),
      table([['Year','Image date','Clear area %','Estimated tree cover %'],
        *[[r['year'],r['date'],f"{r['coverage_fraction']*100:.1f}", 'Unavailable' if r['tree_cover_proxy_percent'] is None else f"{r['tree_cover_proxy_percent']:.1f}"] for r in report['observations']]], [60,140,140,170]),
      Spacer(1,16),paragraph('Change on the same clear area','Heading2'),
      table([['Years','Compared ha','Possible loss ha','Possible gain ha'],
        *[[f"{p['before_year']} - {p['after_year']}",f"{p['common_area_ha']:.2f}",f"{p['suspected_tree_proxy_loss_ha']:.2f}",f"{p['suspected_tree_proxy_gain_ha']:.2f}"] for p in report['comparisons']]], [110,130,135,135]),
      Spacer(1,14),paragraph('These satellite model estimates have not been independently validated as deforestation or regrowth. Inspect the dated images and land use before confirming a change.'),
      paragraph('2026 observations are through their image date, not a completed-year statistic.')]
    for index,row in enumerate(report['observations']):
        if index%2==0:contents.append(PageBreak())
        contents += [paragraph(f"{row['year']} - image acquired {row['date']}",'Heading2'),Image(str(folder/str(row['year'])/'preview.png'),width=400,height=286,kind='proportional'),
          paragraph(row['attribution']),Spacer(1,14)]
    return build('Annual forest-change report',contents)

def dataset_pdf(item,rows):
    return build('Saved satellite observations',[paragraph(item['title']),paragraph(item['scope']),paragraph('Synthetic test data' if item['kind']=='synthetic' else 'Saved satellite observations'),Spacer(1,14),
      table([['Image date','Clear coverage %','Usable pixels'],*[[r['date'],f"{r['coverage_percent']:.1f}",r['usable_pixels']] for r in rows]],[170,170,170]),
      Spacer(1,14),paragraph('Clear coverage describes image visibility, not forest density or accuracy.'),paragraph(item.get('limits','')),paragraph(item['attribution'])])


def fire_history_pdf(report):
    contents=[paragraph('Joga - compartment 279 mapped area'),paragraph('NASA NOAA-20 archive, requested 1 January 2022 through 10 October 2026. 2026 is a partial archive.'),Spacer(1,14),
      table([['Year','Inside mapped area','Nearby (2 km)'],*[[str(row['year'])+(' (partial)' if row['partial_year'] else ''),row['inside_count'],row['nearby_count']] for row in report['observations']]],[130,190,190]),
      Spacer(1,14),paragraph(report['limits']),paragraph(report['attribution']),Spacer(1,14),paragraph('Detection records','Heading2')]
    events=[event for row in report['observations'] for event in row['detections']]
    if events:
        contents.append(table([['Time (IST)','Latitude, longitude','Position'],*[[datetime.fromisoformat(event['observed_at']).astimezone(timezone(timedelta(hours=5,minutes=30))).strftime('%d %b %Y %H:%M'),f"{event['latitude']:.5f}, {event['longitude']:.5f}",'Inside mapped area' if event['scope']=='inside' else 'Nearby'] for event in events]],[170,190,150]))
    contents += [Spacer(1,14),paragraph('NASA archive request: '+str(report['request_id'])),paragraph(report['source_url'])]
    return build('Fire history 2022-2026',contents)
