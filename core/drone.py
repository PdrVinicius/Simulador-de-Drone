# core/drone.py
from core.lista_encadeada import ListaEncadeada
from core.missao import Missao
import random 

class Drone:
    """Representa a entidade Drone e seu histórico de missões."""
    def __init__(self, identificador: str, modelo: str):
        self.identificador = identificador
        self.modelo = modelo
        self.imagem_path = "drone.png"
        # LISTA ENCADEDA PRINCIPAL: Armazena o histórico de Missões
        self.missoes = ListaEncadeada() 
        self.missao_ativa = None
        self.bateria = 100 # Nível inicial da bateria (0-100%)
        self.initial_battery = 100 # Para resetar após a missão

    def iniciar_missao(self, tipo_missao: str):
        if self.missao_ativa is not None:
            return "⚠️ Já existe uma missão em andamento. Finalize antes de iniciar outra."

        self.bateria = self.initial_battery # Reseta a bateria para nova missão
        nova = Missao(tipo_missao)
        self.missao_ativa = nova
        return f"🚀 Missão '{tipo_missao}' iniciada com sucesso."

    def registrar_ponto_voo(self, x: int, y: int, environmental_data):
        if not self.missao_ativa:
            return "❌ Nenhuma missão ativa para registrar ponto."
        
        # Simula consumo de bateria
        consumo = random.uniform(0.5, 2.0)
        self.bateria = max(0, self.bateria - consumo)

        # Chama a inserção do nó de ponto de voo na sub-lista
        self.missao_ativa.registrar_ponto(x, y, self.bateria, environmental_data)
        return "Ponto de voo registrado."

    def finalizar_missao(self):
        if not self.missao_ativa:
            return "❌ Nenhuma missão ativa para finalizar."

        self.missao_ativa.finalizar_missao()
        # Insere a missão concluída na Lista Encadeada Principal
        self.missoes.inserir_final(self.missao_ativa)
        missao_finalizada_tipo = self.missao_ativa.tipo
        self.missao_ativa = None
        return f"✅ Missão '{missao_finalizada_tipo}' finalizada com sucesso."

    def __str__(self):
        return f"🛸 Drone {self.identificador} - Modelo: {self.modelo}"