"""Publica um snapshot por Git Data API, usando a autenticação existente do gh.

Alternativa para ambientes em que a escrita em .git é restrita. Não inclui
credenciais, banco local ou arquivos temporários. Atualiza sem force push.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
ROOT_FILES=['.gitignore','.vercelignore','.env.example','.python-version','iniciar.cmd','README.md','requirements.txt','requirements-docs.txt','vercel.json','app.py','models.py','services.py','catalog.py','seed.py','clock_local.py']
FOLDERS=['templates','public','docs','scripts','tests']

def gh_api(endpoint,method='GET',data=None):
    args=['gh','api',endpoint,'--method',method]
    if data is not None:args+=['--input','-']
    result=subprocess.run(args,input=json.dumps(data,ensure_ascii=False) if data is not None else None,
        cwd=ROOT,encoding='utf-8',capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)

def source_files():
    files=[ROOT/f for f in ROOT_FILES if (ROOT/f).exists()]
    for folder in FOLDERS:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.db'))
    return sorted(files)

def publish(repo,message,dry_run=False):
    files=source_files()
    if dry_run:
        print('\n'.join(str(p.relative_to(ROOT)).replace('\\','/') for p in files));return
    prefix=f'repos/{repo}'
    ref=gh_api(prefix+'/git/ref/heads/main')
    parent=ref['object']['sha']
    previous=gh_api(prefix+'/git/commits/'+parent)
    tree=[]
    for path in files:
        content=path.read_bytes();entry=dict(path=str(path.relative_to(ROOT)).replace('\\','/'),mode='100644',type='blob')
        try:entry['content']=content.decode('utf-8')
        except UnicodeDecodeError:
            blob=gh_api(prefix+'/git/blobs','POST',dict(content=base64.b64encode(content).decode('ascii'),encoding='base64'))
            entry['sha']=blob['sha']
        tree.append(entry)
    new_tree=gh_api(prefix+'/git/trees','POST',dict(base_tree=previous['tree']['sha'],tree=tree))
    commit=gh_api(prefix+'/git/commits','POST',dict(message=message,tree=new_tree['sha'],parents=[parent]))
    gh_api(prefix+'/git/refs/heads/main','PATCH',dict(sha=commit['sha'],force=False))
    print(f'Publicado: {len(files)} arquivos; commit {commit["sha"]}')
    print(f'https://github.com/{repo}/commit/{commit["sha"]}')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',required=True)
    parser.add_argument('--message',required=True)
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    publish(args.repo,args.message,args.dry_run)
