#!/usr/bin/env python3
"""ELF AArch64 .rodata diagnostic filename normalization only; no code/ABI/relocation edits.
Usage: normalize-diagnostics.py INPUT OUTPUT [RECEIPT]
INPUT is preserved; OUTPUT must not exist. Fixed-width replacement preserves every offset.
"""
import pathlib,struct,hashlib,json,sys,re
src,dst=map(pathlib.Path,sys.argv[1:3]);assert not dst.exists(),'output exists'
b=src.read_bytes();h=struct.unpack_from('<16sHHIQQQIHHHHHH',b);assert h[0][:4]==b'\x7fELF' and h[0][4:6]==b'\x02\x01' and h[2]==183
raw=[struct.unpack_from('<IIQQQQIIQQ',b,h[6]+i*h[11]) for i in range(h[12])];st=raw[h[13]];names=b[st[4]:st[4]+st[5]]
sections={names[x[0]:].split(b'\0',1)[0].decode():x for x in raw};ro=sections['.rodata'];assert ro[2]&2 and not ro[2]&5
out=bytearray(b);changes=[]
expected={'aligned_memory.cpp','android_util.cpp','angleutils.cpp'}
# Locate only NUL-terminated absolute diagnostic strings ending in these exact known source suffixes.
for m in re.finditer(rb'[^\x00]+\x00',b[ro[4]:ro[4]+ro[5]]):
 text=m.group()[:-1]
 if not text.startswith(b'/'):continue
 suffix=b'/src/common/';idx=text.rfind(suffix)
 if idx<0 or text[idx+len(suffix):].decode(errors='replace') not in expected:continue
 name=text[idx+len(suffix):].decode();replacement=b'/angle-source'+suffix+name.encode();assert len(replacement)<=len(text)
 replacement=replacement+b' '*(len(text)-len(replacement));off=ro[4]+m.start();out[off:off+len(text)]=replacement
 changes.append({'offset':off,'length':len(text),'source_basename':name,'public_diagnostic':replacement.decode().rstrip()})
assert {c['source_basename'] for c in changes}==expected and len(changes)==3,changes
allowed=set(i for c in changes for i in range(c['offset'],c['offset']+c['length']))
assert all(i in allowed for i,(x,y) in enumerate(zip(b,out)) if x!=y)
checks={}
for name,x in sections.items():
 if x[1]==8:continue # SHT_NOBITS
 before=b[x[4]:x[4]+x[5]];after=out[x[4]:x[4]+x[5]]
 if name!='.rodata':assert before==after,name
 checks[name]={'sha256_before':hashlib.sha256(before).hexdigest(),'sha256_after':hashlib.sha256(after).hexdigest(),'identical':before==after,'executable':bool(x[2]&4)}
assert not re.search(rb'/home/|/workspace/',out)
dst.write_bytes(out);dst.chmod(src.stat().st_mode&0o777)
receipt={'input_sha256':hashlib.sha256(b).hexdigest(),'output_sha256':hashlib.sha256(out).hexdigest(),'bytes':len(b),'method':'three known NUL-terminated .rodata diagnostic source filenames replaced in-place with fixed-width public names; trailing ASCII spaces before original terminator; all offsets/section sizes unchanged','changes':changes,'all_other_bytes_identical':True,'sections':checks,'build_id':'unchanged original ELF build-id; file SHA256 identifies normalized publication variant, not a claim that it was rebuilt or fully benchmarked'}
if len(sys.argv)>3:pathlib.Path(sys.argv[3]).write_text(json.dumps(receipt,indent=2))
print(json.dumps({'input_sha256':receipt['input_sha256'],'output_sha256':receipt['output_sha256'],'changed_diagnostics':len(changes),'executable_and_relocation_sections_identical':True},indent=2))
