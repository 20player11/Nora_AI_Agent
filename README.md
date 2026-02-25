# 🤖 Nora AI — Inteligentní Finanční Asistentka

Nora AI je desktopová aplikace pro správu osobních financí, která kombinuje sílu **AI modelu Gemma 2** s precizní datovou analýzou. Nora vám nejen odpoví na dotazy v češtině, ale také "vidí" do vašich výdajů a dokáže vygenerovat profesionální PDF reporty s grafy.

---

## 🚀 Hlavní Funkce

* **💬 Konverzační AI:** Nora využívá `google/gemma-2-9b-it` přes Hugging Face API. Rozumí češtině a dokáže radit s investicemi i úsporami.
* **📊 Analýza CSV dat:** Importujte své transakce a nechte AI, aby v nich našla trendy.
* **📄 Generování PDF Reportů:** Automatická tvorba finančních přehledů včetně:
    * Výpočtu čisté bilance (Příjmy vs. Výdaje).
    * **Koláčových grafů** kategorií výdajů.
    * Časového razítka exportu.
* **⚡ Multithreading:** Aplikace díky vláknům nikdy nezamrzá. AI přemýšlí na pozadí, zatímco vy můžete dál pracovat.
* **🌙 Moderní UI:** Temné rozhraní (Dark Mode) postavené na knihovně CustomTkinter.

---

## 🛠️ Instalace

Aby Nora fungovala, budete potřebovat Python 3.9+ a nainstalovat následující knihovny:

```bash
pip install pandas customtkinter matplotlib fpdf2 huggingface_hub

# 🔑 Nastavení API
Nora vyžaduje Hugging Face Access Token (zdarma):

Získejte token na huggingface.co/settings/tokens.

Spusťte Noru a vložte token do pole v nastavení.

Klikněte na Uložit Nastavení (token se uloží lokálně do config.json).

📈 Jak Noru používat
Importujte data: Použijte CSV soubor v následujícím formátu (oddělený čárkou):
