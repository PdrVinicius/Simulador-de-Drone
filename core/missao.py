# core/missao.py
from core.lista_encadeada import ListaEncadeada
from core.ponto_voo import PontoDeVoo, calcular_distancia
from datetime import datetime
import time
import random 

class Missao:
    """Gerencia o ciclo de vida e o histórico de uma única missão."""
    def __init__(self, tipo: str):
        self.id = str(int(time.time() * 1000) + random.randint(0, 999)) # ID único baseado no timestamp
        self.tipo = tipo
        self.data_inicio = datetime.now()
        self.data_fim = None
        # LISTA ENCADEDA ANINHADA: Armazena a sequência de PontosDeVoo
        self.pontos_voo = ListaEncadeada() 

    def registrar_ponto(self, x, y, nivel_bateria, environmental_data):
        """Cria e insere um novo PontoDeVoo no final da Lista Encadeada."""
        ponto = PontoDeVoo(x, y, nivel_bateria=nivel_bateria, **environmental_data)
        self.pontos_voo.inserir_final(ponto)

    def finalizar_missao(self):
        self.data_fim = datetime.now()

    def tempo_total(self):
        fim = self.data_fim if self.data_fim else datetime.now()
        return (fim - self.data_inicio).total_seconds()

    def gerar_relatorio(self):
        """
        Gera o relatório percorrendo a Lista Encadeada de Pontos de Voo (self.pontos_voo).
        Isto prova o uso da ED para cálculo de estatísticas.
        """
        if self.pontos_voo.esta_vazia():
            return {"Relatório": "Nenhum ponto registrado."}
        
        atual = self.pontos_voo.inicio
        anterior = None
        
        # Variáveis acumuladoras (necessárias pelo percurso)
        distancia_total = 0.0
        soma_poluicao = 0.0
        soma_densidade = 0.0
        soma_vegetacao = 0.0
        bateria_inicial = self.pontos_voo.inicio.dado.nivel_bateria
        bateria_final = self.pontos_voo.fim.dado.nivel_bateria
        contador = 0
        
        pol_categoria_freq = {} # Usado para o relatório de insalubridade

        while atual:
            ponto_atual = atual.dado
            
            # Cálculo da Distância (requer o ponto anterior)
            if anterior:
                ponto_anterior = anterior.dado
                distancia = calcular_distancia(ponto_anterior.coordenadas, ponto_atual.coordenadas)
                distancia_total += distancia
            
            # Acumuladores de Média
            soma_poluicao += ponto_atual.indice_poluicao_ar
            soma_densidade += ponto_atual.densidade_populacional
            soma_vegetacao += ponto_atual.presenca_areas_verdes
            
            # Frequência de Poluição
            categoria, _ = ponto_atual.categoria_poluicao()
            pol_categoria_freq[categoria] = pol_categoria_freq.get(categoria, 0) + 1
            
            anterior = atual
            atual = atual.proximo
            contador += 1
            
        # --- CÁLCULOS FINAIS ---
        consumo_total = bateria_inicial - bateria_final
        eficiencia_energetica = consumo_total / distancia_total if distancia_total > 0 else 0
        
        categorias = " | ".join([
            f"{k}: {v}" for k, v in pol_categoria_freq.items() if v > 0
        ])

        return {
            "ID da Missão": self.id,
            "Tipo de Missão": self.tipo,
            "Duração (s)": round(self.tempo_total(), 2),
            "Pontos Coletados": contador,
            "Distância percorrida (unidades)": f"{distancia_total:.2f}",
            "Bateria consumida (%)": round(consumo_total, 2),
            "Eficiência energética (Consumo/Distância)": f"{eficiencia_energetica:.4f} %/unidade",
            "Média Poluição (AQI)": round(soma_poluicao / contador, 2),
            "Média densidade populacional": round(soma_densidade / contador, 2),
            "Área média com vegetação (%)": round(soma_vegetacao / contador, 2),
            "Distribuição da Qualidade do Ar": categorias
        }