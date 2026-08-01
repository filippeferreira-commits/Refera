#!/usr/bin/env python3
"""
Refera - Analise mensal por produto (Manutencao + Desocupacao).

Le os dois exports (xlsx) da pasta do Drive, normaliza os dois esquemas de
colunas, e produz um JSON por produto com:
  - series mensais agregadas (receita, chamados, imobiliarias ativas)
  - distribuicao de prioridade
  - lista de clientes priorizados (o que esta caindo + recomendacao)
  - funil detalhado por cliente no mes de referencia

Uso:
  python refera_analysis.py <manutencao.xlsx> <desocupacao.xlsx> <saida.json> [YYYY-MM-referencia]

O mes corrente (incompleto) e descartado; o ultimo mes completo vira referencia.
"""
import sys, os, json, math, re, datetime
from collections import defaultdict
import openpyxl

def _norm(s):
    s = str(s or "").strip().lower()
    for a, b in (("á","a"),("â","a"),("ã","a"),("é","e"),("ê","e"),("í","i"),
                 ("ó","o"),("ô","o"),("õ","o"),("ú","u"),("ç","c")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)

# perfis de coluna por produto: chave comum -> lista de nomes de header (norm)
PROFILE_MANUT = {
    "imo":"imobiliaria","mes":"mes","ch":"qtd chamados","cart":"carteira",
    "imp":"impacto prop.","imp_alt":"impacto","rev":"qtd revisados","apr":"qtd aprovados",
    "fin":"qtd finalizados","cr":"conversao revisado","ca":"conversao aprovados (fechada)",
    "cf":"conversao finalizado","tkf":"tkm prestador finalizado (r$)","rb":"receita bruta (r$)",
}
PROFILE_DESO = {
    "imo":"imobiliaria","mes":"mes","ch":"qtd chamados","cart":"carteira",
    "imp":"impacto realizado proporcional","imp_alt":"impacto realizado","rev":"qtd realizados",
    "apr":"qtd aprovados","fin":"qtd finalizados","cr":"conversao - realizados por pedidos",
    "ca":"conversao - aprovados por realizados","cf":"conversao - finalizados por aprovados",
    "tkf":"tkm prestador finalizado","rb":"receita bruta",
}

def detect_profile(headers):
    hn = [_norm(h) for h in headers]
    if "qtd revisados" in hn:
        return PROFILE_MANUT
    if "qtd realizados" in hn:
        return PROFILE_DESO
    # fallback: manutencao
    return PROFILE_MANUT

def colmap(headers, profile):
    hn = [_norm(h) for h in headers]
    m = {}
    for k, name in profile.items():
        m[k] = hn.index(name) if name in hn else None
    return m

def month_of(v):
    if hasattr(v, "month"):
        return (v.year, v.month)
    return None

def num(v):
    if v is None: return 0.0
    if isinstance(v,(int,float)): return float(v)
    s = str(v).replace("R$","").replace("%","").strip().replace(".","").replace(",",".")
    try: return float(s)
    except: return 0.0

def pct_norm(v):
    """conversoes/impacto podem vir como fracao (0.55) ou percentual (55). Normaliza p/ fracao."""
    x = num(v)
    return x/100.0 if abs(x) > 1.5 else x

