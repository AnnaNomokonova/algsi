import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ─── Целевая функция ───────────────────────────────────────────────────────────

X_MIN, X_MAX = 0.0, 20.0

def f(x):
    return x * np.sin(x)

# ─── Генетический алгоритм (с арифметическим кроссовером) ─────────────────────

def genetic_algorithm(pop_size, generations, crossover_prob, mutation_prob, mutation_scale):
    """
    Минимизирует f(x) на [X_MIN, X_MAX].
    Модификация кроссовера: арифметический (выпуклая комбинация двух родителей).
    Возвращает (лучший_x, лучший_y, история_лучших_значений).
    """
    # Инициализация
    population = np.random.uniform(X_MIN, X_MAX, pop_size)
    best_history = []

    for _ in range(generations):
        fitness = f(population)

        # Элитизм: сохраняем лучшего
        best_idx = np.argmin(fitness)
        best_x = population[best_idx]

        # Отбор турниром
        new_pop = [best_x]  # элита
        while len(new_pop) < pop_size:
            # Выбираем двух родителей через турнир (размер 3)
            idx_a = np.random.choice(pop_size, 3, replace=False)
            idx_b = np.random.choice(pop_size, 3, replace=False)
            parent_a = population[idx_a[np.argmin(fitness[idx_a])]]
            parent_b = population[idx_b[np.argmin(fitness[idx_b])]]

            # Арифметический кроссовер (модификация)
            if np.random.rand() < crossover_prob:
                alpha = np.random.rand()
                child = alpha * parent_a + (1 - alpha) * parent_b
            else:
                child = parent_a

            # Мутация: добавляем гауссовский шум
            if np.random.rand() < mutation_prob:
                child += np.random.normal(0, mutation_scale)

            child = np.clip(child, X_MIN, X_MAX)
            new_pop.append(child)

        population = np.array(new_pop)
        best_history.append(f(best_x))

    best_idx = np.argmin(f(population))
    return population[best_idx], f(population[best_idx]), best_history

# ─── Роевой алгоритм PSO (с ограничением скорости) ───────────────────────────

def pso(swarm_size, iterations, c1, c2, w, vmax):
    """
    Минимизирует f(x) на [X_MIN, X_MAX].
    Модификация: ограничение скорости vmax уменьшается линейно (velocity clamping).
    Возвращает (лучший_x, лучший_y, история_лучших_значений).
    """
    # Инициализация
    pos = np.random.uniform(X_MIN, X_MAX, swarm_size)
    vel = np.random.uniform(-vmax, vmax, swarm_size)
    pbest_pos = pos.copy()
    pbest_val = f(pos)

    gbest_idx = np.argmin(pbest_val)
    gbest_pos = pbest_pos[gbest_idx]
    best_history = []

    for i in range(iterations):
        # Линейное уменьшение vmax (модификация ограничения скорости)
        # Минимум 5 % от начального vmax, чтобы не заморозить рой
        current_vmax = max(vmax * (1 - i / iterations), 0.05 * vmax)

        r1 = np.random.rand(swarm_size)
        r2 = np.random.rand(swarm_size)

        # Обновление скорости
        vel = w * vel + c1 * r1 * (pbest_pos - pos) + c2 * r2 * (gbest_pos - pos)

        # Ограничение скорости
        vel = np.clip(vel, -current_vmax, current_vmax)

        # Обновление позиций
        pos = np.clip(pos + vel, X_MIN, X_MAX)

        # Обновление личного лучшего
        val = f(pos)
        improved = val < pbest_val
        pbest_pos[improved] = pos[improved]
        pbest_val[improved] = val[improved]

        # Обновление глобального лучшего
        gbest_idx = np.argmin(pbest_val)
        gbest_pos = pbest_pos[gbest_idx]
        best_history.append(pbest_val[gbest_idx])

    return gbest_pos, pbest_val[gbest_idx], best_history

# ─── GUI ──────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Нахождение локального минимума")
        self.resizable(False, False)
        self._build_main()

    def _build_main(self):
        """Главное окно: выбор метода."""
        frame = ttk.Frame(self, padding=30)
        frame.pack()

        ttk.Label(frame, text="Выберите метод оптимизации",
                  font=("Arial", 13, "bold")).pack(pady=(0, 20))

        ttk.Button(frame, text="Генетический алгоритм",
                   width=28, command=self._open_ga).pack(pady=6)
        ttk.Button(frame, text="Роевой алгоритм (PSO)",
                   width=28, command=self._open_pso).pack(pady=6)

    def _open_ga(self):
        ParamWindow(self, method="ga")

    def _open_pso(self):
        ParamWindow(self, method="pso")


