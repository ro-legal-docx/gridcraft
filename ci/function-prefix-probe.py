from pathlib import Path
import zipfile,subprocess,json,hashlib,os,sys,xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
r=Path(sys.argv[1]).resolve();r.mkdir();out=r/'results';out.mkdir()
cli=Path(sys.argv[2]).resolve()
if os.name=='nt':cli=cli.with_suffix('.exe')
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def make(path,unsupported):
 cache=1250.25 if unsupported else 30
 formula='GETPIVOTDATA("Suma",$A$1)' if unsupported else 'SUM(A1:A2)'
 parts={
 '[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>',
 '_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
 'xl/workbook.xml':'<workbook xmlns="'+ns['s']+'" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Compatibilitate" sheetId="1" r:id="rId1"/></sheets><calcPr calcId="191029"/></workbook>',
 'xl/_rels/workbook.xml.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
 'xl/styles.xml':'<styleSheet xmlns="'+ns['s']+'"><fonts count="1"><font><sz val="11"/><name val="Arial"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs></styleSheet>',
 'xl/worksheets/sheet1.xml':'<worksheet xmlns="'+ns['s']+'"><dimension ref="A1:E5"/><sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols><col min="1" max="5" width="22" customWidth="1"/></cols><sheetData><row r="1"><c r="A1"><v>10</v></c><c r="B1" s="1"><f>'+escape(formula)+'</f><v>'+str(cache)+'</v></c><c r="C1" s="1"><f>B1*2</f><v>'+str(cache*2)+'</v></c><c r="D1" s="1"><f>SUM(A1:A2)</f><v>30</v></c><c r="E1" s="1"><f>ROUND(C1/3,2)</f><v>'+str(round(cache*2/3,2))+'</v></c></row><row r="2"><c r="A2"><v>20</v></c></row><row r="4"><c r="A4" t="inlineStr"><is><t>TEST compatibilitate</t></is></c></row><row r="5"><c r="A5" t="inlineStr"><is><t>ă â î ș ț Ă Â Î Ș Ț</t></is></c></row></sheetData><pageMargins left="0.3" right="0.3" top="0.3" bottom="0.3" header="0.1" footer="0.1"/><pageSetup paperSize="9" orientation="landscape"/></worksheet>'}
 with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for name,data in parts.items():z.writestr(name,data.encode())
 return {'B1':str(cache),'C1':str(cache*2),'D1':'30','E1':str(round(cache*2/3,2))}
seed=out/'seed.xlsx';make(seed,False)
raw=[('_xlfn.STOCKHISTORY("SYNTHETIC",1)'),('_xlfn.TRANSLATE("test","ro","en")'),('_xlfn.DETECTLANGUAGE("test")'),('_xlfn.COPILOT("SYNTHETIC")'),('_xlfn.SYNTHETICFUTURE(B5)'),('SUM(_xlfn.SYNTHETICFUTURE(B6),1)'),('_xlfn._xlws.SYNTHETICFILTER(B7)'),('_xlfn.SYNTHETICFUTURE(B8)+SYNTHETICFUTURE(B9)'),('_xlfn.SYNTHETICFUTURE(_xlfn._xlws.SYNTHETICFUTURE(B9))+SYNTHETICFUTURE(B8)')]
rows=[f'<row r="{i}"><c r="A{i}"><f>{escape(f)}</f><v>7</v></c><c r="B{i}"><v>1</v></c></row>' for i,f in enumerate(raw,1)]
rows += ['<row r="10"><c r="A10"><f t="shared" si="0" ref="A10:A11">_xlfn.SYNTHETICFUTURE(B10)</f><v>7</v></c></row>','<row r="11"><c r="A11"><f t="shared" si="0"/><v>8</v></c></row>','<row r="12"><c r="A12"><f t="array" ref="A12">_xlfn.SYNTHETICARRAY(B12)</f><v>9</v></c></row>']
known_mixed=[
 'XLOOKUP(B1,C1:C3,D1:D3)+_xlfn.XLOOKUP(B2,C1:C3,D1:D3)',
 '_xlfn.XLOOKUP(B1,C1:C3,D1:D3)+XLOOKUP(B2,C1:C3,D1:D3)',
 'FILTER(B1:B3,B1:B3>0)+_xlfn._xlws.FILTER(C1:C3,C1:C3>0)',
 '_xlfn._xlws.FILTER(B1:B3,B1:B3>0)+FILTER(C1:C3,C1:C3>0)',
]
rows += [f'<row r="{i}"><c r="A{i}"><f>{escape(f)}</f><v>7</v></c></row>' for i,f in enumerate(known_mixed,13)]
source=out/'input.xlsx'
with zipfile.ZipFile(seed) as z,zipfile.ZipFile(source,'x',compression=zipfile.ZIP_DEFLATED) as target:
 for name in z.namelist():target.writestr(name,(f'<worksheet xmlns="{ns["s"]}"><sheetData>'+''.join(rows)+'</sheetData></worksheet>').encode() if name=='xl/worksheets/sheet1.xml' else z.read(name))
