#!/usr/bin/env python3
"""
Refera — Análise mensal por produto (Manutenção + Desocupação).

Reproduz a análise "onde a receita está caindo" com:
  - Visão geral: totais por mês (receita, chamados/engajamento), variação, ofensoras e em evolução;
  - Onde atuar: prioridade + DECOMPOSIÇÃO da receita pelo funil -> pode haver VÁRIOS ofensores
    (toda etapa que caiu >= ~14% na janela de meses fechados), com Detalhamento mês a mês
    e variação de receita e de chamados;
  - Funil por cliente: números-chave por cliente e mês.

Receita = Chamados × ConvRevisado × ConvAprovado × ConvFinalizado × Ticket
(cada fator sai dos números crus, então o produto reproduz a receita exatamente).

IMPORTANTE — defasagem de execução: o último mês ainda está "assentando" (finalizações do mês
continuam entrando no mês seguinte), então Conv. finalizado / Ticket dele vêm subestimados. Por
isso a detecção de queda usa os meses FECHADOS; o último mês aparece como PARCIAL.

Uso:
  python refera_analysis.py <manutencao.xlsx> <desocupacao.xlsx> <saida.json> [AAAA-MM-ref]
"""
import sys, os, json, math, re, datetime
from collections import defaultdict
import openpyxl

LN_DROP = math.log(0.86)      # queda >= ~14% => ofensor
LN_COLLAPSE = math.log(0.45)  # demanda caiu >= ~55% => conversões viram ruído (só "Demanda")

def _norm(s):
    s = str(s or "").strip().lower()
    for a,b in (("á","a"),("â","a"),("ã","a"),("é","e"),("ê","e"),("í","i"),
                ("ó","o"),("ô","o"),("õ","o"),("ú","u"),("ç","c")):
        s=s.replace(a,b)
    return re.sub(r"\s+"," ",s)

PROFILE_MANUT = {"imo":"imobiliaria","mes":"mes","ch":"qtd chamados","cart":"carteira",
    "imp":"impacto prop.","imp_alt":"impacto","rev":"qtd revisados","apr":"qtd aprovados",
    "fin":"qtd finalizados","tkf":"tkm prestador finalizado (r$)","rb":"receita bruta (r$)"}
PROFILE_DESO = {"imo":"imobiliaria","mes":"mes","ch":"qtd chamados","cart":"carteira",
    "imp":"impacto realizado proporcional","imp_alt":"impacto realizado","rev":"qtd realizados",
    "apr":"qtd aprovados","fin":"qtd finalizados","tkf":"tkm prestador finalizado","rb":"receita bruta"}

def detect(headers):
    hn=[_norm(h) for h in headers]
    if "qtd revisados" in hn: return PROFILE_MANUT, "Conv. revisado", "Revisados"
    if "qtd realizados" in hn: return PROFILE_DESO, "Conv. realizado", "Realizados"
    return PROFILE_MANUT, "Conv. revisado", "Revisados"

def num(v):
    if v is None: return 0.0
    if isinstance(v,(int,float)): return float(v)
    s=str(v).replace("R$","").replace("%","").strip().replace(".","").replace(",",".")
    try: return float(s)
    except: return 0.0

def pctnorm(v):
    x=num(v); return x/100.0 if abs(x)>1.5 else x

def load(path):
    wb=openpyxl.load_workbook(path, data_only=True); ws=wb.active
    rows=list(ws.iter_rows(values_only=True)); headers,data=rows[0],rows[1:]
    prof,stage2,stage2n = detect(headers)
    hn=[_norm(h) for h in headers]
    C={k:(hn.index(v) if v in hn else None) for k,v in prof.items()}
    d=defaultdict(dict); months=set()
    for r in data:
        imo=r[C["imo"]] if C["imo"] is not None else None
        if imo is None: continue
        mv=r[C["mes"]] if C["mes"] is not None else None
        if not hasattr(mv,"month"): continue
        ym=(mv.year,mv.month); months.add(ym)
        def g(k,pct=False):
            i=C.get(k)
            if i is None: return 0.0
            return pctnorm(r[i]) if pct else num(r[i])
        imp=g("imp",True) or g("imp_alt",True)
        d[imo][ym]=dict(ch=g("ch"),cart=g("cart"),imp=imp,rev=g("rev"),apr=g("apr"),
                        fin=g("fin"),tkf=g("tkf"),rb=g("rb"))
    return d, sorted(months), stage2, stage2n

