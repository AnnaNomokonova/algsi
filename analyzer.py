import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from main import (
    f, f2,
    genetic_algorithm, genetic_algorithm_2d,
    pso, pso_2d,
    X_MIN, X_MAX, X2_MIN, X2_MAX, Y2_MIN, Y2_MAX,
)

# ──────────────────────────────────────────────────────────────────────────────
# Параметры «классических» версий алгоритмов
# ──────────────────────────────────────────────────────────────────────────────

# Для классического GA: арифметический кроссовер отключён
CLASSIC_GA_CROSSOVER_PROB = 0.0

# Для классического PSO: стандартные коэффициенты без адаптации скорости
CLASSIC_PSO_C1 = 1.5
CLASSIC_PSO_C2 = 1.5
CLASSIC_PSO_W  = 0.5

# Цвета для линий/столбцов на графиках
_PLOT_COLORS = ["steelblue", "darkorange"]

# ──────────────────────────────────────────────────────────────────────────────
# Вспомогательная функция: запуск одного эксперимента
# ──────────────────────────────────────────────────────────────────────────────

def _run_trials(is_ga, func_type, algo_type, vals, n_trials):
    """
    Запускает n_trials прогонов выбранного алгоритма и возвращает
    (bests_array, histos_list).

    algo_type: "classic" или "mod"
    is_ga:     True — GA, False — PSO
    func_type: "1d" или "2d"
    vals:      список числовых параметров алгоритма (порядок — из _PARAM_DEFS)
    """
    bests = []
    histos = []

    for _ in range(n_trials):
        if is_ga:
            pop_size   = int(vals[0])
            generations = int(vals[1])
            crossover_prob = vals[2] if algo_type == "mod" else CLASSIC_GA_CROSSOVER_PROB
            mutation_prob  = vals[3]
            mutation_scale = vals[4]

            if func_type == "1d":
                bx, by, hist, _ = genetic_algorithm(
                    pop_size, generations,
                    crossover_prob, mutation_prob, mutation_scale)
                bests.append(by)
            else:
                bx, by, bval, hist, _ = genetic_algorithm_2d(
                    pop_size, generations,
                    crossover_prob, mutation_prob, mutation_scale)
                bests.append(bval)
        else:
            swarm_size = int(vals[0])
            iterations = int(vals[1])
            if algo_type == "mod":
                c1, c2, w, vmax = vals[2], vals[3], vals[4], vals[5]
            else:
                # Классический PSO: фиксированные «стандартные» коэффициенты
                c1, c2, w, vmax = CLASSIC_PSO_C1, CLASSIC_PSO_C2, CLASSIC_PSO_W, vals[5]

            if func_type == "1d":
                gbest, gval, hist, _ = pso(
                    swarm_size, iterations, c1, c2, w, vmax)
                bests.append(gval)
            else:
                gbest_x, gbest_y, gval, hist, _ = pso_2d(
                    swarm_size, iterations, c1, c2, w, vmax)
                bests.append(gval)

        histos.append(hist)

    return np.array(bests), histos


# ──────────────────────────────────────────────────────────────────────────────
# Описание параметров алгоритмов
# ──────────────────────────────────────────────────────────────────────────────

_GA_PARAMS = [
    ("Размер популяции",      "50"),
    ("Число поколений",       "60"),
    ("P_crossover",           "0.8"),
    ("P_mutation",            "0.1"),
    ("Масштаб мутации",       "0.4"),
]

_PSO_PARAMS = [
    ("Размер роя",            "30"),
    ("Число итераций",        "80"),
    ("c1",                    "1.7"),
    ("c2",                    "1.7"),
    ("Инерция w",             "0.7"),
    ("Vmax",                  "2.5"),
]


# ──────────────────────────────────────────────────────────────────────────────
# Главный класс приложения
# ──────────────────────────────────────────────────────────────────────────────