expected={f'A{i}':f for i,f in enumerate(raw,1)};expected.update(A10='_xlfn.SYNTHETICFUTURE(B10)',A11='_xlfn.SYNTHETICFUTURE(B11)',A12='_xlfn.SYNTHETICARRAY(B12)')
expected.update({f'A{i}':f for i,f in enumerate(known_mixed,13)})
sha=hashlib.sha256(source.read_bytes()).hexdigest();env=os.environ.copy();env.update(XDG_CACHE_HOME=str(out/'cache'),XDG_CONFIG_HOME=str(out/'config'),XDG_DATA_HOME=str(out/'data'))
def read_formulas(path):
 with zipfile.ZipFile(path) as z:xml=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
 return {c.attrib['r']:f.text for c in xml.findall('.//s:c',ns) if (f:=c.find('s:f',ns)) is not None}
def run(src,dest,commands):
 assert not dest.exists()
 args=[str(cli),'run','--in',str(src)]
 for command in commands:args+=['--cmd',command]
 args+=['--out',str(dest)]
 with dest.with_suffix('.log').open('x') as log:p=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=120)
 assert p.returncode==0,dest.with_suffix('.log').read_text()
 return read_formulas(dest)
results=[];current=source
for i in [1,2]:
 dest=out/f'saved-{i}.xlsx';actual=run(current,dest,['cell.set={"cell":"Z20","input":"1"}']);assert all(actual[k]==v for k,v in expected.items()),actual
 results.append({'case':f'unrelated-edit-roundtrip-{i}','formula_cells_checked':len(expected),'prefixes_preserved':True});current=dest
actual=run(source,out/'copy-and-arguments.xlsx',['edit.copy={"range":"A5"}','edit.paste={"at":"D5"}','cell.set={"cell":"A5","input":"=SYNTHETICFUTURE(B6)"}'])
assert actual['D5']=='_xlfn.SYNTHETICFUTURE(E5)' and actual['A5']=='_xlfn.SYNTHETICFUTURE(B6)',actual
results.append({'case':'copy-and-argument-edit','formula_cells_checked':len(expected)+1,'prefixes_preserved':True})
actual=run(source,out/'renamed.xlsx',['sheet.rename={"name":"Synthetic renamed"}']);assert all(actual[k]==v for k,v in expected.items())
results.append({'case':'sheet-rename','formula_cells_checked':len(expected),'prefixes_preserved':True})
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
# Known XLOOKUP calls additionally prove live recalculation, rather than only cached values.
known=out/'known-mixed-values.xlsx'
formula='XLOOKUP(D1,$A$1:$A$2,$B$1:$B$2)+_xlfn.XLOOKUP(D2,$A$1:$A$2,$B$1:$B$2)'
xml=f'<worksheet xmlns="{ns["s"]}"><sheetData><row r="1"><c r="A1"><v>1</v></c><c r="B1"><v>10</v></c><c r="C1"><f>{formula}</f><v>30</v></c><c r="D1"><v>1</v></c></row><row r="2"><c r="A2"><v>2</v></c><c r="B2"><v>20</v></c><c r="D2"><v>2</v></c></row><row r="3"><c r="D3"><v>1</v></c></row></sheetData></worksheet>'
with zipfile.ZipFile(seed) as z,zipfile.ZipFile(known,'x',compression=zipfile.ZIP_DEFLATED) as target:
 for name in z.namelist():target.writestr(name,xml.encode() if name=='xl/worksheets/sheet1.xml' else z.read(name))
known_sha=hashlib.sha256(known.read_bytes()).hexdigest()
def number(path,cell):
 with zipfile.ZipFile(path) as z:sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
 node=next(c for c in sheet.findall('.//s:c',ns) if c.attrib['r']==cell)
 assert node.attrib.get('t')!='e',ET.tostring(node)
 return float(node.find('s:v',ns).text)
dest=out/'known-roundtrip.xlsx';actual=run(known,dest,['cell.set={"cell":"Z20","input":"1"}']);assert actual['C1']==formula and number(dest,'C1')==30
changed=out/'known-recalculated.xlsx';actual=run(known,changed,['cell.set={"cell":"D1","input":"2"}','edit.copy={"range":"C1"}','edit.paste={"at":"C2"}'])
assert actual['C1']==formula and actual['C2']=='XLOOKUP(D2,$A$1:$A$2,$B$1:$B$2)+_xlfn.XLOOKUP(D3,$A$1:$A$2,$B$1:$B$2)',actual
assert number(changed,'C1')==40 and number(changed,'C2')==30
reopened=out/'known-reopened.xlsx';actual=run(changed,reopened,['cell.set={"cell":"Z20","input":"2"}']);assert actual['C1']==formula and number(reopened,'C1')==40 and number(reopened,'C2')==30
assert hashlib.sha256(known.read_bytes()).hexdigest()==known_sha
record={'known_mixed_values':{'source_sha256':known_sha,'source_unchanged':True,'original':30,'after_input_change':40,'copied_cell':30,'reopened':40},'synthetic_only':True,'source_sha256':sha,'source_unchanged':True,'cli_sha256':hashlib.sha256(cli.read_bytes()).hexdigest(),'cases':results,'values_not_qualified':'unsupported functions still require the separate saved-cache policy; this probe checks formula namespaces, not calculation'}
with (out/'results.json').open('x') as f:json.dump(record,f,indent=2)
print(json.dumps(record,indent=2))
