from loader import carregar_receitas
from tabela_hash import TabelaHash, TabelaHashIntegridade
from trie import Trie
from guloso import menu_por_orcamento, menu_por_tempo, menu_por_ingredientes

class LivroDeReceitas:
    def __init__(self):
        self.por_id          = TabelaHash(capacidade=101)
        self.por_categoria   = TabelaHash(capacidade=53)
        self.por_ingrediente = TabelaHash(capacidade=211)
        self.trie            = Trie()
        self.integridade     = TabelaHashIntegridade()
        self._lista          = []
        self.nomes_originais = {}

    def carregar(self, receitas):
        print(f"\nIndexando {len(receitas)} receitas...")

        for r in receitas:
            # busca por ID
            self.por_id.inserir(r.id, r)

            lista_cat = self.por_categoria.buscar(r.categoria)
            if lista_cat is None:
                lista_cat = []
            lista_cat.append(r)
            self.por_categoria.inserir(r.categoria, lista_cat)

            # busca por ingrediente
            for ing in r.ingredientes:
                chave = ing.lower().strip()
                lista_ing = self.por_ingrediente.buscar(chave) or []
                lista_ing.append(r)
                self.por_ingrediente.inserir(chave, lista_ing)

            # busca por prefixo de nome
            self.trie.inserir(r.nome, r.id)

            # guarda assinatura original para modo investigação
            self.integridade.guardar_original(r)

        self._lista = receitas
        print(f"Pronto! {len(receitas)} receitas indexadas.\n")

    def todas(self):
        return self._lista

def linha(char="-", n=55):
    print(char * n)

def exibir_receita(r, detalhado=False):
    print(f"\n  [{r.id}] {r.nome}")
    print(f"       Categoria  : {r.categoria}")
    print(f"       Avaliacao  : {r.avaliacao}/5.0")
    print(f"       Tempo      : {r.tempo_preparo} min")
    print(f"       Custo      : R$ {r.custo:.2f}")
    print(f"       Dificuldade: {r.dificuldade}/5")
    print(f"       Pedidos    : {r.pedidos}")
    if detalhado:
        print(f"       Ingredientes: {', '.join(r.ingredientes)}")

def listar_categorias(livro):
    cats = []
    for r in livro.todas():
        if r.categoria not in cats:
            cats.append(r.categoria)
    cats.sort()

    print("\n  Categorias disponíveis:")
    for c in cats:
        print(f"    - {c}")

def modo_consulta(livro):
    while True:
        linha()
        print("  MODO CONSULTA RAPIDA")
        print("  1. Buscar por ID")
        print("  2. Buscar por prefixo de nome")
        print("  3. Filtrar por categoria")
        print("  4. Buscar por ingrediente")
        print("  0. Voltar")
        op = input("Opcao: ").strip()

        if op == "0":
            break

        elif op == "1":
            id_ = input("ID da receita: ").strip()
            r = livro.por_id.buscar(id_)
            if r:
                exibir_receita(r, detalhado=True)
            else:
                print(f"  Receita ID '{id_}' nao encontrada.")

        elif op == "2":
            prefixo = input("Prefixo do nome: ").strip()
            resultados = livro.trie.busca_prefixo(prefixo)
            if not resultados:
                print(f"  Nenhuma receita comeca com '{prefixo}'.")
            else:
                print(f"\n  {len(resultados)} resultado(s) para '{prefixo}':")
                for nome, ids in resultados[:15]:
                    r = livro.por_id.buscar(ids[0])
                    if r:
                        exibir_receita(r)

        elif op == "3":
            listar_categorias(livro)
            cat = input("\nCategoria: ").strip().title()
            receitas = livro.por_categoria.buscar(cat) or []
            if not receitas:
                print(f"  Categoria '{cat}' nao encontrada.")
            else:
                print(f"\n  {len(receitas)} receita(s) em '{cat}':")
                for r in receitas[:10]:
                    exibir_receita(r)

        elif op == "4":
            ing = input("Ingrediente: ").strip()
            receitas = livro.por_ingrediente.buscar(ing.lower()) or []
            if not receitas:
                print(f"  Nenhuma receita encontrada com '{ing}'.")
            else:
                print(f"\n  {len(receitas)} receita(s) com '{ing}':")
                for r in receitas[:10]:
                    exibir_receita(r)

