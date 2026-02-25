import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import json
from huggingface_hub import InferenceClient

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

class NoraFinanceAI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nora - AI Finanční Asistentka")
        self.geometry("1000 dio 800")

        self.hf_token = self.load_key()
        self.data_context = "" 
        
        # --- UI LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="NORA AI", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=(30, 20), padx=20)

        # Sekce Data
        self.import_btn = ctk.CTkButton(self.sidebar, text="Importovat CSV", command=self.import_csv)
        self.import_btn.pack(pady=10, padx=20)

        # Sekce Nastavení (Ukládání klíče)
        self.settings_label = ctk.CTkLabel(self.sidebar, text="Nastavení API", font=ctk.CTkFont(size=14, weight="bold"))
        self.settings_label.pack(pady=(30, 5), padx=20)
        
        self.token_entry = ctk.CTkEntry(self.sidebar, placeholder_text="HF Token (hf_...)", show="*")
        self.token_entry.pack(pady=5, padx=20)
        if self.hf_token:
            self.token_entry.insert(0, self.hf_token)

        self.save_key_btn = ctk.CTkButton(self.sidebar, text="Uložit Token", fg_color="#34495e", command=self.save_key)
        self.save_key_btn.pack(pady=5, padx=20)

        self.status_label = ctk.CTkLabel(self.sidebar, text="Status: Připravena", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

        # Chat Area
        self.chat_display = ctk.CTkTextbox(self, state="disabled", font=("Segoe UI", 15), corner_radius=15)
        self.chat_display.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Input Area
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")

        self.user_input = ctk.CTkEntry(self.entry_frame, placeholder_text="Zeptej se Nory...", height=50)
        self.user_input.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(self.entry_frame, text="Odeslat", width=120, height=50, command=self.send_message)
        self.send_btn.pack(side="right")

        self.add_to_chat("Nora", "Ahoj! Pokud nemáš nastavený HF Token v sidebaru, prosím vlož ho, abych mohla začít pracovat.")

    def load_key(self):
        """Načte API klíč z lokálního JSON souboru."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("hf_token", "")
        return ""

    def save_key(self):
        """Uloží API klíč do lokálního JSON souboru."""
        key = self.token_entry.get()
        if key:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"hf_token": key}, f)
            self.hf_token = key
            messagebox.showinfo("Nastavení", "Token byl úspěšně uložen lokálně.")
        else:
            messagebox.showwarning("Varování", "Pole pro token je prázdné.")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                self.data_context = df.head(15).to_string(index=False)
                self.status_label.configure(text="Data: Načtena ✅", text_color="#27ae60")
                self.add_to_chat("Systém", "Analýza tabulky je připravena.")
            except Exception as e:
                self.add_to_chat("Systém", f"Chyba: {e}")

    def add_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        if not self.hf_token:
            messagebox.showerror("Chyba", "Chybí Hugging Face Token! Vlož ho prosím do nastavení vlevo.")
            return
            
        user_text = self.user_input.get()
        if not user_text: return
        self.add_to_chat("Ty", user_text)
        self.user_input.delete(0, "end")
        self.get_hf_response(user_text)

    def get_hf_response(self, prompt):
        try:
            client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3", token=self.hf_token)
            system_prompt = "Jsi Nora, česká finanční asistentka. Odpovídej stručně."
            
            full_prompt = f"{system_prompt}\n"
            if self.data_context:
                full_prompt += f"Data uživatele:\n{self.data_context}\n"
            full_prompt += f"Uživatel: {prompt}\nNora:"

            response = ""
            for message in client.chat_completion(
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=500,
                stream=True
            ):
                token = message.choices[0].delta.content
                response += token

            self.add_to_chat("Nora", response.strip())
        except Exception as e:
            self.add_to_chat("Nora", f"Chyba při komunikaci: {e}")

if __name__ == "__main__":
    app = NoraFinanceAI()
    app.mainloop()