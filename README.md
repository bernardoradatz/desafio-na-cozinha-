# desafio-na-cozinha
Repositório - https://github.com/bernardoradatz/desafio-na-cozinha-

Como executar:
1. Instale requests no terminal
pip install requests 
2. Execute o sistema
python main.py

Na primeira execução do código ele baixa automaticamente as receitas do TheMealDB e salva em receitas.json (com 80 receitas por base no código).
Nas execuções seguintes ele apenas carrega o arquivo local, sem necessitar de internet.

Fonte de dados
API - TheMealDB

Endpoints consumidos:
/categories.php — lista todas as categorias de pratos
/filter.php?c=<categoria> — lista resumida de receitas por categoria
/lookup.php?i=<id> — detalhes completos de uma receita

Campos coletados da API:
idMeal → id
strMeal → nome
strCategory → categoria
strIngredient1 até strIngredient20 → lista de ingredientes
strInstructions → modo de preparo
strMealThumb → imagem

Campos simulados deterministicamente (a API não fornece dados financeiros ou de popularidade):
tempo_preparo — sorteado entre valores fixos: 15, 20, 30, 45, 60, 90 ou 120 minutos
custo — valor entre R$ 10,00 e R$ 150,00
dificuldade — nível de 1 a 5
avaliacao — nota entre 2,5 e 5,0
pedidos — quantidade entre 10 e 500

A simulação usa random.Random com seed derivada do MD5 do ID da receita, garantindo que os valores sejam sempre os mesmos para a mesma receita em qualquer execução.


Estrutura de Dados implementadas
1. Tabela Hash - tabela_hash.py
A função hash multiplica o código ASCII de cada caractere por potencia de 31 (primo) para reduzir colisões. Cada posição na tabela é uma lista encadeada de pares [chave, valor]. Quando o fator de carga ultrapassa 0.75 a tabela dobra de capacidade reinserindo os pares (rehash).

Aplicada em três contextos no sistema:
por_id — mapeia ID → Receita, usada na busca direta por identificador
por_categoria — mapeia categoria → lista de receitas, usada no filtro por categoria
por_ingrediente — mapeia ingrediente → lista de receitas, usada na busca por ingrediente
TabelaHashIntegridade — armazena o hash SHA-256 original de cada receita para o Modo Investigação

2. Árvore Trie — trie.py
Cada nó representa um caractere. O caminho da raiz até um nó marcado como fim_palavra forma o nome de uma receita. Para buscar por prefixo, o algoritmo desce letra a letra até o nó correspondente ao último caractere do prefixo e depois faz uma DFS coletando todos os nomes que continuam daquele ponto.

Aplicada em:
Módulo 2 (Busca Rápida): autocomplete por prefixo de nome — digitar "Ch" retorna "Chicken Curry", "Chocolate Cake", etc.
Modo Consulta Rápida, opção de busca por prefixo

3. Algoritmo Guloso — guloso.py
Conceito: a cada passo, escolhe a opção localmente melhor segundo um critério definido, sem voltar atrás. Não garante o ótimo global, mas é eficiente e suas decisões são justificáveis.

Três estratégias implementadas:
menu_por_orcamento(receitas, orcamento_max)
Critério guloso: avaliacao / custo — receitas com maior custo-benefício entram primeiro.
Acumula receitas em ordem decrescente desse índice enquanto o custo total couber no orçamento.

menu_por_tempo(receitas, tempo_max)
Critério guloso: avaliacao / tempo_preparo — receitas mais eficientes em tempo entram primeiro.
Acumula receitas enquanto o tempo total couber no limite definido.

menu_por_ingredientes(receitas, ingredientes, n)
Critério guloso: ingredientes_em_comum / total_ingredientes — receitas que mais aproveitam o que está disponível entram primeiro.
Retorna as N receitas com maior compatibilidade.

Aplicado em:
Módulo 5 (Recomendação do Chef)
Modo Chef (todas as opções)

Modos de Interação

Modo Consulta Rápida
Recuperação eficiente de receitas por diferentes critérios:

Busca por ID — usa Tabela Hash por_id, O(1)
Busca por prefixo de nome — usa Trie, O(M)
Filtro por categoria — usa Tabela Hash por_categoria, O(1)
Busca por ingrediente — usa Tabela Hash por_ingrediente, O(1)

Modo Chef
Recomendação de receitas e montagem de menus com base em restrições:

Menu por orçamento máximo
Menu por tempo máximo disponível
Menu pelos ingredientes que o chef tem em mãos

Modo Investigação
Verificação de integridade das receitas armazenadas:

Verificar receita específica — compara SHA-256 atual com o original registrado na carga
Auditar todas as receitas — percorre todas e lista as corrompidas
Detectar conteúdo duplicado — agrupa receitas por assinatura e identifica grupos com mais de uma entrada
Sabotar receita — altera o nome de uma receita para simular adulteração (persiste até restaurar)
Restaurar receita sabotada — reverte a alteração e confirma que a assinatura volta a bater

Como funciona a integridade:
No momento do carregamento, o sistema calcula o SHA-256 de cada receita a partir de nome, categoria, ingredientes ordenados e tempo de preparo, e armazena essa assinatura em uma Tabela Hash dedicada. A qualquer momento, recalcular o SHA-256 e comparar com o valor guardado revela se a receita foi alterada.