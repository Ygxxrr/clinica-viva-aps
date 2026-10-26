"""Exportação da documentação. Dependências opcionais: reportlab e svglib."""
from pathlib import Path
import re
import sys
from html import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, LongTable, TableStyle, Preformatted, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'docs'/'pdf'
OUT.mkdir(parents=True,exist_ok=True)
FONT_ROOT=Path('C:/Windows/Fonts')
if (FONT_ROOT/'segoeui.ttf').exists():
    for name,file in [('Body','segoeui.ttf'),('BodyBold','segoeuib.ttf'),('BodyItalic','segoeuii.ttf'),('Mono','consola.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(FONT_ROOT/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
elif Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf').exists():
    LINUX_FONTS=Path('/usr/share/fonts/truetype/dejavu')
    for name,file in [('Body','DejaVuSans.ttf'),('BodyBold','DejaVuSans-Bold.ttf'),('BodyItalic','DejaVuSans-Oblique.ttf'),('Mono','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(LINUX_FONTS/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    pdfmetrics.registerFontFamily('Mono',normal='Mono',bold='Mono',italic='Mono',boldItalic='Mono')
else:
    for name,base in [('Body','Helvetica'),('BodyBold','Helvetica-Bold'),('BodyItalic','Helvetica-Oblique'),('Mono','Courier')]:
        pdfmetrics.registerFont(pdfmetrics.Font(name,base,'WinAnsiEncoding'))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')

TEAL=colors.HexColor('#087f78');INK=colors.HexColor('#24463b');MUTED=colors.HexColor('#718a7b');LINE=colors.HexColor('#dce8df')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Text',fontName='Body',fontSize=9.0,leading=14.0,textColor=INK,spaceAfter=7.5))
styles.add(ParagraphStyle(name='H1x',fontName='BodyBold',fontSize=22,leading=28,textColor=TEAL,spaceBefore=5,spaceAfter=17,keepWithNext=True))
styles.add(ParagraphStyle(name='H2x',fontName='BodyBold',fontSize=13,leading=18,textColor=INK,spaceBefore=16,spaceAfter=9,keepWithNext=True))
styles.add(ParagraphStyle(name='H3x',fontName='BodyBold',fontSize=10.4,leading=15,textColor=TEAL,spaceBefore=10,spaceAfter=6,keepWithNext=True))
styles.add(ParagraphStyle(name='Cell',fontName='Body',fontSize=7.5,leading=10.8,textColor=INK,spaceAfter=0))
styles.add(ParagraphStyle(name='CellHead',fontName='BodyBold',fontSize=7.5,leading=10.8,textColor=colors.white,spaceAfter=0))
styles.add(ParagraphStyle(name='Bulletx',parent=styles['Text'],leftIndent=12,firstLineIndent=-10,spaceAfter=6))
styles.add(ParagraphStyle(name='Codex',fontName='Mono',fontSize=7.7,leading=11,textColor=INK,backColor=colors.HexColor('#f1f6f0'),borderPadding=8,spaceBefore=7,spaceAfter=10))

def clean(text):
    return text.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u00a0',' ')

def inline(text):
    text=escape(clean(text))
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'`([^`]+)`',r'<font name="Mono" size="8">\1</font>',text)
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',text)
    return text

def table(rows,width):
    n=len(rows[0]);weights=[1]*n
    if n==3:weights=[.7,2.2,3.2]
    elif n==4:weights=[.9,1.4,2.1,2.4]
    elif n==5:weights=[.9,1.4,1.6,1.8,2.1]
    elif n==2:weights=[1.6,4.4]
    widths=[width*w/sum(weights) for w in weights]
    content=[[Paragraph(inline(cell),styles['CellHead' if i==0 else 'Cell']) for cell in row] for i,row in enumerate(rows)]
    result=LongTable(content,colWidths=widths,repeatRows=1,hAlign='LEFT')
    result.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),TEAL),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f9f3')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.5,TEAL),('LINEBELOW',(0,1),(-1,-1),.3,LINE)]))
    return result

def markdown_story(path,width):
    lines=path.read_text(encoding='utf-8').splitlines();out=[];paragraph=[];i=0
    def flush():
        if paragraph:out.append(Paragraph(inline(' '.join(paragraph)),styles['Text']));paragraph.clear()
    while i<len(lines):
        line=lines[i]
        if line.startswith('```'):
            flush();language=line[3:];code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            if language=='mermaid':
                out.append(Paragraph('Consulte o PDF de diagramas e o arquivo classes.svg para a visão vetorial completa.',styles['Text']))
            else:
                out.append(Preformatted(clean('\n'.join(code)),styles['Codex'],maxLineLength=92))
        elif line.startswith('|'):
            flush();rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c) for c in cells):rows.append(cells)
                i+=1
            i-=1
            if rows:out.extend([table(rows,width),Spacer(1,12)])
        elif line.startswith('#'):
            flush();level=len(line)-len(line.lstrip('#'));out.append(Paragraph(inline(line.lstrip('#').strip()),styles['H1x' if level==1 else 'H2x' if level==2 else 'H3x']))
        elif re.match(r'^[-*] ',line):
            flush();out.append(Paragraph('• '+inline(line[2:]),styles['Bulletx']))
        elif re.match(r'^\d+\. ',line):
            flush();out.append(Paragraph(inline(line),styles['Text']))
        elif not line.strip():flush()
        else:paragraph.append(line)
        i+=1
    flush();return out

