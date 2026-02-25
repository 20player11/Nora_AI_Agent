import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
import pandas as pd

# Základní nastavení vzhledu
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NoraFinanceAI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nora - AI Finanční Asistentka")
        self.geometry("800x600")

        self.data = None  # Zde budou uložena finanční data

        # Rozvržení mřížky (Grid)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Postranní panel
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="NORA AI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)

        self.import_btn = ctk.CTkButton(self.sidebar, text="Importovat data (.csv)", command=self.import_csv)
        self.import_btn.pack(pady=10, padx=20)

        self.status_label = ctk.CTkLabel(self.sidebar, text="Data: Nenahrána", text_color="gray")
        self.status_label.pack(pady=10)

        # Chatovací oblast
        self.chat_frame = ctk.CTkFrame(self, corner_radius=10)
        self.chat_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.chat_display = ctk.CTkTextbox(self.chat_frame, state="disabled", font=("Segoe UI", 14))
        self.chat_display.pack(expand=True, fill="both", padx=10, pady=10)

        # Vstup pro text
        self.entry_frame = ctk.CTkFrame(self, height=100, fg_color="transparent")
        self.entry_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")

        self.user_input = ctk.CTkEntry(self.entry_frame, placeholder_text="Zeptej se Nory na své finance...", font=("Segoe UI", 14))
        self.user_input.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(self.entry_frame, text="Odeslat", width=100, command=self.send_message)
        self.send_btn.pack(side="right")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.status_label.configure(text="Data: Připravena ✅", text_color="green")
                self.add_to_chat("Nora", f"Úspěšně jsem načetla soubor. Obsahuje {len(self.data)} záznamů. Jak ti mohu pomoci?")
            except Exception as e:
                self.add_to_chat("Systém", f"Chyba při nahrávání: {e}")

    def add_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        msg = self.user_input.get()
        if not msg:
            return

        self.add_to_chat("Ty", msg)
        self.user_input.delete(0, "end")
        
        # Logika "přemýšlení" Nory
        self.process_query(msg)

    def process_query(self, query):
        if self.data is None:
            response = "Nejdříve prosím nahraj své finanční údaje (CSV), abych mohla provést přesnou analýzu."
        else:
            # Příklad jednoduché logiky analýzy dat
            # Zde by se normálně volalo LLM s kontextem self.data.to_string()
            if "útrata" in query.lower() or "celkem" in query.lower():
                # Předpokládáme, že v CSV je sloupec 'Castka' nebo 'Amount'
                col = next((c for c in self.data.columns if 'astka' in c or 'Amount' in c), None)
                if col:
                    total = self.data[col].sum()
                    response = f"Na základě tvých dat je tvá celková suma v tabulce: {total:.2f} CZK."
                else:
                    response = "V tabulce jsem nenašla sloupec s částkou. Zkontroluj prosím názvy sloupců."
            else:
                response = "Data vidím! Pokud chceš hlubší analýzu (např. trendy nebo predikce), doporučuji mě propojit s OpenAI API."

        self.add_to_chat("Nora", response)

if __name__ == "__main__":
    app = NoraFinanceAI()
    app.mainloop()