import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import logging

# ---------- Логирование ----------
logging.basicConfig(filename="sorter_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------- CustomTkinter ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Sorting by folders")
app.geometry("800x600")

# ---------- Иконка ----------
icon_path = "Sorting_by_folders_Icon.ico"
if os.path.exists(icon_path):
    try:
        app.iconbitmap(icon_path)
    except Exception as e:
        logging.error(f"Не удалось установить иконку: {e}")

# ---------- Конфиг ----------
def create_default_config(file_path="config.cfg"):
    if not os.path.exists(file_path):
        default_content = """# Расширение = Название папки
.jpg = Images
.png = Images
.mp4 = Videos
.mp3 = Music
.pdf = Documents
.docx = Documents
.zip = Archives
.rar = Archives
.exe = Software
.=Other
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(default_content)

def load_config(file_path="config.cfg"):
    create_default_config(file_path)
    ext_map = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                ext, folder = line.strip().split("=")
                ext_map[ext.strip().lower()] = folder.strip()
    return ext_map

# ---------- Открытие последней папки ----------
def open_last_sorted_folder():
    if hasattr(open_last_sorted_folder, "last_path") and os.path.exists(open_last_sorted_folder.last_path):
        os.startfile(open_last_sorted_folder.last_path)
    else:
        messagebox.showwarning("Внимание", "Папка ещё не сортировалась.")

# ---------- Редактирование config.cfg ----------
def show_config():
    create_default_config()
    config_window = ctk.CTkToplevel(app)
    config_window.title("⚙️ Редактировать config.cfg")
    config_window.geometry("700x500")

    text_box = ctk.CTkTextbox(config_window)
    text_box.pack(fill="both", expand=True, padx=10, pady=(10, 5))

    with open("config.cfg", "r", encoding="utf-8") as f:
        text_box.insert("0.0", f.read())

    def save_and_close():
        try:
            with open("config.cfg", "w", encoding="utf-8") as f:
                f.write(text_box.get("0.0", "end-1c"))
            messagebox.showinfo("Успех", "Файл config.cfg сохранён.")
            config_window.destroy()
        except Exception as e:
            logging.error(f"Ошибка при сохранении config.cfg: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    ctk.CTkButton(config_window, text="💾 Сохранить", command=save_and_close).pack(pady=5)
    ctk.CTkButton(config_window, text="❌ Закрыть", command=config_window.destroy).pack(pady=5)

# ---------- Сортировка ----------
def sort_files(folder=None):
    if not folder:
        folder = filedialog.askdirectory(title="Выберите папку для сортировки")
    if not folder:
        return

    status_label.configure(text="🔄 Идёт сортировка...")
    app.update_idletasks()

    rules = load_config()
    try:
        files = os.listdir(folder)
    except Exception as e:
        logging.error(f"Ошибка чтения папки: {e}")
        return

    for file in files:
        full_path = os.path.join(folder, file)
        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(file)[1].lower()
        dest_folder = rules.get(ext, rules.get(".", "Other"))
        dest_path = os.path.join(folder, dest_folder)
        os.makedirs(dest_path, exist_ok=True)

        try:
            shutil.move(full_path, os.path.join(dest_path, file))
        except Exception as e:
            logging.error(f"Ошибка при перемещении {file}: {e}")

    open_last_sorted_folder.last_path = folder
    messagebox.showinfo("Готово", "✅ Сортировка завершена!")
    status_label.configure(text="✅ Сортировка завершена!")

# ---------- Интерфейс ----------
frame = ctk.CTkFrame(app, corner_radius=12)
frame.pack(padx=20, pady=10, fill="x")

ctk.CTkLabel(frame, text="📁 Sorting by folders", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

ctk.CTkButton(frame, text="📂 Выбрать папку и сортировать", height=40, width=300, fg_color="#5cb85c", hover_color="#4cae4c", command=sort_files).pack(pady=5)
ctk.CTkButton(frame, text="⚙️ Редактировать config.cfg", height=32, width=300, command=show_config).pack(pady=5)
ctk.CTkButton(frame, text="📂 Открыть отсортированную папку", height=32, width=300, command=open_last_sorted_folder).pack(pady=5)

status_label = ctk.CTkLabel(frame, text="⏳ Готов к сортировке", text_color="gray")
status_label.pack(pady=20)

# ---------- Запуск ----------
app.mainloop()
