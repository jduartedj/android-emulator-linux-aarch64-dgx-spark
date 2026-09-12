#!/usr/bin/env python3
"""Conservative token grammar: validate before exec; no emulator/parser side effects."""
import sys,re
args=sys.argv[1:]
if args==['--check']:raise SystemExit(0)
flags={'-no-window','-no-audio','-no-snapshot','-no-snapshot-load','-no-snapshot-save','-no-boot-anim','-wipe-data','-no-metrics'}
values={'-avd','-port','-memory','-cores','-skin','-dpi-device','-timezone','-sysdir','-datadir','-data','-cache','-sdcard'}
avds=0;i=0
while i<len(args):
 a=args[i]
 if a.startswith('@') and re.fullmatch(r'@[A-Za-z0-9_.-]+',a):avds+=1;i+=1;continue
 if a in flags:i+=1;continue
 if a in values:
  if i+1>=len(args) or args[i+1].startswith(('-', '@')):raise SystemExit('Missing/unsafe value for '+a)
  v=args[i+1]
  if a=='-avd':avds+=1
  if a in {'-port','-memory','-cores','-dpi-device'} and not v.isdigit():raise SystemExit('Numeric value required for '+a)
  if a=='-prop' and not re.fullmatch(r'qemu[.]([A-Za-z0-9_.]+)=[A-Za-z0-9_.-]+',v):raise SystemExit('Only bounded qemu guest properties supported')
  i+=2;continue
 raise SystemExit('Unsupported/conflicting argument: '+a+' (renderer, accel, feature, equals forms, -- and -qemu pass-through are owned/rejected)')
if avds!=1:raise SystemExit('Supply exactly one @AVD or -avd NAME')