def load(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    headers, data = rows[0], rows[1:]
    prof = detect_profile(headers)
    C = colmap(headers, prof)
    d = defaultdict(dict)
    months = set()
    for r in data:
        imo = r[C["imo"]] if C["imo"] is not None else None
        if imo is None: continue
        ym = month_of(r[C["mes"]]) if C["mes"] is not None else None
        if ym is None: continue
        months.add(ym)
        def g(k, pct=False):
            i = C.get(k)
            if i is None: return 0.0
            return pct_norm(r[i]) if pct else num(r[i])
        # impacto: usa prop se existir, senao alt
        imp = g("imp", pct=True) or g("imp_alt", pct=True)
        d[imo][ym] = dict(
            ch=g("ch"), cart=g("cart"), imp=imp,
            rev=g("rev"), apr=g("apr"), fin=g("fin"),
            cr=g("cr", pct=True), ca=g("ca", pct=True), cf=g("cf", pct=True),
            tkf=g("tkf"), rb=g("rb"),
        )
    return d, sorted(months)

MESNOME={1:'jan',2:'fev',3:'mar',4:'abr',5:'mai',6:'jun',7:'jul',8:'ago',9:'set',10:'out',11:'nov',12:'dez'}

def analyze(path, ref_year, ref_month):
    d, allmonths = load(path)
    # descarta o mes corrente/futuro (incompleto): mantem meses <= referencia
    ref = (ref_year, ref_month)
    months = [ym for ym in allmonths if ym <= ref]
    # descarta tambem meses finais sem nenhum chamado (placeholders vazios)
    def month_total_ch(ym): return sum(d[i].get(ym,{}).get("ch",0) for i in d)
    while len(months) > 2 and month_total_ch(months[-1]) == 0:
        months.pop()
    labels = [f"{MESNOME[m]}" for (_,m) in months]

    def series(imo,k): return [d[imo].get(ym,{}).get(k,0) for ym in months]
    pc = lambda a,b: ((b-a)/a*100) if a else None

    clients=[]
    for imo in d:
        ch=series(imo,"ch"); rb=series(imo,"rb"); imp=series(imo,"imp")
        rev=series(imo,"rev"); apr=series(imo,"apr"); fin=series(imo,"fin")
        cr=series(imo,"cr"); ca=series(imo,"ca"); cf=series(imo,"cf")
        tkf=series(imo,"tkf"); cart=series(imo,"cart")
        if sum(ch)==0 and sum(rb)==0:
            continue
        ref_rb=rb[-1]; prev_rb=rb[-2] if len(rb)>=2 else 0
        ref_ch=ch[-1]; prev_ch=ch[-2] if len(ch)>=2 else 0
        peak_rb=max(rb); peak_ch=max(ch)
        var_rb=pc(prev_rb, ref_rb)
        var_ch=pc(prev_ch, ref_ch)

        # baseline = media dos ate 3 meses completos ANTES do mes de referencia
        # (suaviza picos de um mes so, que geram falso "caiu/subiu")
        def baseline(sq):
            prior = sq[:-1][-3:]
            return sum(prior)/len(prior) if prior else 0
        base_rb = baseline(rb); base_ch = baseline(ch)
        # escala "recente" do cliente: evita marcar como grande quem so teve 1 pico antigo
        recent_scale = max(base_rb, prev_rb, ref_rb)

        # tendencia (nao pico isolado): receita do mes de ref bem abaixo da media recente
        decline_trend = base_rb>0 and ref_rb <= 0.75*base_rb
        sharp_mom = var_rb is not None and var_rb <= -20 and prev_rb>=800
        # demanda caindo, mas so conta como problema se a receita nao esta se sustentando
        dem_drop = peak_ch>=15 and base_ch>0 and ref_ch <= 0.6*base_ch and ref_rb < 0.9*base_rb

        # driver nivel 1: demanda x monetizacao (log-change baseline->ref)
        rpc_base = base_rb/base_ch if base_ch else 0
        rpc_ref = ref_rb/ref_ch if ref_ch else 0
        lc = math.log(ref_ch/base_ch) if base_ch and ref_ch else (-5 if base_ch and not ref_ch else 0)
        lm = math.log(rpc_ref/rpc_base) if rpc_base and rpc_ref else (-5 if rpc_base and not rpc_ref else 0)
        l1 = "Demanda" if lc < lm else "Monetização"
        convtot_base = baseline([(fin[i]/ch[i] if ch[i] else 0) for i in range(len(ch))]) if len(ch) else 0
        convtot_ref = (fin[-1]/ch[-1]) if ch[-1] else 0
        dtk = pc(baseline(tkf), tkf[-1]) if len(tkf) else None
        dcv = pc(convtot_base, convtot_ref)

        rev_problem = recent_scale>=1000 and (decline_trend or sharp_mom)
        if rev_problem:
            whats = "Demanda" if l1=="Demanda" else ("Ticket médio" if (dtk or 0) < (dcv or 0) else "Conversão")
        elif dem_drop:
            whats="Demanda"
        else:
            whats="—"

        big = recent_scale>=2500; mid = recent_scale>=1000
        growing = ref_rb>=prev_rb and ref_rb>=0.85*max(peak_rb,1) and ref_rb>=800
        if big and rev_problem and decline_trend: pri="ALTA"
        elif big and (rev_problem or dem_drop): pri="MÉDIA"
        elif mid and (rev_problem or dem_drop): pri="MÉDIA"
        elif growing: pri="Positivo"
        elif dem_drop: pri="MÉDIA"
        else: pri="Monitorar"

        clients.append(dict(
            cliente=imo, pri=pri, whats=whats, l1=l1,
            imp=[round(x*100,1) for x in imp], ch=[round(x) for x in ch],
            rb=[round(x) for x in rb], rev=[round(x) for x in rev],
            apr=[round(x) for x in apr], fin=[round(x) for x in fin],
            cr=[round(x*100,1) for x in cr], ca=[round(x*100,1) for x in ca],
            cf=[round(x*100,1) for x in cf], tkf=[round(x) for x in tkf],
            receita_ref=round(ref_rb), receita_prev=round(prev_rb),
            var_receita=(round(var_rb,1) if var_rb is not None else None),
            var_chamados=(round(var_ch,1) if var_ch is not None else None),
            peak_rb=round(peak_rb), chamados_ref=round(ref_ch),
        ))

    pri_order={'ALTA':0,'MÉDIA':1,'Positivo':2,'Monitorar':3}
    clients.sort(key=lambda c:(pri_order[c['pri']], -c['receita_ref']))

    receita_series=[round(sum(d[i].get(ym,{}).get("rb",0) for i in d)) for ym in months]
    chamados_series=[round(sum(d[i].get(ym,{}).get("ch",0) for i in d)) for ym in months]
    ativas_series=[sum(1 for i in d if d[i].get(ym,{}).get("ch",0) or d[i].get(ym,{}).get("rb",0)) for ym in months]
    pri_counts={k:sum(1 for c in clients if c['pri']==k) for k in ['ALTA','MÉDIA','Positivo','Monitorar']}

    return dict(
        labels=labels, receita=receita_series, chamados=chamados_series, ativas=ativas_series,
        pri_counts=pri_counts, clients=clients, ref_label=labels[-1] if labels else "",
    )

def main():
    manut, deso, out = sys.argv[1], sys.argv[2], sys.argv[3]
    if len(sys.argv) > 4:
        ry, rm = map(int, sys.argv[4].split("-"))
    else:
        # referencia = mes anterior ao corrente
        today = datetime.date.today()
        ry = today.year if today.month > 1 else today.year-1
        rm = today.month-1 if today.month > 1 else 12
    result = dict(
        ref=f"{MESNOME[rm]}/{str(ry)[2:]}",
        gerado_em=None,  # preenchido fora (Date indisponivel em alguns contextos)
        manutencao=analyze(manut, ry, rm),
        desocupacao=analyze(deso, ry, rm),
    )
    json.dump(result, open(out,"w"), ensure_ascii=False, indent=1)
    print("SAVED", out)
    for prod in ("manutencao","desocupacao"):
        r=result[prod]
        print(prod, "ref=",r["ref_label"], "receita=",r["receita"], "prioridade=",r["pri_counts"])

if __name__=="__main__":
    main()