MESNOME={1:'jan',2:'fev',3:'mar',4:'abr',5:'mai',6:'jun',7:'jul',8:'ago',9:'set',10:'out',11:'nov',12:'dez'}

REC={
 "Demanda":"• Demanda em queda: CS deve entender a menor abertura de chamados (satisfação, engajamento do gestor, concorrência).",
 "Conv. revisado":"• Chamados entram mas não viram orçamento. Gargalo na revisão/orçamentação — SLA de orçamento e cobertura de prestadores.",
 "Conv. realizado":"• Chamados entram mas não viram orçamento. Gargalo na revisão/orçamentação — SLA de orçamento e cobertura de prestadores.",
 "Conv. aprovado":"• Orçamentos feitos mas não vendem. Revisar preço, proposta e follow-up comercial.",
 "Conv. finalizado":"• Sem ação: a queda veio de finalizações que escorregaram para o mês seguinte (defasagem de execução). Tende a normalizar — só para você saber o porquê da queda.",
 "Ticket médio":"• Volume ok, receita por serviço caiu. Revisar mix de serviços e precificação.",
}

def lc(a,b):
    if a>0 and b>0: return math.log(b/a)
    if a>0 and b<=0: return -5.0
    return None

def brl(v): return f"R$ {round(v):,}".replace(",",".")

