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
```

# 🔑 Nastavení API
Nora vyžaduje Hugging Face Access Token (zdarma):

Získejte token na huggingface.co/settings/tokens.

Spusťte Noru a vložte token do pole v nastavení.

Klikněte na Uložit Nastavení (token se uloží lokálně do config.json).

📈 Jak Noru používat
Importujte data: Použijte CSV soubor v následujícím formátu (oddělený čárkou):

```
Datum,Kategorie,Polozka,Castka,Typ
2024-05-01,Prijem,Vyplata,45000,Prijem
2024-05-02,Byt,Najem,-15000,Vydaj
```

Ptejte se: Např. "Kolik mi zbude, když si koupím nový telefon za 10 000 Kč?"

Vytvořte report: Napište do chatu "Udělej mi report" nebo "Generuj PDF". Nora okamžitě vytvoří soubor Report_DATUM.pdf ve vaší složce.

# 🏗️ Architektura projektu

| **Komponent**  | **Technologie** |
| ------------- | ------------- |
| `GUI`  | CustomTkinter  |
| `AI Model`  | Gemma 2 (9B) via HF Inference  |
| `Zpracování dat`  | Pandas  |
| `Vizualizace`  | Matplotlib  |
| `Export`  | FPDF2  |

> [!TIP]
>## 💡 Tipy pro efektivní používání
>* **Pravidelný export**: Exportujte data ze svého internetového bankovnictví do CSV každý týden, abyste měli s Norou vždy aktuální přehled.
>* **Stručnost v dotazech**: Nora funguje nejlépe, pokud se ptáte přímo. Např. *"Udělej tabulku mých útrat za dopravu"* místo dlouhého vysvětlování.
>* **Kategorizace**: Pokud vaše banka nepoužívá kategorie, přidejte si do CSV sloupec `Kategorie` ručně. Nora pak dokáže vytvořit mnohem přesnější grafy v PDF reportu.
>* **Plánování**: Zkuste se Nory zeptat na simulace: *"Můžu si dovolit dovolenou za 20 000 Kč, když chci měsíčně ušetřit 5 000 Kč?"*

> [!NOTE]
>## ❓ Často kladené otázky (Q&A)
>
>**Otázka: Proč mi Nora odpovídá anglicky?**
>*Odpověď:* Nora má v instrukcích nastavenou češtinu. Pokud přesto odpoví anglicky, stačí jí napsat: *"Odpovídej prosím česky"*. U open-source modelů se to občas stává při prvním dotazu.
>
>**Otázka: Jsou moje finanční data v bezpečí?**
>*Odpověď:* Ano. Vaše CSV data se nikam neukládají. Nora je čte pouze do operační paměti vašeho počítače a posílá je jako textový kontext do Hugging Face API pro analýzu. Pokud chcete maximální soukromí, nepoužívejte v CSV reálná jména nebo >čísla účtů.
>
>**Otázka: Aplikace mi píše "AI Chyba: 401 Unauthorized". Co s tím?**
>*Odpověď:* Tato chyba znamená, že váš Hugging Face Token je neplatný nebo špatně zkopírovaný. Zkontrolujte, zda v nastavení aplikace nemáte v tokenu mezeru navíc.
>
>**Otázka: Můžu Noru používat úplně offline?**
>*Odpověď:* Aktuální verze vyžaduje internetové připojení pro komunikaci s modelem Gemma 2. Pro offline běh by bylo nutné upravit kód pro knihovnu `llama-cpp-python` a stáhnout model přímo do vašeho PC.
>
>**Otázka: PDF report se nevygeneroval, co se stalo?**
>*Odpověď:* Ujistěte se, že máte v CSV souboru sloupec `Castka` s číselnými hodnotami a že soubor není právě otevřený v jiném programu (např. v Excelu), což může blokovat přístup.

> [!IMPORTANT]
># 🔒 Bezpečnost
>Vaše data i API klíče zůstávají u vás. Soubor config.json, dočasné grafy a vygenerované PDF reporty jsou automaticky ignorovány Gitem, aby se předešlo jejich nechtěnému nahrání na veřejný server.

*Vyvinuto jako open-source finanční asistent. Pokud se vám Nora líbí, dejte projektu ⭐!*
