import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import json
import threading
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from huggingface_hub import InferenceClient

# Nastavení vzhledu
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

class NoraFinanceAI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nora AI - Finanční Expertka")
        self.geometry("1100x850")

        # Proměnné
        self.hf_token = self.load_key()
        self.data_context = "" 
        self.last_file_path = ""
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="NORA AI", font=ctk.CTkFont(size=26, weight="bold"))
        self.logo_label.pack(pady=30)

        self.import_btn = ctk.CTkButton(self.sidebar, text="Importovat CSV", command=self.import_csv, height=40)
        self.import_btn.pack(pady=10, padx=20)

        self.token_label = ctk.CTkLabel(self.sidebar, text="Hugging Face Token:", font=("Segoe UI", 12))
        self.token_label.pack(pady=(20, 0))
        
        self.token_entry = ctk.CTkEntry(self.sidebar, placeholder_text="hf_...", show="*")
        self.token_entry.pack(pady=5, padx=20)
        if self.hf_token: self.token_entry.insert(0, self.hf_token)

        self.save_key_btn = ctk.CTkButton(self.sidebar, text="Uložit Nastavení", fg_color="#34495e", command=self.save_key)
        self.save_key_btn.pack(pady=5, padx=20)

        self.progress_bar = ctk.CTkProgressBar(self.sidebar, mode="indeterminate", width=200)
        self.progress_bar.pack(pady=30, padx=20)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.sidebar, text="Status: Připravena", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

        # --- CHAT AREA ---
        self.chat_display = ctk.CTkTextbox(self, state="disabled", font=("Segoe UI", 15), corner_radius=15)
        self.chat_display.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # --- INPUT AREA ---
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")

        self.user_input = ctk.CTkEntry(self.entry_frame, placeholder_text="Zeptej se na finance nebo napiš 'Vytvoř report'...", height=50)
        self.user_input.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(self.entry_frame, text="Odeslat", width=120, height=50, command=self.send_message, font=("Segoe UI", 14, "bold"))
        self.send_btn.pack(side="right")

        self.add_to_chat("Nora", "Ahoj! Jsem Nora. Nahraj své CSV nebo se mě zeptej na cokoliv ohledně financí. Pokud chceš PDF analýzu, stačí napsat 'Vytvoř report'.")

    def load_key(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f: return json.load(f).get("hf_token", "")
        return ""

    def save_key(self):
        key = self.token_entry.get()
        with open(CONFIG_FILE, "w") as f: json.dump({"hf_token": key}, f)
        self.hf_token = key
        messagebox.showinfo("Nastavení", "API Token byl úspěšně uložen.")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.last_file_path = file_path
                df = pd.read_csv(file_path)
                self.data_context = df.head(30).to_string()
                self.add_to_chat("Systém", f"Soubor '{os.path.basename(file_path)}' byl úspěšně importován.")
            except Exception as e:
                self.add_to_chat("Systém", f"Chyba při čtení: {str(e)}")

    def add_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def toggle_thinking(self, busy=True):
        if busy:
            self.status_label.configure(text="Nora pracuje...", text_color="#3498db")
            self.progress_bar.start()
            self.send_btn.configure(state="disabled")
        else:
            self.status_label.configure(text="Status: Připravena", text_color="gray")
            self.progress_bar.stop()
            self.send_btn.configure(state="normal")

    def send_message(self):
        text = self.user_input.get()
        if not text: return
        if not self.hf_token:
            messagebox.showwarning("Token", "Nejdříve vlož a ulož HF Token vlevo!")
            return
        
        self.add_to_chat("Ty", text)
        self.user_input.delete(0, "end")
        
        self.toggle_thinking(True)
        threading.Thread(target=self.process_request, args=(text,), daemon=True).start()

    def process_request(self, text):
        # Rozhodnutí: AI nebo PDF Report?
        if any(kw in text.lower() for kw in ["report", "pdf", "graf", "analyzuj data"]):
            self.generate_pdf_report()
        else:
            self.get_ai_response(text)

    def generate_pdf_report(self):
        if not self.last_file_path:
            self.after(0, lambda: self.add_to_chat("Nora", "Nemám žádná data. Prosím, nahraj nejdříve CSV soubor."))
            self.after(0, lambda: self.toggle_thinking(False))
            return

        try:
            df = pd.read_csv(self.last_file_path)
            df['Castka'] = pd.to_numeric(df['Castka'])
            
            prijmy = df[df['Castka'] > 0]['Castka'].sum()
            vydaje = abs(df[df['Castka'] < 0]['Castka'].sum())
            bilance = prijmy - vydaje

            # Graf výdajů
            vydaje_df = df[df['Castka'] < 0].copy()
            vydaje_df['Castka'] = abs(vydaje_df['Castka'])
            stats = vydaje_df.groupby('Kategorie')['Castka'].sum()
            
            plt.figure(figsize=(6, 5))
            stats.plot(kind='pie', autopct='%1.1f%%', colors=['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6'])
            plt.title("Struktura výdajů")
            plt.ylabel('')
            plt.savefig("temp_chart.png")
            plt.close()

            # PDF Tvorba
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(200, 20, "Financni Report Nora AI", ln=True, align='C')
            
            pdf.set_font("Helvetica", "", 12)
            pdf.ln(10)
            pdf.cell(200, 10, f"Datum exportu: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
            pdf.cell(200, 10, f"Celkove prijmy: {prijmy:,.2f} Kc".replace(',', ' '), ln=True)
            pdf.cell(200, 10, f"Celkove vydaje: {vydaje:,.2f} Kc".replace(',', ' '), ln=True)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(200, 10, f"Cista bilance: {bilance:,.2f} Kc".replace(',', ' '), ln=True)
            
            pdf.image("temp_chart.png", x=50, y=80, w=110)
            
            pdf_name = f"Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            pdf.output(pdf_name)

            self.after(0, lambda: self.add_to_chat("Nora", f"✅ Report vytvořen! Soubor '{pdf_name}' najdeš ve složce s programem. Obsahuje přehled tvých financí i graf výdajů."))
        except Exception as e:
            err_str = str(e)
            self.after(0, lambda: self.add_to_chat("Nora", f"Chyba při reportu: {err_str}"))
        finally:
            self.after(0, lambda: self.toggle_thinking(False))

    def get_ai_response(self, prompt):
        try:
            model_id = "google/gemma-2-9b-it"
            client = InferenceClient(model_id, token=self.hf_token)
            
            system_msg = "Jsi Nora, finanční expertka. Odpovídej věcně a POUZE česky. Pokud máš data, zanalyzuj je stručně."
            messages = [{"role": "user", "content": f"{system_msg}\nData: {self.data_context}\nDotaz: {prompt}"}]

            response = ""
            for message in client.chat_completion(messages=messages, max_tokens=800, stream=True):
                token = message.choices[0].delta.content
                if token: response += token

            res_text = response.strip()
            self.after(0, lambda: self.add_to_chat("Nora", res_text))
        except Exception as err:
            err_msg = str(err)
            self.after(0, lambda: self.add_to_chat("Nora", f"AI Chyba: {err_msg}"))
        finally:
            self.after(0, lambda: self.toggle_thinking(False))

if __name__ == "__main__":
    NoraFinanceAI().mainloop()