def analyze(path, ry, rm):
    d, allm, stage2, stage2n = load(path)
    ref=(ry,rm)
    months=[m for m in allm if m<=ref]
    def tot_ch(m): return sum(d[i].get(m,{}).get("ch",0) for i in d)
    while len(months)>3 and tot_ch(months[-1])==0:
        months.pop()
    labels=[MESNOME[m] for (_,m) in months]
    n=len(months)
    # o último mês do arquivo é o mês FECHADO de referência (ex.: julho no export de julho).
    win = months[-3:]
    wlab=[MESNOME[m] for (_,m) in win]
    prev = months[-2] if n>=2 else months[-1]
    refm = months[-1]

    def ser(imo,k,ms):
        return [d[imo].get(m,{}).get(k,0) for m in ms]
    def conv(imo,m):
        r=d[imo].get(m,{})
        ch=r.get("ch",0); rev=r.get("rev",0); apr=r.get("apr",0); fin=r.get("fin",0); rb=r.get("rb",0)
        return dict(crev=(rev/ch if ch else 0), capr=(apr/rev if rev else 0),
            cfin=(fin/apr if apr else 0), ticket=(rb/fin if fin else 0),
            ch=ch, rev=rev, apr=apr, fin=fin, rb=rb, cart=r.get("cart",0),
            imp=r.get("imp",0), tkf=r.get("tkf",0))

    clients=[]
    for imo in d:
        rb_all=ser(imo,"rb",months); ch_all=ser(imo,"ch",months)
        if sum(rb_all)==0 and sum(ch_all)==0: continue
        
        w0,w2=win[0],win[-1]; c0,c2=conv(imo,w0),conv(imo,w2)
        factors=[("Demanda","ch"),(stage2,"crev"),("Conv. aprovado","capr"),
                 ("Conv. finalizado","cfin"),("Ticket médio","ticket")]
        def fval(c,key):
            v=c[key]
            return min(v,1.0) if key=="cfin" else v   # >100% de conv. finalizado = defasagem, não desempenho
        dem_lc=lc(fval(c0,"ch"),fval(c2,"ch"))
        rev_lc=lc(c0["rb"],c2["rb"])
        dem_off = dem_lc is not None and dem_lc<=LN_DROP
        # conversão/ticket só contam quando há problema real: receita caiu OU demanda caiu.
        allow_conv = dem_off or (rev_lc is not None and rev_lc<=LN_DROP)
        drops=[]
        for label,key in factors:
            if key=="ch":
                if dem_off: drops.append((label,key,dem_lc))
                continue
            if not allow_conv: continue
            if key=="ticket" and (c0["fin"]<3 or c2["fin"]<3): continue  # ticket instável em baixo volume
            l=lc(fval(c0,key),fval(c2,key))
            if l is not None and l<=LN_DROP: drops.append((label,key,l))
        ch_lc=dem_lc
        if ch_lc is not None and ch_lc<=LN_COLLAPSE and any(k=="ch" for _,k,_ in drops):
            drops=[t for t in drops if t[1]=="ch"]   # demanda desabou -> conversões viram ruído
        if any(k!="cfin" for _,k,_ in drops) or rev_lc is None or rev_lc>=0:
            # conv. finalizado só quando é o ÚNICO ofensor E a receita caiu de fato
            # (não finalizar ≈ defasagem de execução, não é problema; se a receita subiu, ignorar)
            drops=[t for t in drops if t[1]!="cfin"]
        if not drops and rev_lc is not None and rev_lc<=LN_DROP:
            cand=[(lab,key,lc(fval(c0,key),fval(c2,key))) for lab,key in factors
                  if lc(fval(c0,key),fval(c2,key)) is not None]
            if cand: cand.sort(key=lambda t:t[2]); drops=[cand[0]]
        drops.sort(key=lambda t:t[2])

        def detail(label,key):
            vs=[conv(imo,m) for m in win]
            if key=="ch":
                return "Demanda: "+" → ".join(f"{MESNOME[m[1]]} {round(v['ch'])}"+(f" ({v['imp']*100:.0f}%)" if v['cart'] else "") for m,v in zip(win,vs))
            if key=="ticket":
                return "Ticket médio: "+" → ".join(f"{MESNOME[m[1]]} {brl(v['ticket'])}" for m,v in zip(win,vs))
            return f"{label}: "+" → ".join(f"{MESNOME[m[1]]} {v[key]*100:.0f}%" for m,v in zip(win,vs))

        offenders=[{"label":lab,"detalhe":detail(lab,key)} for lab,key,_ in drops]
        recs=[]
        for lab,_,_ in drops:
            r=REC.get(lab)
            if r and r not in recs: recs.append(r)

        rb_prev=d[imo].get(prev,{}).get("rb",0); rb_ref=d[imo].get(refm,{}).get("rb",0)
        ch_prev=d[imo].get(prev,{}).get("ch",0); ch_ref=d[imo].get(refm,{}).get("ch",0)
        pc=lambda a,b: ((b-a)/a*100) if a else None
        var_rb=pc(rb_prev,rb_ref); var_ch=pc(ch_prev,ch_ref)
        scale=max(ser(imo,"rb",win)) if win else 0
        has=len(offenders)>0
        sole_cfin = has and len(offenders)==1 and offenders[0]['label']=="Conv. finalizado"
        growing=(not has) and rb_ref>=rb_prev and rb_ref>=0.85*max(rb_all+[1]) and rb_ref>=800
        if sole_cfin:                       # informativo (sem ação) -> nunca ALTA
            pri="MÉDIA" if scale>=800 else "Monitorar"
        elif has and scale>=4000: pri="ALTA"
        elif has and scale>=800: pri="MÉDIA"
        elif growing: pri="Positivo"
        else: pri="Monitorar"

        fmonths=months[-4:]
        funil=[]
        for m in fmonths:
            v=conv(imo,m)
            funil.append(dict(mes=MESNOME[m[1]], parcial=False, cart=round(v["cart"]),
                ch=round(v["ch"]), imp=round(v["imp"]*100,1), rev=round(v["rev"]),
                crev=round(v["crev"]*100), apr=round(v["apr"]), capr=round(v["capr"]*100),
                fin=round(v["fin"]), cfin=round(v["cfin"]*100), tkf=round(v["tkf"]),
                ticket=round(v["ticket"]), rb=round(v["rb"])))

        clients.append(dict(cliente=imo, pri=pri, no_action=sole_cfin, offenders=offenders,
            offenders_lbl=[o["label"] for o in offenders], recs=recs,
            imp3=[round(x*100,1) for x in ser(imo,"imp",win)],
            ch3=[round(x) for x in ser(imo,"ch",win)],
            rb=[round(x) for x in rb_all], ch=[round(x) for x in ch_all],
            receita_prev=round(rb_prev), receita_ref=round(rb_ref),
            var_rb=(round(var_rb,1) if var_rb is not None else None),
            var_ch=(round(var_ch,1) if var_ch is not None else None),
            scale=round(scale), funil=funil))

    order={'ALTA':0,'MÉDIA':1,'Positivo':2,'Monitorar':3}
    clients.sort(key=lambda c:(order[c['pri']], -c['receita_ref']))

    receita=[round(sum(d[i].get(m,{}).get("rb",0) for i in d)) for m in months]
    chamados=[round(sum(d[i].get(m,{}).get("ch",0) for i in d)) for m in months]
    ativas=[sum(1 for i in d if d[i].get(m,{}).get("ch",0) or d[i].get(m,{}).get("rb",0)) for m in months]
    pri_counts={k:sum(1 for c in clients if c['pri']==k) for k in ['ALTA','MÉDIA','Positivo','Monitorar']}

    movers=[c for c in clients if max(c['receita_prev'],c['receita_ref'])>=300 and c['var_rb'] is not None]
    ofens=sorted([c for c in movers if c['receita_ref']<c['receita_prev']],
                 key=lambda c:(c['receita_ref']-c['receita_prev']))[:8]
    evol=sorted([c for c in movers if c['receita_ref']>c['receita_prev']],
                key=lambda c:-(c['receita_ref']-c['receita_prev']))[:8]
    def mvr(c): return dict(cliente=c['cliente'], r_prev=c['receita_prev'], r_ref=c['receita_ref'],
                            dabs=c['receita_ref']-c['receita_prev'], dpct=c['var_rb'])

    ridx={m:i for i,m in enumerate(months)}
    iprev,iref=ridx[prev],ridx[refm]
    ov_months=months[-4:]
    overview=dict(
        metric_months=[MESNOME[m[1]] for m in ov_months],
        metric_parcial=[False for m in ov_months],
        receita_row=[round(sum(d[i].get(m,{}).get("rb",0) for i in d)) for m in ov_months],
        chamados_row=[round(sum(d[i].get(m,{}).get("ch",0) for i in d)) for m in ov_months],
        var_receita=dict(a=receita[iprev], b=receita[iref],
                         pct=round((receita[iref]-receita[iprev])/receita[iprev]*100,1) if receita[iprev] else None),
        var_chamados=dict(a=chamados[iprev], b=chamados[iref],
                          pct=round((chamados[iref]-chamados[iprev])/chamados[iprev]*100,1) if chamados[iprev] else None),
        ofensoras=[mvr(c) for c in ofens], evolucao=[mvr(c) for c in evol],
    )
    return dict(labels=labels, receita=receita, chamados=chamados, ativas=ativas,
        win_labels=wlab, ref_label=MESNOME[refm[1]], prev_label=MESNOME[prev[1]],
        partial_label="", stage2=stage2, stage2n=stage2n,
        pri_counts=pri_counts, overview=overview, clients=clients)

def main():
    manut,deso,out=sys.argv[1],sys.argv[2],sys.argv[3]
    if len(sys.argv)>4: ry,rm=map(int,sys.argv[4].split("-"))
    else:
        t=datetime.date.today(); ry=t.year if t.month>1 else t.year-1; rm=t.month-1 if t.month>1 else 12
    res=dict(ref=f"{MESNOME[rm]}/{str(ry)[2:]}", gerado_em=None,
             manutencao=analyze(manut,ry,rm), desocupacao=analyze(deso,ry,rm))
    json.dump(res, open(out,"w"), ensure_ascii=False, indent=1)
    print("SAVED",out)
    for p in ("manutencao","desocupacao"):
        r=res[p]; print(p,"ref(fechado)=",r["ref_label"],"win=",r["win_labels"],r["pri_counts"])

if __name__=="__main__": main()
