#!/usr/bin/env python3
"""Gera o dashboard HTML (self-contained, comparação de meses interativa) a partir do analise.json.
Uso: python build_dashboard.py analise.json index.html "01/08/2026 08:26 (BRT)" """
import sys, json
inp = sys.argv[1] if len(sys.argv)>1 else "analise.json"
out = sys.argv[2] if len(sys.argv)>2 else "index.html"
gerado = sys.argv[3] if len(sys.argv)>3 else ""
data = json.load(open(inp)); data["gerado_em"]=gerado
DATA_JSON = json.dumps(data, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Refera — Painel de Receita e Indicadores</title>
<style>
  :root{--bg:#f4f5f3;--surface-1:#fff;--surface-2:#f6f7f4;--line:#e6e7e3;
    --text-primary:#14140f;--text-secondary:#57564f;--text-muted:#8a897f;
    --series-1:#2a78d6;--series-1-soft:#cde2fb;--series-2:#eb6834;--series-2-soft:#fbe0d3;
    --good:#0ca30c;--critical:#d03b3b;--serious:#ec835a;--neutral:#9a998f;--info:#5f6b7a;--navy:#1f3864;
    --o-demanda:#2a78d6;--o-conv2:#7a5cd0;--o-aprov:#0f9b6c;--o-fin:#9a998f;--o-ticket:#d2559a;
    --shadow:0 1px 2px rgba(0,0,0,.05),0 6px 20px rgba(20,20,15,.05);--radius:14px;}
  :root[data-theme="dark"]{--bg:#121211;--surface-1:#1c1c1a;--surface-2:#232320;--line:#33332e;
    --text-primary:#f4f4ef;--text-secondary:#c3c2b7;--text-muted:#8f8e83;
    --series-1:#3987e5;--series-1-soft:#1c3a5e;--series-2:#d95926;--series-2-soft:#4a2a1c;
    --good:#2bb52b;--critical:#e05a5a;--serious:#f0956b;--neutral:#7d7c72;--info:#9aa4b3;--navy:#9bb4e0;
    --o-demanda:#5a9bea;--o-conv2:#a596ec;--o-aprov:#3bbd8c;--o-fin:#8f8e83;--o-ticket:#e07ab0;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 6px 22px rgba(0,0,0,.35);}
  *{box-sizing:border-box}html,body{margin:0}
  body{background:var(--bg);color:var(--text-primary);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.45}
  .wrap{max-width:1200px;margin:0 auto;padding:24px 18px 70px}
  header.top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap}
  .brand{display:flex;align-items:center;gap:12px}
  .logo{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--navy),var(--series-1));display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:18px}
  h1{font-size:20px;margin:0;letter-spacing:-.3px}
  .sub{color:var(--text-secondary);font-size:13px;margin-top:2px}
  .theme-btn{border:1px solid var(--line);background:var(--surface-1);color:var(--text-secondary);border-radius:9px;padding:7px 12px;font-size:13px;cursor:pointer}
  .compare{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:var(--surface-1);border:1px solid var(--line);border-left:3px solid var(--series-1);border-radius:10px;padding:11px 14px;margin:16px 0 4px;box-shadow:var(--shadow)}
  .compare b{font-size:13.5px}
  .compare select{font-size:14px;font-weight:650;color:var(--text-primary);background:var(--surface-2);border:1px solid var(--line);border-radius:8px;padding:6px 10px;cursor:pointer}
  .compare .arw{color:var(--text-muted);font-weight:700}
  .compare .quick{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}
  .compare .quick button{font-size:12px;border:1px solid var(--line);background:var(--surface-2);color:var(--text-secondary);border-radius:20px;padding:4px 11px;cursor:pointer}
  .compare .quick button:hover{color:var(--text-primary);border-color:var(--series-1)}
  .compare .hint2{font-size:12px;color:var(--text-muted);flex-basis:100%;margin-top:2px}
  .tabs{display:flex;gap:8px;margin:16px 0 16px;border-bottom:1px solid var(--line)}
  .tab{appearance:none;border:0;background:none;padding:10px 4px;margin-right:16px;font-size:15px;font-weight:600;color:var(--text-muted);cursor:pointer;border-bottom:2.5px solid transparent;transform:translateY(1px)}
  .tab[aria-selected="true"]{color:var(--text-primary);border-bottom-color:var(--series-1)}
  .tab .pill{display:inline-block;min-width:20px;padding:0 6px;margin-left:6px;border-radius:20px;font-size:12px;background:var(--surface-2);color:var(--text-secondary);font-weight:700}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0 18px}
  .kpi{background:var(--surface-1);border:1px solid var(--line);border-radius:var(--radius);padding:15px 16px 13px;box-shadow:var(--shadow)}
  .kpi .label{font-size:11.5px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.4px;font-weight:600}
  .kpi .val{font-size:25px;font-weight:750;letter-spacing:-.6px;margin-top:6px;font-variant-numeric:tabular-nums}
  .kpi .delta{font-size:12.5px;margin-top:3px;font-weight:600}
  .up{color:var(--good)}.down{color:var(--critical)}.flat{color:var(--text-muted)}
  .card{background:var(--surface-1);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:18px;margin-bottom:18px}
  .card h2{font-size:15px;margin:0 0 2px;letter-spacing:-.2px}
  .card .hint{font-size:12.5px;color:var(--text-muted);margin:0 0 12px}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:840px){.grid2{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}
  th{font-size:10.5px;text-transform:uppercase;letter-spacing:.3px;color:var(--text-muted);font-weight:700;position:sticky;top:0;background:var(--surface-1);z-index:1}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
  tr:hover td{background:var(--surface-2)}
  .metric-tbl td,.metric-tbl th{text-align:right}.metric-tbl td:first-child,.metric-tbl th:first-child{text-align:left;color:var(--text-secondary);font-weight:600}
  .hiCol{background:var(--series-1-soft) !important;opacity:1}
  .parc{color:var(--text-muted)}
  .sentence{font-size:13.5px;margin:12px 0 2px;padding:10px 12px;background:var(--surface-2);border-radius:9px;line-height:1.7}
  .badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700;color:#fff;letter-spacing:.2px}
  .b-ALTA{background:var(--critical)}.b-MÉDIA{background:var(--serious)}.b-Positivo{background:var(--good)}.b-Monitorar{background:var(--neutral)}
  .b-Informativo{background:transparent;color:var(--info);border:1px solid var(--info)}
  .chip{display:inline-block;padding:2px 8px;border-radius:6px;font-size:11.5px;font-weight:650;margin:0 4px 4px 0;color:#fff}
  .det{font-size:11.5px;color:var(--text-secondary);margin-top:2px;line-height:1.5}
  .det .dline{display:flex;gap:6px;align-items:baseline}
  .dot{width:8px;height:8px;border-radius:50%;flex:none;position:relative;top:1px}
  .rec{font-size:12px;color:var(--text-secondary);max-width:300px;line-height:1.5}
  .rec.muted{color:var(--text-muted);font-style:italic}
  .cli{font-weight:650}.prog{font-variant-numeric:tabular-nums;font-size:12.5px;white-space:nowrap}
  .varbig{font-weight:750;font-size:13.5px}
  .scroll{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:10px}
  .scroll table th{background:var(--surface-1)}
  .prio-legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;margin-bottom:10px}
  .prio-legend span{display:inline-flex;align-items:center;gap:6px;color:var(--text-secondary)}
  details summary{cursor:pointer;font-weight:650;font-size:15px;padding:2px 0;list-style:none}
  details summary::-webkit-details-marker{display:none}
  .fgrp td{border-bottom:1px solid var(--line)}.fgrp td:first-child{font-weight:650}
  .fsub td{color:var(--text-secondary);border-bottom:1px dashed var(--line)}
  .chart-svg{width:100%;height:auto;display:block;overflow:visible}
  .axis text{fill:var(--text-muted);font-size:11px}.grid line{stroke:var(--line);stroke-width:1}
  .foot{color:var(--text-muted);font-size:12px;margin-top:24px;line-height:1.6}
  .tip{position:fixed;pointer-events:none;background:var(--text-primary);color:var(--bg);font-size:12px;padding:6px 9px;border-radius:7px;opacity:0;transition:opacity .08s;z-index:20;white-space:nowrap;font-weight:600}
  .spark{display:block}
</style></head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand"><div class="logo">R</div>
      <div><h1>Refera — Painel de Receita e Indicadores</h1><div class="sub" id="subtitle"></div></div>
    </div>
    <button class="theme-btn" id="themeBtn">◐ Tema</button>
  </header>
  <div class="compare">
    <b>Comparar:</b>
    <select id="selA"></select><span class="arw">→</span><select id="selB"></select>
    <div class="quick" id="quick"></div>
    <div class="hint2" id="chint"></div>
  </div>
  <div class="tabs" id="tabs" role="tablist"></div>
  <div id="panel"></div>
  <div class="foot" id="foot"></div>
</div>
<div class="tip" id="tip"></div>
<script>
const DATA=__DATA_JSON__;
const PRODs=[["manutencao","Manutenção"],["desocupacao","Desocupação"]];
const MONTHS=DATA.manutencao.labels_short, MLAB=DATA.manutencao.labels, NM=MONTHS.length;
const LN_DROP=Math.log(0.90), LN_COLL=Math.log(0.45); // ofensor: etapa caiu >= ~10%
const PRI_COLOR={ALTA:"var(--critical)","MÉDIA":"var(--serious)",Positivo:"var(--good)",Monitorar:"var(--neutral)"};
const OFF_COLOR={"Demanda":"var(--o-demanda)","Conv. revisado":"var(--o-conv2)","Conv. realizado":"var(--o-conv2)","Conv. aprovado":"var(--o-aprov)","Conv. finalizado":"var(--o-fin)","Ticket médio (final.)":"var(--o-ticket)"};
const REC={
 "Demanda":"• Demanda em queda: CS deve entender a menor abertura de chamados (satisfação, engajamento do gestor, concorrência).",
 "Conv. revisado":"• Chamados entram mas não viram orçamento. Gargalo na revisão/orçamentação — SLA de orçamento e cobertura de prestadores.",
 "Conv. realizado":"• Chamados entram mas não viram orçamento. Gargalo na revisão/orçamentação — SLA de orçamento e cobertura de prestadores.",
 "Conv. aprovado":"• Orçamentos feitos mas não vendem. Revisar preço, proposta e follow-up comercial.",
 "Conv. finalizado":"• Sem ação (defasagem): as finalizações escorregaram para o mês seguinte. A receita e o ticket finalizado menores são consequência disso e tendem a normalizar — só para você saber o porquê da queda.",
 "Ticket médio (final.)":"• Volume ok, mas a receita por serviço finalizado caiu. Revisar mix de serviços e precificação.",
};
const fmt=n=>n==null?"—":Math.round(n).toLocaleString("pt-BR");
const brl=n=>"R$ "+(n==null?"—":Math.round(n).toLocaleString("pt-BR"));
const pct=v=>v==null?"—":(v>0?"+":"")+v.toLocaleString("pt-BR",{maximumFractionDigits:1})+"%";
const arrow=v=>v==null?"":(v>0?"▲":(v<0?"▼":"■"));
const cls=v=>v==null?"flat":(v>0?"up":(v<0?"down":"flat"));
const tip=document.getElementById("tip");
function showTip(h,x,y){tip.innerHTML=h;tip.style.opacity=1;tip.style.left=(x+12)+"px";tip.style.top=(y+12)+"px";}
function hideTip(){tip.style.opacity=0;}

let selA=NM>=2?NM-2:0, selB=NM-1;

function conv(cl,i){const ch=cl.ch[i]||0,rev=cl.rev[i]||0,apr=cl.apr[i]||0,fin=cl.fin[i]||0,rb=cl.rb[i]||0,cart=cl.cart[i]||0;
  return {ch,rev,apr,fin,rb,cart,gmv:(cl.gmv&&cl.gmv[i])||0,tkf:cl.tkf[i]||0,crev:ch?rev/ch:0,capr:rev?apr/rev:0,cfin:apr?fin/apr:0,ticket:fin?rb/fin:0,imp:cart?ch/cart:0};}
const fval=(c,k)=>k==="cfin"?Math.min(c[k],1.0):c[k];
const lc=(a,b)=>(a>0&&b>0)?Math.log(b/a):((a>0&&b<=0)?-5:null);
function detail(cl,key,idxs,stage2){
  const V=idxs.map(i=>conv(cl,i));
  if(key==="ch") return "Demanda: "+idxs.map((i,j)=>`${MONTHS[i]} ${Math.round(V[j].ch)}`+(V[j].cart?` (${(V[j].imp*100).toFixed(0)}%)`:"")).join(" → ");
  if(key==="tkf") return "Ticket médio (final.): "+idxs.map((i,j)=>`${MONTHS[i]} ${brl(V[j].tkf)}`).join(" → ");
  const lbl=key==="crev"?stage2:(key==="capr"?"Conv. aprovado":"Conv. finalizado");
  return `${lbl}: `+idxs.map((i,j)=>`${MONTHS[i]} ${(V[j][key]*100).toFixed(0)}%`).join(" → ");
}
function analyzeProduct(prod,iA,iB){
  const stage2=prod.stage2; const idxs=[]; for(let i=iA;i<=iB;i++) idxs.push(i);
  const factors=[["Demanda","ch"],[stage2,"crev"],["Conv. aprovado","capr"],["Conv. finalizado","cfin"],["Ticket médio (final.)","tkf"]];
  const clients=prod.clients.map(cl=>{
    const c0=conv(cl,iA), c2=conv(cl,iB);
    const dem_lc=lc(fval(c0,"ch"),fval(c2,"ch")), rev_lc=lc(c0.rb,c2.rb);
    const dem_off=dem_lc!==null&&dem_lc<=LN_DROP, allow=dem_off||(rev_lc!==null&&rev_lc<=LN_DROP);
    let drops=[];
    for(const [label,key] of factors){
      if(key==="ch"){ if(dem_off) drops.push([label,key,dem_lc]); continue; }
      if(!allow) continue;
      if(key==="tkf"&&(c0.fin<3||c2.fin<3)) continue;
      const l=lc(fval(c0,key),fval(c2,key));
      if(l!==null&&l<=LN_DROP) drops.push([label,key,l]);
    }
    if(dem_lc!==null&&dem_lc<=LN_COLL&&drops.some(t=>t[1]==="ch")) drops=drops.filter(t=>t[1]==="ch");
    let no_action=false;
    const upstream=drops.filter(t=>["ch","crev","capr"].includes(t[1]));
    const cfin_in=drops.some(t=>t[1]==="cfin");
    if(upstream.length===0){
      if(cfin_in && rev_lc!==null && rev_lc<0){
        // nada caiu a montante (demanda/orçamento/venda ok) e a finalização escorregou:
        // DEFASAGEM -> informativo. O ticket finalizado menor é consequência da baixa finalização.
        drops=drops.filter(t=>t[1]==="cfin"); no_action=true;
      } else {
        drops=drops.filter(t=>t[1]!=="cfin"); // finalização ok: mantém o resto (ex.: ticket que caiu de fato)
      }
    } else {
      drops=drops.filter(t=>t[1]!=="cfin");    // problema real a montante: conv. finalizado é ruído
    }
    if(!drops.length&&rev_lc!==null&&rev_lc<=LN_DROP){
      let cand=factors.filter(([lb,k])=>k!=="cfin").map(([lb,k])=>[lb,k,lc(fval(c0,k),fval(c2,k))]).filter(t=>t[2]!==null&&t[2]<0);
      if(cand.length){cand.sort((a,b)=>a[2]-b[2]);drops=[cand[0]];}
    }
    drops.sort((a,b)=>a[2]-b[2]);
    const offenders=drops.map(([lb,k])=>({label:lb,detalhe:detail(cl,k,idxs,stage2)}));
    const recs=[]; drops.forEach(([lb])=>{if(REC[lb]&&!recs.includes(REC[lb]))recs.push(REC[lb]);});
    const rbA=cl.rb[iA]||0,rbB=cl.rb[iB]||0,chA=cl.ch[iA]||0,chB=cl.ch[iB]||0;
    const var_rb=rbA?(rbB-rbA)/rbA*100:null, var_ch=chA?(chB-chA)/chA*100:null;
    let scale=0; for(let i=iA;i<=iB;i++) scale=Math.max(scale,cl.rb[i]||0);
    const peakAll=Math.max(...cl.rb,1), has=offenders.length>0;
    const growing=!has&&rbB>=rbA&&rbB>=0.85*peakAll&&rbB>=800;
    let pri; if(no_action) pri=scale>=800?"Informativo":"Monitorar";
    else if(has&&scale>=4000) pri="ALTA"; else if(has&&scale>=800) pri="MÉDIA";
    else if(growing) pri="Positivo"; else pri="Monitorar";
    return {cliente:cl.cliente,pri,no_action,offenders,offenders_lbl:offenders.map(o=>o.label),recs,
      rbA,rbB,chA,chB,var_rb,var_ch,scale,rbSeries:cl.rb,raw:cl,
      ch_win:idxs.map(i=>cl.ch[i]||0), imp_win:idxs.map(i=>{const c=cl.cart[i]||0;return c?(cl.ch[i]||0)/c*100:0;})};
  });
  const ord={ALTA:0,"MÉDIA":1,Informativo:2,Positivo:3,Monitorar:4};
  clients.sort((a,b)=>ord[a.pri]-ord[b.pri]||b.rbB-a.rbB);
  const pri_counts={ALTA:0,"MÉDIA":0,Informativo:0,Positivo:0,Monitorar:0}; clients.forEach(c=>pri_counts[c.pri]++);
  const receita=[],chamados=[],ativas=[];
  for(let i=0;i<NM;i++){let r=0,ch=0,a=0;prod.clients.forEach(cl=>{r+=cl.rb[i]||0;ch+=cl.ch[i]||0;if((cl.ch[i]||0)||(cl.rb[i]||0))a++;});receita.push(r);chamados.push(ch);ativas.push(a);}
  const movers=clients.filter(c=>Math.max(c.rbA,c.rbB)>=300&&c.var_rb!==null);
  const ofens=movers.filter(c=>c.rbB<c.rbA).sort((a,b)=>(a.rbB-a.rbA)-(b.rbB-b.rbA)).slice(0,8);
  const evol=movers.filter(c=>c.rbB>c.rbA).sort((a,b)=>(b.rbB-b.rbA)-(a.rbB-a.rbA)).slice(0,8);
  return {clients,pri_counts,receita,chamados,ativas,ofens,evol,idxs};
}

function lineChart(labels,values,opts){opts=opts||{};const money=opts.money,color=opts.color||"var(--series-1)",soft=opts.soft||"var(--series-1-soft)",hi=opts.hi||[];
  const W=560,H=210,pad={l:52,r:16,t:16,b:24},iw=W-pad.l-pad.r,ih=H-pad.t-pad.b;
  const max=Math.max(...values,1),min=Math.min(...values,0),nx=labels.length;
  const X=i=>pad.l+(nx<=1?iw/2:iw*i/(nx-1)),Y=v=>pad.t+ih-ih*(v-min)/((max-min)||1);
  let grid="",axis="";
  for(let t=0;t<=4;t++){const val=min+(max-min)*t/4,y=Y(val);grid+=`<line x1="${pad.l}" y1="${y}" x2="${W-pad.r}" y2="${y}"/>`;
    axis+=`<text x="${pad.l-8}" y="${y+4}" text-anchor="end">${money?(val/1000).toLocaleString("pt-BR",{maximumFractionDigits:0})+"k":fmt(val)}</text>`;}
  let xlab="";labels.forEach((l,i)=>{const on=hi.includes(i);xlab+=`<text x="${X(i)}" y="${H-6}" text-anchor="middle" ${on?`fill="${color}" font-weight="700"`:''}>${l}</text>`;});
  let guides="";hi.forEach(i=>{guides+=`<line x1="${X(i)}" y1="${pad.t}" x2="${X(i)}" y2="${pad.t+ih}" stroke="${color}" stroke-width="1" stroke-dasharray="3 3" opacity=".5"/>`;});
  const line=values.map((v,i)=>`${i?'L':'M'} ${X(i)} ${Y(v)}`).join(" ");
  const area=`M ${X(0)} ${Y(min)} `+values.map((v,i)=>`L ${X(i)} ${Y(v)}`).join(" ")+` L ${X(nx-1)} ${Y(min)} Z`;
  let dots="";values.forEach((v,i)=>{const on=hi.includes(i);dots+=`<circle cx="${X(i)}" cy="${Y(v)}" r="${on?5.5:4}" fill="${on?color:'var(--surface-1)'}" stroke="${color}" stroke-width="2" data-i="${i}" data-v="${v}" class="pt"/>`;});
  return `<svg class="chart-svg" viewBox="0 0 ${W} ${H}"><g class="grid">${grid}</g>${guides}<g class="axis">${axis}${xlab}</g>
    <path d="${area}" fill="${soft}" opacity=".45"/><path d="${line}" fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>${dots}</svg>`;}
function spark(vals,dir){const W=92,H=24,p=3;const max=Math.max(...vals,1),min=Math.min(...vals,0);
  const X=i=>p+(W-2*p)*i/((vals.length-1)||1),Y=v=>p+(H-2*p)-(H-2*p)*(v-min)/((max-min)||1);
  const line=vals.map((v,i)=>`${i?'L':'M'} ${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ");
  const col=dir==null?"var(--neutral)":(dir<0?"var(--critical)":"var(--good)"),last=vals[vals.length-1];
  return `<svg class="spark" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><path d="${line}" fill="none" stroke="${col}" stroke-width="1.7" stroke-linejoin="round"/><circle cx="${X(vals.length-1).toFixed(1)}" cy="${Y(last).toFixed(1)}" r="2.3" fill="${col}"/></svg>`;}
function kpi(label,val,delta,sub){let d="";if(delta!=null)d=`<div class="delta ${cls(delta)}">${arrow(delta)} ${pct(delta)} <span style="color:var(--text-muted);font-weight:500">vs ${sub}</span></div>`;
  return `<div class="kpi"><div class="label">${label}</div><div class="val">${val}</div>${d}</div>`;}
function moversTable(title,arr,A,B){
  if(!arr.length) return `<div><div class="hint" style="font-weight:700;color:var(--text-secondary);margin-bottom:6px">${title}</div><div class="hint">—</div></div>`;
  const rows=arr.map(m=>{const dA=m.rbB-m.rbA;return `<tr><td class="cli">${m.cliente}</td><td class="num">${brl(m.rbA)}</td><td class="num">${brl(m.rbB)}</td>
    <td class="num ${cls(dA)}">${(dA>0?"+":"")+fmt(dA)}</td><td class="num ${cls(dA)}">${pct(m.var_rb)}</td></tr>`;}).join("");
  return `<div><div class="hint" style="font-weight:700;color:var(--text-secondary);margin-bottom:6px">${title}</div>
    <table><thead><tr><th>Cliente</th><th class="num">Rec ${A}</th><th class="num">Rec ${B}</th><th class="num">Δ R$</th><th class="num">Δ%</th></tr></thead><tbody>${rows}</tbody></table></div>`;}

function render(key){
  const prod=DATA[key];
  const iA=Math.min(selA,prod.labels_short.length-1), iB=Math.min(selB,prod.labels_short.length-1);
  const A=MONTHS[iA],B=MONTHS[iB],res=analyzeProduct(prod,iA,iB);
  const L=prod.labels_short,rev=res.receita,ch=res.chamados,pcnt=res.pri_counts;
  const revV=rev[iA]?(rev[iB]-rev[iA])/rev[iA]*100:null, chV=ch[iA]?(ch[iB]-ch[iA])/ch[iA]*100:null;
  // tabs pill counts
  document.querySelectorAll(".tab").forEach((t,ix)=>{const a=analyzeProduct(DATA[PRODs[ix][0]],iA,iB).pri_counts.ALTA;
    t.querySelector(".pill").textContent=a+" alta"; t.querySelector(".pill").style.cssText=a?"background:var(--critical);color:#fff":"";});

  const kpis=`<div class="kpis">
    ${kpi("Receita bruta — "+B,brl(rev[iB]),revV,A)}
    ${kpi("Chamados — "+B+" · engajamento",fmt(ch[iB]),chV,A)}
    ${kpi("Imobiliárias ativas — "+B,fmt(res.ativas[iB]),null)}
    ${kpi("Clientes prioridade ALTA",pcnt.ALTA,null)}</div>`;

  const idxs=res.idxs;
  const mhead=idxs.map(i=>`<th class="num ${(i===iA||i===iB)?'hiCol':''}">${L[i]}</th>`).join("");
  const rrow=idxs.map(i=>`<td class="num ${(i===iA||i===iB)?'hiCol':''}">${fmt(rev[i])}</td>`).join("");
  const crow=idxs.map(i=>`<td class="num ${(i===iA||i===iB)?'hiCol':''}">${fmt(ch[i])}</td>`).join("");
  const sentence=`<div class="sentence"><b>Receita</b> ${A}→${B}: ${brl(rev[iA])} → ${brl(rev[iB])} <span class="${cls(revV)}">${arrow(revV)} ${pct(revV)}</span>
     &nbsp;·&nbsp; <b>Chamados</b> (engajamento) ${A}→${B}: ${fmt(ch[iA])} → ${fmt(ch[iB])} <span class="${cls(chV)}">${arrow(chV)} ${pct(chV)}</span></div>`;
  const visao=`<div class="card"><h2>Visão geral da carteira</h2><p class="hint">Soma de todos os clientes por mês (${L[iA]}…${L[iB]}). Colunas destacadas = meses comparados.</p>
    <table class="metric-tbl"><thead><tr><th>Métrica</th>${mhead}</tr></thead>
      <tbody><tr><td>Receita bruta (R$)</td>${rrow}</tr><tr><td>Chamados (total)</td>${crow}</tr></tbody></table>${sentence}
    <div class="grid2" style="margin-top:14px">${moversTable("Principais ofensoras (maior queda de receita)",res.ofens,A,B)}${moversTable("Em evolução (maior ganho de receita)",res.evol,A,B)}</div></div>`;

  const charts=`<div class="grid2">
    <div class="card"><h2>Receita bruta por mês</h2><p class="hint">${L[0]}–${L[NM-1]} · destaque nos meses comparados (${A}, ${B}).</p><div id="lc-rev">${lineChart(L,rev,{money:true,hi:[iA,iB]})}</div></div>
    <div class="card"><h2>Chamados por mês <span style="color:var(--text-muted);font-weight:500">· engajamento</span></h2><p class="hint">Abertura de chamados — principal sinal de engajamento.</p><div id="lc-ch">${lineChart(L,ch,{money:false,color:"var(--series-2)",soft:"var(--series-2-soft)",hi:[iA,iB]})}</div></div></div>`;

  const act=res.clients.filter(c=>c.pri==="ALTA"||c.pri==="MÉDIA"||c.pri==="Informativo");
  const legend=`<div class="prio-legend">
    <span><i class="dot" style="background:var(--critical)"></i>ALTA ${pcnt.ALTA}</span><span><i class="dot" style="background:var(--serious)"></i>MÉDIA ${pcnt["MÉDIA"]}</span>
    <span><i class="dot" style="background:var(--info)"></i>Informativo ${pcnt.Informativo}</span><span><i class="dot" style="background:var(--good)"></i>Positivo ${pcnt.Positivo}</span><span><i class="dot" style="background:var(--neutral)"></i>Monitorar ${pcnt.Monitorar}</span></div>`;
  const winlab=idxs.map(i=>L[i]).join("→");
  const rows=act.map(c=>{
    const chips=c.offenders.map(o=>`<span class="chip" style="background:${OFF_COLOR[o.label]||'var(--neutral)'}">${o.label}</span>`).join("")||"—";
    const det=c.offenders.map(o=>`<div class="dline"><i class="dot" style="background:${OFF_COLOR[o.label]||'var(--neutral)'}"></i><span>${o.detalhe}</span></div>`).join("");
    const dR=c.rbB-c.rbA;
    return `<tr>
      <td class="cli">${c.cliente}</td>
      <td><span class="badge b-${c.pri}">${c.pri}</span></td>
      <td>${chips}<div class="det">${det}</div></td>
      <td class="num"><span class="prog">${brl(c.rbA)} → ${brl(c.rbB)}</span><br><span class="varbig ${cls(dR)}">${arrow(dR)} ${pct(c.var_rb)}</span> ${spark(c.rbSeries,c.var_rb)}</td>
      <td class="num"><span class="prog">${c.ch_win.map(fmt).join(" → ")}</span><br><span class="varbig ${cls(c.var_ch)}">${arrow(c.var_ch)} ${pct(c.var_ch)}</span><br><span class="parc" style="font-size:11px">pen. ${c.imp_win.map(x=>x.toLocaleString("pt-BR",{maximumFractionDigits:1})+"%").join(" → ")}</span></td>
      <td class="${c.no_action?'rec muted':'rec'}">${c.recs.join("<br>")}</td></tr>`;}).join("");
  const onde=`<div class="card"><h2>Onde atuar</h2>
    <p class="hint">Ofensores da receita por cliente na comparação ${A}→${B} (detalhado mês a mês: ${winlab}). "O que está caindo" pode ter vários indicadores. <b>Informativo</b> = queda por defasagem de finalização, sem ação.</p>${legend}
    <div class="scroll"><table><thead><tr><th>Cliente</th><th>Prior.</th><th>O que está caindo · detalhamento</th><th class="num">Receita ${A}→${B}</th><th class="num">Chamados (${winlab}) · engaj.</th><th>Recomendação</th></tr></thead>
      <tbody>${rows||`<tr><td colspan="6" class="parc">Nenhum cliente em queda relevante nesta comparação.</td></tr>`}</tbody></table></div></div>`;

  const fc=res.clients.filter(c=>c.rbSeries.some(x=>x>0)||c.raw.ch.some(x=>x>0));
  const frows=fc.map(c=>idxs.map((i,j)=>{const f=conv(c.raw,i);
    return `<tr class="${j===0?'fgrp':'fsub'}"><td>${j===0?c.cliente:""}</td><td class="${(i===iA||i===iB)?'hiCol':''}">${L[i]}</td>
      <td class="num">${fmt(f.cart)}</td><td class="num">${fmt(f.ch)}</td><td class="num">${(f.imp*100).toLocaleString("pt-BR",{maximumFractionDigits:1})}%</td>
      <td class="num">${fmt(f.rev)}</td><td class="num">${(f.crev*100).toFixed(0)}%</td><td class="num">${fmt(f.apr)}</td><td class="num">${(f.capr*100).toFixed(0)}%</td>
      <td class="num">${fmt(f.fin)}</td><td class="num">${(f.cfin*100).toFixed(0)}%</td><td class="num">${brl(f.tkf)}</td><td class="num">${brl(f.gmv)}</td><td class="num" style="font-weight:650">${brl(f.rb)}</td></tr>`;}).join("")).join("");
  const funil=`<div class="card"><details><summary>Funil por cliente — números-chave por mês (${fc.length} clientes) ▾</summary>
    <p class="hint" style="margin-top:8px">Meses da comparação (${winlab}). Conv. finalizado pode passar de 100% (defasagem). Ticket = Tkm prestador finalizado.</p>
    <div class="scroll"><table><thead><tr><th>Cliente</th><th>Mês</th><th class="num">Carteira</th><th class="num">Chamados</th><th class="num">Impacto</th>
      <th class="num">${prod.stage2n}</th><th class="num">Conv.</th><th class="num">Aprov.</th><th class="num">Conv.</th><th class="num">Final.</th><th class="num">Conv.</th>
      <th class="num">Ticket (Tkm prest. final.)</th><th class="num">GMV vend.</th><th class="num">Receita</th></tr></thead><tbody>${frows}</tbody></table></div></details></div>`;

  document.getElementById("panel").innerHTML=kpis+visao+charts+onde+funil;
  document.getElementById("chint").textContent=`Comparando ${MLAB[iA]} → ${MLAB[iB]} · ${idxs.length} ${idxs.length>1?'meses':'mês'} na janela.`;
  wireHover();
}
function wireHover(){document.querySelectorAll("#lc-rev svg .pt,#lc-ch svg .pt").forEach(p=>{const svg=p.closest("svg"),money=svg.parentElement.id==="lc-rev";
  p.addEventListener("mousemove",e=>{const i=+p.dataset.i;showTip(`<b>${MLAB[i]}</b> · ${money?brl(+p.dataset.v):fmt(+p.dataset.v)+" chamados"}`,e.clientX,e.clientY);p.setAttribute("r","6");});
  p.addEventListener("mouseleave",()=>{hideTip();p.setAttribute("r","4");});});}
function cur(){return PRODs[[...document.querySelectorAll(".tab")].findIndex(t=>t.getAttribute("aria-selected")==="true")][0];}

// setup
document.getElementById("subtitle").textContent="Manutenção e Desocupação · dados até "+MLAB[NM-1];
document.getElementById("foot").innerHTML=
  "Funil: Carteira → Chamados <span class='parc'>(Impacto = penetração = chamados/carteira)</span> → Revisados/Realizados (orçamento) → Aprovados (venda) → Finalizados (execução) → Ticket médio finalizado (Tkm prestador finalizado) → Receita bruta.<br>"+
  "'O que está caindo' vem da decomposição da receita pelo funil entre os dois meses escolhidos; um cliente pode ter vários ofensores (toda etapa que caiu ≥~14%). Quando a demanda desaba, as conversões viram ruído e o ofensor é Demanda. "+
  "Conv. finalizado só é destacado quando é o único motivo e a receita caiu (informativo, sem ação).<br>Atualizado em "+(DATA.gerado_em||"—")+".";
const selAE=document.getElementById("selA"),selBE=document.getElementById("selB");
MLAB.forEach((l,i)=>{selAE.add(new Option(l,i));selBE.add(new Option(l,i));});
selAE.value=selA; selBE.value=selB;
function onSel(){let a=+selAE.value,b=+selBE.value; if(a>=b){ if(this===selAE){b=Math.min(a+1,NM-1); if(a>=b)a=Math.max(0,b-1);} else {a=Math.max(0,b-1);} }
  selA=a;selB=b;selAE.value=a;selBE.value=b;render(cur());}
selAE.onchange=onSel; selBE.onchange=onSel;
// atalhos
const quick=[["Mês a mês",()=>[NM-2,NM-1]],["Trimestre",()=>[Math.max(0,NM-4),NM-1]],["Ano todo",()=>[0,NM-1]]];
const qEl=document.getElementById("quick");
quick.forEach(([lab,fn])=>{const b=document.createElement("button");b.textContent=lab;b.onclick=()=>{const[a,z]=fn();selA=a;selB=z;selAE.value=a;selBE.value=z;render(cur());};qEl.appendChild(b);});

const tabsEl=document.getElementById("tabs");
PRODs.forEach(([k,name],i)=>{const b=document.createElement("button");b.className="tab";b.setAttribute("role","tab");b.setAttribute("aria-selected",i===0);
  b.innerHTML=name+`<span class="pill"></span>`;
  b.onclick=()=>{document.querySelectorAll(".tab").forEach(t=>t.setAttribute("aria-selected",false));b.setAttribute("aria-selected",true);render(k);};
  tabsEl.appendChild(b);});
document.getElementById("themeBtn").onclick=()=>{const r=document.documentElement;r.setAttribute("data-theme",r.getAttribute("data-theme")==="dark"?"light":"dark");render(cur());};
render("manutencao");
</script></body></html>"""
HTML = HTML.replace("__DATA_JSON__", DATA_JSON)
open(out,"w",encoding="utf-8").write(HTML)
print("WROTE",out,len(HTML),"bytes")