def modo_chef(livro):
    todas = livro.todas()

    while True:
        linha()
        print("  MODO CHEF - Recomendacao Inteligente")
        print("  1. Menu por orcamento")
        print("  2. Menu por tempo")
        print("  3. Menu pelos ingredientes requisitados")
        print("  0. Voltar")
        op = input("Opcao: ").strip()

        if op == "0":
            break

        elif op == "1":
            try:
                orcamento = float(input("Orcamento maximo (R$): ").strip())
                res = menu_por_orcamento(todas, orcamento)
                if not res["receitas"]:
                    print("  Nenhuma receita cabe nesse orcamento.")
                else:
                    print(f"\n  Menu Economico (ate R$ {orcamento:.2f})")
                    print(f"  Custo total: R$ {res['custo_total']:.2f}")
                    print(f"  Aval. media: {res['avaliacao_media']}/5.0")

                    for r in res["receitas"]:
                        exibir_receita(r)

            except ValueError:
                print("  Valor invalido.")

        elif op == "2":
            try:
                tempo = int(input("Tempo maximo disponivel (minutos): ").strip())
                res = menu_por_tempo(todas, tempo)
                
                if not res["receitas"]:
                    print("  Nenhuma receita cabe nesse tempo.")
                else:
                    print(f"\n  Menu Rapido (ate {tempo} min)")
                    print(f"  Tempo total : {res['tempo_total']} min")
                    print(f"  Aval. media : {res['avaliacao_media']}/5.0")

                    for r in res["receitas"]:
                        exibir_receita(r)
            except ValueError:
                print("  Valor invalido.")

        elif op == "3":
            ing_str = input("Ingredientes disponíveis (separados por virgula): ").strip()
            ingredientes = [i.strip() for i in ing_str.split(",") if i.strip()]

            try:
                n = int(input("Quantas sugestoes? (padrao 5): ").strip() or "5")
            except ValueError:
                n = 5

            res = menu_por_ingredientes(todas, ingredientes, n)

            if not res["receitas"]:
                print("\n  Nenhuma receita encontrada com esses ingredientes.")
            else:
                print(f"\n  Menu pelos seus ingredientes")
                
                for i in range(len(res["receitas"])):
                    r = res["receitas"][i]
                    cob = res["coberturas"][i]
                    exibir_receita(r)
                    print(f"       Cobertura: {cob}% dos ingredientes disponiveis")

