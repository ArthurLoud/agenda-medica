from tkinter import StringVar
from ttkbootstrap import ttk
from tkinter import Entry
import re

from utils import formatar_hora
import db
from consultas_page import abrir_pagina_consultas

class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda de Consultas Médicas")
        self.root.geometry("700x500")

        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill="both", expand=True)

        # Nome do paciente
        ttk.Label(self.frame, text="Nome do Paciente:").grid(row=0, column=0, sticky="w", pady=5)
        self.paciente_var = StringVar()
        self.paciente_entry = ttk.Entry(self.frame, textvariable=self.paciente_var, width=50)
        self.paciente_entry.grid(row=0, column=1, pady=5)

        # Médico
        ttk.Label(self.frame, text="Médico:").grid(row=1, column=0, sticky="w", pady=5)
        self.medico_var = StringVar()
        self.medico_combobox = ttk.Combobox(self.frame, textvariable=self.medico_var, state="readonly", width=47)
        self.medico_combobox['values'] = [m[1] for m in self.carregar_medicos()]
        self.medico_combobox.grid(row=1, column=1, pady=5)

        # Data
        ttk.Label(self.frame, text="Data da Consulta (DD/MM/AAAA):").grid(row=2, column=0, sticky="w", pady=5)
        self.data_var = StringVar()
        self.data_entry = Entry(self.frame, textvariable=self.data_var, width=50)
        self.data_entry.grid(row=2, column=1, pady=5)
        self.data_entry.bind("<KeyRelease>", self.formatar_data)

        # Hora
        ttk.Label(self.frame, text="Hora (HH:MM):").grid(row=3, column=0, sticky="w", pady=5)
        self.hora_var = StringVar()
        self.hora_entry = ttk.Entry(self.frame, textvariable=self.hora_var, width=50)
        self.hora_entry.grid(row=3, column=1, pady=5)

        # Status
        self.status_label = ttk.Label(self.frame, text="", bootstyle="warning")
        self.status_label.grid(row=4, columnspan=2, pady=10)

        # Botão Agendar
        self.botao_agendar = ttk.Button(self.frame, text="Agendar Consulta", command=self.agendar)
        self.botao_agendar.grid(row=5, columnspan=2, pady=10)

        # Botão Ver Consultas
        self.botao_consultas = ttk.Button(self.frame, text="Ver Consultas", command=lambda: abrir_pagina_consultas(self.root))
        self.botao_consultas.grid(row=6, columnspan=2, pady=5)

        # Cadastrar novo médico
        ttk.Label(self.frame, text="Cadastrar Novo Médico:").grid(row=7, column=0, sticky="w", pady=5)
        self.novo_medico_var = StringVar()
        self.novo_medico_entry = ttk.Entry(self.frame, textvariable=self.novo_medico_var, width=50)
        self.novo_medico_entry.grid(row=7, column=1, pady=5)

        self.botao_cadastrar_medico = ttk.Button(self.frame, text="Cadastrar Médico", command=self.cadastrar_medico)
        self.botao_cadastrar_medico.grid(row=8, column=1, sticky="e", pady=5)

    def carregar_medicos(self):
        with db.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicos")
            self.medicos = cursor.fetchall()
        return self.medicos

    def formatar_data(self, event=None):
        texto = self.data_var.get()
        cursor_pos = self.data_entry.index("insert")
        texto_limpo = re.sub(r'\D', '', texto)

        novo = ''
        if len(texto_limpo) > 0:
            novo += texto_limpo[:2]
        if len(texto_limpo) > 2:
            novo += '/' + texto_limpo[2:4]
        if len(texto_limpo) > 4:
            novo += '/' + texto_limpo[4:8]

        self.data_var.set(novo)

        # Ajustar o cursor após digitar /
        novo_cursor = cursor_pos
        if cursor_pos in [2, 5]:
            novo_cursor += 1
        self.data_entry.icursor(min(novo_cursor, len(novo)))

    def limpar_campos(self):
        self.paciente_var.set("")
        self.medico_var.set("")
        self.data_var.set("")
        self.hora_var.set("")

    def agendar(self):
        paciente = self.paciente_var.get()
        medico_nome = self.medico_var.get()
        data_str = self.data_var.get()
        hora_str = self.hora_var.get()

        # Formatar hora
        hora = formatar_hora(hora_str)

        # Validar formato da hora
        if not re.match(r'^\d{2}:\d{2}$', hora):
            self.status_label.config(text="Hora inválida. Use formato HH:MM.", bootstyle="danger")
            return

        # Validar hora cheia
        minutos = hora.split(":")[1]
        if minutos != "00":
            self.status_label.config(text="Horário deve ser na hora cheia (ex: 09:00, 10:00).", bootstyle="danger")
            return

        # Validar data
        try:
            dia, mes, ano = map(int, data_str.split("/"))
            data = f"{ano:04d}-{mes:02d}-{dia:02d}"
        except ValueError:
            self.status_label.config(text="Data inválida. Use o formato DD/MM/AAAA.", bootstyle="danger")
            return

        if not all([paciente, medico_nome, data, hora]):
            self.status_label.config(text="Preencha todos os campos.", bootstyle="danger")
            return

        # Buscar ID do médico
        medico_id = [m[0] for m in self.medicos if m[1] == medico_nome][0]

        sucesso = db.agendar_consulta(paciente, medico_id, data, hora)
        if sucesso:
            self.status_label.config(text="Consulta agendada com sucesso!", bootstyle="success")
            self.limpar_campos()
        else:
            self.status_label.config(text="Horário indisponível.", bootstyle="danger")

    def cadastrar_medico(self):
        nome = self.novo_medico_var.get().strip()
        if not nome:
            self.status_label.config(text="Digite o nome do médico.", bootstyle="warning")
            return

        try:
            with db.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO medicos (nome) VALUES (%s)", (nome,))
                conn.commit()
        except Exception as e:
            self.status_label.config(text=f"Erro: {e}", bootstyle="danger")
            return

        self.status_label.config(text="Médico cadastrado com sucesso!", bootstyle="success")
        self.novo_medico_var.set("")
        self.medico_combobox['values'] = [m[1] for m in self.carregar_medicos()]
        self.medico_combobox.current(0)
