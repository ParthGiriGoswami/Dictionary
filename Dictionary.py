import customtkinter as ctk, sqlite3
from tkinter import Listbox, Scrollbar, RIGHT, Y, LEFT, END, messagebox
class DictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dictionary App")
        self.root.geometry("1000x700+10+10")
        self.add_window = None
        self.edit_window = None
        self.init_db()
        self.build_ui()
        self.load_words()
    def init_db(self):
        conn = sqlite3.connect("dictionary.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                meaning TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    def build_ui(self):
        self.left_frame = ctk.CTkFrame(self.root, width=350)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.search_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Type to filter words...")
        self.search_entry.pack(pady=(10, 5), padx=10, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_words)
        self.listbox_frame = ctk.CTkFrame(self.left_frame)
        self.listbox_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.scrollbar = Scrollbar(self.listbox_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.word_listbox = Listbox(
            self.listbox_frame,
            yscrollcommand=self.scrollbar.set,
            exportselection=False,
            bg="black",
            fg="white",
            font=("Arial", 13),
            width=40
        )
        self.word_listbox.pack(side=LEFT, fill="both", expand=True)
        self.scrollbar.config(command=self.word_listbox.yview)
        self.word_listbox.bind("<<ListboxSelect>>", self.on_word_select)
        self.right_frame = ctk.CTkFrame(self.root)
        self.right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        top_row = ctk.CTkFrame(self.right_frame)
        top_row.pack(fill="x", pady=(10, 5), padx=10)
        self.word_search = ctk.CTkEntry(top_row, placeholder_text="Enter word to search...")
        self.word_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        search_btn = ctk.CTkButton(top_row, text="Search", command=self.search_word)
        search_btn.pack(side="left")
        self.meaning_box = ctk.CTkTextbox(self.right_frame, height=300)
        self.meaning_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.meaning_box.configure(state="disabled")
        button_row = ctk.CTkFrame(self.right_frame)
        button_row.pack(pady=(5, 10))
        ctk.CTkButton(button_row, text="➕ Add Word", command=self.open_add_window).pack(side="left", padx=10)
        ctk.CTkButton(button_row, text="✏️ Edit Word", command=self.open_edit_window).pack(side="left", padx=10)
        ctk.CTkButton(button_row, text="🗑 Delete Word", command=self.delete_word).pack(side="left", padx=10)
    def load_words(self):
        conn = sqlite3.connect("dictionary.db")
        cursor = conn.cursor()
        cursor.execute("SELECT word FROM dictionary ORDER BY word ASC")
        self.all_words = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.update_listbox(self.all_words)
    def update_listbox(self, word_list):
        self.word_listbox.delete(0, END)
        for word in word_list:
            self.word_listbox.insert(END, word)
    def filter_words(self, event=None):
        query = self.search_entry.get().strip().lower()
        filtered = [w for w in self.all_words if query in w.lower()]
        self.update_listbox(filtered)
    def on_word_select(self, event):
        selection = self.word_listbox.curselection()
        if selection:
            word = self.word_listbox.get(selection[0])
            self.display_word(word)
    def display_word(self, word):
        conn = sqlite3.connect("dictionary.db")
        cursor = conn.cursor()
        cursor.execute("SELECT meaning FROM dictionary WHERE word = ?", (word,))
        result = cursor.fetchone()
        conn.close()
        self.word_search.delete(0, END)
        self.word_search.insert(0, word)
        self.meaning_box.configure(state="normal")
        self.meaning_box.delete("1.0", END)
        self.meaning_box.insert("1.0", result[0] if result else "No meaning found")
        self.meaning_box.configure(state="disabled")
    def search_word(self):
        word = self.word_search.get().strip()
        if word:
            self.display_word(word)
    def open_add_window(self):
        if self.add_window and self.add_window.winfo_exists():
            self.add_window.focus()
            return
        self.add_window = ctk.CTkToplevel(self.root)
        self.add_window.title("Add New Word")
        self.add_window.geometry("400x300")
        self._bring_to_front(self.add_window)
        ctk.CTkLabel(self.add_window, text="Word:").pack(pady=(20, 5))
        word_entry = ctk.CTkEntry(self.add_window)
        word_entry.pack(padx=20)
        ctk.CTkLabel(self.add_window, text="Meaning:").pack(pady=(20, 5))
        meaning_entry = ctk.CTkTextbox(self.add_window, height=100)
        meaning_entry.pack(padx=20)
        def save():
            word = word_entry.get().strip()
            meaning = meaning_entry.get("1.0", END).strip()
            if word and meaning:
                conn = sqlite3.connect("dictionary.db")
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO dictionary (word, meaning) VALUES (?, ?)", (word, meaning))
                    conn.commit()
                except sqlite3.IntegrityError:
                    pass
                conn.close()
                self.load_words()
                self.display_word(word)
                self.add_window.destroy()
                self.add_window = None
        ctk.CTkButton(self.add_window, text="Save", command=save).pack(pady=20)
        self.add_window.protocol("WM_DELETE_WINDOW", lambda: self._close_window("add"))
    def open_edit_window(self):
        if self.edit_window and self.edit_window.winfo_exists():
            self.edit_window.focus()
            return
        selection = self.word_listbox.curselection()
        if not selection:
            return
        selected_word = self.word_listbox.get(selection[0])
        conn = sqlite3.connect("dictionary.db")
        cursor = conn.cursor()
        cursor.execute("SELECT meaning FROM dictionary WHERE word = ?", (selected_word,))
        result = cursor.fetchone()
        conn.close()
        if not result:
            return
        self.edit_window = ctk.CTkToplevel(self.root)
        self.edit_window.title("Edit Word")
        self.edit_window.geometry("400x300")
        self._bring_to_front(self.edit_window)
        ctk.CTkLabel(self.edit_window, text=f"Editing: {selected_word}").pack(pady=(20, 5))
        meaning_entry = ctk.CTkTextbox(self.edit_window, height=100)
        meaning_entry.pack(padx=20)
        meaning_entry.insert("1.0", result[0])
        def save_edit():
            new_meaning = meaning_entry.get("1.0", END).strip()
            if new_meaning:
                conn = sqlite3.connect("dictionary.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE dictionary SET meaning = ? WHERE word = ?", (new_meaning, selected_word))
                conn.commit()
                conn.close()
                self.display_word(selected_word)
                self.edit_window.destroy()
                self.edit_window = None
        ctk.CTkButton(self.edit_window, text="Save Changes", command=save_edit).pack(pady=20)
        self.edit_window.protocol("WM_DELETE_WINDOW", lambda: self._close_window("edit"))
    def delete_word(self):
        selection = self.word_listbox.curselection()
        if not selection:
            return
        word = self.word_listbox.get(selection[0])
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{word}'?")
        if not confirm:
            return
        conn = sqlite3.connect("dictionary.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dictionary WHERE word = ?", (word,))
        conn.commit()
        conn.close()
        self.load_words()
        self.meaning_box.configure(state="normal")
        self.meaning_box.delete("1.0", END)
        self.meaning_box.configure(state="disabled")
        self.word_search.delete(0, END)
    def _close_window(self, window_type):
        if window_type == "add" and self.add_window:
            self.add_window.destroy()
            self.add_window = None
        elif window_type == "edit" and self.edit_window:
            self.edit_window.destroy()
            self.edit_window = None
    def _bring_to_front(self, window):
        window.lift()
        window.attributes("-topmost", True)
        window.after(10, lambda: window.attributes("-topmost", False))
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = DictionaryApp(root)
    root.mainloop()