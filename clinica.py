from datetime import datetime, date, time, timedelta
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

SLOT_MINUTOS = 30
HORA_INICIO = 8
HORA_FIM    = 17

class Pessoa:
    def __init__(self, cpf, nome, telefone, email):
        self.cpf = cpf; self.nome = nome; self.telefone = telefone; self.email = email

class Medico:
    def __init__(self, pessoa, crm, especialidade):
        self.pessoa = pessoa; self.crm = crm; self.especialidade = especialidade

class Paciente:
    def __init__(self, pessoa):
        self.pessoa = pessoa

class Consulta:
    def __init__(self, crm_medico, cpf_paciente, inicio_datetime, observacoes=None):
        self.crm_medico = crm_medico; self.cpf_paciente = cpf_paciente
        self.inicio = inicio_datetime; self.observacoes = observacoes
    @property
    def fim(self): return self.inicio + timedelta(minutes=SLOT_MINUTOS)

class Clinica:
    def __init__(self, nome):
        self.nome = nome; self.medicos = []; self.pacientes = []; self.consultas = []
    def adicionar_medico(self, cpf, nome, telefone, email, crm, esp):
        self.medicos.append(Medico(Pessoa(cpf, nome, telefone, email), crm, esp))
    def adicionar_paciente(self, cpf, nome, telefone, email):
        self.pacientes.append(Paciente(Pessoa(cpf, nome, telefone, email)))
    def _buscar_medico_por_crm(self, crm): return next((m for m in self.medicos if m.crm == crm), None)
    def _buscar_paciente_por_cpf(self, cpf): return next((p for p in self.pacientes if p.pessoa.cpf == cpf), None)
    def _tem_conflito(self, crm, cpf, inicio):
        novo_fim = inicio + timedelta(minutes=SLOT_MINUTOS)
        for c in self.consultas:
            if (inicio < c.fim) and (c.inicio < novo_fim) and (c.crm_medico == crm or c.cpf_paciente == cpf):
                return True
        return False
    def _gerar_slots_do_dia(self, dia: date):
        atual = datetime.combine(dia, time(HORA_INICIO, 0))
        limite = datetime.combine(dia, time(HORA_FIM, 0))
        while atual < limite:
            yield atual; atual += timedelta(minutes=SLOT_MINUTOS)
    def encontrar_primeiro_slot_livre(self, crm, cpf, dia: date):
        for slot in self._gerar_slots_do_dia(dia):
            if not self._tem_conflito(crm, cpf, slot):
                return slot
        return None
    def agendar_consulta_por_data(self, crm, cpf, dia: date, obs=None):
        if not self._buscar_medico_por_crm(crm): raise ValueError("Médico não encontrado.")
        if not self._buscar_paciente_por_cpf(cpf): raise ValueError("Paciente não encontrado.")
        slot = self.encontrar_primeiro_slot_livre(crm, cpf, dia)
        if not slot: raise ValueError("Não há horários disponíveis para este dia.")
        self.consultas.append(Consulta(crm, cpf, slot, obs)); return slot
    def listar_consultas(self): return sorted(self.consultas, key=lambda c: c.inicio)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clínica - Cadastro e Agendamento")
        self.geometry("1000x650")
        self.clinica = Clinica("Clínica Saúde Total")
        self._montar_ui()

    def _montar_ui(self):
        root = tk.Frame(self); root.pack(fill="both", expand=True, padx=8, pady=6)
        root.grid_columnconfigure(0, weight=1); root.grid_columnconfigure(1, weight=1)

        fm = tk.LabelFrame(root, text="Médicos"); fm.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self._sec_medicos(fm)
        fp = tk.LabelFrame(root, text="Pacientes"); fp.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self._sec_pacientes(fp)
        fc = tk.LabelFrame(root, text="Consultas (duração 30 min; horário automático)")
        fc.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4, pady=4)
        root.grid_rowconfigure(1, weight=1)
        self._sec_consultas(fc)

    def _entry(self, parent, w): return tk.Entry(parent, width=w)

    def _sec_medicos(self, f):
        labels = ["CPF","Nome","Telefone","Email","CRM","Especialidade"]
        for i,t in enumerate(labels): tk.Label(f,text=t).grid(row=0,column=i,sticky="w",padx=2,pady=1)
        self.e_m_cpf=self._entry(f,16); self.e_m_cpf.grid(row=1,column=0,padx=2,pady=1,sticky="we")
        self.e_m_nome=self._entry(f,20); self.e_m_nome.grid(row=1,column=1,padx=2,pady=1,sticky="we")
        self.e_m_tel=self._entry(f,16); self.e_m_tel.grid(row=1,column=2,padx=2,pady=1,sticky="we")
        self.e_m_email=self._entry(f,20); self.e_m_email.grid(row=1,column=3,padx=2,pady=1,sticky="we")
        self.e_m_crm=self._entry(f,10); self.e_m_crm.grid(row=1,column=4,padx=2,pady=1,sticky="we")
        self.e_m_esp=self._entry(f,18); self.e_m_esp.grid(row=1,column=5,padx=2,pady=1,sticky="we")
        tk.Button(f,text="Cadastrar Médico",command=self._cad_med).grid(row=1,column=6,padx=4,pady=1,sticky="w")
        self.lb_med=tk.Listbox(f,height=5); self.lb_med.grid(row=2,column=0,columnspan=7,sticky="nsew",padx=2,pady=4)
        for i in range(6): f.grid_columnconfigure(i,weight=1); f.grid_rowconfigure(2,weight=1)

    def _sec_pacientes(self, f):
        labels = ["CPF","Nome","Telefone","Email"]
        for i,t in enumerate(labels): tk.Label(f,text=t).grid(row=0,column=i,sticky="w",padx=2,pady=1)
        self.e_p_cpf=self._entry(f,16); self.e_p_cpf.grid(row=1,column=0,padx=2,pady=1,sticky="we")
        self.e_p_nome=self._entry(f,20); self.e_p_nome.grid(row=1,column=1,padx=2,pady=1,sticky="we")
        self.e_p_tel=self._entry(f,16); self.e_p_tel.grid(row=1,column=2,padx=2,pady=1,sticky="we")
        self.e_p_email=self._entry(f,20); self.e_p_email.grid(row=1,column=3,padx=2,pady=1,sticky="we")
        tk.Button(f,text="Cadastrar Paciente",command=self._cad_pac).grid(row=1,column=4,padx=4,pady=1,sticky="w")
        self.lb_pac=tk.Listbox(f,height=5); self.lb_pac.grid(row=2,column=0,columnspan=5,sticky="nsew",padx=2,pady=4)
        for i in range(4): f.grid_columnconfigure(i,weight=1); f.grid_rowconfigure(2,weight=1)

    def _sec_consultas(self, f):
        tk.Label(f,text="CRM do Médico").grid(row=0,column=0,sticky="w",padx=1,pady=0)
        tk.Label(f,text="CPF do Paciente").grid(row=0,column=1,sticky="w",padx=1,pady=0)
        tk.Label(f,text="Data (DD/MM/AAAA)").grid(row=0,column=2,sticky="w",padx=1,pady=0)
        tk.Label(f,text="Observações").grid(row=0,column=3,sticky="w",padx=8,pady=0)

        self.cb_crm=ttk.Combobox(f,state="readonly",width=18); self.cb_crm.grid(row=1,column=0,padx=1,pady=0,sticky="w")
        self.cb_cpf=ttk.Combobox(f,state="readonly",width=18); self.cb_cpf.grid(row=1,column=1,padx=1,pady=0,sticky="w")

        df = tk.Frame(f); df.grid(row=1,column=2,sticky="w",padx=1,pady=0)
        self.cb_dia=ttk.Combobox(df,state="readonly",width=3,values=[f"{d:02d}" for d in range(1,32)])
        self.cb_mes=ttk.Combobox(df,state="readonly",width=3,values=[f"{m:02d}" for m in range(1,13)])
        ano_atual=datetime.now().year
        self.cb_ano=ttk.Combobox(df,state="readonly",width=5,values=[str(ano_atual+i) for i in range(0,3)])
        self.cb_dia.grid(row=0,column=0,padx=(0,1)); tk.Label(df,text="/").grid(row=0,column=1)
        self.cb_mes.grid(row=0,column=2,padx=(1,1)); tk.Label(df,text="/").grid(row=0,column=3)
        self.cb_ano.grid(row=0,column=4,padx=(1,0))

        self.e_obs=self._entry(f,40); self.e_obs.grid(row=1,column=3,padx=6,pady=0,sticky="we")
        tk.Button(f,text="Agendar Consulta",command=self._agendar).grid(row=1,column=4,padx=6,pady=0,sticky="w")

        self.lb_con=tk.Listbox(f,height=12)
        self.lb_con.grid(row=2,column=0,columnspan=5,sticky="nsew",padx=1,pady=4)

        for i in range(4): f.grid_columnconfigure(i,weight=1)
        f.grid_rowconfigure(2,weight=1)

        hoje=datetime.now().date()
        self.cb_dia.set(f"{hoje.day:02d}"); self.cb_mes.set(f"{hoje.month:02d}"); self.cb_ano.set(str(hoje.year))
        self._refresh_fontes_consulta()

    def _cad_med(self):
        try:
            cpf=self.e_m_cpf.get().strip(); nome=self.e_m_nome.get().strip()
            tel=self.e_m_tel.get().strip(); email=self.e_m_email.get().strip()
            crm=self.e_m_crm.get().strip(); esp=self.e_m_esp.get().strip()
            if not (cpf and nome and tel and email and crm and esp): raise ValueError("Preencha todos os campos do médico.")
            self.clinica.adicionar_medico(cpf,nome,tel,email,crm,esp)
            self.lb_med.insert(tk.END,f"CRM: {crm} | Nome: {nome} | Esp.: {esp} | CPF: {cpf}")
            self._refresh_fontes_consulta()
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _cad_pac(self):
        try:
            cpf=self.e_p_cpf.get().strip(); nome=self.e_p_nome.get().strip()
            tel=self.e_p_tel.get().strip(); email=self.e_p_email.get().strip()
            if not (cpf and nome and tel and email): raise ValueError("Preencha todos os campos do paciente.")
            self.clinica.adicionar_paciente(cpf,nome,tel,email)
            self.lb_pac.insert(tk.END,f"CPF: {cpf} | Nome: {nome} | Tel: {tel}")
            self._refresh_fontes_consulta()
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _agendar(self):
        try:
            crm=self.cb_crm.get().strip(); cpf=self.cb_cpf.get().strip()
            d=self.cb_dia.get(); m=self.cb_mes.get(); a=self.cb_ano.get()
            obs=self.e_obs.get().strip() or None
            if not (crm and cpf and d and m and a): raise ValueError("Selecione CRM, CPF e a data.")
            dia=datetime.strptime(f"{d}/{m}/{a}","%d/%m/%Y").date()
            slot=self.clinica.agendar_consulta_por_data(crm,cpf,dia,obs)
            self._refresh_consultas(); messagebox.showinfo("Sucesso",f"Consulta marcada às {slot:%H:%M}.")
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _refresh_fontes_consulta(self):
        self.cb_crm["values"]=[m.crm for m in self.clinica.medicos]
        self.cb_cpf["values"]=[p.pessoa.cpf for p in self.clinica.pacientes]

    def _refresh_consultas(self):
        self.lb_con.delete(0, tk.END)
        for c in self.clinica.listar_consultas():
            self.lb_con.insert(tk.END, f"{c.inicio:%d/%m/%Y %H:%M} até {c.fim:%H:%M} | CRM: {c.crm_medico} | CPF: {c.cpf_paciente}"
                                 + (f" | Obs: {c.observacoes}" if c.observacoes else ""))

if __name__ == "__main__":
    App().mainloop()
