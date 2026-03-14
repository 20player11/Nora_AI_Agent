# Guide to Contributing

## Contribution Levels

Nora je komplexní projekt, který vyžaduje různé úrovně odbornosti. Podívejte se, kde můžete nejlépe pomoci na základě vašich zkušeností.

| Level | Contribution Type | Required Skills |
| ----- | ----------------- | --------------- |
| L1    | Documentation & Typos | Markdown, English/Czech |
| L2    | Bug Fixes & UI Tweaks | Python, React, CSS |
| L3    | Core AI Logic         | LLM Prompting, Data Science |
| L4    | Financial Integrations| PSD2 APIs, Encryption, Auth |

## How to Get Started

Chceme, aby proces přispívání byl co nejhladší. Postupujte podle tohoto průvodce:

1.  **Hledání úkolu:** Podívejte se do sekce [Issues](https://github.com/20player11/Nora_AI_Agent/issues). Hledejte štítky jako `good first issue` pro začátečníky nebo `help wanted` pro pokročilé funkce.
2.  **Vytvoření Forku:** Klikněte na tlačítko "Fork" v horní části repozitáře. Tím si vytvoříte vlastní kopii projektu, kde můžete bezpečně experimentovat.
3.  **Lokální nastavení:**
    * Naklonujte si svůj fork: `git clone https://github.com/VASE-JMENO/nora.git`
    * Vytvořte novou větev: `git checkout -b feature/nazev-vasi-funkce`
    * Nainstalujte vývojové závislosti: `pip install -r requirements-dev.txt`
4.  **Vývoj a testování:** Před odesláním se ujistěte, že váš kód splňuje naše standardy. Spusťte testy pomocí příkazu `pytest`.
5.  **Odeslání Pull Requestu (PR):** Pošlete své změny zpět do hlavního repozitáře. V popisu PR jasně uveďte, jaký problém řešíte a jaké testy jste provedli.

## Standards for Financial Logic

Protože Nora pracuje s penězi uživatelů, klademe extrémní důraz na přesnost:

* **Matematická integrita:** Jakákoliv změna ve výpočtech (úroky, predikce, zůstatky) musí obsahovat srovnávací test s manuálně ověřeným výsledkem.
* **Žádné halucinace:** AI modely nesmí generovat vymyšlená čísla. Všechny odpovědi Nory musí být podloženy reálnými daty z transakční historie.
* **Čistý kód:** Používejte smysluplné názvy proměnných (místo `x` použijte `remaining_budget`).



## Need Help?

Pokud si nejste jistí technickým řešením nebo máte dotaz k architektuře, neváhejte se zeptat přímo v diskuzi u daného Issue nebo se připojte k našemu komunitnímu kanálu.

**Děkujeme, že pomáháte dělat Noru chytřejší a bezpečnější pro všechny!**
