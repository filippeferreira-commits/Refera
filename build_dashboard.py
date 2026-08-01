#!/usr/bin/env python3
"""Gera o dashboard HTML (self-contained) a partir do analise.json.
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
  :root{
    --bg:#f4f5f3;--surface-1:#fff;--surface-2:#f6f7f4;--line:#e6e7e3;
    --text-primary:#14140f;--text-secondary:#57564f;--text-muted:#8a897f;
    --series-1:#2a78d6;--series-1-soft:#cde2fb;--series-2:#eb6834;--series-2-soft:#fbe0d3;
    --good:#0ca30c;--critical:#d03b3b;--serious:#ec835a;--neutral:#9a998f;
    --navy:#1f3864;
    --o-demanda:#2a78d6;--o-conv2:#7a5cd0;--o-aprov:#0f9b6c;--o-fin:#9a998f;--o-ticket:#d2559a;
    --shadow:0 1px 2px rgba(0,0,0,.05),0 6px 20px rgba(20,20,15,.05);--radius:14px;
  }
  :root[data-theme="dark"]{
    --bg:#121211;--surface-1:#1c1c1a;--surface-2:#232320;--line:#33332e;
    --text-primary:#f4f4ef;--text-secondary:#c3c2b7;--text-muted:#8f8e83;
    --series-1:#3987e5;--series-1-soft:#1c3a5e;--series-2:#d95926;--series-2-soft:#4a2a1c;
    --good:#2bb52b;--critical:#e05a5a;--serious:#f0956b;--neutral:#7d7c72;--navy:#9bb4e0;
    --o-demanda:#5a9bea;--o-conv2:#a596ec;--o-aprov:#3bbd8c;--o-fin:#8f8e83;--o-ticket:#e07ab0;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 6px 22px rgba(0,0,0,.35);
  }
  *{box-sizing:border-box}html,body{margin:0}
  body{background:var(--bg);color:var(--text-primary);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.45}
  .wrap{max-width:1200px;margin:0 auto;padding:24px 18px 70px}
  header.top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap}
  .brand{display:flex;align-items:center;gap:12px}
  .logo{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--navy),var(--series-1));display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:18px}
  h1{font-size:20px;margin:0;letter-spacing:-.3px}
  .sub{color:var(--text-secondary);font-size:13px;margin-top:2px}
  .theme-btn{border:1px solid var(--line);background:var(--surface-1);color:var(--text-secondary);border-radius:9px;padding:7px 12px;font-size:13px;cursor:pointer}
  .note{background:var(--surface-2);border:1px solid var(--line);border-left:3px solid var(--series-1);border-radius:8px;padding:9px 12px;font-size:12.5px;color:var(--text-secondary);margin:16px 0 4px}
  .tabs{display:flex;gap:8px;margin:18px 0 16px;border-bottom:1px solid var(--line)}
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
  .parc{color:var(--text-muted)}
  .sentence{font-size:13.5px;margin:12px 0 2px;padding:10px 12px;background:var(--surface-2);border-radius:9px;line-height:1.7}
  .badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700;color:#fff;letter-spacing:.2px}
  .b-ALTA{background:var(--critical)}.b-MÉDIA{background:var(--serious)}.b-Positivo{background:var(--good)}.b-Monitorar{background:var(--neutral)}
  .chip{display:inline-block;padding:2px 8px;border-radius:6px;font-size:11.5px;font-weight:650;margin:0 4px 4px 0;color:#fff}
  .det{font-size:11.5px;color:var(--text-secondary);margin-top:2px;line-height:1.5}
  .det .dline{display:flex;gap:6px;align-items:baseline}
  .dot{width:8px;height:8px;border-radius:50%;flex:none;position:relative;top:1px}
  .rec{font-size:12px;color:var(--text-secondary);max-width:300px;line-height:1.5}
  .rec.muted{color:var(--text-muted);font-style:italic}
  .cli{font-weight:650}
  .prog{font-variant-numeric:tabular-nums;font-size:12.5px;white-space:nowrap}
  .varbig{font-weight:750;font-size:13.5px}
  .scroll{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:10px}
  .scroll table th{background:var(--surface-1)}
  .prio-legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;margin-bottom:10px}
  .prio-legend span{display:inline-flex;align-items:center;gap:6px;color:var(--text-secondary)}
  details summary{cursor:pointer;font-weight:650;font-size:15px;padding:2px 0;list-style:none}
  details summary::-webkit-details-marker{display:none}
  .fgrp td{border-bottom:1px solid var(--line)}
  .fgrp td:first-child{font-weight:650}
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
  <div class="note" id="parcnote"></div>
  <div class="tabs" id="tabs" role="tablist"></div>
  <div id="panel"></div>
  <div class="foot" id="foot"></div>
</div>
<div class="tip" id="tip"></div>
<script>
const DATA = __DATA_JSON__;
const PRODs = [["manutencao","Manutenção"],["desocupacao","Desocupação"]];
const PRI_COLOR={ALTA:"var(--critical)","MÉDIA":"var(--serious)",Positivo:"var(--good)",Monitorar:"var(--neutral)"};
const OFF_COLOR={"Demanda":"var(--o-demanda)","Conv. revisado":"var(--o-conv2)","Conv. realizado":"var(--o-conv2)","Conv. aprovado":"var(--o-aprov)","Conv. finalizado":"var(--o-fin)","Ticket médio":"var(--o-ticket)"};
const fmt=n=>n==null?"—":Math.round(n).toLocaleString("pt-BR");
const brl=n=>"R$ "+(n==null?"—":Math.round(n).toLocaleString("pt-BR"));
const pct=v=>v==null?"—":(v>0?"+":"")+v.toLocaleString("pt-BR",{maximumFractionDigits:1})+"%";
const arrow=v=>v==null?"":(v>0?"▲":(v<0?"▼":"■"));
const cls=v=>v==null?"flat":(v>0?"up":(v<0?"down":"flat"));
const tip=document.getElementById("tip");
function showTip(h,x,y){tip.innerHTML=h;tip.style.opacity=1;tip.style.left=(x+12)+"px";tip.style.top=(y+12)+"px";}
function hideTip(){tip.style.opacity=0;}

document.getElementById("subtitle").textContent="Manutenção e Desocupação · referência "+DATA.ref;
const anyd=DATA.manutencao;
document.getElementById("parcnote").innerHTML=
  "<b>"+anyd.partial_label+" é parcial</b> — as finalizações do mês ainda entram no mês seguinte (defasagem de execução), então os totais de "+anyd.partial_label+
  " podem subir. A análise de <i>onde atuar</i> e as variações comparam os <b>meses fechados</b> ("+anyd.win_labels.join("→")+"). "+
  "Conv. finalizado caindo só é destacado quando é o único motivo da queda — e, nesse caso, é informativo (defasagem), sem ação.";
document.getElementById("foot").innerHTML=
  "Funil: Carteira → Chamados <span class='parc'>(Impacto = penetração = chamados/carteira)</span> → "+
  "Revisados/Realizados (orçamento) → Aprovados (venda) → Finalizados (execução) → Ticket médio (receita/finalizado) → Receita bruta.<br>"+
  "'O que está caindo' vem da decomposição da receita pelo funil na janela de meses fechados; um cliente pode ter vários ofensores (toda etapa que caiu ≥~14%). "+
  "Quando a demanda desaba, as conversões viram ruído e o ofensor é Demanda.<br>Atualizado em "+(DATA.gerado_em||"—")+".";

const tabsEl=document.getElementById("tabs");
PRODs.forEach(([k,name],i)=>{
  const b=document.createElement("button");b.className="tab";b.setAttribute("role","tab");b.setAttribute("aria-selected",i===0);
  const a=DATA[k].pri_counts.ALTA||0;
  b.innerHTML=name+`<span class="pill" style="${a?'background:var(--critical);color:#fff':''}">${a} alta</span>`;
  b.onclick=()=>{document.querySelectorAll(".tab").forEach(t=>t.setAttribute("aria-selected",false));b.setAttribute("aria-selected",true);render(k);};
  tabsEl.appendChild(b);
});

function lineChart(labels,values,opts){
  opts=opts||{};const money=opts.money,partial=opts.partial,color=opts.color||"var(--series-1)",soft=opts.soft||"var(--series-1-soft)";
  const W=560,H=210,pad={l:52,r:16,t:14,b:24},iw=W-pad.l-pad.r,ih=H-pad.t-pad.b;
  const max=Math.max(...values,1),min=Math.min(...values,0),nx=labels.length;
  const X=i=>pad.l+(nx<=1?iw/2:iw*i/(nx-1)),Y=v=>pad.t+ih-ih*(v-min)/((max-min)||1);
  let grid="",axis="";
  for(let t=0;t<=4;t++){const val=min+(max-min)*t/4,y=Y(val);
    grid+=`<line x1="${pad.l}" y1="${y}" x2="${W-pad.r}" y2="${y}"/>`;
    axis+=`<text x="${pad.l-8}" y="${y+4}" text-anchor="end">${money?(val/1000).toLocaleString("pt-BR",{maximumFractionDigits:0})+"k":fmt(val)}</text>`;}
  let xlab="";labels.forEach((l,i)=>xlab+=`<text x="${X(i)}" y="${H-6}" text-anchor="middle">${l}${(partial&&i===nx-1)?"*":""}</text>`);
  const nseg = partial? nx-1 : nx;
  const solid=values.slice(0,nseg).map((v,i)=>`${i?'L':'M'} ${X(i)} ${Y(v)}`).join(" ");
  const area=`M ${X(0)} ${Y(min)} `+values.slice(0,nseg).map((v,i)=>`L ${X(i)} ${Y(v)}`).join(" ")+` L ${X(nseg-1)} ${Y(min)} Z`;
  let dash="";
  if(partial&&nx>=2) dash=`<path d="M ${X(nx-2)} ${Y(values[nx-2])} L ${X(nx-1)} ${Y(values[nx-1])}" fill="none" stroke="${color}" stroke-width="2.2" stroke-dasharray="4 3" opacity=".7"/>`;
  let dots="";values.forEach((v,i)=>{const par=partial&&i===nx-1;
    dots+=`<circle cx="${X(i)}" cy="${Y(v)}" r="4.3" fill="${par?'var(--surface-1)':color}" stroke="${color}" stroke-width="2" data-i="${i}" data-v="${v}" class="pt"/>`;});
  const lv=values[nx-1];const lbl=`<text x="${X(nx-1)}" y="${Y(lv)-11}" text-anchor="end" fill="${color}" font-weight="700" font-size="11.5">${money?brl(lv):fmt(lv)}${partial?"*":""}</text>`;
  return `<svg class="chart-svg" viewBox="0 0 ${W} ${H}"><g class="grid">${grid}</g><g class="axis">${axis}${xlab}</g>
    <path d="${area}" fill="${soft}" opacity=".5"/><path d="${solid}" fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>${dash}${dots}${lbl}</svg>`;
}
function spark(vals,dir){const W=92,H=24,p=3;const max=Math.max(...vals,1),min=Math.min(...vals,0);
  const X=i=>p+(W-2*p)*i/((vals.length-1)||1),Y=v=>p+(H-2*p)-(H-2*p)*(v-min)/((max-min)||1);
  const line=vals.map((v,i)=>`${i?'L':'M'} ${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ");
  const col=dir==null?"var(--neutral)":(dir<0?"var(--critical)":"var(--good)");const last=vals[vals.length-1];
  return `<svg class="spark" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><path d="${line}" fill="none" stroke="${col}" stroke-width="1.7" stroke-linejoin="round"/><circle cx="${X(vals.length-1).toFixed(1)}" cy="${Y(last).toFixed(1)}" r="2.3" fill="${col}"/></svg>`;}

function kpi(label,val,delta,sub){
  let d="";if(delta!=null){d=`<div class="delta ${cls(delta)}">${arrow(delta)} ${pct(delta)} <span style="color:var(--text-muted);font-weight:500">vs ${sub}</span></div>`;}
  return `<div class="kpi"><div class="label">${label}</div><div class="val">${val}</div>${d}</div>`;}

function moversTable(title,arr,d){
  if(!arr.length) return `<div><div class="hint" style="font-weight:700;color:var(--text-secondary);margin-bottom:6px">${title}</div><div class="hint">—</div></div>`;
  const rows=arr.map(m=>`<tr><td class="cli">${m.cliente}</td><td class="num">${brl(m.r_prev)}</td><td class="num">${brl(m.r_ref)}</td>
    <td class="num ${cls(m.dabs)}">${(m.dabs>0?"+":"")+fmt(m.dabs)}</td><td class="num ${cls(m.dabs)}">${pct(m.dpct)}</td></tr>`).join("");
  return `<div><div class="hint" style="font-weight:700;color:var(--text-secondary);margin-bottom:6px">${title}</div>
    <table><thead><tr><th>Cliente</th><th class="num">Rec ${d.prev_label}</th><th class="num">Rec ${d.ref_label}</th><th class="num">Δ R$</th><th class="num">Δ%</th></tr></thead><tbody>${rows}</tbody></table></div>`;}

function render(key){
  const d=DATA[key],L=d.labels,rev=d.receita,ch=d.chamados,n=L.length;
  const revV=n>=2&&rev[n-2]?Math.round((rev[n-1]-rev[n-2])/rev[n-2]*1000)/10:null;
  const chV=n>=2&&ch[n-2]?Math.round((ch[n-1]-ch[n-2])/ch[n-2]*1000)/10:null;
  const pcnt=d.pri_counts,ov=d.overview,plab=d.partial_label,prevlab=L[n-2];
  const kpis=`<div class="kpis">
    ${kpi("Receita bruta — "+plab+" (parcial)",brl(rev[n-1]),revV,prevlab)}
    ${kpi("Chamados — "+plab+" · engajamento",fmt(ch[n-1]),chV,prevlab)}
    ${kpi("Imobiliárias ativas — "+plab,fmt(d.ativas[n-1]),null)}
    ${kpi("Clientes prioridade ALTA",pcnt.ALTA,null)}</div>`;

  // Visão geral
  const mm=ov.metric_months,mp=ov.metric_parcial;
  const head=mm.map((m,i)=>`<th class="num">${m}${mp[i]?"*":""}</th>`).join("");
  const rrow=ov.receita_row.map(v=>`<td class="num">${fmt(v)}</td>`).join("");
  const crow=ov.chamados_row.map(v=>`<td class="num">${fmt(v)}</td>`).join("");
  const vr=ov.var_receita,vc=ov.var_chamados;
  const sentence=`<div class="sentence"><b>Receita</b> ${d.prev_label}→${d.ref_label}: ${brl(vr.a)} → ${brl(vr.b)} <span class="${cls(vr.pct)}">${arrow(vr.pct)} ${pct(vr.pct)}</span>
     &nbsp;·&nbsp; <b>Chamados</b> (engajamento) ${d.prev_label}→${d.ref_label}: ${fmt(vc.a)} → ${fmt(vc.b)} <span class="${cls(vc.pct)}">${arrow(vc.pct)} ${pct(vc.pct)}</span></div>`;
  const visao=`<div class="card"><h2>Visão geral da carteira</h2><p class="hint">Soma de todos os clientes por mês. ${plab}* é parcial. Variações comparam os dois últimos meses fechados.</p>
    <table class="metric-tbl"><thead><tr><th>Métrica</th>${head}</tr></thead>
      <tbody><tr><td>Receita bruta (R$)</td>${rrow}</tr><tr><td>Chamados (total)</td>${crow}</tr></tbody></table>
    ${sentence}
    <div class="grid2" style="margin-top:14px">${moversTable("Principais ofensoras (maior queda de receita)",ov.ofensoras,d)}${moversTable("Em evolução (maior ganho de receita)",ov.evolucao,d)}</div></div>`;

  // charts
  const charts=`<div class="grid2">
    <div class="card"><h2>Receita bruta por mês</h2><p class="hint">${L[0]}–${plab} · ${plab}* parcial.</p><div id="lc-rev">${lineChart(L,rev,{money:true,partial:true})}</div></div>
    <div class="card"><h2>Chamados por mês <span style="color:var(--text-muted);font-weight:500">· engajamento</span></h2><p class="hint">Abertura de chamados — principal sinal de engajamento.</p><div id="lc-ch">${lineChart(L,ch,{money:false,partial:true,color:"var(--series-2)",soft:"var(--series-2-soft)"})}</div></div></div>`;

  // Onde atuar
  const act=d.clients.filter(c=>c.pri==="ALTA"||c.pri==="MÉDIA");
  const legend=`<div class="prio-legend">
    <span><i class="dot" style="background:var(--critical)"></i>ALTA ${pcnt.ALTA}</span>
    <span><i class="dot" style="background:var(--serious)"></i>MÉDIA ${pcnt["MÉDIA"]}</span>
    <span><i class="dot" style="background:var(--good)"></i>Positivo ${pcnt.Positivo}</span>
    <span><i class="dot" style="background:var(--neutral)"></i>Monitorar ${pcnt.Monitorar}</span></div>`;
  const rows=act.map(c=>{
    const chips=c.offenders.map(o=>`<span class="chip" style="background:${OFF_COLOR[o.label]||'var(--neutral)'}">${o.label}</span>`).join("")||"—";
    const det=c.offenders.map(o=>`<div class="dline"><i class="dot" style="background:${OFF_COLOR[o.label]||'var(--neutral)'}"></i><span>${o.detalhe}</span></div>`).join("");
    const dR=c.receita_ref-c.receita_prev;
    const recCls=c.no_action?"rec muted":"rec";
    return `<tr>
      <td class="cli">${c.cliente}${c.no_action?' <span class="parc" style="font-weight:500">(informativo)</span>':''}</td>
      <td><span class="badge b-${c.pri}">${c.pri}</span></td>
      <td>${chips}<div class="det">${det}</div></td>
      <td class="num"><span class="prog">${brl(c.receita_prev)} → ${brl(c.receita_ref)}</span><br><span class="varbig ${cls(dR)}">${arrow(dR)} ${pct(c.var_rb)}</span> ${spark(c.rb,c.var_rb)}</td>
      <td class="num"><span class="prog">${c.ch3.join(" → ")}</span><br><span class="varbig ${cls(c.var_ch)}">${arrow(c.var_ch)} ${pct(c.var_ch)}</span><br><span class="parc" style="font-size:11px">pen. ${c.imp3.map(x=>x.toLocaleString("pt-BR")+"%").join(" → ")}</span></td>
      <td class="${recCls}">${c.recs.join("<br>")}</td></tr>`;}).join("");
  const onde=`<div class="card"><h2>Onde atuar — prioridade ALTA e MÉDIA</h2>
    <p class="hint">Ofensores da receita por cliente (janela ${d.win_labels.join("→")}). "O que está caindo" pode ter vários indicadores; o Detalhamento mostra cada um mês a mês.</p>${legend}
    <div class="scroll"><table><thead><tr><th>Cliente</th><th>Prior.</th><th>O que está caindo · detalhamento</th><th class="num">Receita ${d.prev_label}→${d.ref_label}</th><th class="num">Chamados (${d.win_labels.join("→")}) · engaj.</th><th>Recomendação</th></tr></thead>
      <tbody>${rows||`<tr><td colspan="6" class="parc">Nenhum cliente em queda relevante.</td></tr>`}</tbody></table></div></div>`;

  // Funil por cliente
  const fc=d.clients.filter(c=>c.rb.some(x=>x>0)||c.ch.some(x=>x>0));
  const frows=fc.map(c=>c.funil.map((f,i)=>`<tr class="${i===0?'fgrp':'fsub'}">
      <td>${i===0?c.cliente:""}</td><td>${f.mes}${f.parcial?"*":""}</td><td class="num">${fmt(f.cart)}</td><td class="num">${fmt(f.ch)}</td>
      <td class="num">${f.imp.toLocaleString("pt-BR")}%</td><td class="num">${fmt(f.rev)}</td><td class="num">${f.crev}%</td>
      <td class="num">${fmt(f.apr)}</td><td class="num">${f.capr}%</td><td class="num">${fmt(f.fin)}</td><td class="num">${f.cfin}%</td>
      <td class="num">${brl(f.tkf)}</td><td class="num">${brl(f.ticket)}</td><td class="num" style="font-weight:650">${brl(f.rb)}</td></tr>`).join("")).join("");
  const funil=`<div class="card"><details><summary>Funil por cliente — números-chave por mês (${fc.length} clientes) ▾</summary>
    <p class="hint" style="margin-top:8px">Últimos 4 meses por cliente. ${plab}* parcial. Conv. finalizado pode passar de 100% (defasagem). Ticket médio = receita/finalizados.</p>
    <div class="scroll"><table><thead><tr><th>Cliente</th><th>Mês</th><th class="num">Carteira</th><th class="num">Chamados</th><th class="num">Impacto</th>
      <th class="num">${d.stage2n}</th><th class="num">Conv.</th><th class="num">Aprov.</th><th class="num">Conv.</th><th class="num">Final.</th><th class="num">Conv.</th>
      <th class="num">Tkm prest.</th><th class="num">Ticket</th><th class="num">Receita</th></tr></thead><tbody>${frows}</tbody></table></div></details></div>`;

  document.getElementById("panel").innerHTML=kpis+visao+charts+onde+funil;
  wireHover();
}
function wireHover(){
  document.querySelectorAll("#lc-rev svg .pt,#lc-ch svg .pt").forEach(p=>{
    const svg=p.closest("svg"),money=svg.parentElement.id==="lc-rev";
    p.addEventListener("mousemove",e=>{const i=+p.dataset.i;const lab=DATA[cur()].labels[i];
      showTip(`<b>${lab}</b> · ${money?brl(+p.dataset.v):fmt(+p.dataset.v)+" chamados"}`,e.clientX,e.clientY);p.setAttribute("r","6");});
    p.addEventListener("mouseleave",()=>{hideTip();p.setAttribute("r","4.3");});});
}
function cur(){return PRODs[[...document.querySelectorAll(".tab")].findIndex(t=>t.getAttribute("aria-selected")==="true")][0];}
document.getElementById("themeBtn").onclick=()=>{const r=document.documentElement;r.setAttribute("data-theme",r.getAttribute("data-theme")==="dark"?"light":"dark");render(cur());};
render("manutencao");
</script></body></html>"""
HTML = HTML.replace("__DATA_JSON__", DATA_JSON)
open(out,"w",encoding="utf-8").write(HTML)
print("WROTE",out,len(HTML),"bytes")
