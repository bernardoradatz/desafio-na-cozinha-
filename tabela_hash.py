import hashlib

class TabelaHash:
    def __init__(self, capacidade=101):
        self.capacidade = capacidade
        self.buckets = []
        for i in range(capacidade):
            self.buckets.append([])
        self.tamanho = 0

    def hash(self, chave):
        h = 0
        for c in str(chave):
            h = (h * 31 + ord(c)) % self.capacidade
        return h
    
    def inserir(self, chave, valor):
        idx = self.hash(chave)
        bucket = self.buckets[idx]

        for par in bucket:
            if par[0] == chave:
                par[1] = valor
                return
        bucket.append([chave, valor])
        self.tamanho += 1

        if self.tamanho / self.capacidade > 0.75:
            self.rehash()

    def rehash(self):
        antiga = self.buckets
        self.capacidade = self.capacidade *2 + 1

        self.buckets = []
        for i in range(self.capacidade):
            self.buckets.append([])
        self.tamanho = 0

        for bucket in antiga:
             for chave, valor in bucket:
                 self.inserir(chave, valor)

    def buscar(self, chave):
        idx = self.hash(chave)
        for par in self.buckets[idx]:
            if par[0] == chave:
                return par[1]
        return None
    def remover(self, chave):
        idx = self.hash(chave)
        bucket = self.buckets[idx]

        tamanho_bucket = len(bucket)
        for i in range(tamanho_bucket):
            par = bucket[i]
            if par[0] == chave:
                bucket.pop(i)
                self.tamanho -= 1
                return True
        return False
    
    def todos_valores(self):
            resultado = []
            for bucket in self.buckets:
                for chave, valor in bucket:
                    resultado.append(valor)
            return resultado
    
    def fator_carga(self):
        return self.tamanho / self.capacidade

    def estatisticas(self):
        gavetas_ocupadas = 0
        max_colisoes = 0
        
        for bucket in self.buckets:
            tamanho_bucket = len(bucket)
            if tamanho_bucket > 0:
                gavetas_ocupadas += 1
                if tamanho_bucket > max_colisoes:
                    max_colisoes = tamanho_bucket

        return {
            "total_receitas": self.tamanho,
            "gavetas_totais": self.capacidade,
            "fator_de_carga": round(self.fator_carga(), 3),
            "gavetas_usadas": gavetas_ocupadas,
            "pior_colisao": max_colisoes,
        }

class TabelaHashIntegridade:
    def __init__(self):
        self.tabela = TabelaHash(capacidade=53)

    def _gerar_assinatura(self, receita):
        ingredientes_ord = "".join(sorted(receita.ingredientes))
        texto = f"{receita.nome}{receita.categoria}{ingredientes_ord}{receita.tempo_preparo}"
        
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()

    def guardar_original(self, receita):
        assinatura = self._gerar_assinatura(receita)
        self.tabela.inserir(str(receita.id), assinatura)

    def verificar_se_foi_sabotada(self, receita):
        assinatura_original = self.tabela.buscar(str(receita.id))
        assinatura_atual = self._gerar_assinatura(receita)
        
        return assinatura_original == assinatura_atual