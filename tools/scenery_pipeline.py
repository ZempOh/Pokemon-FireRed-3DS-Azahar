#!/usr/bin/env python3
"""Reusable scenery inventory and exact-candidate release gate; no publishing side effects."""
import argparse
import hashlib
import json
from pathlib import Path

PROFILE=Path(__file__).with_name('scenery_profiles.json')
SOURCE_EXT={'.c','.h','.cpp','.py','.kt','.java','.json','.toml'}

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def fingerprint(repo,profile):
    files={}
    for directory in profile['sources']:
        root=repo/directory
        if not root.is_dir():raise ValueError('Missing source directory: '+str(root))
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.suffix in SOURCE_EXT and '__pycache__' not in p.parts:
                files[p.relative_to(repo).as_posix()]=digest(p)
    for key in ('entrypoints','active_models','room_models'):
        values=profile.get(key,[])
        if isinstance(values,str):values=[values]
        for rel in values:
            if not (repo/rel).is_file():raise ValueError('Missing active input: '+rel)
    body=json.dumps({'profile':profile,'files':files},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(body).hexdigest(),files

def inventory(workspace,config,games):
    result={'schema':1,'scope':config['scope'],'games':{}}
    for game in games:
        profile=config['games'][game]
        source_hash,files=fingerprint(workspace/profile['repo'],profile)
        result['games'][game]={'source_sha256':source_hash,'files':files,
            'active_paths':{k:v for k,v in profile.items() if k not in ('sources','repo')},
            'coverage':{family:'unverified' for family in config['families']}}
    return result

def gate(workspace,config,candidate,report_path):
    report_path=report_path.resolve();report=json.loads(report_path.read_text())
    game=report['game'];profile=config['games'][game]
    current,_=fingerprint(workspace/profile['repo'],profile)
    errors=[]
    if report.get('source_sha256')!=current:errors.append('Source changed since testing')
    if report.get('artifact_sha256')!=digest(candidate):errors.append('Artifact differs from tested build')
    if report.get('device')!='AYN Thor':errors.append('Thor qualification missing')
    if not report.get('build_commit'):errors.append('Build provenance missing')
    checks=report.get('checks',{})
    for name in config['required_checks']:
        check=checks.get(name,{})
        if check.get('passed') is not True:errors.append(name+': not passed');continue
        evidence=check.get('evidence',[])
        if not evidence:errors.append(name+': no evidence');continue
        for item in evidence:
            path=(report_path.parent/item['path']).resolve()
            if not path.is_file() or digest(path)!=item.get('sha256'):
                errors.append(name+': missing or changed evidence')
    coverage=report.get('coverage',{})
    # Partial releases are allowed only when named as partial. An "all assets"
    # claim needs evidence-backed completion of every declared family.
    if report.get('claim')=='all_environment_assets':
        for family in config['families']:
            if coverage.get(family)!='passed':errors.append(family+': coverage incomplete')
    elif report.get('claim')!='partial_environment_update':
        errors.append('Explicit release scope missing')
    return {'game':game,'eligible':not errors,'errors':errors,
            'artifact_sha256':digest(candidate),'source_sha256':current,
            'note':'Evidence integrity gate only; game-specific metric and visual checks must already have passed.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True,help='Parent of the game checkouts')
    parser.add_argument('--profiles',type=Path,default=PROFILE)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('inventory');p.add_argument('--game',action='append');p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('gate');p.add_argument('--candidate',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();config=json.loads(args.profiles.read_text())
    if args.command=='inventory':result=inventory(args.workspace,config,args.game or list(config['games']))
    else:result=gate(args.workspace,config,args.candidate,args.report)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(str(args.output))
    if args.command=='gate' and not result['eligible']:raise SystemExit(1)
if __name__=='__main__':main()
