import json
import os
import random
import hashlib

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

BASE_URL = "https://www.themealdb.com/api/json/v1/1"
CACHE_FILE = "receitas.json"


class Receita:
    def __init__(self, id, nome, categoria, ingredientes,
                 tempo_preparo, custo, dificuldade, avaliacao,
                 pedidos, instrucoes="", thumb=""):
        self.id = str(id)
        self.nome = nome
        self.categoria = categoria
        self.ingredientes = ingredientes
        self.tempo_preparo = tempo_preparo
        self.custo = custo
        self.dificuldade = dificuldade
        self.avaliacao = avaliacao
        self.pedidos = pedidos
        self.instrucoes = instrucoes
        self.thumb = thumb

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def __repr__(self):
        return f"Receita(id={self.id}, nome='{self.nome}', cat='{self.categoria}', aval={self.avaliacao})"


def simular_numericos(id_str):
    seed = int(hashlib.md5(id_str.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)

    tempo = rng.choice([15, 20, 30, 45, 60, 90, 120])
    custo = round(rng.uniform(10.0, 150.0), 2)
    dificuldade = rng.randint(1, 5)
    avaliacao = round(rng.uniform(2.5, 5.0), 1)
    pedidos = rng.randint(10, 500)

    return tempo, custo, dificuldade, avaliacao, pedidos


def parse_meal(meal):
    id_str = meal.get("idMeal", "0")

    ingredientes = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "")
        if ing and ing.strip():
            ingredientes.append(ing.strip())

    tempo, custo, dificuldade, avaliacao, pedidos = simular_numericos(id_str)

    return Receita(
        id=id_str,
        nome=meal.get("strMeal", ""),
        categoria=meal.get("strCategory", ""),
        ingredientes=ingredientes,
        instrucoes=meal.get("strInstructions", ""),
        thumb=meal.get("strMealThumb", ""),
        tempo_preparo=tempo,
        custo=custo,
        dificuldade=dificuldade,
        avaliacao=avaliacao,
        pedidos=pedidos,
    )


def buscar_categorias():
    r = requests.get(f"{BASE_URL}/categories.php", timeout=10)
    r.raise_for_status()

    dados_json = r.json()
    categorias_encontradas = []

    for c in dados_json["categories"]:
        categorias_encontradas.append(c["strCategory"])

    return categorias_encontradas


def buscar_ids_por_categoria(categoria):
    r = requests.get(f"{BASE_URL}/filter.php?c={categoria}", timeout=10)
    r.raise_for_status()

    meals = r.json().get("meals") or []
    ids = []

    for m in meals:
        ids.append(m["idMeal"])

    return ids


def buscar_receita_por_id(id_meal):
    r = requests.get(f"{BASE_URL}/lookup.php?i={id_meal}", timeout=30)
    r.raise_for_status()

    meals = r.json().get("meals")
    if not meals:
        return None

    return parse_meal(meals[0])


def carregar_da_api(max_receitas=80):
    if not REQUESTS_OK:
        raise ImportError("Instale requests: pip install requests")

    print("Conectando a TheMealDB...")
    categorias = buscar_categorias()
    receitas = []
    ids_vistos = set()

    for cat in categorias:
        if len(receitas) >= max_receitas:
            break
        print(f" Categoria: {cat}")
        ids = buscar_ids_por_categoria(cat)

        for id_meal in ids:
            if len(receitas) >= max_receitas:
                break
            if id_meal in ids_vistos:
                continue
            ids_vistos.add(id_meal)

            receita = buscar_receita_por_id(id_meal)
            if receita:
                receitas.append(receita)
                print(f"- {receita.nome}")

    return receitas


def salvar_cache(receitas, caminho=CACHE_FILE):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in receitas], f, ensure_ascii=False, indent=2)
    print(f"{len(receitas)} receitas salvas em '{caminho}'")


def carregar_cache(caminho=CACHE_FILE):
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    receitas = []
    for d in dados:
        receitas.append(Receita.from_dict(d))

    print(f" {len(receitas)} receitas carregadas de '{caminho}'")
    return receitas


def carregar_receitas(forcar_api=False, max_receitas=80):
    if not forcar_api and os.path.exists(CACHE_FILE):
        return carregar_cache()

    receitas = carregar_da_api(max_receitas)
    salvar_cache(receitas)
    return receitas