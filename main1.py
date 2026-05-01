import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("750x450")

        self.workouts = []
        self.load_from_file()

        # Поля ввода
        input_frame = tk.LabelFrame(root, text="Новая тренировка", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e")
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="e")
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, width=15)
        self.type_combo['values'] = ("Бег", "Велосипед", "Плавание", "Силовая", "Йога", "Другое")
        self.type_combo.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Длительность (мин):").grid(row=1, column=0, sticky="e")
        self.duration_entry = tk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Button(input_frame, text="Добавить тренировку", command=self.add_workout, bg="lightgreen").grid(row=1, column=2, columnspan=2, pady=5)

        # Фильтры
        filter_frame = tk.LabelFrame(root, text="Фильтры", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0)
        self.filter_date_entry = tk.Entry(filter_frame, width=12)
        self.filter_date_entry.grid(row=0, column=1)

        tk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=2)
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, width=12)
        self.filter_type_combo['values'] = ("Все", "Бег", "Велосипед", "Плавание", "Силовая", "Йога", "Другое")
        self.filter_type_combo.current(0)
        self.filter_type_combo.grid(row=0, column=3)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10)
        tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5)

        # Таблица записей
        self.tree = ttk.Treeview(root, columns=("date", "type", "duration"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки сохранения/загрузки
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_file, bg="lightblue").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_file).pack(side="left", padx=5)

        self.update_table()

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_workout(self):
        date = self.date_entry.get().strip()
        workout_type = self.type_var.get().strip()
        duration = self.duration_entry.get().strip()

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        if not workout_type:
            messagebox.showerror("Ошибка", "Выберите тип тренировки")
            return
        try:
            duration_val = float(duration)
            if duration_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return

        self.workouts.append({
            "date": date,
            "type": workout_type,
            "duration": duration_val
        })
        self.update_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.type_var.set("")
        self.duration_entry.delete(0, tk.END)

    def update_table(self, filtered_workouts=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = filtered_workouts if filtered_workouts is not None else self.workouts
        for w in data:
            self.tree.insert("", tk.END, values=(
                w["date"],
                w["type"],
                w["duration"]
            ))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_type = self.filter_type_var.get().strip()

        filtered = self.workouts[:]

        if filter_date:
            filtered = [w for w in filtered if w["date"] == filter_date]

        if filter_type and filter_type != "Все":
            filtered = [w for w in filtered if w["type"] == filter_type]

        self.update_table(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_type_var.set("Все")
        self.update_table()

    def save_to_file(self):
        with open("training_data.json", "w", encoding="utf-8") as f:
            json.dump(self.workouts, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Сохранено", "Тренировки сохранены в training_data.json")

    def load_from_file(self):
        if not os.path.exists("training_data.json"):
            return
        try:
            with open("training_data.json", "r", encoding="utf-8") as f:
                self.workouts = json.load(f)
            self.update_table()
            messagebox.showinfo("Загружено", "Данные загружены из training_data.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()