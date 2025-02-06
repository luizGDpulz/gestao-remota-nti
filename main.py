import mysql.connector  
from tkinter import *  
from tkinter import ttk, messagebox  

class EmployeeDialog(Toplevel):
    def __init__(self, parent, on_save, dados=None):
        super().__init__(parent)
        self.on_save = on_save
        self.dados = dados or {}
        self.title("Novo Funcionário" if not dados else "Editar Funcionário")
        self.criar_interface()
        self.preencher_campos()

    def criar_interface(self):
        campos = [
            ("Nome", 0),
            ("CPF", 1),
            ("Cargo", 2),
            ("Departamento", 3)
        ]

        self.entries = {}
        for campo, row in campos:
            Label(self, text=f"{campo}:").grid(row=row, column=0, padx=5, pady=2, sticky=W)
            entry = Entry(self, width=30)
            entry.grid(row=row, column=1, padx=5, pady=2)
            self.entries[campo] = entry

        btn_frame = Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        Button(btn_frame, text="Salvar", command=self.validar).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=LEFT, padx=5)

    def preencher_campos(self):
        for campo, entry in self.entries.items():
            entry.insert(0, self.dados.get(campo, ""))

    def validar(self):
        dados = {campo: entry.get().strip() for campo, entry in self.entries.items()}
        
        for campo, valor in dados.items():
            if not valor:
                messagebox.showerror("Erro", f"Campo {campo} obrigatório!")
                return
                
        self.on_save(dados, self.dados.get('id'))
        self.destroy()

class AppCRUD:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("Gestão de Funcionários Remota")  
        self.conexao = mysql.connector.connect(  
            host='',  
            port='',
            user='',  
            password='',  
            database=''  
        )  
        self.cursor = self.conexao.cursor()  
        self.criar_interface()

    def criar_interface(self):  
        # Botões
        btn_frame = Frame(self.root, pady=10)
        btn_frame.pack()
        
        Button(btn_frame, text="Adicionar", command=self.abrir_adicionar).grid(row=0, column=0, padx=5)
        Button(btn_frame, text="Editar", command=self.abrir_editar).grid(row=0, column=1, padx=5)
        Button(btn_frame, text="Excluir", command=self.excluir).grid(row=0, column=2, padx=5)

        # Treeview
        self.tree = ttk.Treeview(self.root, columns=('Nome', 'CPF', 'Cargo', 'Departamento'), show='headings')
        colunas = [
            ('ID', 80),
            ('Nome', 200),
            ('CPF', 150),
            ('Cargo', 150),
            ('Departamento', 150)
        ]
        
        for col, width in colunas:
            if col == 'ID':
                self.tree.column('#0', width=width, anchor=W)
                self.tree.heading('#0', text=col)
            else:
                self.tree.column(col, width=width, anchor=W)
                self.tree.heading(col, text=col)
                
        self.tree.pack(fill=BOTH, expand=1, padx=10, pady=10)
        self.carregar_dados()

    def abrir_adicionar(self):
        EmployeeDialog(self.root, self.salvar_dados)

    def abrir_editar(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um registro para editar!")
            return
            
        item = self.tree.item(selecao[0])
        dados = {
            'id': item['text'],
            'Nome': item['values'][0],
            'CPF': item['values'][1],
            'Cargo': item['values'][2],
            'Departamento': item['values'][3]
        }
        EmployeeDialog(self.root, self.salvar_dados, dados)

    def salvar_dados(self, dados, id=None):
        try:
            if id:  # Edição
                query = """UPDATE Funcionarios SET
                          nome = %s, cpf = %s, cargo = %s, departamento = %s
                          WHERE id = %s"""
                valores = (dados['Nome'], dados['CPF'], dados['Cargo'], dados['Departamento'], id)
            else:  # Inserção
                query = """INSERT INTO Funcionarios
                          (nome, cpf, cargo, departamento)
                          VALUES (%s, %s, %s, %s)"""
                valores = (dados['Nome'], dados['CPF'], dados['Cargo'], dados['Departamento'])

            self.cursor.execute(query, valores)
            self.conexao.commit()
            self.carregar_dados()
            messagebox.showinfo("Sucesso", "Operação realizada com sucesso!")
            
        except mysql.connector.Error as e:
            messagebox.showerror("Erro", f"Falha na operação: {e}")

    def excluir(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um registro para excluir!")
            return

        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este registro?"):
            try:
                id_registro = self.tree.item(selecao[0])['text']
                self.cursor.execute("DELETE FROM Funcionarios WHERE id = %s", (id_registro,))
                self.conexao.commit()
                self.carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {e}")

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.cursor.execute("SELECT id, nome, cpf, cargo, departamento FROM Funcionarios")
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', text=row[0], values=row[1:])

if __name__ == "__main__":  
    root = Tk()  
    root.geometry("900x600")
    AppCRUD(root)  
    root.mainloop()
