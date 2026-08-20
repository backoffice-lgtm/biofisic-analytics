import { rpc, dashboardFilters } from "./_lib/supabase.mjs";

function xmlEscape(v){ return String(v ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
function colName(n){ let s=""; while(n){ n--; s=String.fromCharCode(65+n%26)+s; n=Math.floor(n/26); } return s; }
function crc32(buf){ let crc=0xffffffff; for(const b of buf){ crc^=b; for(let k=0;k<8;k++) crc=(crc>>>1)^((crc&1)?0xedb88320:0); } return (crc^0xffffffff)>>>0; }
function u16(n){ const b=Buffer.alloc(2); b.writeUInt16LE(n); return b; }
function u32(n){ const b=Buffer.alloc(4); b.writeUInt32LE(n>>>0); return b; }
function zipStore(files){
  const locals=[], centrals=[]; let offset=0;
  for(const [name,data0] of files){ const data=Buffer.isBuffer(data0)?data0:Buffer.from(data0,"utf8"); const nb=Buffer.from(name,"utf8"); const crc=crc32(data); const local=Buffer.concat([Buffer.from([0x50,0x4b,0x03,0x04]),u16(20),u16(0),u16(0),u16(0),u16(0),u32(crc),u32(data.length),u32(data.length),u16(nb.length),u16(0),nb,data]); locals.push(local); const central=Buffer.concat([Buffer.from([0x50,0x4b,0x01,0x02]),u16(20),u16(20),u16(0),u16(0),u16(0),u16(0),u32(crc),u32(data.length),u32(data.length),u16(nb.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(offset),nb]); centrals.push(central); offset+=local.length; }
  const cd=Buffer.concat(centrals); const end=Buffer.concat([Buffer.from([0x50,0x4b,0x05,0x06]),u16(0),u16(0),u16(files.length),u16(files.length),u32(cd.length),u32(offset),u16(0)]); return Buffer.concat([...locals,cd,end]);
}
function rowsFromTab(payload){
  const rows=[["BioFisic Analytics",payload.tabKey||""],["Fonte",payload.sourceFile||""] ,["",""],["Indicador","Valor","Detalhe"]];
  for(const c of payload?.tab?.cards || []) rows.push([c.label||"",c.value??"",c.sub||c.metric||""]);
  for(const chart of payload?.tab?.charts || []){
    rows.push(["",""]); rows.push([chart.title||chart.type||"Gráfico", chart.subtitle||""]);
    const chartRows = chart.rows || [];
    if(Array.isArray(chartRows)) for(const r of chartRows.slice(0,500)) rows.push([r.label||r.unit||"",r.value??r.total??"",(r.display ?? r.pct ?? "")]);
  }
  return rows;
}
function worksheet(rows){
  const xmlRows=rows.map((r,ri)=>`<row r="${ri+1}">${r.map((v,ci)=>{ const ref=`${colName(ci+1)}${ri+1}`; return typeof v==="number"?`<c r="${ref}"><v>${v}</v></c>`:`<c r="${ref}" t="inlineStr"><is><t>${xmlEscape(v)}</t></is></c>`; }).join("")}</row>`).join("");
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>${xmlRows}</sheetData></worksheet>`;
}
export default async (request)=>{
  if(request.method!=="POST") return new Response(JSON.stringify({error:"Use POST."}),{status:405,headers:{"content-type":"application/json"}});
  try{
    const body=await request.json(); const filters=dashboardFilters(body); const tabs=["ativos","vendas","cancelamentos","financeiro","frequencia","isaias"];
    const payloads=[]; for(const tab of tabs) payloads.push(await rpc("biofisic_dashboard_tab",{p_tab:tab,p_filters:filters,p_force:false},45000));
    const names=["Visao_Geral","Vendas","Cancelamentos","Financeiro","Frequencia","Analise"];
    const files=[];
    files.push(["[Content_Types].xml",`<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>${names.map((_,i)=>`<Override PartName="/xl/worksheets/sheet${i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join("")}</Types>`]);
    files.push(["_rels/.rels",`<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`]);
    files.push(["xl/workbook.xml",`<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>${names.map((n,i)=>`<sheet name="${n}" sheetId="${i+1}" r:id="rId${i+1}"/>`).join("")}</sheets></workbook>`]);
    files.push(["xl/_rels/workbook.xml.rels",`<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${names.map((_,i)=>`<Relationship Id="rId${i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i+1}.xml"/>`).join("")}</Relationships>`]);
    payloads.forEach((p,i)=>files.push([`xl/worksheets/sheet${i+1}.xml`,worksheet(rowsFromTab(p))]));
    const book=zipStore(files);
    return new Response(book,{status:200,headers:{"content-type":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","content-disposition":"attachment; filename=dashboard_biofisic.xlsx","cache-control":"no-store"}});
  }catch(error){ return new Response(JSON.stringify({error:error?.message||String(error)}),{status:error?.status||500,headers:{"content-type":"application/json","cache-control":"no-store"}}); }
};
