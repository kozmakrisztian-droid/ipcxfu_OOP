from abc import ABC, abstractmethod
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class Jarat(ABC):
    def __init__(self, kod, cel, ar):
        self.kod = kod
        self.cel = cel
        self.ar = ar

    @abstractmethod
    def tipus(self):
        pass

    def ar_formazva(self):
        return f"{self.ar:,}".replace(",", " ")


class BelfoldiJarat(Jarat):
    def tipus(self):
        return "Belföldi"


class NemzetkoziJarat(Jarat):
    def tipus(self):
        return "Nemzetközi"


class Legitarsasag:
    def __init__(self, nev):
        self.nev = nev
        self.jaratok = {}

    def jarat_hozzaad(self, jarat):
        self.jaratok[jarat.kod] = jarat

    def keres(self, kod):
        return self.jaratok.get(kod.upper())


class Foglalas:
    def __init__(self, azonosito, utas, jarat, datum):
        self.azonosito = azonosito
        self.utas = utas
        self.jarat = jarat
        self.datum = datum


class FoglalasiRendszer:
    def __init__(self, legitarsasag):
        self.legitarsasag = legitarsasag
        self.foglalasok = {}
        self.kovetkezo_id = 1

    def datum_ervenyes(self, datum):
        try:
            megadott = datetime.strptime(datum, "%Y-%m-%d").date()
            return megadott >= datetime.now().date()
        except ValueError:
            return False

    def uj_foglalas(self, nev, jaratkod, datum):
        if not nev.strip():
            raise ValueError("Az utas neve nem lehet üres.")

        if not self.datum_ervenyes(datum):
            raise ValueError("Hibás vagy múltbeli dátum. Példa: 2026-07-10")

        jarat = self.legitarsasag.keres(jaratkod)

        if jarat is None:
            raise ValueError("Nincs ilyen járat.")

        foglalas = Foglalas(
            self.kovetkezo_id,
            nev.strip(),
            jarat,
            datum
        )

        self.foglalasok[self.kovetkezo_id] = foglalas
        self.kovetkezo_id += 1

        return foglalas

    def foglalas_torol(self, azonosito):
        if azonosito not in self.foglalasok:
            raise ValueError("Nincs ilyen foglalási ID.")

        del self.foglalasok[azonosito]


