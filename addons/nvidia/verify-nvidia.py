#!/usr/bin/env python3
"""Read-only evidence check for an explicitly selected disposable emulator serial."""
import argparse,pathlib,subprocess,json,re,os,struct,hashlib
ap=argparse.ArgumentParser();ap.add_argument('--serial',required=True);ap.add_argument('--adb',default='/usr/bin/adb');a=ap.parse_args()
if not re.fullmatch(r'emulator-\d+',a.serial):raise SystemExit('Requires explicit emulator serial; no physical device')
sf=subprocess.check_output([a.adb,'-s',a.serial,'shell','dumpsys','SurfaceFlinger'],text=True,timeout=20)
gles=next((s for s in sf.splitlines() if s.startswith('GLES:')),'')
if 'NVIDIA' not in gles or any(s.lower() in gles.lower() for s in ['SwiftShader','llvmpipe','softpipe']):raise SystemExit('NOT verified NVIDIA: '+gles)
port=a.serial.split('-')[1];procs=[]
for d in pathlib.Path('/proc').iterdir():
 if not d.name.isdigit():continue
 try:
  cmd=(d/'cmdline').read_bytes().split(b'\0')
  exe=os.readlink(d/'exe')
  if pathlib.Path(exe).name!='qemu-system-aarch64-headless':continue
  if b'-port' not in cmd or cmd.index(b'-port')+1>=len(cmd) or cmd[cmd.index(b'-port')+1]!=port.encode():continue
  header=pathlib.Path(exe).read_bytes()[:64]
  if header[:4]!=b'\x7fELF' or struct.unpack_from('<H',header,18)[0]!=183:continue
  maps=(d/'maps').read_text();fds=[]
  for f in (d/'fd').iterdir():
   try:fds.append(os.readlink(f))
   except OSError:pass
  if 'libnvidia-glcore' in maps and 'libshadertranslator.so' in maps and '/dev/kvm' in fds:
   procs.append({'pid':int(d.name),'exe':exe,'sha256':hashlib.sha256(pathlib.Path(exe).read_bytes()).hexdigest(),'loaded_driver_and_addon':sorted(set(l.split()[-1] for l in maps.splitlines() if 'libnvidia' in l or 'libshadertranslator.so' in l)),'kvm_handles':[f for f in fds if 'kvm' in f]})
 except OSError:pass
if not procs:raise SystemExit('Guest string present but matching native process/driver/addon/KVM evidence missing')
gpu=subprocess.check_output(['nvidia-smi'],text=True,timeout=20)
if not any(re.search(r'\b'+str(p['pid'])+r'\s+G\s',gpu) for p in procs):raise SystemExit('Matching QEMU graphics-process usage not observed in nvidia-smi')
print(json.dumps({'status':'VERIFIED_NVIDIA_OPENGL','guest_gles':gles,'processes':procs,'gpu_process_output':gpu},indent=2))
