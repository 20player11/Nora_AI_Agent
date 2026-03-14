import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import json
import sqlite3
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from huggingface_hub import InferenceClient

# --- DEFINICE BAREV (Light/Dark Mode) ---
COLORS = {
    "bg_sidebar": ("#EBEBEB", "#1a1c1e"),
    "bg_main": ("#F5F5F5", "#0d0d0d"),
    "bg_card": ("#FFFFFF", "#252525"),
    "text_main": ("#000000", "#FFFFFF"),
    "text_sub": ("#666666", "#aaaaaa"),
    "border": ("#DBDBDB", "#333333"),
    "accent": "#3498db",
    "danger": "#e74c3c",
    "success": "#2ecc71"
}

CONFIG_FILE = "config.json"

class NoraFinanceAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. NAČTENÍ KONFIGURACE
        self.config = self.load_config()
        self.hf_token = self.config.get("hf_token", "")
        self.monthly_limit = self.config.get("limit", 5000)
        app_mode = self.config.get("appearance", "Dark")
        ctk.set_appearance_mode(app_mode)

        # 2. SKRYTÍ OKNA PRO INTRO
        self.withdraw()
        self.show_modern_intro()

        # 3. NASTAVENÍ OKNA
        self.title("Nora AI - Digital Financial Intelligence")
        self.geometry("1350x900")
        self.configure(fg_color=COLORS["bg_main"])

        # 4. DATABÁZE A PŘIPOJENÍ
        self.db_conn = sqlite3.connect("nora_history.db", check_same_thread=False)
        self.create_db()
        
        # Inicializace stavových proměnných
        self.data_context = "" 
        self.df = None
        self.canvas = None
        
        # 5. UI LAYOUT (Mřížka)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR KONSTRUKCE ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="NORA AI", font=ctk.CTkFont(size=32, weight="bold"))
        self.logo_label.pack(pady=(50, 10))
        
        self.version_label = ctk.CTkLabel(self.sidebar, text="v2.5 High-Tech Edition", font=ctk.CTkFont(size=10), text_color=COLORS["text_sub"])
        self.version_label.pack(pady=(0, 30))

        self.import_btn = ctk.CTkButton(self.sidebar, text="📂 IMPORT CSV DAT", command=self.import_csv, 
                                         height=50, corner_radius=12, font=("Segoe UI", 14, "bold"),
                                         fg_color=COLORS["accent"], hover_color="#2980b9")
        self.import_btn.pack(pady=10, padx=30)

        self.clear_btn = ctk.CTkButton(self.sidebar, text="🗑️ VYMAZAT HISTORII", fg_color="transparent", 
                                        border_width=1, border_color=COLORS["border"], 
                                        command=self.clear_chat_history, corner_radius=12)
        self.clear_btn.pack(pady=10, padx=30)

        # --- CHAT AREA KONSTRUKCE ---
        self.chat_display = ctk.CTkTextbox(self, state="disabled", font=("Segoe UI", 16), corner_radius=25, 
                                           fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        self.chat_display.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        # --- DASHBOARD PANEL KONSTRUKCE ---
        self.dashboard = ctk.CTkFrame(self, width=380, corner_radius=25, fg_color=COLORS["bg_sidebar"])
        self.dashboard.grid(row=0, column=2, padx=25, pady=25, sticky="nsew")
        
        ctk.CTkLabel(self.dashboard, text="FINANČNÍ PŘEHLED", font=("Segoe UI", 20, "bold")).pack(pady=25)
        
        # Karta zůstatku
        self.balance_card = ctk.CTkFrame(self.dashboard, fg_color=COLORS["bg_card"], corner_radius=20)
        self.balance_card.pack(pady=10, padx=25, fill="x")
        
        ctk.CTkLabel(self.balance_card, text="Aktuální zůstatek", font=("Segoe UI", 12), text_color=COLORS["text_sub"]).pack(pady=(15, 0))
        self.balance_value = ctk.CTkLabel(self.balance_card, text="0.00 Kč", font=("Segoe UI", 26, "bold"))
        self.balance_value.pack(pady=(5, 15))

        # Karta limitu
        self.status_card = ctk.CTkFrame(self.dashboard, fg_color=COLORS["bg_card"], corner_radius=20)
        self.status_card.pack(pady=10, padx=25, fill="x")
        self.status_label = ctk.CTkLabel(self.status_card, text="Limit: --", font=("Segoe UI", 14))
        self.status_label.pack(pady=15)

        # Tlačítko nastavení
        self.settings_btn = ctk.CTkButton(self.dashboard, text="⚙️ Nastavení", width=120, height=40, 
                                           fg_color=COLORS["bg_card"], hover_color=COLORS["border"],
                                           text_color=COLORS["text_main"], command=self.open_settings, corner_radius=15)
        self.settings_btn.pack(side="bottom", pady=30)

        # --- INPUT FRAME KONSTRUKCE ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=1, padx=25, pady=(0, 25), sticky="ew")

        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Zeptej se Nory na své finance...", 
                                       height=60, corner_radius=18, border_width=1, fg_color=COLORS["bg_card"])
        self.user_input.pack(side="left", expand=True, fill="x", padx=(0, 15))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="ODESLAT", width=140, height=60, corner_radius=18,
                                       command=self.send_message, font=("Segoe UI", 14, "bold"))
        self.send_btn.pack(side="right")

    # --- MODERNÍ INTRO 2.0 (OPRAVENÉ) ---
    def show_modern_intro(self):
        self.intro = ctk.CTkToplevel()
        self.intro.geometry("600x400")
        self.intro.overrideredirect(True)
        sw, sh = self.intro.winfo_screenwidth(), self.intro.winfo_screenheight()
        self.intro.geometry(f"600x400+{(sw-600)//2}+{(sh-400)//2}")
        
        self.canvas_intro = tk.Canvas(self.intro, highlightthickness=0, width=600, height=400, bg="white")
        self.canvas_intro.pack()

        # Dekorativní grafika
        self.canvas_intro.create_oval(380, -120, 900, 450, fill="#e1f1ff", outline="") 
        self.canvas_intro.create_polygon(320, 400, 600, 0, 600, 400, fill="#1e90ff", outline="") 
        self.canvas_intro.create_polygon(480, 400, 600, 120, 600, 400, fill="#0056b3", outline="")

        # Textové logo (bez letter_spacing, aby to neházelo chybu)
        self.canvas_intro.create_text(253, 163, text="NORA", font=("Arial", 90, "bold"), fill="#f2f2f2")
        self.nora_text = self.canvas_intro.create_text(250, 160, text="NORA", font=("Arial", 90, "bold"), fill="#002d5b")
        self.canvas_intro.create_text(250, 235, text="POWERED BY FINANCIAL AI", font=("Arial", 12, "bold"), fill="#1e90ff")

        # Loading bar (Kanálek a Progress)
        self.canvas_intro.create_rectangle(100, 300, 450, 303, fill="#f0f0f0", outline="")
        self.load_progress = self.canvas_intro.create_rectangle(100, 300, 100, 303, fill="#00bfff", outline="")
        
        self.animate_intro(100)

    def animate_intro(self, w):
        if w < 450:
            step = (450 - w) / 18 + 1.2
            new_w = w + step
            self.canvas_intro.coords(self.load_progress, 100, 300, new_w, 303)
            self.intro.after(35, lambda: self.animate_intro(new_w))
        else:
            self.intro.after(800, self.finish_intro)

    def finish_intro(self):
        self.intro.destroy()
        self.deiconify()
        self.load_history_into_chat()

    # --- NASTAVENÍ A KONFIGURACE ---
    def open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Konfigurace Nory")
        win.geometry("500x600")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="NASTAVENÍ SYSTÉMU", font=("Segoe UI", 22, "bold")).pack(pady=30)
        
        ctk.CTkLabel(win, text="Hugging Face API Token:", font=("Segoe UI", 12)).pack(anchor="w", padx=50)
        tk_entry = ctk.CTkEntry(win, width=400, show="*")
        tk_entry.insert(0, self.hf_token)
        tk_entry.pack(pady=(5, 20))

        ctk.CTkLabel(win, text="Měsíční výdajový limit (CZK):", font=("Segoe UI", 12)).pack(anchor="w", padx=50)
        lim_entry = ctk.CTkEntry(win, width=400)
        lim_entry.insert(0, str(self.monthly_limit))
        lim_entry.pack(pady=(5, 20))

        ctk.CTkLabel(win, text="Vizuální téma:", font=("Segoe UI", 12)).pack(anchor="w", padx=50)
        mode_opt = ctk.CTkOptionMenu(win, values=["Dark", "Light", "System"], command=self.change_appearance, width=400)
        mode_opt.set(ctk.get_appearance_mode())
        mode_opt.pack(pady=(5, 30))

        def save():
            self.hf_token = tk_entry.get()
            try:
                self.monthly_limit = int(lim_entry.get())
            except ValueError:
                self.monthly_limit = 5000
            
            with open(CONFIG_FILE, "w") as f:
                json.dump({"hf_token": self.hf_token, "limit": self.monthly_limit, "appearance": mode_opt.get()}, f)
            win.destroy()
            self.update_dashboard()
            messagebox.showinfo("Nora AI", "Nastavení uloženo.")
        
        ctk.CTkButton(win, text="ULOŽIT VŠE", command=save, height=45, width=200, fg_color=COLORS["success"]).pack(pady=20)

    def change_appearance(self, mode):
        ctk.set_appearance_mode(mode)
        if self.df is not None:
            self.draw_chart()

    # --- DATABÁZE A HISTORIE ---
    def create_db(self):
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("SELECT time FROM chat LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("DROP TABLE IF EXISTS chat")
            cursor.execute("CREATE TABLE chat (role TEXT, content TEXT, time TEXT)")
            self.db_conn.commit()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_history(self, role, content):
        self.db_conn.cursor().execute("INSERT INTO chat (role, content, time) VALUES (?, ?, ?)", 
                                       (role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.db_conn.commit()

    def load_history_into_chat(self):
        try:
            rows = self.db_conn.cursor().execute("SELECT role, content FROM chat ORDER BY time DESC LIMIT 15").fetchall()
            for role, content in reversed(rows):
                self.add_to_chat(role, content)
        except:
            pass

    def clear_chat_history(self):
        if messagebox.askyesno("Potvrzení", "Opravdu chceš smazat celou historii konverzace?"):
            self.db_conn.cursor().execute("DELETE FROM chat")
            self.db_conn.commit()
            self.chat_display.configure(state="normal")
            self.chat_display.delete("1.0", "end")
            self.chat_display.configure(state="disabled")

    # --- LOGIKA IMPORTU A ANALÝZY ---
    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Soubory", "*.csv")])
        if path:
            try:
                self.df = pd.read_csv(path)
                if 'Castka' in self.df.columns:
                    self.df['Castka'] = pd.to_numeric(self.df['Castka'], errors='coerce').fillna(0)
                
                self.data_context = self.df.head(30).to_string()
                self.update_dashboard()
                self.vampire_hunter()
                self.add_to_chat("Systém", f"Úspěšně importováno {len(self.df)} záznamů.")
            except Exception as e:
                messagebox.showerror("Chyba", f"Chyba při zpracování: {e}")

    def vampire_hunter(self):
        keywords = ["netflix", "spotify", "hbo", "disney", "apple", "google", "o2", "t-mobile", "vodafone", "cez", "eon", "najem", "pojisteni"]
        found = []
        if self.df is not None:
            for _, row in self.df.iterrows():
                popis = str(row.get('Popis', '')).lower()
                if any(k in popis for k in keywords) and row['Castka'] < 0:
                    found.append(f"• {row.get('Popis')} ({abs(row['Castka'])} Kč)")
        
        if found:
            unique_vamps = "\n".join(list(set(found))[:10])
            self.add_to_chat("Nora", f"🔍 **Vampire Hunter Analýza:**\nIdentifikovala jsem tyto fixní výdaje:\n{unique_vamps}")

    def update_dashboard(self):
        if self.df is None: return
        
        total_balance = self.df['Castka'].sum()
        expenses = abs(self.df[self.df['Castka'] < 0]['Castka'].sum())
        
        self.balance_value.configure(text=f"{total_balance:,.2f} Kč".replace(',', ' '))
        
        percent = (expenses / self.monthly_limit) * 100
        color = COLORS["success"] if percent < 80 else COLORS["danger"]
        self.status_label.configure(
            text=f"Výdaje: {expenses:,.0f} / {self.monthly_limit} Kč ({percent:.1f}%)",
            text_color=color
        )
        self.draw_chart()

    def draw_chart(self):
        if self.canvas: self.canvas.get_tk_widget().destroy()
        if self.df is None or self.df[self.df['Castka'] < 0].empty: return
        
        stats = self.df[self.df['Castka'] < 0].groupby('Kategorie')['Castka'].sum().abs()
        fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
        curr_mode = ctk.get_appearance_mode()
        bg_col = COLORS["bg_sidebar"][0] if curr_mode == "Light" else COLORS["bg_sidebar"][1]
        text_col = "black" if curr_mode == "Light" else "white"
        
        fig.patch.set_facecolor(bg_col)
        ax.set_facecolor(bg_col)
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22']
        stats.plot(kind='pie', autopct='%1.0f%%', ax=ax, colors=colors, 
                   wedgeprops={'width': 0.4, 'edgecolor': bg_col}, 
                   textprops={'color': text_col, 'weight': 'bold', 'size': 9})
        
        ax.set_ylabel('')
        plt.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.dashboard)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20, padx=20)

    # --- KOMUNIKACE S AI ---
    def add_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert("end", f"[{timestamp}] {sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        text = self.user_input.get().strip()
        if not text: return
        
        self.add_to_chat("Ty", text)
        self.save_history("Ty", text)
        self.user_input.delete(0, "end")
        
        threading.Thread(target=self.get_ai_response, args=(text,), daemon=True).start()

    def get_ai_response(self, prompt):
        try:
            if not self.hf_token:
                self.after(0, lambda: self.add_to_chat("Nora", "⚠️ Chybí API Token! Nastav ho v ozubeném kolečku."))
                return

            client = InferenceClient("google/gemma-2-9b-it", token=self.hf_token)
            
            # Kontext pro AI
            rows = self.db_conn.cursor().execute("SELECT role, content FROM chat ORDER BY time DESC LIMIT 6").fetchall()
            history_str = "\n".join([f"{r}: {c}" for r, c in reversed(rows)])
            
            prompt_final = (
                f"Jsi Nora, finanční expertka. Odpovídej česky, stručně a užitečně.\n"
                f"Historie: {history_str}\n"
                f"Data uživatele: {self.data_context}\n"
                f"Limit: {self.monthly_limit} Kč.\n"
                f"Otázka: {prompt}"
            )
            
            messages = [{"role": "user", "content": prompt_final}]
            
            full_res = ""
            for message in client.chat_completion(messages=messages, max_tokens=1000, stream=True):
                if message.choices:
                    chunk = message.choices[0].delta.content
                    if chunk: full_res += chunk

            if full_res:
                self.after(0, lambda r=full_res: (self.add_to_chat("Nora", r.strip()), self.save_history("Nora", r.strip())))
            else:
                self.after(0, lambda: self.add_to_chat("Nora", "Omlouvám se, nepodařilo se mi vygenerovat odpověď."))

        except Exception as e:
            self.after(0, lambda err=str(e): self.add_to_chat("Nora", f"❌ Chyba: {err}"))

if __name__ == "__main__":
    app = NoraFinanceAI()
    app.mainloop()