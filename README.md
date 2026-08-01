# Refera — Painel de Receita e Indicadores

Dashboard automático por produto (Manutenção e Desocupação) publicado via GitHub Pages.

**Link do painel:** https://filippeferreira-commits.github.io/Refera/

## Como funciona
Toda virada de mês, uma tarefa do Claude (Cowork) roda automaticamente:
1. Lê da pasta do Google Drive os 2 exports mais recentes (Manutenção e Desocupação);
2. Roda `refera_analysis.py` (funil + priorização por cliente);
3. Gera o `index.html` com `build_dashboard.py`;
4. Faz commit/push neste repositório — o Pages republica o mesmo link.

## Rodar manualmente
```
python3 refera_analysis.py manutencao.xlsx desocupacao.xlsx analise.json AAAA-MM
python3 build_dashboard.py analise.json index.html "DD/MM/AAAA HH:MM (BRT)"
```
