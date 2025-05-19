import tkinter as tk
from tkinter import simpledialog, messagebox
import db
from agenda_app import AgendaApp  # Supondo que sua classe AgendaApp está nesse arquivo

def main():
    # Criar as tabelas no banco (se ainda não existirem)
    db.criar_tabelas()

    # Janela principal do Tkinter
    root = tk.Tk()

    # Criar a interface da agenda
    app = AgendaApp(root)

    # Exemplo simples para cadastrar um médico antes de começar
    # Você pode remover essa parte se quiser cadastrar via interface
    if messagebox.askyesno("Cadastrar Médico", "Deseja cadastrar um médico agora?"):
        nome_medico = simpledialog.askstring("Novo Médico", "Digite o nome do médico:")
        if nome_medico:
            sucesso = db.cadastrar_medico(nome_medico)
            if sucesso:
                messagebox.showinfo("Sucesso", "Médico cadastrado com sucesso!")
                # Atualiza lista de médicos na combobox (se tiver)
                app.medico_combobox['values'] = [m[1] for m in app.carregar_medicos()]
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar médico.")

    root.mainloop()

if __name__ == "__main__":
    main()

