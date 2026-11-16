"""Offline extraction from the owner's exact official 2.03 Windows updater.

Requires cabextract and fwtool.py commit cdba742b73eed5981480c326aeb30033aabf0223.
Never executes the updater, Sony ELF, or any extracted code.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import wbi

EXE_SHA='386970919b758b59de849cd954efd31de00e5f9e435056ce99a7c212a4aca584'
CAB_SHA='5b73eb2e4b7c5b30efef027fad87c88aeabbf4cdffd051aaf63e5a8c3dfa4b7a'
DAT_SHA='8f1cae050e96403ee035dd0b858417916c0c8c60d6eed777afbea159c71ace64'
FWTOOL_COMMIT='cdba742b73eed5981480c326aeb30033aabf0223'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4194304),b''):h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--exe',type=Path,required=True)
    ap.add_argument('--fwtool',type=Path,required=True)
    ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.exe.stat().st_size!=376353248 or digest(args.exe)!=EXE_SHA:
        raise SystemExit('Unknown updater size/hash; stop')
    commit=subprocess.check_output(['git','-C',str(args.fwtool),'rev-parse','HEAD'],text=True).strip()
    if commit!=FWTOOL_COMMIT:
        raise SystemExit('Use the pinned fwtool commit')
    # Do not execute a modified extractor checkout.
    if subprocess.check_output(['git','-C',str(args.fwtool),'status','--porcelain','--untracked-files=no']):
        raise SystemExit('fwtool checkout has tracked modifications')
    extractor = 'expand' if os.name == 'nt' else 'cabextract'
    if not shutil.which(extractor):raise SystemExit('Install ' + extractor + ' first')
    args.work_dir.mkdir(mode=0o700,parents=True,exist_ok=False)
    cab=args.work_dir/'installer.cab'
    table=bytes.maketrans(bytes(range(256)),bytes(range(255,-1,-1)))
    with args.exe.open('rb') as src,cab.open('xb') as dst:
        src.seek(465444);remaining=375877134
        while remaining:
            data=src.read(min(4194304,remaining))
            if not data:raise RuntimeError('Truncated updater')
            dst.write(data.translate(table));remaining-=len(data)
    if digest(cab)!=CAB_SHA:raise RuntimeError('CAB hash mismatch')
    cab_dir = args.work_dir/'cab'
    cab_dir.mkdir()
    if os.name == 'nt':
        subprocess.run(['expand','-F:FirmwareData_ZVE10V203.dat',str(cab),str(cab_dir)],check=True)
    else:
        subprocess.run(['cabextract','-q','-F','*FirmwareData*','-d',str(cab_dir),str(cab)],check=True)
    dat_path=args.work_dir/'cab/FirmwareData_ZVE10V203.dat'
    if digest(dat_path)!=DAT_SHA:raise RuntimeError('DAT hash mismatch')
    sys.path.insert(0,str(args.fwtool.resolve()))
    from fwtool.sony import dat,fdat
    from fwtool import archive
    decoded_path=args.work_dir/'firmware.fdat'
    with dat_path.open('rb') as src,decoded_path.open('xb') as dst:
        _,decoded=fdat.decryptFdat(dat.readDat(src).firmwareData)
        shutil.copyfileobj(decoded,dst,4194304)
    found=[]
    with decoded_path.open('rb') as src:
        for item in archive.readArchive(fdat.readFdat(src).fs):
            if item.path=='/bin/ud_wbi_drop.elf':
                data=item.contents.read();wbi.validate_tool(data);found.append(data)
    if len(found)!=1:raise RuntimeError('Expected exactly one known Sony tool')
    args.out.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with args.out.open('xb') as stream:
        args.out.chmod(0o600);stream.write(found[0])
    (args.work_dir/'provenance.json').write_text(json.dumps({'exe_sha256':EXE_SHA,
        'cab_sha256':CAB_SHA,'dat_sha256':DAT_SHA,'fwtool_commit':commit,'tool_sha256':wbi.TOOL_HASH},indent=2)+'\n')
    print('Verified Sony WBI tool:',args.out)

if __name__=='__main__':main()
