# Klinik-Patientenverwaltungssystem
# Designed by Isa Mohsenian :)
# letzte Version mit Suchfunktion

import tkinter as tk
from tkinter import ttk, simpledialog
import json
import os


class Benachrichtigung:
    """Klasse für Benachrichtigungen in Lila"""

    @staticmethod
    def zeigen(parent, titel, nachricht, ist_erfolg=True):
        popup = tk.Toplevel(parent)
        popup.title(titel)

        # Farben
        if ist_erfolg:
            hauptfarbe = '#6B2DC6'  # Lila für Erfolg
            akzentfarbe = '#9B4DFF'  # Helllila
            icon = "✅"
        else:
            hauptfarbe = '#EF4444'  # Rot für Fehler
            akzentfarbe = '#DC2626'  # Dunkelrot
            icon = "❌"

        popup.configure(bg=hauptfarbe)
        popup.geometry("400x180")
        popup.resizable(False, False)

        # Zentrieren
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 90
        popup.geometry(f"+{x}+{y}")

        # Rahmen
        frame = tk.Frame(popup, bg='white', relief=tk.RAISED, bd=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Icon
        tk.Label(frame, text=icon, font=("Arial", 35), bg='white').pack(pady=(15, 5))

        # Nachricht
        tk.Label(frame, text=nachricht, font=("Arial", 11, "bold"),
                 bg='white', fg='#333333', wraplength=350, justify='center').pack(pady=5, padx=15)

        # Button
        tk.Button(frame, text="OK", command=popup.destroy,
                  bg=hauptfarbe if ist_erfolg else akzentfarbe,
                  fg='white', font=("Arial", 10, "bold"),
                  padx=20, pady=5, cursor='hand2',
                  activebackground=akzentfarbe, bd=0).pack(pady=(10, 15))

        # Automatisches Schließen nach 3 Sekunden
        popup.after(3000, popup.destroy)

        return popup


class KlinikVerwaltung:
    def __init__(self, root):
        self.root = root
        self.root.title("Klinik-Patientenverwaltung")
        self.root.geometry("1100x700")
        self.root.configure(bg='#E8D5F5')

        # Farben
        self.primary = '#6B2DC6'  # Lila Hauptfarbe
        self.secondary = '#9B4DFF'  # Helllila
        self.white = '#FFFFFF'
        self.light_bg = '#F3E8FF'  # Ganz helles Lila für Hintergrund

        # Dateien
        self.pw_file = "passwort.json"
        self.data_file = "patienten.json"

        # Daten
        self.patienten = []  # Alle Patienten (Original)
        self.gefilterte_patienten = []  # für Suche
        self.next_id = 1
        self.current_edit_id = None
        self.such_text = ""  # Aktueller Suchtext

        # UI Elemente
        self.btn_register = None
        self.btn_edit = None
        self.entry_vorname = None
        self.entry_nachname = None
        self.entry_alter = None
        self.entry_aktennummer = None
        self.text_krankengeschichte = None
        self.hint_label = None
        self.tree = None
        self.suche_entry = None  # Suchfeld

        self.root.withdraw()
        self.start()

    def show_notification(self, nachricht, ist_erfolg=True):
        """Zeigt eine lila Benachrichtigung an"""
        Benachrichtigung.zeigen(self.root, "Benachrichtigung", nachricht, ist_erfolg)

    def start(self):
        """Startet die Anwendung"""
        if os.path.exists(self.pw_file):
            self.show_login()
        else:
            self.first_time_setup()

    def first_time_setup(self):
        """Erstmalige Einrichtung - Passwort erstellen"""
        pw = simpledialog.askstring("Passwort einrichten",
                                    "🏥 Willkommen beim Klinik-System!\n\n"
                                    "Bitte erstellen Sie ein 4-stelliges Passwort:\n"
                                    "(Nur Ziffern 0-9)",
                                    parent=self.root,
                                    show='*')

        if pw:
            if len(pw) == 4 and pw.isdigit():
                pw2 = simpledialog.askstring("Passwort bestätigen",
                                             "Bitte wiederholen Sie Ihr Passwort:",
                                             parent=self.root,
                                             show='*')
                if pw == pw2:
                    with open(self.pw_file, 'w') as f:
                        json.dump({"password": pw}, f)
                    self.show_notification("✅ Passwort wurde erfolgreich erstellt!", True)
                    self.show_login()
                else:
                    self.show_notification("❌ Passwörter stimmen nicht überein!", False)
                    self.first_time_setup()
            else:
                self.show_notification("❌ Passwort muss genau 4 Ziffern enthalten!", False)
                self.first_time_setup()
        else:
            self.root.quit()

    def show_login(self):
        """Login-Dialog anzeigen"""
        pw = simpledialog.askstring("Login",
                                    "🔐 Klinik System Login\n\n"
                                    "Bitte geben Sie Ihr Passwort ein:",
                                    parent=self.root,
                                    show='*')

        if pw:
            try:
                with open(self.pw_file, 'r') as f:
                    data = json.load(f)
                    if pw == data.get("password", ""):
                        self.show_notification("✅ Login erfolgreich! Willkommen zurück!", True)
                        self.root.deiconify()
                        self.load_data()
                        self.create_ui()
                        self.filter_patienten()  # Initiale Filterung
                        self.update_table()
                        self.show_welcome()
                    else:
                        self.show_notification("❌ Falsches Passwort! Bitte versuchen Sie es erneut.", False)
                        self.show_login()
            except:
                self.show_notification("❌ Fehler beim Laden des Passworts!", False)
                self.show_login()
        else:
            self.root.quit()

    def change_password(self):
        """Passwort ändern"""
        old = simpledialog.askstring("Passwort ändern",
                                     "Aktuelles Passwort eingeben:",
                                     parent=self.root,
                                     show='*')
        if not old:
            return

        try:
            with open(self.pw_file, 'r') as f:
                data = json.load(f)
                if old != data.get("password", ""):
                    self.show_notification("❌ Aktuelles Passwort ist falsch!", False)
                    return
        except:
            self.show_notification("❌ Fehler beim Laden!", False)
            return

        new = simpledialog.askstring("Passwort ändern",
                                     "Neues Passwort (4 Ziffern):",
                                     parent=self.root,
                                     show='*')
        if not new:
            return

        if len(new) != 4 or not new.isdigit():
            self.show_notification("❌ Passwort muss genau 4 Ziffern enthalten!", False)
            return

        confirm = simpledialog.askstring("Passwort ändern",
                                         "Neues Passwort wiederholen:",
                                         parent=self.root,
                                         show='*')
        if new != confirm:
            self.show_notification("❌ Passwörter stimmen nicht überein!", False)
            return

        with open(self.pw_file, 'w') as f:
            json.dump({"password": new}, f)

        self.show_notification("✅ Passwort wurde erfolgreich geändert!", True)

    def load_data(self):
        """Lädt Patientendaten"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patienten = data.get("patienten", [])
                    self.next_id = data.get("next_id", 1)
            except:
                self.patienten = []
                self.next_id = 1
        else:
            self.patienten = []
            self.next_id = 1

    def save_data(self):
        """Speichert Patientendaten"""
        try:
            data = {
                "patienten": self.patienten,
                "next_id": self.next_id
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def filter_patienten(self):
        """Filtert Patienten basierend auf Suchtext"""
        if not self.such_text.strip():
            # Wenn Suchtext leer ist, zeige alle Patienten
            self.gefilterte_patienten = self.patienten.copy()
        else:
            # Suche in Vorname und Nachname (case-insensitive)
            such_lower = self.such_text.lower()
            self.gefilterte_patienten = [
                p for p in self.patienten
                if such_lower in p["vorname"].lower()
                   or such_lower in p["nachname"].lower()
                   or such_lower in p["aktennummer"].lower()  # Auch in Aktennummer suchen
            ]

        # Tabelle aktualisieren
        self.update_table()

        # Anzahl der gefundenen Patienten anzeigen
        anzahl_gefunden = len(self.gefilterte_patienten)
        gesamt = len(self.patienten)
        if self.such_text.strip():
            self.hint_label.config(text=f"🔍 {anzahl_gefunden} von {gesamt} Patienten gefunden")
        else:
            self.hint_label.config(text="")

    def on_suche_change(self, event=None):
        """Wird aufgerufen, wenn sich der Suchtext ändert"""
        self.such_text = self.suche_entry.get().strip()
        self.filter_patienten()

    def suche_clearen(self):
        """Löscht das Suchfeld und zeigt alle Patienten"""
        self.suche_entry.delete(0, tk.END)
        self.such_text = ""
        self.filter_patienten()
        self.suche_entry.focus()

    def create_ui(self):
        """Erstellt die Benutzeroberfläche"""

        # ========== MENÜLEISTE ==========
        menu = tk.Frame(self.root, bg=self.white, pady=10)
        menu.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(menu, text="📋 Patientenverwaltung", font=("Arial", 18, "bold"),
                 bg=self.white, fg=self.primary).pack(side=tk.LEFT, padx=20)

        # Passwort ändern Button
        tk.Button(menu, text="🔐 Passwort ändern", command=self.change_password,
                  bg=self.primary, fg='white', font=("Arial", 9, "bold"),
                  padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=5)

        self.btn_register = tk.Button(menu, text="➕ Neuen Patienten registrieren",
                                      command=self.register_patient,
                                      bg=self.secondary, fg='white',
                                      font=("Arial", 10, "bold"),
                                      padx=15, pady=5, cursor='hand2')
        self.btn_register.pack(side=tk.RIGHT, padx=10)

        self.btn_edit = tk.Button(menu, text="✏️ Patienten bearbeiten",
                                  command=self.edit_patient,
                                  bg=self.secondary, fg='white',
                                  font=("Arial", 10, "bold"),
                                  padx=15, pady=5, cursor='hand2')
        self.btn_edit.pack(side=tk.RIGHT, padx=10)

        # ========== SUCHLEISTE (NEU) ==========
        such_frame = tk.Frame(self.root, bg=self.white, relief=tk.RAISED, bd=1)
        such_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Innerer Container für die Suche
        such_container = tk.Frame(such_frame, bg=self.white)
        such_container.pack(pady=8, padx=10)

        # Such-Label
        tk.Label(such_container, text="🔍 Suche:", font=("Arial", 10, "bold"),
                 bg=self.white, fg=self.primary).pack(side=tk.LEFT, padx=(0, 10))

        # Such-Eingabefeld
        self.suche_entry = tk.Entry(such_container, width=35, font=("Arial", 10),
                                    relief=tk.SOLID, bd=1)
        self.suche_entry.pack(side=tk.LEFT, padx=5)
        self.suche_entry.bind('<KeyRelease>', self.on_suche_change)  # Bei jeder Tastatureingabe filtern

        # Löschen-Button
        tk.Button(such_container, text="✖ Löschen", command=self.suche_clearen,
                  bg=self.secondary, fg='white', font=("Arial", 9, "bold"),
                  padx=10, pady=3, cursor='hand2').pack(side=tk.LEFT, padx=10)

        # Hinweis für die Suche
        such_hinweis = tk.Label(such_container, text="(Suche in Vorname, Nachname oder Aktennummer)",
                                font=("Arial", 8, "italic"), bg=self.white, fg='gray')
        such_hinweis.pack(side=tk.LEFT, padx=10)

        # ========== EINGABEFORMULAR ==========
        form = tk.Frame(self.root, bg=self.white, relief=tk.RAISED, bd=1)
        form.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(form, text="✏️ Patientendaten eingeben / bearbeiten", font=("Arial", 12, "bold"),
                 bg=self.white, fg=self.primary).pack(pady=10)

        container = tk.Frame(form, bg=self.white)
        container.pack(padx=20, pady=10)

        # Zeile 1
        row1 = tk.Frame(container, bg=self.white)
        row1.pack(pady=5)
        tk.Label(row1, text="Vorname:", bg=self.white, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.entry_vorname = tk.Entry(row1, width=20, font=("Arial", 10))
        self.entry_vorname.pack(side=tk.LEFT, padx=5)
        tk.Label(row1, text="Nachname:", bg=self.white, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.entry_nachname = tk.Entry(row1, width=20, font=("Arial", 10))
        self.entry_nachname.pack(side=tk.LEFT, padx=5)

        # Zeile 2
        row2 = tk.Frame(container, bg=self.white)
        row2.pack(pady=5)
        tk.Label(row2, text="Alter:", bg=self.white, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.entry_alter = tk.Entry(row2, width=10, font=("Arial", 10))
        self.entry_alter.pack(side=tk.LEFT, padx=5)
        tk.Label(row2, text="Aktennummer:", bg=self.white, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.entry_aktennummer = tk.Entry(row2, width=15, font=("Arial", 10))
        self.entry_aktennummer.pack(side=tk.LEFT, padx=5)

        # Zeile 3
        tk.Label(container, text="Krankengeschichte:", bg=self.white,
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 0))
        self.text_krankengeschichte = tk.Text(container, width=80, height=4,
                                              font=("Arial", 10))
        self.text_krankengeschichte.pack(pady=5)

        # Buttons
        btn_frame2 = tk.Frame(container, bg=self.white)
        btn_frame2.pack(pady=10)

        tk.Button(btn_frame2, text="🗑️ Felder leeren", command=self.clear_form,
                  bg='#EF4444', fg='white', font=("Arial", 9, "bold"),
                  padx=15, pady=3, cursor='hand2').pack(side=tk.LEFT, padx=5)

        self.hint_label = tk.Label(container, text="", bg=self.white,
                                   font=("Arial", 9, "italic"), fg=self.secondary)
        self.hint_label.pack(pady=5)

        # ========== TABELLE ==========
        table_frame = tk.Frame(self.root, bg=self.white, relief=tk.RAISED, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(table_frame, text="📋 Patientenliste", font=("Arial", 12, "bold"),
                 bg=self.white, fg=self.primary).pack(pady=10)

        table_container = tk.Frame(table_frame, bg=self.white)
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_y = tk.Scrollbar(table_container)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        columns = ("id", "vorname", "nachname", "alter", "aktennummer", "geschichte")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings",
                                 yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set, height=12)

        # Styling der Tabelle
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 9), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        self.tree.heading("id", text="ID")
        self.tree.heading("vorname", text="Vorname")
        self.tree.heading("nachname", text="Nachname")
        self.tree.heading("alter", text="Alter")
        self.tree.heading("aktennummer", text="Aktennummer")
        self.tree.heading("geschichte", text="Krankengeschichte")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("vorname", width=150)
        self.tree.column("nachname", width=150)
        self.tree.column("alter", width=60, anchor=tk.CENTER)
        self.tree.column("aktennummer", width=120)
        self.tree.column("geschichte", width=450)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def show_welcome(self):
        """Willkommens-Popup"""
        popup = tk.Toplevel(self.root)
        popup.title("Willkommen")

        # Farben
        hauptfarbe = '#6B2DC6'  # Lila

        popup.configure(bg=hauptfarbe)
        popup.geometry("480x270")
        popup.resizable(False, False)

        # Zentrieren
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 240
        y = (popup.winfo_screenheight() // 2) - 135
        popup.geometry(f"+{x}+{y}")

        # Rahmen
        frame = tk.Frame(popup, bg='white', relief=tk.RAISED, bd=3)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # محتوای اصلی با استفاده از grid برای کنترل بهتر
        main_frame = tk.Frame(frame, bg='white')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        # Icon
        icon_label = tk.Label(main_frame, text="🏥", font=("Arial", 40), bg='white')
        icon_label.grid(row=0, column=0, pady=(10, 5))

        # Titel
        title_label = tk.Label(main_frame, text="Willkommen im Klinik-System!",
                               font=("Arial", 14, "bold"),
                               bg='white', fg=hauptfarbe)
        title_label.grid(row=1, column=0, pady=(0, 5))

        # Designer
        designer_label = tk.Label(main_frame, text="Designed by Isa Mohsenian",
                                  font=("Arial", 10, "italic"),
                                  bg='white', fg='#9B4DFF')
        designer_label.grid(row=2, column=0, pady=(0, 10))

        # Trennlinie
        separator = tk.Frame(main_frame, bg='#E8D5F5', height=2)
        separator.grid(row=3, column=0, sticky="ew", padx=20, pady=5)

        # Anzahl Patienten
        anzahl = len(self.patienten)
        count_label = tk.Label(main_frame, text=f"📊 {anzahl} Patienten gespeichert",
                               font=("Arial", 11, "bold"),
                               bg='white', fg=hauptfarbe)
        count_label.grid(row=4, column=0, pady=(10, 15))

        # OK Button
        ok_btn = tk.Button(main_frame, text="OK", command=popup.destroy,
                           bg=hauptfarbe, fg='white', font=("Arial", 10, "bold"),
                           padx=25, pady=5, cursor='hand2',
                           activebackground='#9B4DFF', bd=0, width=10)
        ok_btn.grid(row=5, column=0, pady=(0, 10))

        # تنظیم وزن ستون برای
        main_frame.grid_columnconfigure(0, weight=1)

        # Automatisches Schließen nach 4 Sekunden
        popup.after(4000, popup.destroy)

    def clear_form(self):
        """Löscht das Formular"""
        if self.entry_vorname:
            self.entry_vorname.delete(0, tk.END)
            self.entry_nachname.delete(0, tk.END)
            self.entry_alter.delete(0, tk.END)
            self.entry_aktennummer.delete(0, tk.END)
            self.text_krankengeschichte.delete("1.0", tk.END)
            self.current_edit_id = None
            self.hint_label.config(text="")
            if self.btn_register:
                self.btn_register.config(text="➕ Neuen Patienten registrieren")

    def register_patient(self):
        """Registriert einen neuen Patienten"""
        vorname = self.entry_vorname.get().strip()
        nachname = self.entry_nachname.get().strip()
        alter = self.entry_alter.get().strip()
        aktennummer = self.entry_aktennummer.get().strip()
        geschichte = self.text_krankengeschichte.get("1.0", tk.END).strip()

        if not vorname or not nachname:
            self.show_notification("Bitte Vornamen und Nachnamen eingeben!", False)
            return

        try:
            alter_int = int(alter)
            if alter_int < 0 or alter_int > 150:
                raise ValueError
        except:
            self.show_notification("Bitte ein gültiges Alter (0-150) eingeben!", False)
            return

        if not aktennummer:
            self.show_notification("Bitte Aktennummer eingeben!", False)
            return

        for p in self.patienten:
            if p["aktennummer"] == aktennummer:
                self.show_notification(f"Aktennummer {aktennummer} existiert bereits!", False)
                return

        patient = {
            "id": self.next_id,
            "vorname": vorname,
            "nachname": nachname,
            "alter": alter_int,
            "aktennummer": aktennummer,
            "krankengeschichte": geschichte
        }

        self.patienten.append(patient)
        self.next_id += 1

        if self.save_data():
            self.filter_patienten()  # Filter anwenden
            self.clear_form()
            self.show_notification(f"✅ Patient {vorname} {nachname} wurde erfolgreich registriert!", True)
        else:
            self.show_notification("Fehler beim Speichern der Daten!", False)

    def edit_patient(self):
        """Bearbeitet einen Patienten"""
        if self.current_edit_id is None:
            self.show_notification("Bitte wählen Sie zuerst einen Patienten aus!", False)
            return

        vorname = self.entry_vorname.get().strip()
        nachname = self.entry_nachname.get().strip()
        alter = self.entry_alter.get().strip()
        aktennummer = self.entry_aktennummer.get().strip()
        geschichte = self.text_krankengeschichte.get("1.0", tk.END).strip()

        if not vorname or not nachname:
            self.show_notification("Bitte Vornamen und Nachnamen eingeben!", False)
            return

        try:
            alter_int = int(alter)
            if alter_int < 0 or alter_int > 150:
                raise ValueError
        except:
            self.show_notification("Bitte ein gültiges Alter (0-150) eingeben!", False)
            return

        if not aktennummer:
            self.show_notification("Bitte Aktennummer eingeben!", False)
            return

        for p in self.patienten:
            if p["aktennummer"] == aktennummer and p["id"] != self.current_edit_id:
                self.show_notification(f"Aktennummer {aktennummer} existiert bereits!", False)
                return

        for p in self.patienten:
            if p["id"] == self.current_edit_id:
                p["vorname"] = vorname
                p["nachname"] = nachname
                p["alter"] = alter_int
                p["aktennummer"] = aktennummer
                p["krankengeschichte"] = geschichte
                break

        if self.save_data():
            self.filter_patienten()  # Filter anwenden
            self.clear_form()
            self.show_notification(f"✅ Patient {vorname} {nachname} wurde erfolgreich bearbeitet!", True)
        else:
            self.show_notification("Fehler beim Speichern der Daten!", False)

    def on_select(self, event=None):
        """Wählt einen Patienten aus der Tabelle aus (aus gefilterter Liste)"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        patient_id = item["values"][0]

        # Suche in der gefilterten Liste (nicht in der Original-Liste)
        for p in self.gefilterte_patienten:
            if p["id"] == patient_id:
                self.clear_form()
                self.entry_vorname.insert(0, p["vorname"])
                self.entry_nachname.insert(0, p["nachname"])
                self.entry_alter.insert(0, str(p["alter"]))
                self.entry_aktennummer.insert(0, p["aktennummer"])
                self.text_krankengeschichte.insert("1.0", p["krankengeschichte"])

                self.current_edit_id = patient_id
                self.hint_label.config(text=f"✏️ Bearbeite: {p['vorname']} {p['nachname']}")
                self.btn_register.config(text="💾 Änderungen speichern")
                break

    def update_table(self):
        """Aktualisiert die Tabelle mit den gefilterten Patienten"""
        if not self.tree:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in self.gefilterte_patienten:
            geschichte = p["krankengeschichte"][:50] + "..." if len(p["krankengeschichte"]) > 50 else p[
                "krankengeschichte"]
            self.tree.insert("", tk.END, values=(
                p["id"], p["vorname"], p["nachname"], p["alter"], p["aktennummer"], geschichte
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = KlinikVerwaltung(root)
    root.mainloop()