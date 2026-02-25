import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import json
import threading
from huggingface_hub import InferenceClient

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

class NoraFinanceAI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nora AI - Smart Finance")
        self.geometry("1000x800")

        self.hf_token = self.load_key()
        self.data_context = "" 
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="NORA AI", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=30, padx=20)

        self.import_btn = ctk.CTkButton(self.sidebar, text="Importovat CSV", command=self.import_csv)
        self.import_btn.pack(pady=10, padx=20)

        self.token_entry = ctk.CTkEntry(self.sidebar, placeholder_text="HF Token", show="*")
        self.token_entry.pack(pady=5, padx=20)
        if self.hf_token: self.token_entry.insert(0, self.hf_token)

        self.save_key_btn = ctk.CTkButton(self.sidebar, text="Uložit Token", command=self.save_key)
        self.save_key_btn.pack(pady=5, padx=20)

        # Indikátor přemýšlení (Progress bar)
        self.progress_bar = ctk.CTkProgressBar(self.sidebar, mode="indeterminate", width=200)
        self.progress_bar.pack(pady=20, padx=20)
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="Status: Připravena", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

        # Chat display
        self.chat_display = ctk.CTkTextbox(self, state="disabled", font=("Segoe UI", 15), corner_radius=15)
        self.chat_display.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Input box
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")

        self.user_input = ctk.CTkEntry(self.entry_frame, placeholder_text="Zeptej se Nory...", height=50)
        self.user_input.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(self.entry_frame, text="Odeslat", width=120, height=50, command=self.send_message)
        self.send_btn.pack(side="right")

    def load_key(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f: return json.load(f).get("hf_token", "")
        return ""

    def save_key(self):
        key = self.token_entry.get()
        with open(CONFIG_FILE, "w") as f: json.dump({"hf_token": key}, f)
        self.hf_token = key
        messagebox.showinfo("Nastavení", "Token bezpečně uložen.")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                self.data_context = df.head(20).to_string()
                self.add_to_chat("Systém", "Finanční data byla úspěšně importována.")
            except Exception as e:
                self.add_to_chat("Systém", f"Chyba při čtení CSV: {str(e)}")

    def add_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def toggle_thinking(self, busy=True):
        """Zapne/vypne animaci a zablokuje vstup."""
        if busy:
            self.status_label.configure(text="Nora přemýšlí...", text_color="#3498db")
            self.progress_bar.start()
            self.send_btn.configure(state="disabled")
        else:
            self.status_label.configure(text="Status: Připravena", text_color="gray")
            self.progress_bar.stop()
            self.send_btn.configure(state="normal")

    def send_message(self):
        text = self.user_input.get()
        if not text or not self.hf_token: return
        
        self.add_to_chat("Ty", text)
        self.user_input.delete(0, "end")
        
        self.toggle_thinking(True)
        threading.Thread(target=self.get_ai_response, args=(text,), daemon=True).start()

    def get_ai_response(self, prompt):
        try:
            client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3", token=self.hf_token)
            
            system_msg = "Jsi Nora, finanční expertka. Odpovídej věcně a POUZE česky. Ignoruj reklamy. Pokud máš k dispozici data, analyzuj je."
            msgs = [{"role": "system", "content": system_msg}]
            if self.data_context:
                msgs.append({"role": "system", "content": f"KONTEXT DAT: {self.data_context}"})
            msgs.append({"role": "user", "content": prompt})

            response = ""
            for message in client.chat_completion(messages=msgs, max_tokens=600, stream=True):
                token = message.choices[0].delta.content
                if token: response += token

            final_text = response.strip()
            self.after(0, lambda: self.add_to_chat("Nora", final_text))
        except Exception as err:
            # Oprava NameError: převedeme chybu na string okamžitě
            error_msg = str(err)
            self.after(0, lambda: self.add_to_chat("Nora", f"Chyba: {error_msg}"))
        finally:
            self.after(0, lambda: self.toggle_thinking(False))

if __name__ == "__main__":
    app = NoraFinanceAI()
    app.mainloop()