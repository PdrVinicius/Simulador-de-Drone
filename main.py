# main.py
import tkinter as tk
# Importamos APENAS a classe principal da Interface
from gui.interface import InterfaceDrone 

if __name__ == "__main__":
    # 1. Cria a janela raiz do Tkinter
    root = tk.Tk()
    root.geometry("800x700")
    
    # 2. Instancia a classe InterfaceDrone, passando a janela raiz (root)
    app = InterfaceDrone(root) 
    
    # 3. Inicia o loop de eventos da interface gráfica
    root.mainloop()