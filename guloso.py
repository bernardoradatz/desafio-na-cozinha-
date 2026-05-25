import math

def menu_por_orcamento(receitas, orcamento_max):
    candidatos = []
    for r in receitas:
        if 0 < r.custo <= orcamento_max:
            candidatos.append(r)

    candidatos.sort(key=lambda r: r.avaliacao / r.custo, reverse=True)

    selecionados = []
    custo_acumulado = 0.0
 
    for receita in candidatos:
        if custo_acumulado + receita.custo <= orcamento_max:
            selecionados.append(receita)
            custo_acumulado += receita.custo
 
    if len(selecionados) == 0:
        media = 0.0
    else:
        soma = 0
        for r in selecionados:
            soma += r.avaliacao
        media = soma / len(selecionados)
 
    return {
        "receitas": selecionados,
        "custo_total": round(custo_acumulado, 2),
        "avaliacao_media": round(media, 2),
        "criterio": "maior avaliacao/custo primeiro (guloso)",
    }
 
 
def menu_por_tempo(receitas, tempo_max):
    candidatos = []
    for r in receitas:
        if 0 < r.tempo_preparo <= tempo_max:
            candidatos.append(r)
 
    candidatos.sort(key=lambda r: r.avaliacao / r.tempo_preparo, reverse=True)
 
    selecionados = []
    tempo_acumulado = 0
 
    for receita in candidatos:
        if tempo_acumulado + receita.tempo_preparo <= tempo_max:
            selecionados.append(receita)
            tempo_acumulado += receita.tempo_preparo
 
    if len(selecionados) == 0:
        media = 0.0
    else:
        soma = 0
        for r in selecionados:
            soma += r.avaliacao
        media = soma / len(selecionados)
 
    return {
        "receitas": selecionados,
        "tempo_total": tempo_acumulado,
        "avaliacao_media": round(media, 2),
        "criterio": "maior avaliacao/tempo primeiro (guloso)",
    }
 

def menu_por_ingredientes(receitas, ing_disp, n):
    disponiveis = {i.lower() for i in ing_disp}

    def compatibilidade(receita):
        total = len(receita.ingredientes)
        if total == 0:
            return 0
        iguais = 0 

        for ing in receita.ingredientes:
            if ing.lower().strip() in disponiveis:
                iguais += 1
        return iguais / total
    
    candidatos = sorted(receitas, key=compatibilidade, reverse=True)
    selecionados = candidatos[:n]

    return {
        "receitas": selecionados,
        "coberturas": [round(compatibilidade(r) * 100, 1) for r in selecionados],
        "criterio": "% ingredientes disponíveis / total da receita",
    }