class FoglalasiAblak:
    def __init__(self, root, rendszer):
        self.root = root
        self.rendszer = rendszer
        self.aktualis_nezet = "foglalasok"

        self.ZOLD = "#008f11"
        self.ZOLD_AKTIV = "#00FF04"
        self.PIROS = "#ff1a1a"
        self.SOTET = "#161616"
        self.PANEL = "#222222"
        self.FEHER = "#ffffff"

        self.gombok = {}

        self.root.title("🦅 Sólyom Airways")
        self.root.geometry("1180x680")
        self.root.resizable(False, False)
        self.root.configure(bg=self.SOTET)

        self.fejlec_letrehozasa()
        self.gombok_letrehozasa()
        self.nezet_cim_letrehozasa()
        self.tabla_stilus()
        self.tabla_letrehozasa()

        self.foglalasok_listazasa()

    def fejlec_letrehozasa(self):
        cim = tk.Label(
            self.root,
            text="🦅 SÓLYOM AIRWAYS",
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 24, "bold")
        )
        cim.pack(pady=(15, 8))

    def gombok_letrehozasa(self):
        kulso_keret = tk.Frame(self.root, bg=self.SOTET)
        kulso_keret.pack(fill="x", padx=35, pady=5)

        bal_keret = tk.Frame(kulso_keret, bg=self.SOTET)
        bal_keret.pack(side="left")

        kozep_keret = tk.Frame(kulso_keret, bg=self.SOTET)
        kozep_keret.pack(side="left", expand=True)

        jobb_keret = tk.Frame(kulso_keret, bg=self.SOTET)
        jobb_keret.pack(side="right")

        self.gomb_letrehoz(bal_keret, "jaratok", "JÁRATOK", self.jaratok_listazasa)
        self.gomb_letrehoz(bal_keret, "foglalasok", "FOGLALÁSOK", self.foglalasok_listazasa)

        self.gomb_letrehoz(kozep_keret, "uj", "ÚJ FOGLALÁS", self.uj_foglalas_ablak)

        self.gomb_letrehoz(jobb_keret, "torles", "TÖRLÉS", self.foglalas_torlese)
        self.gomb_letrehoz(jobb_keret, "kilepes", "KILÉPÉS", self.root.destroy)

    def gomb_letrehoz(self, szulo, kulcs, szoveg, parancs):
        gomb = tk.Button(
            szulo,
            text=szoveg,
            bg=self.ZOLD,
            fg=self.FEHER,
            activebackground=self.PIROS,
            activeforeground=self.FEHER,
            font=("Segoe UI", 10, "bold"),
            width=17,
            height=3,
            bd=0,
            cursor="hand2",
            command=parancs
        )

        gomb.pack(side="left", padx=6, pady=6)

        gomb.bind("<Enter>", lambda event: self.gomb_hover_be(kulcs))
        gomb.bind("<Leave>", lambda event: self.gomb_hover_ki(kulcs))

        self.gombok[kulcs] = gomb

    def gomb_hover_be(self, kulcs):
        self.gombok[kulcs].config(bg=self.PIROS)

    def gomb_hover_ki(self, kulcs):
        if kulcs == self.aktualis_nezet:
            self.gombok[kulcs].config(bg=self.ZOLD_AKTIV)
        else:
            self.gombok[kulcs].config(bg=self.ZOLD)

    def aktiv_gomb_beallitasa(self, aktiv_kulcs):
        for kulcs, gomb in self.gombok.items():
            if kulcs == aktiv_kulcs:
                gomb.config(bg=self.ZOLD_AKTIV)
            else:
                gomb.config(bg=self.ZOLD)

    def nezet_cim_letrehozasa(self):
        self.nezet_cim = tk.Label(
            self.root,
            text="",
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 14, "bold")
        )
        self.nezet_cim.pack(pady=(12, 0))

    def nezet_cim_frissitese(self, szoveg):
        self.nezet_cim.config(text=szoveg)

    def tabla_stilus(self):
        stilus = ttk.Style()
        stilus.theme_use("clam")

        stilus.configure(
            "Treeview",
            background=self.PANEL,
            foreground=self.FEHER,
            fieldbackground=self.PANEL,
            rowheight=30,
            font=("Segoe UI", 10),
            borderwidth=0
        )

        stilus.configure(
            "Treeview.Heading",
            background=self.ZOLD,
            foreground=self.FEHER,
            font=("Segoe UI", 10, "bold")
        )

        stilus.map(
            "Treeview",
            background=[("selected", self.PIROS)],
            foreground=[("selected", self.FEHER)]
        )

    def tabla_letrehozasa(self):
        self.tabla_keret = tk.Frame(self.root, bg=self.SOTET)

        self.tabla_keret.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        self.tabla = None

    def tabla_ujraepitese(self, oszlopok, fejlecek, szelessegek):
        if self.tabla is not None:
            self.tabla.destroy()

        self.tabla = ttk.Treeview(
            self.tabla_keret,
            columns=oszlopok,
            show="headings",
            height=20
        )

        for oszlop in oszlopok:
            self.tabla.heading(oszlop, text=fejlecek[oszlop])
            self.tabla.column(
                oszlop,
                width=szelessegek[oszlop][0],
                anchor=szelessegek[oszlop][1]
            )

        self.tabla.pack(fill="both", expand=True)

    def foglalas_oszlopok_beallitasa(self):
        oszlopok = ("id", "utas", "jarat", "cel", "datum", "ar")

        fejlecek = {
            "id": "ID",
            "utas": "UTAS",
            "jarat": "JÁRAT",
            "cel": "CÉLÁLLOMÁS",
            "datum": "DÁTUM",
            "ar": "ÁR"
        }

        szelessegek = {
            "id": (100, "center"),
            "utas": (200, "center"),
            "jarat": (200, "center"),
            "cel": (200, "center"),
            "datum": (200, "center"),
            "ar": (100, "center")
        }

        self.tabla_ujraepitese(oszlopok, fejlecek, szelessegek)

    def jarat_oszlopok_beallitasa(self):
        oszlopok = ("tipus", "jarat", "cel", "ar")

        fejlecek = {
            "tipus": "TÍPUS",
            "jarat": "JÁRAT",
            "cel": "CÉLÁLLOMÁS",
            "ar": "ÁR"
        }

        szelessegek = {
            "tipus": (250, "center"),
            "jarat": (250, "center"),
            "cel": (250, "center"),
            "ar": (250, "center")
        }

        self.tabla_ujraepitese(oszlopok, fejlecek, szelessegek)

    def foglalasok_listazasa(self):
        self.aktualis_nezet = "foglalasok"
        self.aktiv_gomb_beallitasa("foglalasok")
        self.nezet_cim_frissitese("📋 AKTUÁLIS FOGLALÁSOK")

        self.foglalas_oszlopok_beallitasa()

        for foglalas in self.rendszer.foglalasok.values():
            self.tabla.insert(
                "",
                "end",
                values=(
                    foglalas.azonosito,
                    foglalas.utas,
                    foglalas.jarat.kod,
                    foglalas.jarat.cel,
                    foglalas.datum,
                    foglalas.jarat.ar_formazva() + " Ft"
                )
            )

    def jaratok_listazasa(self):
        self.aktualis_nezet = "jaratok"
        self.aktiv_gomb_beallitasa("jaratok")
        self.nezet_cim_frissitese("✈ ELÉRHETŐ JÁRATOK")

        self.jarat_oszlopok_beallitasa()

        for jarat in self.rendszer.legitarsasag.jaratok.values():
            self.tabla.insert(
                "",
                "end",
                values=(
                    jarat.tipus(),
                    jarat.kod,
                    jarat.cel,
                    jarat.ar_formazva() + " Ft"
                )
            )

    def uj_foglalas_ablak(self):
        ablak = tk.Toplevel(self.root)
        ablak.title("Új foglalás")
        ablak.geometry("520x340")
        ablak.resizable(False, False)
        ablak.configure(bg=self.SOTET)
        ablak.grab_set()

        tk.Label(
            ablak,
            text="ÚJ FOGLALÁS",
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        tk.Label(
            ablak,
            text="Utas neve:",
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 10, "bold")
        ).pack()

        nev_mezo = tk.Entry(
            ablak,
            width=42,
            font=("Segoe UI", 10)
        )
        nev_mezo.pack(pady=5)

        tk.Label(
            ablak,
            text="Választható járat:",
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(8, 0))

        jarat_lista = []

        for jarat in self.rendszer.legitarsasag.jaratok.values():
            jarat_lista.append(
                f"{jarat.kod} | {jarat.cel} | {jarat.ar_formazva()} Ft | {jarat.tipus()}"
            )

        jarat_combo = ttk.Combobox(
            ablak,
            values=jarat_lista,
            width=58,
            state="readonly",
            font=("Segoe UI", 9)
        )
        jarat_combo.pack(pady=5)

        if jarat_lista:
            jarat_combo.current(0)

        tk.Label(
            ablak,
            text="Utazás dátuma, pl. 2026-07-10:",
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(8, 0))

        datum_mezo = tk.Entry(
            ablak,
            width=42,
            font=("Segoe UI", 10)
        )
        datum_mezo.pack(pady=5)

        def mentes():
            try:
                nev = nev_mezo.get()
                datum = datum_mezo.get()
                kivalasztott = jarat_combo.get()

                if not kivalasztott:
                    raise ValueError("Válassz ki egy járatot.")

                jaratkod = kivalasztott.split(" | ")[0]

                self.rendszer.uj_foglalas(
                    nev,
                    jaratkod,
                    datum
                )

                ablak.destroy()
                self.foglalasok_listazasa()

            except ValueError as hiba:
                self.sajat_uzenet("Hiba", str(hiba))

        mentes_gomb = self.kis_gomb(
            ablak,
            "FOGLALÁS MENTÉSE",
            mentes
        )

        mentes_gomb.pack(pady=18)

    def kis_gomb(self, szulo, szoveg, parancs):
        gomb = tk.Button(
            szulo,
            text=szoveg,
            bg=self.ZOLD,
            fg=self.FEHER,
            activebackground=self.PIROS,
            activeforeground=self.FEHER,
            font=("Segoe UI", 10, "bold"),
            width=24,
            height=2,
            bd=0,
            cursor="hand2",
            command=parancs
        )

        gomb.bind("<Enter>", lambda event: gomb.config(bg=self.PIROS))
        gomb.bind("<Leave>", lambda event: gomb.config(bg=self.ZOLD))

        return gomb

    def sajat_uzenet(self, cim, szoveg):
        ablak = tk.Toplevel(self.root)
        ablak.title(cim)
        ablak.geometry("420x220")
        ablak.resizable(False, False)
        ablak.configure(bg=self.SOTET)
        ablak.grab_set()

        tk.Label(
            ablak,
            text=cim.upper(),
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=18)

        tk.Label(
            ablak,
            text=szoveg,
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 10),
            wraplength=360,
            justify="center"
        ).pack(pady=8)

        ok_gomb = self.kis_gomb(ablak, "OK", ablak.destroy)
        ok_gomb.pack(pady=18)

    def torles_megerosites_ablak(self, azonosito, utas, jarat, cel, datum):
        ablak = tk.Toplevel(self.root)
        ablak.title("Törlés megerősítése")
        ablak.geometry("460x320")
        ablak.resizable(False, False)
        ablak.configure(bg=self.SOTET)
        ablak.grab_set()

        tk.Label(
            ablak,
            text="⚠ TÖRLÉS MEGERŐSÍTÉSE",
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 15, "bold")
        ).pack(pady=18)

        szoveg = (
            "Biztosan törlöd ezt a foglalást?\n\n"
            f"ID: {azonosito}\n"
            f"Utas: {utas}\n"
            f"Járat: {jarat}\n"
            f"Cél: {cel}\n"
            f"Dátum: {datum}"
        )

        tk.Label(
            ablak,
            text=szoveg,
            bg=self.SOTET,
            fg=self.FEHER,
            font=("Segoe UI", 10),
            justify="left"
        ).pack(pady=5)

        gombkeret = tk.Frame(ablak, bg=self.SOTET)
        gombkeret.pack(pady=20)

        def torles():
            self.rendszer.foglalas_torol(azonosito)
            ablak.destroy()
            self.foglalasok_listazasa()

        igen_gomb = self.kis_gomb(gombkeret, "IGEN, TÖRLÖM", torles)
        igen_gomb.pack(side="left", padx=8)

        megse_gomb = self.kis_gomb(gombkeret, "MÉGSE", ablak.destroy)
        megse_gomb.pack(side="left", padx=8)

    def foglalas_torlese(self):
        if self.aktualis_nezet != "foglalasok":
            self.sajat_uzenet(
                "Figyelem",
                "Törölni csak a foglalások nézetben lehet."
            )
            return

        kijelolt = self.tabla.selection()

        if not kijelolt:
            self.sajat_uzenet(
                "Figyelem",
                "Először válassz ki egy foglalást."
            )
            return

        sor = self.tabla.item(kijelolt[0])
        adatok = sor["values"]

        azonosito = int(adatok[0])
        utas = adatok[1]
        jarat = adatok[2]
        cel = adatok[3]
        datum = adatok[4]

        self.torles_megerosites_ablak(
            azonosito,
            utas,
            jarat,
            cel,
            datum
        )


