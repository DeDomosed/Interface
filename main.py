import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD
from PIL import Image, ImageTk
import os
import re
from results_page import ResultsPage  # Импорт страницы результатов


class ImageApp(TkinterDnD.Tk):
    def __init__(self, min_width=350, min_height=350):
        super().__init__()
        self.title("Выбор файлов и Drag-and-Drop")
        self.geometry("800x600")

        self.process_button = tk.Button(self, text="Обработать изображения", command=self.open_results_page)
        self.process_button.pack(pady=10)

        self.min_width = min_width
        self.min_height = min_height
        self.minsize(self.min_width, self.min_height)

        self.resizable(True, True)

        self.choose_files_button = tk.Button(self, text="Выбрать файлы", command=self.choose_files)
        self.choose_files_button.pack(pady=10)

        self.drop_label = tk.Label(self, text="Или перетащите изображения сюда", bg="lightgray", width=50, height=5)
        self.drop_label.pack(pady=20)

        self.image_frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        self.drop_label.drop_target_register('DND_Files')
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)

        self.results_page = ResultsPage(self)

        #добавлен список для хранения всех картинок
        self.images = []

    def choose_files(self):
        file_paths = tk.filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=(("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*"))
        )
        if file_paths:
            for file_path in file_paths:
                self.display_image(file_path)

    def on_drop(self, event):
        file_paths = self.extract_file_paths(event.data)
        if not file_paths:
            self.drop_label.config(text="Ошибка: не удалось извлечь файлы из перетаскивания")
            return

        for file_path in file_paths:
            file_path = file_path.strip('{}')
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.display_image(file_path)
            else:
                self.drop_label.config(text=f"Файл '{file_path}' не является изображением")

    def extract_file_paths(self, data):
        file_paths = re.findall(r'\{[^}]+\}|[^\s\{]+', data)
        if not file_paths:
            file_paths = data.split()
        return file_paths

    def display_image(self, file_path):
        try:
            if not os.path.exists(file_path):
                self.drop_label.config(text=f"Ошибка: файл '{file_path}' не существует")
                return

            self.images.append(file_path)
            print(self.images)
            image = Image.open(file_path)
            #добавлены ширина и высота картинки
            image_width = 200
            image_height = 150
            image.thumbnail((image_width, image_height))
            photo = ImageTk.PhotoImage(image)

            image_label = tk.Label(self.image_frame, image=photo)
            image_label.photo = photo
            #image_label.pack(side="left", padx=10, pady=10, fill=tk.Y, expand=True)
            i = len(self.images) - 1
            columns_count = self.image_frame.winfo_width() // image_width
            image_label.grid(row=i//columns_count, column=i%columns_count)

            # Добавляем обработчик нажатия на миниатюру
            image_label.bind("<Button-1>", lambda event, path=file_path: self.open_large_image(path))

        except Exception as e:
            self.drop_label.config(text=f"Ошибка при загрузке изображения: {str(e)}")

    def open_large_image(self, file_path):
        """Открывает изображение в большем размере с ограничением размера окна."""
        try:
            # Открываем изображение в оригинальном размере
            image = Image.open(file_path)

            # Ограничиваем размер изображения, если оно слишком большое
            max_width = 800  # Максимальная ширина окна
            max_height = 600  # Максимальная высота окна

            # Получаем текущие размеры изображения
            img_width, img_height = image.size  # image.size возвращает (width, height)

            # Вычисляем новый размер изображения с учетом максимальных ограничений
            aspect_ratio = img_width / img_height
            if img_width > max_width or img_height > max_height:
                if aspect_ratio > 1:
                    new_width = max_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = max_height
                    new_width = int(new_height * aspect_ratio)

                # Используем LANCZOS для ресайза
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Создаем новое окно для отображения изображения
            top = tk.Toplevel(self)
            top.title("Просмотр изображения")

            # Конвертируем изображение в формат для отображения
            photo = ImageTk.PhotoImage(image)

            # Отображаем изображение в новом окне
            image_label = tk.Label(top, image=photo)
            image_label.photo = photo  # Сохраняем ссылку на изображение
            image_label.pack(padx=20, pady=20)

            # Устанавливаем размер окна с учетом изображения
            top.geometry(f"{image.width + 40}x{image.height + 40}")  # Учитываем отступы

            # Добавляем кнопку для закрытия окна
            close_button = tk.Button(top, text="Закрыть", command=top.destroy)
            close_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {e}")

    def open_results_page(self):
        print("Нажата кнопка 'Обработать изображения'. Открываем страницу результатов...")
        try:
            self.results_page.display_results("result.json")  # Путь к JSON-файлу с результатами
            self.results_page.pack(fill=tk.BOTH, expand=True)

            for widget in self.winfo_children():
                if widget != self.results_page:
                    widget.pack_forget()
        except Exception as e:
            print(f"Ошибка при открытии страницы результатов: {e}")


if __name__ == "__main__":
    app = ImageApp()
    app.mainloop()