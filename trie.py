class TrieNode:
    def __init__(self):
        self.filhos = {}
        self.fim_palavra = False
        self.receitas_ids = []

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def inserir(self, nome, id_receita):
        nome = nome.lower().strip()
        node = self.root

        for char in nome:
            if char not in node.filhos:
                node.filhos[char] = TrieNode()
            node = node.filhos[char]

        node.fim_palavra = True
        if id_receita not in node.receitas_ids:
            node.receitas_ids.append(id_receita)
    
    def busca_prefixo(self, prefixo): 
        prefixo = prefixo.lower().strip()
        node_prefixo = self.navegar(prefixo)

        if node_prefixo is None:
            return []
        
        resultados = []
        self.palavras(node_prefixo, prefixo, resultados)
        return resultados
    
    def navegar(self, texto):
        node = self.root

        for char in texto:
            if char not in node.filhos:
                return None
            node = node.filhos[char]

        return node
    
    def palavras(self, node, prefixo_atual, resultados):
        if node.fim_palavra:
            resultados.append((prefixo_atual, node.receitas_ids.copy()))
        
        for char, filho in sorted(node.filhos.items()):
            self.palavras(filho, prefixo_atual + char, resultados)