def rendszer_letrehozasa():
    legitarsasag = Legitarsasag("Sólyom Airways")

    legitarsasag.jarat_hozzaad(BelfoldiJarat("HU123", "Debrecen", 18000))
    legitarsasag.jarat_hozzaad(BelfoldiJarat("HU234", "Szeged", 16500))
    legitarsasag.jarat_hozzaad(BelfoldiJarat("HU345", "Pécs", 17200))
    legitarsasag.jarat_hozzaad(BelfoldiJarat("HU456", "Győr", 15500))
    legitarsasag.jarat_hozzaad(BelfoldiJarat("HU567", "Miskolc", 14900))

    legitarsasag.jarat_hozzaad(NemzetkoziJarat("GB987", "London", 65000))
    legitarsasag.jarat_hozzaad(NemzetkoziJarat("DE876", "Berlin", 55000))
    legitarsasag.jarat_hozzaad(NemzetkoziJarat("IT765", "Róma", 59000))
    legitarsasag.jarat_hozzaad(NemzetkoziJarat("ES654", "Madrid", 72000))
    legitarsasag.jarat_hozzaad(NemzetkoziJarat("FR543", "Párizs", 68500))

    rendszer = FoglalasiRendszer(legitarsasag)

    rendszer.uj_foglalas("Kovács Anna", "HU123", "2026-07-10")
    rendszer.uj_foglalas("Nagy Péter", "HU234", "2026-07-14")
    rendszer.uj_foglalas("Szabó Éva", "HU345", "2026-08-01")
    rendszer.uj_foglalas("Tóth Béla", "HU456", "2026-08-12")
    rendszer.uj_foglalas("Varga Dóra", "HU567", "2026-08-28")
    rendszer.uj_foglalas("Kiss Gábor", "GB987", "2026-09-18")
    rendszer.uj_foglalas("Molnár Júlia", "DE876", "2026-10-03")
    rendszer.uj_foglalas("Farkas László", "IT765", "2026-10-22")
    rendszer.uj_foglalas("Balogh Réka", "ES654", "2026-11-11")
    rendszer.uj_foglalas("Horváth Máté", "FR543", "2026-12-02")

    return rendszer


if __name__ == "__main__":
    rendszer = rendszer_letrehozasa()

    root = tk.Tk()
    app = FoglalasiAblak(root, rendszer)
    root.mainloop()