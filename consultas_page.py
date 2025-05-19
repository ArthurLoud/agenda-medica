from tkinter import Toplevel, StringVar, END
from ttkbootstrap import ttk
import db
from utils import formatar_hora

def abrir_pagina_consultas(master):
    janela = Toplevel(master)
    janela.title("Consultas Agendadas")
    janela.geometry("700x500")

    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Médico:").grid(row=0, column=0, sticky="w", pady=5)
    medico_var = StringVar()
    medico_combobox = ttk.Combobox(frame, textvariable=medico_var, state="readonly", width=40)

    with db.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medicos")
        medicos = cursor.fetchall()

    medico_combobox['values'] = ["Todos"] + [m[1] for m in medicos]
    medico_combobox.grid(row=0, column=1, pady=5)
    medico_combobox.current(0)  # Default: "Todos"

    lista_consultas = ttk.Treeview(frame, columns=("ID", "Paciente", "Médico", "Data", "Hora"), show="headings", height=12)
    lista_consultas.grid(row=1, column=0, columnspan=2, pady=10)

    for col in ("ID", "Paciente", "Médico", "Data", "Hora"):
        lista_consultas.heading(col, text=col)

    def carregar_consultas(*_):
        for item in lista_consultas.get_children():
            lista_consultas.delete(item)

        nome_medico = medico_var.get()

        with db.conectar() as conn:
            cursor = conn.cursor()
            if nome_medico == "Todos":
                cursor.execute("""
                    SELECT c.id, c.paciente, m.nome, c.data, c.hora
                    FROM consultas c
                    JOIN medicos m ON c.medico_id = m.id
                    ORDER BY c.data, c.hora
                """)
            else:
                medico_id = [m[0] for m in medicos if m[1] == nome_medico][0]
                cursor.execute("""
                    SELECT c.id, c.paciente, m.nome, c.data, c.hora
                    FROM consultas c
                    JOIN medicos m ON c.medico_id = m.id
                    WHERE c.medico_id = %s
                    ORDER BY c.data, c.hora
                """, (medico_id,))

            consultas = cursor.fetchall()

        for c in consultas:
            lista_consultas.insert("", END, values=c)

    def cancelar():
        selecionado = lista_consultas.selection()
        if selecionado:
            consulta_id = lista_consultas.item(selecionado[0])['values'][0]
            db.cancelar_consulta(consulta_id)
            carregar_consultas()
            status_label.config(text="Consulta cancelada com sucesso.", bootstyle="danger")

    def alterar():
        selecionado = lista_consultas.selection()
        if not selecionado:
            status_label.config(text="Selecione uma consulta para alterar.", bootstyle="warning")
            return

        item = lista_consultas.item(selecionado[0])
        consulta_id = item['values'][0]
        data_atual = item['values'][3]
        hora_atual = item['values'][4]

        nova_data = nova_data_var.get().strip()
        nova_hora = nova_hora_var.get().strip()

        nova_data = nova_data if nova_data else data_atual
        nova_hora = formatar_hora(nova_hora) if nova_hora else hora_atual

        sucesso = db.alterar_consulta(consulta_id, nova_data, nova_hora)

        if sucesso:
            status_label.config(text="Consulta alterada com sucesso.", bootstyle="success")
            nova_data_var.set("")
            nova_hora_var.set("")
            carregar_consultas()
        else:
            status_label.config(text="Erro ao alterar consulta.", bootstyle="danger")

    medico_combobox.bind("<<ComboboxSelected>>", carregar_consultas)

    nova_data_var = StringVar()
    nova_hora_var = StringVar()

    ttk.Label(frame, text="Nova Data:").grid(row=2, column=0, sticky="w", pady=5)
    ttk.Entry(frame, textvariable=nova_data_var, width=40).grid(row=2, column=1, pady=5)

    ttk.Label(frame, text="Nova Hora:").grid(row=3, column=0, sticky="w", pady=5)
    ttk.Entry(frame, textvariable=nova_hora_var, width=40).grid(row=3, column=1, pady=5)

    ttk.Button(frame, text="Alterar", command=alterar).grid(row=4, column=0, pady=10)
    ttk.Button(frame, text="Cancelar Consulta", command=cancelar).grid(row=4, column=1, pady=10)

    status_label = ttk.Label(frame, text="", bootstyle="info")
    status_label.grid(row=5, columnspan=2, pady=5)

    carregar_consultas()
