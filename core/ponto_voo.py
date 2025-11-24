# core/ponto_voo.py
import random
import math

def calcular_distancia(coord1: tuple, coord2: tuple) -> float:
    """Calcula a distância euclidiana entre dois pontos (células do mapa)."""
    x1, y1 = coord1
    x2, y2 = coord2
    # Teorema de Pitágoras: sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class PontoDeVoo:
    """Representa os dados coletados em uma célula do mapa (o dado do nó da sub-lista)."""
    def __init__(self, x, y, nivel_bateria, **environmental_data):
        self.coordenadas = (x, y)
        self.nivel_bateria = nivel_bateria # Recebido do drone

        # Dados de Telemetria (gerados aleatoriamente ou fixos)
        self.altitude = random.randint(30, 150)
        self.velocidade = random.randint(5, 30)
        self.direcao_vento = random.choice(["N", "NE", "E", "SE", "S", "SO", "O", "NO"])
        self.temperatura_ambiente = random.randint(15, 35)
        self.status_carga = random.choice(["com pacote", "sem pacote"])
        self.status_camera = random.choice(["ligada", "desligada"])
        self.num_fotos_registradas = random.randint(0, 5)

        # Dados do Ambiente Sobrevoado (recebidos da lógica do mapa)
        self.tipo_area = environmental_data.get("tipo_area", "desconhecida")
        self.densidade_populacional = environmental_data.get("densidade_populacional", 0)
        self.presenca_areas_verdes = environmental_data.get("presenca_areas_verdes", 0)
        self.indice_poluicao_ar = environmental_data.get("indice_poluicao_ar", 0)
        self.presenca_construcoes_altas = environmental_data.get("presenca_construcoes_altas", "não")
        self.sinal_gps = environmental_data.get("sinal_gps", "forte")
        self.intensidade_ruido = environmental_data.get("intensidade_ruido", 50)


    def gerar_telemetria_aleatoria(self, current_battery):
        """Atualiza dados de telemetria baseados no estado atual do drone."""
        self.nivel_bateria = max(0, current_battery) # Garante que a bateria final seja o valor correto

    def categoria_poluicao(self):
        """Retorna a categoria e a cor da poluição do ar com base no índice."""
        p = self.indice_poluicao_ar
        if p <= 40:
            return "Ótima", "#00FF00"
        elif 41 <= p <= 80:
            return "Moderada", "#FFFF00"
        elif 81 <= p <= 120:
            return "Insalubre (sensíveis)", "#FFA500"
        elif 121 <= p <= 200:
            return "Insalubre", "#FF0000"
        elif 201 <= p <= 300:
            return "Muito insalubre", "#800080"
        else:
            return "Perigosa", "#8B0000"

    def __str__(self):
        return f"Ponto({self.coordenadas[0]},{self.coordenadas[1]}) - Bateria: {self.nivel_bateria:.1f}%"