def footer(c,doc):
    w,h=doc.pagesize;c.saveState()
    c.setStrokeColor(LINE);c.line(46,38,w-46,38)
    c.setFont('Body',7);c.setFillColor(MUTED)
    c.drawString(46,25,'CLÍNICA SILVA  /  APS II  /  26.10.2026')
    c.drawRightString(w-46,25,str(doc.page))
    c.restoreState()

def cover(title,subtitle):
    return [Spacer(1,65),Paragraph('CLÍNICA SILVA',ParagraphStyle(name='CoverBrand',fontName='BodyBold',fontSize=13,textColor=TEAL,leading=20,spaceAfter=35)),
      Paragraph(title,ParagraphStyle(name='CoverTitle',fontName='BodyBold',fontSize=36,leading=43,textColor=INK,spaceAfter=22)),
      Paragraph(subtitle,ParagraphStyle(name='CoverSub',fontName='Body',fontSize=12,leading=20,textColor=MUTED,spaceAfter=35)),
      Paragraph('Análise e Projeto de Sistemas II<br/>26 de outubro de 2026',styles['Text']),
      Spacer(1,30),Paragraph('Protótipo acadêmico com dados fictícios.<br/>Nomes completos e RGMs do grupo: preencher com os integrantes reais.',styles['Text']),
      Spacer(1,25),Paragraph('Sistema: https://clinica-silva.vercel.app<br/>Código: https://github.com/Ygxxrr/clinica-viva-aps',styles['Text']),PageBreak()]

def build(name,title,subtitle,sources):
    doc=SimpleDocTemplate(str(OUT/name),pagesize=A4,rightMargin=46,leftMargin=46,topMargin=47,bottomMargin=55,title=title,author='Clínica Silva - Projeto acadêmico')
    story=cover(title,subtitle)
    for i,source in enumerate(sources):
        if i:story.append(PageBreak())
        story.extend(markdown_story(ROOT/'docs'/source,doc.width))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('PDF:',name)

def build_diagrams():
    target=OUT/'Diagramas-Clinica-Silva.pdf';c=canvas.Canvas(str(target),pagesize=landscape(A3));c.setTitle('Clínica Silva - Diagramas UML')
    specs=[('casos-de-uso','Casos de uso - visão completa'),('classes','Classes - visão completa (amplie para consultar)'),('classes-1','Classes - cadastros e estrutura'),('classes-2','Classes - atendimento'),('classes-3','Classes - financeiro'),('classes-4','Classes - acesso e rastreabilidade')]
    for i,(file,title) in enumerate(specs):
        drawing=svg2rlg(str(ROOT/'docs'/f'{file}.svg'))
        size=A3 if drawing.height>drawing.width*1.15 else landscape(A3)
        c.setPageSize(size)
        w,h=size;c.setFillColor(TEAL);c.setFont('BodyBold',18);c.drawString(35,h-40,title)
        scale=min((w-70)/drawing.width,(h-110)/drawing.height)
        drawing.scale(scale,scale);drawing.width*=scale;drawing.height*=scale
        renderPDF.draw(drawing,c,(w-drawing.width)/2,(h-110-drawing.height)/2+45)
        c.setFillColor(MUTED);c.setFont('Body',8);c.drawString(35,22,'CLÍNICA SILVA / APS II - SVGs vetoriais e fontes editáveis disponíveis no repositório.');c.drawRightString(w-35,22,str(i+1));c.showPage()
    c.save();print('PDF:',target.name)

if __name__=='__main__':
    build('Documentacao-Clinica-Silva.pdf','Documentação\ndo projeto','Requisitos, regras de negócio, rastreabilidade, organização do trabalho e casos de uso.', ['ANALISE.md','RASTREABILIDADE.md','SCRUM.md','CASOS_DE_USO.md','CLASSES.md'])
    build('Guia-Apresentacao-Clinica-Silva.pdf','Guia para\na apresentação','Roteiro de demonstração, arquitetura e respostas comentadas para estudar o funcionamento do sistema.', ['APRESENTACAO.md'])
    build_diagrams()
