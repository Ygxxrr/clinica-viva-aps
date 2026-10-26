"""Transforma o tutorial da aplicação em Markdown e PDF para estudo offline."""
from pathlib import Path
from html.parser import HTMLParser
import re
import sys

ROOT=Path(__file__).resolve().parents[1]

class TutorialMarkdown(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output=[];self.skip=0;self.in_table=False;self.cell=None;self.row=[];self.rows=[]
    def emit(self,value):
        if self.cell is not None:self.cell.append(value)
        else:self.output.append(value)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='nav':self.skip+=1
        if self.skip:return
        if tag=='p' and attrs.get('class')=='eyebrow':self.skip+=1;return
        if tag=='table':self.in_table=True;self.rows=[]
        elif tag=='tr':self.row=[]
        elif tag in ('td','th'):self.cell=[]
        elif tag=='h2':self.emit('\n\n## ')
        elif tag=='h3':self.emit('\n\n### ')
        elif tag=='p':self.emit('\n\n')
        elif tag=='li':self.emit('\n- ')
        elif tag=='strong':self.emit('**')
        elif tag=='code':self.emit('`')
        elif tag=='br':self.emit(' ')
    def handle_endtag(self,tag):
        if self.skip:
            if tag in ('nav','p'):self.skip-=1
            return
        if tag in ('td','th'):
            self.row.append(re.sub(r'\s+',' ',''.join(self.cell or [])).strip());self.cell=None
        elif tag=='tr':self.rows.append(self.row)
        elif tag=='table':
            self.in_table=False;self.emit('\n\n')
            for i,row in enumerate(self.rows):
                self.emit('| '+' | '.join(row)+' |\n')
                if i==0:self.emit('| '+' | '.join('---' for _ in row)+' |\n')
            self.emit('\n')
        elif tag in ('strong','code'):self.emit('**' if tag=='strong' else '`')
        elif tag in ('h2','h3','p','ol','ul','section'):self.emit('\n\n')
    def handle_data(self,data):
        if not self.skip:self.emit(data)

def source():
    html=(ROOT/'templates/tutorial.html').read_text(encoding='utf-8').split('{% block content %}',1)[1]
    html=re.sub(r'{%.*?%}|{{.*?}}','',html,flags=re.S)
    parser=TutorialMarkdown();parser.feed(html)
    content='# Tutorial completo - Clínica Silva\n\nNavegação e funcionalidades da versão Roxo Aurora.\n\n'+''.join(parser.output)
    content=re.sub(r'\n{3,}','\n\n',content)
    path=ROOT/'docs/TUTORIAL.md';path.write_text(content.strip()+'\n',encoding='utf-8')
    return path

def build_pdf(out):
    # Dependências opcionais declaradas em requirements-docs.txt.
    sys.argv=[sys.argv[0],str(out)]
    import generate_documents as docs
    docs.TEAL=docs.colors.HexColor('#7452bf')
    for key in ('H1x','H3x'):docs.styles[key].textColor=docs.TEAL
    doc=docs.SimpleDocTemplate(str(out/'Tutorial-Clinica-Silva.pdf'),pagesize=docs.A4,leftMargin=46,rightMargin=46,topMargin=47,bottomMargin=55,title='Tutorial completo - Clínica Silva',author='Clínica Silva - Projeto acadêmico')
    story=[docs.Spacer(1,55),docs.Paragraph('CLÍNICA SILVA · ROXO AURORA',docs.styles['H3x']),docs.Spacer(1,25),docs.Paragraph('Tutorial completo<br/>do sistema',docs.styles['H1x']),docs.Paragraph('Acesso, navegação, funcionalidades, roteiro de apresentação e limites da versão acadêmica.',docs.styles['Text']),docs.Spacer(1,25),docs.Paragraph('Sistema: https://clinica-viva-aps.vercel.app<br/>Ajuda no sistema: menu Ajuda ou link Como usar.',docs.styles['Text']),docs.Spacer(1,25),docs.Paragraph('Use este material para estudar e ensaiar. Os exemplos usam dados fictícios e as ações de demonstração alteram os registros do ambiente.',docs.styles['Text']),docs.PageBreak()]
    story.extend(docs.markdown_story(ROOT/'docs/TUTORIAL.md',doc.width))
    doc.build(story,onFirstPage=docs.footer,onLaterPages=docs.footer)
    print('Tutorial em PDF:',out/'Tutorial-Clinica-Silva.pdf')

if __name__=='__main__':
    source()
    destination=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'public/downloads'
    destination.mkdir(parents=True,exist_ok=True)
    build_pdf(destination)
