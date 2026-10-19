"""Map classic TIFF grayscale strip ownership without decoding pixels."""
import argparse
import hashlib
import json
import struct
import sys


def inspect(raw):
    if not 8<=len(raw)<=8388608 or raw[:2] not in (b'II',b'MM'):raise ValueError('classic TIFF required, at most 8 MiB')
    e='<' if raw[:2]==b'II' else '>'
    def unpack(fmt,offset):
        size=struct.calcsize(e+fmt)
        if offset<0 or offset+size>len(raw):raise ValueError('field outside file')
        return struct.unpack_from(e+fmt,raw,offset)
    if unpack('H',2)[0]!=42:raise ValueError('only classic TIFF version 42; BigTIFF unsupported')
    offset=unpack('I',4)[0];seen=set();pages=[];metadata=[(0,8,'header')];strips=[]
    sizes={1:1,2:1,3:2,4:4,5:8,6:1,7:1,8:2,9:4,10:8,11:4,12:8}
    while offset:
        if offset in seen or len(seen)>=32 or offset%2:raise ValueError('IFD cycle, alignment or count limit')
        seen.add(offset);n=unpack('H',offset)[0]
        if n>128:raise ValueError('at most 128 fields per IFD')
        stop=offset+2+12*n+4
        if stop>len(raw):raise ValueError('IFD outside file')
        metadata.append((offset,stop,'IFD '+str(len(pages))));tags={}
        for i in range(n):
            pos=offset+2+12*i;tag,typ,count=unpack('HHI',pos)
            if tag in tags or typ not in sizes or count<1:raise ValueError('duplicate tag, unknown type or empty field')
            length=sizes[typ]*count
            start=pos+8 if length<=4 else unpack('I',pos+8)[0]
            if start+length>len(raw) or (length>4 and start%2):raise ValueError('tag payload outside file or unaligned')
            if length>4:metadata.append((start,start+length,'tag '+str(tag)))
            vals=None
            if typ in (3,4) and tag in (256,257,258,259,262,273,277,278,279,284):
                if count>4096:raise ValueError('tag value count limit')
                vals=list(unpack(('H' if typ==3 else 'I')*count,start))
            tags[tag]=(typ,count,vals)
        def values(tag,default=None):
            if tag not in tags:
                if default is not None:return [default]
                raise ValueError('missing required tag '+str(tag))
            typ,count,vals=tags[tag]
            if tag in (258,259,262,277,284) and typ!=3:raise ValueError('sample/compression fields require SHORT')
            if typ not in (3,4) or vals is None:raise ValueError('required tags must be SHORT/LONG')
            return vals
        def single(tag,default=None):
            vals=values(tag,default)
            if len(vals)!=1:raise ValueError('scalar tag has multiple values')
            return vals[0]
        w,h=single(256),single(257);rows=single(278)
        if not 1<=w<=1000000 or not 1<=h<=1000000 or not 1<=rows<=1000000:raise ValueError('dimension or rows-per-strip limit')
        if single(258)!=8 or single(259)!=1 or single(262) not in (0,1) or single(277,1)!=1 or single(284,1)!=1:
            raise ValueError('only uncompressed, one-sample, 8-bit grayscale strips')
        if any(t in tags for t in (322,323,324,325,330)):raise ValueError('tiles and SubIFDs unsupported')
        offsets=values(273);counts=values(279);expected=(h+rows-1)//rows
        if len(offsets)!=expected or len(counts)!=expected or expected>4096:raise ValueError('strip array count mismatch or limit')
        page={'ifd_offset':offset,'width':w,'height':h,'rows_per_strip':rows,'strips':[]}
        for i,(lo,count) in enumerate(zip(offsets,counts)):
            if count!=w*min(rows,h-i*rows) or lo+count>len(raw):raise ValueError('strip byte count or file boundary mismatch')
            label='page '+str(len(pages))+' strip '+str(i)
            strips.append((lo,lo+count,label));page['strips'].append({'range':[lo,lo+count],'rows':[i*rows,min(h,(i+1)*rows)]})
        pages.append(page);offset=unpack('I',stop-4)[0]
    if not pages:raise ValueError('at least one IFD required')
    if len(strips)>4096:raise ValueError('at most 4096 strips across file')
    findings=[];total=0
    for i,a in enumerate(strips):
        for b in strips[i+1:]+metadata:
            lo=max(a[0],b[0]);hi=min(a[1],b[1])
            if lo<hi:
                total+=1
                if len(findings)<256:findings.append({'owners':[a[2],b[2]],'range':[lo,hi],'exact_alias':a[:2]==b[:2]})
    return {'sha256':hashlib.sha256(raw).hexdigest(),'byte_order':'little' if e=='<' else 'big',
            'pages':pages,'metadata_ranges':[{'range':[a,b],'owner':s} for a,b,s in metadata],
            'overlap_count':total,'omitted_overlaps':total-len(findings),'findings':findings}


def example():
    tags=[(256,4,2),(257,4,2),(258,3,8),(259,3,1),(262,3,1),(273,4,122),(277,3,1),(278,4,2),(279,4,4)]
    return b'II'+struct.pack('<HIH',42,8,len(tags))+b''.join(struct.pack('<HHI',t,k,1)+(struct.pack('<H',v)+b'\0\0' if k==3 else struct.pack('<I',v)) for t,k,v in tags)+bytes(4)+bytes(range(4))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',nargs='?');p.add_argument('--make-example');a=p.parse_args()
    try:
        if bool(a.input)==bool(a.make_example):raise ValueError('specify input OR --make-example NEW_FILE')
        if a.make_example:
            with open(a.make_example,'xb') as f:f.write(example())
            return 0
        with open(a.input,'rb') as f:raw=f.read(8388609)
        r=inspect(raw);print(json.dumps(r,indent=2));return int(bool(r['findings']))
    except (ValueError,OSError,struct.error) as e:print(str(e),file=sys.stderr);return 2


if __name__=='__main__':sys.exit(main())