def modo_investigacao(livro):
    todas = livro.todas()

    while True:
        linha()
        print("  MODO INVESTIGACAO - Integridade das Receitas")
        print("  1. Verificar receita especifica")
        print("  2. Auditar todas as receitas")
        print("  3. Detectar conteudo duplicado")
        print("  4. Sabotar receita")
        print("  5. Restaurar receita sabotada")
        print("  0. Voltar")
        op = input("Opcao: ").strip()

        if op == "0":
            break

        elif op == "1":
            id_ = input("ID da receita: ").strip()
            r = livro.por_id.buscar(id_)
            if not r:
                print(f"  ID '{id_}' nao encontrado.")
                continue
            integra = livro.integridade.verificar_se_foi_sabotada(r)
            status = "INTEGRA" if integra else "CORROMPIDA"
            print(f"\n  Receita : {r.nome}")
            print(f"  Status  : {status}")

        elif op == "2":
            print("\n  Auditando todas as receitas...")
            corrompidas = []
            for r in todas:
                if not livro.integridade.verificar_se_foi_sabotada(r):
                    corrompidas.append(r)

            if corrompidas:
                print(f"  {len(corrompidas)} receita(s) corrompida(s):")
                for r in corrompidas:
                    print(f"    - {r.nome} (ID: {r.id})")
            else:
                print(f"  Todas as {len(todas)} receitas estao integras!")

        elif op == "3":
            print("\n  Procurando duplicatas de conteudo...")
            grupos = {}
            for r in todas:
                sig = livro.integridade._gerar_assinatura(r)
                if sig not in grupos:
                    grupos[sig] = []
                grupos[sig].append(r)

            duplicatas = {s: rs for s, rs in grupos.items() if len(rs) > 1}

            if not duplicatas:
                print("  Nenhum conteudo duplicado encontrado.")
            else:
                print(f"  {len(duplicatas)} grupo(s) com conteudo identico:")
                for sig, receitas in duplicatas.items():
                    nomes = [r.nome for r in receitas]
                    ids   = [r.id  for r in receitas]
                    print(f"    IDs {ids} -> {nomes}")
        
        elif op == "4":
            id_ = input("ID da receita para sabotar: ").strip()
            r = livro.por_id.buscar(id_)
            if not r:
                print("  ID nao encontrado.")
                continue

            livro.nomes_originais[r.id] = r.nome
            r.nome = r.nome + " (ADULTERADA PELO RIVAL)"
            
            print(f"\n  Receita sabotada: {r.nome}")
            print(f"  Use a opcao 5 para restaurar.")
        elif op == "5":
            if not livro.nomes_originais:
                print("\n  Nenhuma receita foi sabotada nesta sessao.")
                continue
 
            print("\n  Receitas sabotadas nesta sessao:")
            ids_sabotados = list(livro.nomes_originais.keys())
            for i, id_r in enumerate(ids_sabotados):
                r = livro.por_id.buscar(id_r)
                print(f"    {i+1}. [{id_r}] {r.nome}")
 
            id_ = input("\n  ID da receita para restaurar: ").strip()
 
            if id_ not in livro.nomes_originais:
                print("  Esse ID nao foi sabotado nesta sessao.")
                continue
 
            r = livro.por_id.buscar(id_)
            r.nome = livro.nomes_originais[id_]
            del livro.nomes_originais[id_]
 
            integra = livro.integridade.verificar_se_foi_sabotada(r)
            print(f"\n  Receita restaurada: {r.nome}")

def menu_principal(livro):
    while True:
        linha("=")
        print("  DESAFIO NA COZINHA — Sistema do Chef Jacquin")
        linha("=")
        print(f"  Receitas carregadas: {len(livro.todas())}")
        linha()
        print("  1. Modo Consulta Rapida")
        print("  2. Modo Chef (Recomendacao)")
        print("  3. Modo Investigacao (Integridade)")
        print("  4. Estatisticas do sistema")
        print("  5. Listar receitas")
        print("  0. Sair")
        linha()
        op = input("Opcao: ").strip()

        if op == "0":
            print("\n  Ate logo, Chef!\n")
            break
        elif op == "1":
            modo_consulta(livro)
        elif op == "2":
            modo_chef(livro)
        elif op == "3":
            modo_investigacao(livro)
        elif op == "4":
            print(f"\n  Estatisticas:")
            stats = livro.por_id.estatisticas()
            for chave, val in stats.items():
                print(f"    {chave}: {val}")
        elif op == "5":
            todas = livro.todas()
            if not todas:
                print("\n  Nenhuma receita encontrada no sistema.")
            else:
                print("\n=================== CARDÁPIO COMPLETO ===================")
                print(f"{'ID':<10} | {'Nome da Receita':<45} | {'Categoria'}")
                print("-" * 75)
                
                for r in receitas:
                    print(f"{r.id:<10} | {r.nome:<45} | {r.categoria}")
                    
                print("-" * 75)
                print(f"Total: {len(receitas)} receitas listadas prontas para consulta.")

if __name__ == "__main__":
    print("\n  Iniciando Desafio na Cozinha...\n")
    receitas = carregar_receitas()
    livro = LivroDeReceitas()
    livro.carregar(receitas)
    menu_principal(livro)