class ParamWindow(tk.Toplevel):
    """Окно настройки параметров, запуска и просмотра результата."""

    GA_PARAMS = [
        ("Размер популяции",    "pop_size",       "50"),
        ("Число поколений",     "generations",    "100"),
        ("Вероятность кроссовера", "crossover_prob", "0.8"),
        ("Вероятность мутации", "mutation_prob",  "0.1"),
        ("Масштаб мутации",     "mutation_scale", "0.5"),
    ]

    PSO_PARAMS = [
        ("Размер роя",          "swarm_size",  "30"),
        ("Число итераций",      "iterations",  "100"),
        ("c1 (когнитивный)",    "c1",          "1.5"),
        ("c2 (социальный)",     "c2",          "1.5"),
        ("Инерция w",           "w",           "0.7"),
        ("Макс. скорость Vmax", "vmax",        "3.0"),
    ]

    def __init__(self, parent, method):
        super().__init__(parent)
        self.method = method
        self.title("Генетический алгоритм" if method == "ga"
                   else "Роевой алгоритм (PSO)")
        self.resizable(False, False)
        self.entries = {}
        self._build()

    def _build(self):
        left = ttk.Frame(self, padding=15)
        left.pack(side=tk.LEFT, fill=tk.Y)

        params = self.GA_PARAMS if self.method == "ga" else self.PSO_PARAMS

        ttk.Label(left, text="Параметры", font=("Arial", 11, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10))

        for row, (label, key, default) in enumerate(params, start=1):
            ttk.Label(left, text=label + ":").grid(
                row=row, column=0, sticky=tk.W, pady=3, padx=(0, 8))
            var = tk.StringVar(value=default)
            ttk.Entry(left, textvariable=var, width=10).grid(
                row=row, column=1, sticky=tk.W)
            self.entries[key] = var

        ttk.Button(left, text="▶  Запустить",
                   command=self._run).grid(
            row=len(params) + 1, column=0, columnspan=2, pady=15)

        self.status = ttk.Label(left, text="", foreground="green")
        self.status.grid(row=len(params) + 2, column=0, columnspan=2)

        # Правая часть — место для графика
        self.right = ttk.Frame(self, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _get(self, key, cast=float):
        return cast(self.entries[key].get())

    def _run(self):
        self.status.config(text="Вычисление...", foreground="blue")
        self.update()

        try:
            if self.method == "ga":
                best_x, best_y, history = genetic_algorithm(
                    pop_size=self._get("pop_size", int),
                    generations=self._get("generations", int),
                    crossover_prob=self._get("crossover_prob"),
                    mutation_prob=self._get("mutation_prob"),
                    mutation_scale=self._get("mutation_scale"),
                )
            else:
                best_x, best_y, history = pso(
                    swarm_size=self._get("swarm_size", int),
                    iterations=self._get("iterations", int),
                    c1=self._get("c1"),
                    c2=self._get("c2"),
                    w=self._get("w"),
                    vmax=self._get("vmax"),
                )
        except (ValueError, Exception) as e:
            self.status.config(text=f"Ошибка: {e}", foreground="red")
            return

        self.status.config(
            text=f"Минимум: f({best_x:.4f}) = {best_y:.4f}", foreground="green")

        self._draw(best_x, best_y, history)

    def _draw(self, best_x, best_y, history):
        # Удаляем старый график, если есть
        for widget in self.right.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
        fig.tight_layout(pad=3)

        # График функции
        xs = np.linspace(X_MIN, X_MAX, 500)
        ax1.plot(xs, f(xs), color="royalblue", label="f(x) = x·sin(x)")
        ax1.scatter([best_x], [best_y], color="red", zorder=5,
                    label=f"Минимум ({best_x:.3f}, {best_y:.3f})")
        ax1.set_title("Функция f(x) = x·sin(x)")
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)

        # График сходимости
        ax2.plot(history, color="darkorange")
        ax2.set_title("Сходимость алгоритма")
        ax2.set_xlabel("Итерация / Поколение")
        ax2.set_ylabel("Лучшее значение f(x)")
        ax2.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=self.right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)


# ─── Запуск ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
