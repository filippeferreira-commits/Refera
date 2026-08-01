#!/usr/bin/env python3
"""
Refera — Extração mensal por produto (Manutenção + Desocupação).

Emite um JSON com os dados CRUS por cliente e mês (chamados, carteira, revisados/realizados,
aprovados, finalizados, ticket do prestador, receita bruta). A análise "onde a receita está
caindo" (decomposição do funil, ofensores, prioridade, visão geral) roda no navegador, para
permitir escolher interativamente quais meses comparar.

Uso:
  python refera_analysis.py <manutencao.xlsx> <desocupacao.xlsx> <saida.json> [AAAA-MM-ref]
"""
import sys, os, json, re, datetime
from collections import defaultdict
import openpyxl

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
        d[imo][ym]=dict(ch=g("ch"),cart=g("cart"),rev=g("rev"),apr=g("apr"),
                        fin=g("fin"),tkf=g("tkf"),rb=g("rb"))
    return d, sorted(months), stage2, stage2n

MESNOME={1:'jan',2:'fev',3:'mar',4:'abr',5:'mai',6:'jun',7:'jul',8:'ago',9:'set',10:'out',11:'nov',12:'dez'}

def extract(path, ry, rm):
    d, allm, stage2, stage2n = load(path)
    ref=(ry,rm)
    months=[m for m in allm if m<=ref]
    def tot_ch(m): return sum(d[i].get(m,{}).get("ch",0) for i in d)
    while len(months)>3 and tot_ch(months[-1])==0: months.pop()
    labels=[f"{MESNOME[m]}/{str(y)[2:]}" for (y,m) in months]
    labels_short=[MESNOME[m] for (_,m) in months]
    def ser(imo,k): return [d[imo].get(m,{}).get(k,0) for m in months]
    clients=[]
    for imo in d:
        rb=ser(imo,"rb"); ch=ser(imo,"ch")
        if sum(rb)==0 and sum(ch)==0: continue
        clients.append(dict(cliente=imo,
            cart=[round(x) for x in ser(imo,"cart")],
            ch=[round(x) for x in ch],
            rev=[round(x) for x in ser(imo,"rev")],
            apr=[round(x) for x in ser(imo,"apr")],
            fin=[round(x) for x in ser(imo,"fin")],
            tkf=[round(x) for x in ser(imo,"tkf")],
            rb=[round(x) for x in rb]))
    clients.sort(key=lambda c:-c["rb"][-1] if c["rb"] else 0)
    return dict(labels=labels, labels_short=labels_short, stage2=stage2, stage2n=stage2n, clients=clients)

def main():
    manut,deso,out=sys.argv[1],sys.argv[2],sys.argv[3]
    if len(sys.argv)>4: ry,rm=map(int,sys.argv[4].split("-"))
    else:
        t=datetime.date.today(); ry=t.year if t.month>1 else t.year-1; rm=t.month-1 if t.month>1 else 12
    res=dict(ref=f"{MESNOME[rm]}/{str(ry)[2:]}", gerado_em=None,
             manutencao=extract(manut,ry,rm), desocupacao=extract(deso,ry,rm))
    json.dump(res, open(out,"w"), ensure_ascii=False, indent=1)
    print("SAVED",out)
    for p in ("manutencao","desocupacao"):
        r=res[p]; print(p,"meses=",r["labels_short"],"clientes=",len(r["clients"]))

if __name__=="__main__": main()