class AnalyzerApp(tk.Tk):
    """GUI-приложение для сравнения классической и модифицированной версий GA/PSO."""

    def __init__(self):
        super().__init__()
        self.title("Анализ эффективности алгоритмов оптимизации")
        self.resizable(True, True)
        self._build_gui()

    def _build_gui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ga_tab  = ttk.Frame(notebook)
        pso_tab = ttk.Frame(notebook)
        notebook.add(ga_tab,  text="Генетический алгоритм")
        notebook.add(pso_tab, text="Роевой алгоритм (PSO)")

        self._build_algo_tab(ga_tab,  is_ga=True)
        self._build_algo_tab(pso_tab, is_ga=False)

    # ------------------------------------------------------------------
    # Построение вкладки
    # ------------------------------------------------------------------

    def _build_algo_tab(self, tab, is_ga):
        param_defs = _GA_PARAMS if is_ga else _PSO_PARAMS

        # ── Левая панель управления ──
        ctrl = ttk.Frame(tab, padding=12)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        row = 0

        # Функция
        ttk.Label(ctrl, text="Целевая функция", font=("Arial", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))
        row += 1

        func_var = tk.StringVar(value="1d")
        ttk.Radiobutton(ctrl, text="f(x) = x·sin(x)  [1D]",
                        variable=func_var, value="1d").grid(
            row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        ttk.Radiobutton(ctrl, text="f(x,y) — сложная [2D]",
                        variable=func_var, value="2d").grid(
            row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="we", pady=8)
        row += 1

        # Режим сравнения
        ttk.Label(ctrl, text="Режим сравнения", font=("Arial", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))
        row += 1

        mode_var = tk.StringVar(value="both")
        for text, value in [("Оба (сравнение)",          "both"),
                             ("Только модифицированный",  "mod"),
                             ("Только классический",      "classic")]:
            ttk.Radiobutton(ctrl, text=text, variable=mode_var, value=value).grid(
                row=row, column=0, columnspan=2, sticky=tk.W)
            row += 1

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="we", pady=8)
        row += 1

        # Число запусков
        ttk.Label(ctrl, text="Число запусков:").grid(
            row=row, column=0, sticky=tk.W)
        runs_var = tk.StringVar(value="20")
        ttk.Entry(ctrl, textvariable=runs_var, width=6).grid(
            row=row, column=1, sticky=tk.W)
        row += 1

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="we", pady=8)
        row += 1

        # Параметры алгоритма
        ttk.Label(ctrl, text="Параметры алгоритма", font=("Arial", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))
        row += 1

        param_entries = []
        for label, default in param_defs:
            ttk.Label(ctrl, text=label + ":").grid(
                row=row, column=0, sticky=tk.W, pady=2)
            ent = ttk.Entry(ctrl, width=8)
            ent.insert(0, default)
            ent.grid(row=row, column=1, sticky=tk.W, padx=(4, 0))
            param_entries.append(ent)
            row += 1

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="we", pady=8)
        row += 1

        # Кнопка запуска и статус
        run_btn = ttk.Button(ctrl, text="▶  Сравнить", width=20)
        run_btn.grid(row=row, column=0, columnspan=2, pady=(4, 2))
        row += 1

        status_lbl = ttk.Label(ctrl, text="", foreground="blue", wraplength=200)
        status_lbl.grid(row=row, column=0, columnspan=2, sticky=tk.W)

        # ── Правая панель результатов ──
        results_frame = ttk.Frame(tab)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        run_btn["command"] = lambda: self._run_experiment(
            is_ga, func_var, mode_var, runs_var,
            param_entries, results_frame, status_lbl)

    # ------------------------------------------------------------------
    # Запуск эксперимента
    # ------------------------------------------------------------------

    def _run_experiment(self, is_ga, func_var, mode_var, runs_var,
                        param_entries, results_frame, status_lbl):
        # Очищаем предыдущие результаты
        for widget in results_frame.winfo_children():
            widget.destroy()
        self.update()

        # Считываем параметры
        try:
            vals = [float(e.get()) for e in param_entries]
        except ValueError:
            status_lbl.config(text="Ошибка: некорректные параметры", foreground="red")
            return

        try:
            n_trials = max(1, int(runs_var.get()))
        except ValueError:
            status_lbl.config(text="Ошибка: некорректное число запусков", foreground="red")
            return

        func_type = func_var.get()
        mode = mode_var.get()

        status_lbl.config(text="Выполняется вычисление…", foreground="blue")
        self.update()

        # Прогоны
        results = []  # [(label, bests_array, histos_list), ...]
        try:
            if mode in ("both", "classic"):
                bests_c, histos_c = _run_trials(is_ga, func_type, "classic", vals, n_trials)
                results.append(("Классический", bests_c, histos_c))
            if mode in ("both", "mod"):
                bests_m, histos_m = _run_trials(is_ga, func_type, "mod", vals, n_trials)
                results.append(("Модифицированный", bests_m, histos_m))
        except Exception as exc:
            status_lbl.config(text=f"Ошибка выполнения: {exc}", foreground="red")
            return

        # ── Графики ──
        self._draw_results(results, func_type, results_frame)

        # ── Текстовый отчёт ──
        report_lines = []
        for label, bests, _ in results:
            report_lines.append(
                f"{label}: средний минимум = {np.mean(bests):.5f},  std = {np.std(bests):.5f}")
        report_text = "\n".join(report_lines)

        tk.Label(results_frame, text=report_text, justify=tk.LEFT,
                 font=("Arial", 10), foreground="darkgreen",
                 bg=self.cget("bg")).pack(anchor=tk.W, padx=8, pady=(0, 6))

        status_lbl.config(text="Готово", foreground="green")

    # ------------------------------------------------------------------
    # Отрисовка графиков
    # ------------------------------------------------------------------

    def _draw_results(self, results, func_type, parent):
        fig, (ax_hist, ax_conv) = plt.subplots(1, 2, figsize=(11, 4))
        fig.tight_layout(pad=3.5)

        colors = _PLOT_COLORS

        # ── График 1: гистограмма распределения минимумов ──
        for idx, (label, bests, _) in enumerate(results):
            ax_hist.hist(bests, bins=min(12, len(bests)),
                         alpha=0.65, color=colors[idx % len(colors)],
                         label=label, edgecolor="white")
        ax_hist.set_title("Распределение найденных минимумов", fontsize=11)
        ax_hist.set_xlabel("Минимальное значение функции")
        ax_hist.set_ylabel("Частота")
        ax_hist.legend(fontsize=9)
        ax_hist.grid(True, alpha=0.3)

        # ── График 2: усреднённые кривые сходимости ──
        for idx, (label, _, histos) in enumerate(results):
            max_len = max(len(h) for h in histos)
            padded = np.array([
                h + [h[-1]] * (max_len - len(h)) for h in histos
            ])
            mean_curve = np.mean(padded, axis=0)
            std_curve  = np.std(padded,  axis=0)
            iters = np.arange(max_len)
            color = colors[idx % len(colors)]
            ax_conv.plot(iters, mean_curve, color=color, label=label)
            ax_conv.fill_between(iters,
                                 mean_curve - std_curve,
                                 mean_curve + std_curve,
                                 color=color, alpha=0.15)

        dim_label = "итерации/поколения"
        ax_conv.set_title("Усреднённые кривые сходимости", fontsize=11)
        ax_conv.set_xlabel(dim_label.capitalize())
        ax_conv.set_ylabel("Лучшее значение функции")
        ax_conv.legend(fontsize=9)
        ax_conv.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        plt.close(fig)


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    AnalyzerApp().mainloop()
