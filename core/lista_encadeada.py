# core/lista_encadeada.py

class No:
    """Representa um nó em uma lista encadeada."""
    def __init__(self, dado):
        self.dado = dado
        self.proximo = None

class ListaEncadeada:
    """Implementação manual da Lista Encadeada."""
    def __init__(self):
        self.inicio = None
        self.fim = None # Ponteiro para fim otimiza 'inserir_final'

    def esta_vazia(self) -> bool:
        return self.inicio is None

    def inserir_final(self, dado):
        """Insere um novo nó no final da lista. O(1) se usar self.fim."""
        novo_no = No(dado)
        if self.esta_vazia():
            self.inicio = novo_no
            self.fim = novo_no
        else:
            # Manipulação explícita do ponteiro 'next'
            self.fim.proximo = novo_no
            self.fim = novo_no

    def remover(self, dado) -> bool:
        """Remove o primeiro nó com o dado especificado."""
        if self.esta_vazia():
            return False
        
        atual = self.inicio
        anterior = None
        
        while atual:
            # Assumindo que o dado tem um atributo 'id' para comparação (usado em Missao)
            if hasattr(atual.dado, 'id') and atual.dado.id == dado.id:
                if anterior is None:
                    self.inicio = atual.proximo
                    if self.inicio is None:
                        self.fim = None
                else:
                    anterior.proximo = atual.proximo
                    if atual.proximo is None:
                        self.fim = anterior
                return True
            anterior = atual
            atual = atual.proximo
        return False

    def to_list(self):
        """Converte a lista encadeada em uma lista Python (para relatórios ou GUI)."""
        items = []
        current = self.inicio
        while current:
            items.append(current.dado)
            current = current.proximo
        return items

    def tamanho(self) -> int:
        contador = 0
        atual = self.inicio
        while atual:
            contador += 1
            atual = atual.proximo
        return contador