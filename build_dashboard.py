#!/usr/bin/env python3
"""
Gera o dashboard HTML (self-contained) a partir do analise.json.
Uso: python build_dashboard.py analise.json dashboard.html "01/08/2026 08:26"
"""
import sys, json

inp = sys.argv[1] if len(sys.argv) > 1 else "analise.json"
out = sys.argv[2] if len(sys.argv) > 2 else "dashboard.html"
gerado = sys.argv[3] if len(sys.argv) > 3 else ""

data = json.load(open(inp))
data["gerado_em"] = gerado
DATA_JSON = json.dumps(data, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Refera — Painel de Receita e Indicadores</title>
<style>
  :root{
    --bg:#f4f5f3; --surface-1:#ffffff; --surface-2:#f7f8f6; --line:#e6e7e3;
    --text-primary:#14140f; --text-secondary:#57564f; --text-muted:#8a897f;
    --series-1:#2a78d6; --series-1-soft:#cde2fb;
    --good:#0ca30c; --warning:#e08a12; --serious:#ec835a; --critical:#d03b3b; --neutral:#9a998f;
    --navy:#1f3864;
    --shadow:0 1px 2px rgba(0,0,0,.05), 0 6px 20px rgba(20,20,15,.05);
    --radius:14px;
  }
  :root[data-theme="dark"]{
    --bg:#121211; --surface-1:#1c1c1a; --surface-2:#232320; --line:#33332e;
    --text-primary:#f4f4ef; --text-secondary:#c3c2b7; --text-muted:#8f8e83;
    --series-1:#3987e5; --series-1-soft:#1c3a5e;
    --good:#2bb52b; --warning:#f0a92a; --serious:#f0956b; --critical:#e05a5a; --neutral:#7d7c72;
    --navy:#9bb4e0;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 6px 22px rgba(0,0,0,.35);
  }
  *{box-sizing:border-box}
  html,body{margin:0}
  body{background:var(--bg); color:var(--text-primary);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased; line-height:1.45;}
  .wrap{max-width:1160px; margin:0 auto; padding:26px 20px 70px;}
  header.top{display:flex; align-items:flex-start; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-bottom:6px;}
  .brand{display:flex; align-items:center; gap:12px;}
  .logo{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--navy),var(--series-1));
    display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:18px;letter-spacing:-.5px;}
  h1{font-size:20px; margin:0; letter-spacing:-.3px;}
  .sub{color:var(--text-secondary); font-size:13px; margin-top:2px;}
  .theme-btn{border:1px solid var(--line); background:var(--surface-1); color:var(--text-secondary);
    border-radius:9px; padding:7px 12px; font-size:13px; cursor:pointer;}
  .theme-btn:hover{color:var(--text-primary)}
  .tabs{display:flex; gap:8px; margin:20px 0 18px; border-bottom:1px solid var(--line);}
  .tab{appearance:none;border:0;background:none;padding:10px 4px;margin-right:14px;font-size:15px;font-weight:600;
    color:var(--text-muted);cursor:pointer;border-bottom:2.5px solid transparent;transform:translateY(1px);}
  .tab[aria-selected="true"]{color:var(--text-primary);border-bottom-color:var(--series-1);}
  .tab .pill{display:inline-block;min-width:20px;padding:0 6px;margin-left:6px;border-radius:20px;font-size:12px;
    background:var(--surface-2);color:var(--text-secondary);font-weight:700;}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}
  .kpi{background:var(--surface-1);border:1px solid var(--line);border-radius:var(--radius);padding:16px 16px 14px;box-shadow:var(--shadow);}
  .kpi .label{font-size:12px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.4px;font-weight:600;}
  .kpi .val{font-size:26px;font-weight:750;letter-spacing:-.6px;margin-top:7px;font-variant-numeric:tabular-nums;}
  .kpi .delta{font-size:12.5px;margin-top:3px;font-weight:600;display:flex;align-items:center;gap:5px;}
  .up{color:var(--good)} .down{color:var(--critical)} .flat{color:var(--text-muted)}
  .card{background:var(--surface-1);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);
    padding:18px 18px 14px;margin-bottom:20px;}
  .card h2{font-size:15px;margin:0 0 2px;letter-spacing:-.2px;}
  .card .hint{font-size:12.5px;color:var(--text-muted);margin:0 0 12px;}
  .grid2{display:grid;grid-template-columns:1.5fr 1fr;gap:20px;}
  @media(max-width:820px){.grid2{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}}
  .chart-svg{width:100%;height:auto;display:block;overflow:visible;}
  .axis text{fill:var(--text-muted);font-size:11px;}
  .grid line{stroke:var(--line);stroke-width:1;}
  .prio-legend{display:flex;flex-direction:column;gap:10px;justify-content:center;height:100%;}
  .prio-row{display:flex;align-items:center;gap:10px;font-size:13.5px;}
  .prio-row .bar{height:16px;border-radius:5px;min-width:6px;}
  .prio-row .nm{width:88px;color:var(--text-secondary);font-weight:600;}
  .prio-row .ct{margin-left:auto;font-weight:700;font-variant-numeric:tabular-nums;}
  .dot{width:9px;height:9px;border-radius:50%;display:inline-block;flex:none;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:middle;}
  th{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:var(--text-muted);font-weight:700;
    position:sticky;top:0;background:var(--surface-1);}
  td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}
  tr:hover td{background:var(--surface-2);}
  .badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11.5px;font-weight:700;color:#fff;letter-spacing:.2px;}
  .b-ALTA{background:var(--critical)} .b-MÉDIA{background:var(--serious)}
  .b-Positivo{background:var(--good)} .b-Monitorar{background:var(--neutral)}
  .whats{font-weight:650;}
  .w-Demanda{color:#1f5fa5} .w-Conversão{color:#6d3ec8} .w-Ticket\ médio{color:#b5451b}
  :root[data-theme="dark"] .w-Demanda{color:#79aef0} :root[data-theme="dark"] .w-Conversão{color:#b6a3f0}
  :root[data-theme="dark"] .w-Ticket\ médio{color:#f0956b}
  .rec{color:var(--text-secondary);font-size:12.5px;max-width:340px;}
  .cli{font-weight:650;}
  .scroll{max-height:460px;overflow:auto;border:1px solid var(--line);border-radius:10px;}
  .scroll table th{background:var(--surface-1);}
  details.funil summary{cursor:pointer;font-weight:650;font-size:14px;padding:4px 0;color:var(--text-primary);}
  .foot{color:var(--text-muted);font-size:12px;margin-top:26px;line-height:1.6;}
  .spark{display:block}
  .tip{position:fixed;pointer-events:none;background:var(--text-primary);color:var(--bg);font-size:12px;
    padding:6px 9px;border-radius:7px;opacity:0;transition:opacity .08s;z-index:20;white-space:nowrap;font-weight:600;
    box-shadow:0 4px 14px rgba(0,0,0,.25);}
  .miss{color:var(--text-muted);}
  .seg{display:flex;height:9px;border-radius:5px;overflow:hidden;background:var(--surface-2);margin-top:3px;}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand">
      <div class="logo">R</div>
      <div>
        <h1>Refera — Painel de Receita e Indicadores</h1>
        <div class="sub" id="subtitle"></div>
      </div>
    </div>
    <button class="theme-btn" id="themeBtn">◐ Tema</button>
  </header>

  <div class="tabs" id="tabs" role="tablist"></div>
  <div id="panel"></div>

  <div class="foot" id="foot"></div>
</div>
<div class="tip" id="tip"></div>

<script>
const DATA = __DATA_JSON__;
const PROducts = [["manutencao","Manutenção"],["desocupacao","Desocupação"]];
const REC = {
  "Demanda":"Demanda caindo — CS deve entender a queda de abertura de chamados (satisfação, engajamento do gestor, concorrência).",
  "Conversão":"Perda no funil — chamados abrem mas não viram orçamento/venda/execução. Revisar SLA de orçamento e aprovação.",
  "Ticket médio":"Volume ok, valor por serviço caiu. Revisar mix de serviços e precificação.",
  "—":"Acompanhar mensalmente."
};
const PRI_COLOR = {ALTA:"var(--critical)","MÉDIA":"var(--serious)",Positivo:"var(--good)",Monitorar:"var(--neutral)"};
const fmt = n => (n==null?"—":n.toLocaleString("pt-BR"));
const brl = n => "R$ "+ (n==null?"—":Math.round(n).toLocaleString("pt-BR"));
const pctTxt = v => v==null?"—":(v>0?"+":"")+v.toLocaleString("pt-BR",{maximumFractionDigits:1})+"%";
const tip = document.getElementById("tip");
function showTip(html,x,y){tip.innerHTML=html;tip.style.opacity=1;tip.style.left=(x+12)+"px";tip.style.top=(y+12)+"px";}
function hideTip(){tip.style.opacity=0;}

document.getElementById("subtitle").textContent =
  "Mês de referência: "+DATA.ref+"  ·  Manutenção e Desocupação";
document.getElementById("foot").innerHTML =
  "Funil: Carteira → Chamados <span class='miss'>(Impacto = penetração)</span> → Revisados/Realizados (orçamento) → "+
  "Aprovados (venda) → Finalizados (execução) → Ticket médio → Receita bruta.<br>"+
  "O mês corrente (incompleto) é descartado; a queda é medida pela tendência dos últimos meses, não por um pico isolado. "+
  "Conv. finalizados pode passar de 100% (execução de chamados de meses anteriores — defasagem).<br>"+
  "Atualizado em "+ (DATA.gerado_em||"—") +".";

// ---------- tabs
const tabsEl = document.getElementById("tabs");
PROducts.forEach(([k,name],i)=>{
  const b=document.createElement("button");
  b.className="tab"; b.setAttribute("role","tab"); b.setAttribute("aria-selected", i===0);
  const alta = DATA[k].pri_counts.ALTA||0;
  b.innerHTML = name + `<span class="pill" style="${alta?'background:var(--critical);color:#fff':''}">${alta} alta</span>`;
  b.onclick=()=>{document.querySelectorAll(".tab").forEach(t=>t.setAttribute("aria-selected",false));
    b.setAttribute("aria-selected",true); render(k);};
  tabsEl.appendChild(b);
});

// ---------- line chart (single series, receita por mês)
function lineChart(labels, values){
  const W=680,H=230, pad={l:52,r:18,t:16,b:26};
  const iw=W-pad.l-pad.r, ih=H-pad.t-pad.b;
  const max=Math.max(...values,1), min=Math.min(...values,0);
  const nx=labels.length;
  const X=i=> pad.l + (nx<=1?iw/2: iw*i/(nx-1));
  const Y=v=> pad.t + ih - ih*(v-min)/((max-min)||1);
  const ticks=4;
  let grid="",axis="";
  for(let t=0;t<=ticks;t++){
    const val=min+(max-min)*t/ticks, y=Y(val);
    grid+=`<line x1="${pad.l}" y1="${y}" x2="${W-pad.r}" y2="${y}"/>`;
    axis+=`<text x="${pad.l-8}" y="${y+4}" text-anchor="end">${(val/1000).toLocaleString("pt-BR",{maximumFractionDigits:0})}k</text>`;
  }
  let xlab="";
  labels.forEach((l,i)=> xlab+=`<text x="${X(i)}" y="${H-6}" text-anchor="middle">${l}</text>`);
  const area=`M ${X(0)} ${Y(min)} `+values.map((v,i)=>`L ${X(i)} ${Y(v)}`).join(" ")+` L ${X(nx-1)} ${Y(min)} Z`;
  const line=values.map((v,i)=>`${i?'L':'M'} ${X(i)} ${Y(v)}`).join(" ");
  let dots="";
  values.forEach((v,i)=>{dots+=`<circle cx="${X(i)}" cy="${Y(v)}" r="4.5" fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2"
     data-i="${i}" data-v="${v}" data-l="${labels[i]}" class="pt"/>`;});
  // last point label
  const lv=values[nx-1];
  const lbl=`<text x="${X(nx-1)}" y="${Y(lv)-12}" text-anchor="end" fill="var(--series-1)" font-weight="700" font-size="12">${brl(lv)}</text>`;
  return `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" role="img">
    <g class="grid">${grid}</g><g class="axis">${axis}${xlab}</g>
    <path d="${area}" fill="var(--series-1-soft)" opacity=".45"/>
    <path d="${line}" fill="none" stroke="var(--series-1)" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
    ${dots}${lbl}
    <rect x="0" y="0" width="${W}" height="${H}" fill="transparent" id="lc-hit"></rect>
  </svg>`;
}

// ---------- sparkline
function spark(values, dir){
  const W=104,H=26,p=3;
  const max=Math.max(...values,1),min=Math.min(...values,0);
  const X=i=>p+(W-2*p)*i/((values.length-1)||1);
  const Y=v=>p+(H-2*p)-(H-2*p)*(v-min)/((max-min)||1);
  const line=values.map((v,i)=>`${i?'L':'M'} ${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ");
  const last=values[values.length-1];
  const col = dir==null ? "var(--neutral)" : (dir<0 ? "var(--critical)":"var(--good)");
  return `<svg class="spark" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <path d="${line}" fill="none" stroke="${col}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="${X(values.length-1).toFixed(1)}" cy="${Y(last).toFixed(1)}" r="2.4" fill="${col}"/></svg>`;
}

function kpi(label,val,delta){
  let d="";
  if(delta!=null){const cls=delta>0?"up":(delta<0?"down":"flat");const ar=delta>0?"▲":(delta<0?"▼":"■");
    d=`<div class="delta ${cls}">${ar} ${pctTxt(delta)}<span style="color:var(--text-muted);font-weight:500"> vs mês ant.</span></div>`;}
  return `<div class="kpi"><div class="label">${label}</div><div class="val">${val}</div>${d}</div>`;
}

function render(key){
  const d=DATA[key];
  const L=d.labels, rev=d.receita, cham=d.chamados;
  const n=L.length;
  const revVar = n>=2 && rev[n-2] ? Math.round((rev[n-1]-rev[n-2])/rev[n-2]*1000)/10 : null;
  const chVar = n>=2 && cham[n-2] ? Math.round((cham[n-1]-cham[n-2])/cham[n-2]*1000)/10 : null;
  const ativas = d.ativas[n-1];
  const pc=d.pri_counts;
  const totalPri = pc.ALTA+pc["MÉDIA"]+pc.Positivo+pc.Monitorar;
  const maxPri = Math.max(pc.ALTA,pc["MÉDIA"],pc.Positivo,pc.Monitorar,1);

  const kpis = `<div class="kpis">
    ${kpi("Receita bruta ("+d.ref_label+")", brl(rev[n-1]), revVar)}
    ${kpi("Chamados ("+d.ref_label+")", fmt(cham[n-1]), chVar)}
    ${kpi("Imobiliárias ativas", fmt(ativas), null)}
    ${kpi("Clientes prioridade ALTA", pc.ALTA, null)}
  </div>`;

  const prioLegend = ["ALTA","MÉDIA","Positivo","Monitorar"].map(k=>{
    const w = 100*(pc[k])/maxPri;
    return `<div class="prio-row"><span class="nm">${k}</span>
      <span class="bar" style="width:${Math.max(w, pc[k]?8:0)}%;background:${PRI_COLOR[k]}"></span>
      <span class="ct">${pc[k]}</span></div>`;
  }).join("");

  const charts = `<div class="grid2">
    <div class="card"><h2>Receita bruta por mês</h2><p class="hint">Total do produto, ${L[0]}–${L[n-1]}/${DATA.ref.split('/')[1]}.</p>
      <div id="lcbox">${lineChart(L,rev)}</div></div>
    <div class="card"><h2>Carteira por prioridade</h2><p class="hint">${totalPri} clientes ativos.</p>
      <div class="prio-legend">${prioLegend}</div></div>
  </div>`;

  // priorização (ALTA + MÉDIA)
  const act = d.clients.filter(c=>c.pri==="ALTA"||c.pri==="MÉDIA");
  const rowsAct = act.map(c=>`<tr>
     <td class="cli">${c.cliente}</td>
     <td><span class="badge b-${c.pri}">${c.pri}</span></td>
     <td class="whats w-${c.whats}">${c.whats}</td>
     <td class="num">${brl(c.receita_ref)}</td>
     <td class="num ${c.var_receita==null?'flat':(c.var_receita<0?'down':'up')}">${pctTxt(c.var_receita)}</td>
     <td>${spark(c.rb, c.var_receita)}</td>
     <td class="rec">${REC[c.whats]||""}</td></tr>`).join("");
  const prioCard = `<div class="card"><h2>Onde atuar — prioridade ALTA e MÉDIA</h2>
    <p class="hint">Clientes com queda de receita relevante, ordenados por prioridade e tamanho. "O que está caindo": demanda (chamados), conversão (funil) ou ticket médio.</p>
    <div class="scroll"><table><thead><tr>
      <th>Cliente</th><th>Prioridade</th><th>O que está caindo</th><th class="num">Receita ${d.ref_label}</th>
      <th class="num">Var.</th><th>Tendência</th><th>Recomendação</th></tr></thead>
      <tbody>${rowsAct||`<tr><td colspan="7" class="miss">Nenhum cliente em queda relevante neste mês.</td></tr>`}</tbody></table></div></div>`;

  // funil por cliente (todos ativos)
  const funilRows = d.clients.map(c=>{
    const i=n-1;
    return `<tr>
      <td class="cli">${c.cliente}</td>
      <td><span class="badge b-${c.pri}" style="font-size:10.5px">${c.pri}</span></td>
      <td class="num">${fmt(c.ch[i])}</td>
      <td class="num">${c.imp[i]?c.imp[i].toLocaleString("pt-BR",{maximumFractionDigits:1})+"%":"—"}</td>
      <td class="num">${fmt(c.rev[i])}</td>
      <td class="num">${fmt(c.apr[i])}</td>
      <td class="num">${fmt(c.fin[i])}</td>
      <td class="num">${c.cf[i]?c.cf[i]+"%":"—"}</td>
      <td class="num">${brl(c.tkf[i])}</td>
      <td class="num" style="font-weight:650">${brl(c.rb[i])}</td></tr>`;
  }).join("");
  const funilCard = `<div class="card"><details class="funil"><summary>Funil por cliente — ${d.ref_label} (${d.clients.length} clientes ativos) ▾</summary>
    <p class="hint" style="margin-top:10px">Etapas do funil no mês de referência. Impacto = chamados / carteira (penetração).</p>
    <div class="scroll"><table><thead><tr>
      <th>Cliente</th><th>Prior.</th><th class="num">Chamados</th><th class="num">Impacto</th>
      <th class="num">Revis./Realiz.</th><th class="num">Aprov.</th><th class="num">Finaliz.</th>
      <th class="num">Conv. fin.</th><th class="num">Ticket</th><th class="num">Receita</th></tr></thead>
      <tbody>${funilRows}</tbody></table></div></details></div>`;

  document.getElementById("panel").innerHTML = kpis + charts + prioCard + funilCard;
  wireLineHover(key);
}

function wireLineHover(key){
  const d=DATA[key], svg=document.querySelector("#lcbox svg");
  if(!svg) return;
  const pts=[...svg.querySelectorAll(".pt")];
  pts.forEach(p=>{
    p.addEventListener("mousemove",e=>{
      const i=+p.dataset.i;
      showTip(`<b>${d.labels[i]}</b> · ${brl(+p.dataset.v)}`, e.clientX, e.clientY);
      p.setAttribute("r","6.5");
    });
    p.addEventListener("mouseleave",()=>{hideTip();p.setAttribute("r","4.5");});
  });
}

// theme toggle
document.getElementById("themeBtn").onclick=()=>{
  const r=document.documentElement;
  r.setAttribute("data-theme", r.getAttribute("data-theme")==="dark"?"light":"dark");
  const k=document.querySelector('.tab[aria-selected="true"]');
  render(PROducts[[...document.querySelectorAll(".tab")].indexOf(k)][0]);
};

render("manutencao");
</script>
</body>
</html>"""

HTML = HTML.replace("__DATA_JSON__", DATA_JSON)
open(out, "w", encoding="utf-8").write(HTML)
print("WROTE", out, len(HTML), "bytes")
