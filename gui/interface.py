# gui/interface.py
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import random
import time
import math
import os
from PIL import Image, ImageTk

# IMPORTAR CLASSES DO CORE
from core.drone import Drone
from core.missao import Missao
from core.lista_encadeada import ListaEncadeada
from core.ponto_voo import PontoDeVoo, calcular_distancia 

# Configurações de Mapa e Células
LARGURA_MAPA = 17 
ALTURA_MAPA = 10   
MAP_TYPES = ["Urbano", "Rural", "Misto"]

class InterfaceDrone:
    """Interface gráfica principal com design de Abas (ttk.Notebook)."""

    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Missão de Drones")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50") 

        # Configurações de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook.Tab', font=('Inter', 12, 'bold'), padding=[10, 5])
        self.style.configure('TFrame', background='#34495e')
        self.style.configure('TButton', font=('Inter', 12, 'bold'), background='#42A5F5', foreground='white', borderwidth=0, padding=12)
        
        # ESTILO DAS SETAS (Botões de Navegação) - AZUL ELÉTRICO
        # A lógica de borda arredondada que causava o TclError foi REMOVIDA.
        self.style.configure('Arrow.TButton', 
                             font=('Inter', 16, 'bold'), 
                             background='#007BFF',   # Azul Elétrico Base
                             foreground='black',      # Cor do Texto (Seta)
                             width=4)
        self.style.map('Arrow.TButton', 
                       background=[('active', '#0056B3')], # Azul Escuro (Ao Clicar)
                       relief=[('pressed', 'groove')])

        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='green', thickness=20)
        self.style.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange', thickness=20)
        self.style.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness=20)

        # Gerenciamento de Drones
        self.drones = {
            "DRN001": Drone("DRN001", "Phantom Vision"),
            "DRN002": Drone("DRN002", "Mavic Explorer")
        }
        self.drone_selecionado_id = "DRN001"
        self.drone = self.drones[self.drone_selecionado_id]
        
        # Posição inicial do drone 
        self.x, self.y = LARGURA_MAPA // 2, ALTURA_MAPA // 2 

        # Mapa de dados ambientais
        self.map_type = MAP_TYPES[0]
        self.environmental_map_data = {}
        self._initialize_environmental_map(self.map_type)

        # Estrutura principal com Abas (Notebook)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Inicializa as abas
        self.tab_simulacao = ttk.Frame(self.notebook, padding=10, style='TFrame')
        self.tab_telemetria = ttk.Frame(self.notebook, padding=10, style='TFrame')
        self.tab_relatorios = ttk.Frame(self.notebook, padding=10, style='TFrame')
        
        self.notebook.add(self.tab_simulacao, text="Simulação & Controle")
        self.notebook.add(self.tab_telemetria, text="Telemetria & Status")
        self.notebook.add(self.tab_relatorios, text="Relatórios & Histórico")
        
        self._setup_simulacao_tab()
        self._setup_telemetria_tab()
        self._setup_relatorios_tab()

        self.on_canvas_resize(None)
        self.update_telemetry_display()
        self.exibir_relatorio(initial_load=True)

    def _setup_simulacao_tab(self):
        # Frame do Canvas (Mapa)
        self.canvas_frame = ttk.Frame(self.tab_simulacao, padding=5, relief="raised")
        self.canvas_frame.pack(side=tk.TOP, expand=True, fill='both')

        self.canvas = tk.Canvas(self.canvas_frame, bg="#FFFFFF", bd=0, relief="flat", highlightthickness=0)
        self.canvas.pack(expand=True, fill='both')
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_map_click)

        # Frame de Controles (abaixo do mapa)
        self.control_frame = ttk.Frame(self.tab_simulacao, padding=10, style='TFrame')
        self.control_frame.pack(side=tk.BOTTOM, fill='x', pady=10)
        self.control_frame.grid_columnconfigure(0, weight=1); self.control_frame.grid_columnconfigure(1, weight=1)
        self.control_frame.grid_columnconfigure(2, weight=1); self.control_frame.grid_columnconfigure(3, weight=1)

        # Seleção de Mapa
        ttk.Label(self.control_frame, text="Tipo de Mapa:", font=('Inter', 10, 'bold'), background='#34495e', foreground='#E0E0E0').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.map_combobox = ttk.Combobox(self.control_frame, values=MAP_TYPES, state="readonly", font=('Inter', 10), width=18)
        self.map_combobox.set(self.map_type)
        self.map_combobox.bind("<<ComboboxSelected>>", self.on_map_select)
        self.map_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Botões de Ação
        ttk.Button(self.control_frame, text="Iniciar Missão", command=self.iniciar_missao).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(self.control_frame, text="Finalizar Missão", command=self.finalizar_missao).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Controles de Navegação (Centralizados)
        nav_frame = ttk.Frame(self.control_frame, style='TFrame')
        nav_frame.grid(row=1, column=1, columnspan=2, pady=10)
        
        ttk.Button(nav_frame, text="↑", command=lambda: self.mover_drone(0, -1), style='Arrow.TButton').grid(row=0, column=1)
        ttk.Button(nav_frame, text="←", command=lambda: self.mover_drone(-1, 0), style='Arrow.TButton').grid(row=1, column=0)
        ttk.Label(nav_frame, text="MANUAL", background='#34495e', foreground='white', anchor='center').grid(row=1, column=1, padx=5)
        ttk.Button(nav_frame, text="→", command=lambda: self.mover_drone(1, 0), style='Arrow.TButton').grid(row=1, column=2)
        ttk.Button(nav_frame, text="↓", command=lambda: self.mover_drone(0, 1), style='Arrow.TButton').grid(row=2, column=1)

        ttk.Button(self.control_frame, text="Simulação Automática", command=self.simular_movimento_automatico).grid(row=2, column=0, columnspan=1, padx=5, pady=5, sticky="ew")


    def _setup_telemetria_tab(self):
        # Configuração da Aba 2: Telemetria & Status
        drone_select_frame = ttk.Frame(self.tab_telemetria, style='TFrame', padding=5)
        drone_select_frame.pack(fill='x', pady=10)
        ttk.Label(drone_select_frame, text="Drone Ativo:", font=('Inter', 12, 'bold'), background='#34495e', foreground='#E0E0E0').pack(side=tk.LEFT, padx=10)
        self.drone_combobox = ttk.Combobox(drone_select_frame, values=list(self.drones.keys()), state="readonly", font=('Inter', 10), width=15)
        self.drone_combobox.set(self.drone_selecionado_id)
        self.drone_combobox.bind("<<ComboboxSelected>>", self.on_drone_select)
        self.drone_combobox.pack(side=tk.LEFT, padx=10)
        
        battery_panel = ttk.Frame(self.tab_telemetria, padding=10, relief="groove")
        battery_panel.pack(fill='x', pady=10)
        ttk.Label(battery_panel, text="Nível de Bateria", font=('Inter', 14, 'bold'), background='#34495e', foreground='white').pack()
        self.battery_progressbar = ttk.Progressbar(battery_panel, orient="horizontal", length=300, mode="determinate", style="green.Horizontal.TProgressbar")
        self.battery_progressbar.pack(pady=10, fill='x')
        self.battery_label = ttk.Label(battery_panel, text="Bateria: 100%", font=('Inter', 12, 'bold'), background='#34495e', foreground='#E0E0E0')
        self.battery_label.pack()

        # Painel de Dados de Telemetria
        telemetry_grid = ttk.Frame(self.tab_telemetria, padding=10, relief="groove")
        telemetry_grid.pack(fill='both', expand=True, pady=10)
        ttk.Label(telemetry_grid, text="Dados de Telemetria (Último Ponto)", font=('Inter', 14, 'bold'), background='#34495e', foreground='white').grid(row=0, column=0, columnspan=2, pady=10)
        
        self.telemetry_labels = {}
        telemetry_fields = ["Altitude", "Velocidade", "Vento", "Carga", "Câmera", "Fotos", "Coordenadas", "Tipo de Área", "Poluição (AQI)"]
        for i, field in enumerate(telemetry_fields):
            row = i // 2 + 1
            col = i % 2
            
            ttk.Label(telemetry_grid, text=f"{field}:", font=('Inter', 10, 'bold'), anchor="w", background='#34495e', foreground='#E0E0E0').grid(row=row, column=col*2, padx=10, pady=5, sticky="w")
            label_value = ttk.Label(telemetry_grid, text="N/A", font=('Inter', 10), anchor="w", background='#34495e', foreground='white')
            label_value.grid(row=row, column=col*2 + 1, padx=10, pady=5, sticky="w")
            self.telemetry_labels[field] = label_value
            telemetry_grid.grid_columnconfigure(col*2, weight=1)

    def _setup_relatorios_tab(self):
        # Configuração da Aba 3: Relatórios & Histórico
        ttk.Label(self.tab_relatorios, text="Histórico de Missões Finalizadas", font=('Inter', 16, 'bold'), background='#34495e', foreground='white').pack(pady=10)

        report_frame = ttk.Frame(self.tab_relatorios, style='TFrame')
        report_frame.pack(expand=True, fill='both', pady=10)
        
        self.report_text = tk.Text(report_frame, wrap="word", bg="#FFFFFF", fg="black", font=('Inter', 10), bd=0, relief="flat", padx=10, pady=10)
        self.report_text.pack(side=tk.LEFT, expand=True, fill='both')

        scrollbar = ttk.Scrollbar(report_frame, command=self.report_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.report_text.config(yscrollcommand=scrollbar.set)
        
        ttk.Button(self.tab_relatorios, text="Atualizar Relatórios", command=self.exibir_relatorio).pack(pady=5)


    # Lógica do mapa e geração de dados
    def _initialize_environmental_map(self, map_type):
        """Inicializa os dados ambientais para cada célula do mapa baseado no tipo."""
        map_data = {}
        areas_possiveis = ["urbana", "residencial", "industrial", "rural", "mata", "zona de risco"]
        
        if map_type == "Urbano":
            weights = [40, 20, 30, 5, 0, 5] # Maior chance de Urbano
        elif map_type == "Rural":
            weights = [5, 5, 0, 50, 35, 5] # Maior chance de Rural
        else: # Misto
            weights = [15, 15, 15, 20, 20, 15] # Distribuição uniforme

        for r in range(ALTURA_MAPA):
            for c in range(LARGURA_MAPA):
                area = random.choices(areas_possiveis, weights=weights, k=1)[0]
                
                # Definir base de poluição e densidade com base no tipo de área
                if area == "industrial":
                    poluicao_base = random.randint(150, 350)
                    densidade_base = random.randint(500, 1500)
                elif area == "mata":
                    poluicao_base = random.randint(10, 50)
                    densidade_base = random.randint(1, 10)
                else:
                    poluicao_base = random.randint(50, 150)
                    densidade_base = random.randint(50, 500)

                env_data = {
                    "tipo_area": area,
                    "densidade_populacional": densidade_base + random.randint(-50, 50),
                    "presenca_areas_verdes": random.randint(0, 100),
                    "indice_poluicao_ar": poluicao_base + random.randint(-10, 10),
                    "presenca_construcoes_altas": area in ["urbana", "industrial"],
                    "sinal_gps": random.choice(["forte", "fraco", "perdido"]) if area == "zona de risco" else "forte",
                    "intensidade_ruido": random.randint(30, 100)
                }
                map_data[(c, r)] = env_data
        
        self.environmental_map_data = map_data
        
    def on_map_select(self, event):
        """Atualiza o mapa quando o usuário seleciona um novo tipo."""
        new_type = self.map_combobox.get()
        if new_type != self.map_type:
            self.map_type = new_type
            self._initialize_environmental_map(new_type)
            self.desenhar_mapa()
            messagebox.showinfo("Novo Mapa", f"Mapa '{new_type}' carregado. Inicie uma nova missão.")
            # Reposiciona o drone
            self.x, self.y = LARGURA_MAPA // 2, ALTURA_MAPA // 2
            self.drone.missao_ativa = None
            self.drone.bateria = self.drone.initial_battery
            self.update_telemetry_display()


    def desenhar_mapa(self):
        """Renderiza o mapa com o drone (imagem) e pontos visitados."""
        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        cell_size_w = canvas_width / LARGURA_MAPA
        cell_size_h = canvas_height / ALTURA_MAPA
        self.current_cell_size = min(cell_size_w, cell_size_h) 

        offset_x = (canvas_width - (self.current_cell_size * LARGURA_MAPA)) / 2
        offset_y = (canvas_height - (self.current_cell_size * ALTURA_MAPA)) / 2

        default_cell_color = "#FFFFFF" 
        
        # 1. Desenha as células do fundo
        for linha in range(ALTURA_MAPA):
            for coluna in range(LARGURA_MAPA):
                x0 = offset_x + coluna * self.current_cell_size
                y0 = offset_y + linha * self.current_cell_size
                x1 = x0 + self.current_cell_size
                y1 = y0 + self.current_cell_size

                cor_celula = default_cell_color

                if self.drone.missao_ativa:
                    pontos = self.drone.missao_ativa.pontos_voo.to_list()
                    for ponto in pontos:
                        if ponto.coordenadas == (coluna, linha):
                            _, cor_poluicao = ponto.categoria_poluicao()
                            cor_celula = cor_poluicao 
                            break
                    
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=cor_celula, outline="#BDC3C7", width=1) 

        # 2. Desenha o caminho (linha azul)
        if self.drone.missao_ativa and not self.drone.missao_ativa.pontos_voo.esta_vazia():
            path_coords = []
            pontos = self.drone.missao_ativa.pontos_voo.to_list()
            for ponto in pontos:
                px, py = ponto.coordenadas
                path_coords.append(offset_x + px * self.current_cell_size + self.current_cell_size / 2)
                path_coords.append(offset_y + py * self.current_cell_size + self.current_cell_size / 2)
            
            if len(path_coords) >= 4:
                self.canvas.create_line(path_coords, fill="#3F51B5", width=3, smooth=True, tags="drone_path")
                self.canvas.tag_lower("drone_path")

        # 3. 🚁 DESENHAR O DRONE (IMAGEM)
        drone_x_center = offset_x + self.x * self.current_cell_size + self.current_cell_size / 2
        drone_y_center = offset_y + self.y * self.current_cell_size + self.current_cell_size / 2
        
        try:
            # Tenta pegar o caminho definido no drone.py, ou usa "drone.png" como padrão
            caminho_imagem = getattr(self.drone, 'imagem_path', "drone.png")
            
            if not os.path.exists(caminho_imagem):
                raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

            # Carrega e redimensiona
            tamanho_icone = int(self.current_cell_size * 0.8)
            img_original = Image.open(caminho_imagem)
            img_redimensionada = img_original.resize((tamanho_icone, tamanho_icone), Image.Resampling.LANCZOS)
            
            self.drone_icon_img = ImageTk.PhotoImage(img_redimensionada)
            self.canvas.create_image(drone_x_center, drone_y_center, image=self.drone_icon_img, tags="drone_icon")
            
        except Exception as e:
            # Fallback para o triângulo se der erro
            print(f"Usando triângulo. Erro: {e}")
            drone_size = self.current_cell_size * 0.4
            pontos_drone = [
                drone_x_center, drone_y_center - drone_size * 0.8,  
                drone_x_center + drone_size * 0.6, drone_y_center + drone_size * 0.5, 
                drone_x_center - drone_size * 0.6, drone_y_center + drone_size * 0.5  
            ]
            self.canvas.create_polygon(pontos_drone, fill="#FF0000", outline="#8B0000", width=1, tags="drone_icon")
    
    # Lógica de Controle
    def iniciar_missao(self):
        response = self.drone.iniciar_missao("")
        if "⚠️" in response:
            messagebox.showwarning("Aviso", response)
            return

        tipo = simpledialog.askstring("Tipo de Missão", "Digite o tipo da missão:", parent=self.root)
        if not tipo:
            self.drone.missao_ativa = None 
            return

        self.drone.iniciar_missao(tipo)
        self.x, self.y = LARGURA_MAPA // 2, ALTURA_MAPA // 2 
        
        # Registro do Ponto Inicial
        env_data_start = self.environmental_map_data.get((self.x, self.y), {})
        self.drone.registrar_ponto_voo(self.x, self.y, env_data_start) # Insere nó na ED
        
        self.desenhar_mapa()
        self.update_telemetry_display()
        messagebox.showinfo("Sucesso", f"Missão '{tipo}' iniciada com sucesso.")

    def mover_drone(self, dx, dy):
        if self.drone.missao_ativa is None:
            messagebox.showwarning("Erro", "Inicie uma missão primeiro!")
            return
        
        if self.drone.bateria <= 0:
            messagebox.showerror("Bateria Esgotada", "O drone ficou sem bateria e não pode se mover!")
            self.finalizar_missao()
            return

        novo_x = self.x + dx
        novo_y = self.y + dy

        if 0 <= novo_x < LARGURA_MAPA and 0 <= novo_y < ALTURA_MAPA:
            self.x = novo_x
            self.y = novo_y
            
            env_data = self.environmental_map_data.get((self.x, self.y), {})
            self.drone.registrar_ponto_voo(self.x, self.y, env_data) # Insere nó na ED
            self.desenhar_mapa()
            self.update_telemetry_display()
        else:
            messagebox.showwarning("Movimento inválido", "O drone não pode sair do mapa.")

    def simular_movimento_automatico(self):
        if self.drone.missao_ativa is None:
            messagebox.showwarning("Erro", "Inicie uma missão primeiro!")
            return
        
        passos = 15
        
        def _auto_move_step(step_count):
            if step_count >= passos or self.drone.bateria <= 0:
                if self.drone.bateria <= 0:
                    messagebox.showerror("Bateria Esgotada", "A simulação automática foi interrompida: bateria esgotada!")
                    self.finalizar_missao()
                else:
                    messagebox.showinfo("Simulação Concluída", "A simulação automática terminou os passos definidos.")
                return

            # Simula um movimento
            direcoes = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
            direcao = random.choice(direcoes)
            
            novo_x = self.x + direcao[0]
            novo_y = self.y + direcao[1]

            if 0 <= novo_x < LARGURA_MAPA and 0 <= novo_y < ALTURA_MAPA:
                self.x = novo_x
                self.y = novo_y
                env_data = self.environmental_map_data.get((self.x, self.y), {})
                self.drone.registrar_ponto_voo(self.x, self.y, env_data) # Insere nó na ED
                self.desenhar_mapa()
                self.update_telemetry_display()
                self.root.after(300, lambda: _auto_move_step(step_count + 1)) # Pausa de 300ms
            else:
                _auto_move_step(step_count + 1)

        _auto_move_step(0)

    def finalizar_missao(self):
        response = self.drone.finalizar_missao()
        messagebox.showinfo("Missão Finalizada", response)
        self.desenhar_mapa()
        self.update_telemetry_display()
        self.exibir_relatorio() 

    def update_telemetry_display(self):
        # Lógica de atualização da telemetria na Aba 2
        current_drone_obj = self.drone
        current_mission = current_drone_obj.missao_ativa

        self.battery_label.config(text=f"Bateria: {current_drone_obj.bateria:.1f}%")
        self.battery_progressbar['value'] = current_drone_obj.bateria

        if current_drone_obj.bateria > 50:
            self.battery_progressbar.configure(style="green.Horizontal.TProgressbar")
        elif 20 <= current_drone_obj.bateria <= 50:
            self.battery_progressbar.configure(style="orange.Horizontal.TProgressbar")
        else:
            self.battery_progressbar.configure(style="red.Horizontal.TProgressbar")

        if current_mission and not current_mission.pontos_voo.esta_vazia():
            last_ponto = current_mission.pontos_voo.fim.dado
            
            self.telemetry_labels["Coordenadas"].config(text=f"({last_ponto.coordenadas[0]}, {last_ponto.coordenadas[1]})")
            self.telemetry_labels["Altitude"].config(text=f"{last_ponto.altitude}m")
            self.telemetry_labels["Poluição (AQI)"].config(text=f"{last_ponto.indice_poluicao_ar} ({last_ponto.categoria_poluicao()[0]})")
            self.telemetry_labels["Velocidade"].config(text=f"{last_ponto.velocidade} km/h")
            self.telemetry_labels["Vento"].config(text=f"{last_ponto.direcao_vento}")
            self.telemetry_labels["Carga"].config(text=f"{last_ponto.status_carga}")
            self.telemetry_labels["Câmera"].config(text=f"{last_ponto.status_camera}")
            self.telemetry_labels["Fotos"].config(text=f"{last_ponto.num_fotos_registradas}")
            self.telemetry_labels["Tipo de Área"].config(text=last_ponto.tipo_area.title())
            
        else:
            for field in self.telemetry_labels:
                self.telemetry_labels[field].config(text="N/A")

    def exibir_relatorio(self, initial_load=False):
        """Atualiza a área de texto de relatórios na Aba 3."""
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)

        atual = self.drone.missoes.inicio
        if not atual:
            if not initial_load:
                self.report_text.insert(tk.END, "Nenhum relatório disponível para este drone.")
            self.report_text.config(state=tk.DISABLED)
            return

        # Insere todos os relatórios
        i = 1
        while atual:
            # Chama gerar_relatorio(), que percorre a Lista Encadeada
            relatorio = atual.dado.gerar_relatorio() 
            self.report_text.insert(tk.END, f"\n--- Missão {i} ({atual.dado.tipo}) ---\n", "mission_header")
            
            for k, v in relatorio.items():
                self.report_text.insert(tk.END, f"- {k}: {v}\n")
            
            atual = atual.proximo
            i += 1
        
        self.report_text.tag_configure("mission_header", font=('Inter', 12, 'bold'), foreground='#42A5F5')
        self.report_text.config(state=tk.DISABLED)

    def on_canvas_resize(self, event):
        """Redesenha o mapa quando o canvas é redimensionado."""
        self.desenhar_mapa()

    def on_map_click(self, event):
        """Exibe detalhes da célula clicada."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        cell_size_w = canvas_width / LARGURA_MAPA
        cell_size_h = canvas_height / ALTURA_MAPA
        current_cell_size = min(cell_size_w, cell_size_h)

        offset_x = (canvas_width - (current_cell_size * LARGURA_MAPA)) / 2
        offset_y = (canvas_height - (current_cell_size * ALTURA_MAPA)) / 2

        clicked_col = int((event.x - offset_x) / current_cell_size)
        clicked_row = int((event.y - offset_y) / current_cell_size)

        if 0 <= clicked_col < LARGURA_MAPA and 0 <= clicked_row < ALTURA_MAPA:
            self.show_cell_details(clicked_col, clicked_row)
        else:
            messagebox.showinfo("Informação", "Clique dentro dos limites do mapa.")

    def show_cell_details(self, col, row):
        """Exibe uma nova janela com detalhes da célula clicada."""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalhes da Célula ({col}, {row})")
        details_window.transient(self.root)
        details_window.grab_set()
        details_window.resizable(False, False)
        details_window.configure(bg="#2c3e50")

        details_frame = ttk.Frame(details_window, style='TFrame', padding=20)
        details_frame.pack(expand=True, fill='both')

        ttk.Label(details_frame, text="Dados Ambientais:", font=('Inter', 14, 'bold'), background='#34495e', foreground='white').pack(pady=5, anchor="w")
        env_data = self.environmental_map_data.get((col, row), {})
        
        # Lógica de exibição de dados ambientais
        for key, value in env_data.items():
            display_key = key.replace('_', ' ').title()
            if "populacional" in key:
                display_value = f"{value} hab/km²"
            elif "areas_verdes" in key:
                display_value = f"{value}%"
            elif "poluicao_ar" in key:
                ponto_temp = PontoDeVoo(0,0,indice_poluicao_ar=value, **env_data)
                display_value = f"{value} ({ponto_temp.categoria_poluicao()[0]})"
            elif "ruido" in key:
                display_value = f"{value} dB"
            else:
                display_value = value
            ttk.Label(details_frame, text=f"- {display_key}: {display_value}", font=('Inter', 10), background='#34495e', foreground='#E0E0E0').pack(anchor="w", padx=10)

        close_button = ttk.Button(details_frame, text="Fechar", command=details_window.destroy)
        close_button.pack(pady=15)
        
    def on_drone_select(self, event):
        """Atualiza o drone ativo quando um novo é selecionado no combobox."""
        selected_id = self.drone_combobox.get()
        if selected_id in self.drones:
            self.drone_selecionado_id = selected_id
            self.drone = self.drones[selected_id]
            self.x, self.y = LARGURA_MAPA // 2, ALTURA_MAPA // 2 
            self.desenhar_mapa()
            self.update_telemetry_display()
            messagebox.showinfo("Drone Selecionado", f"Drone '{selected_id}' selecionado com sucesso.")