"""
benchmark_gui.py — GUI для сравнения алгоритмов оптимизации
«с модификацией» vs «без модификации», подбора гиперпараметров и визуализации.

Запуск: python benchmark_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import csv
import itertools
import traceback
import functools
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ─── Импорт алгоритмов ────────────────────────────────────────────────────────

from main import (
    genetic_algorithm,
    genetic_algorithm_2d,
    pso,
    pso_2d,
)
from baseline_algorithms import (
    genetic_algorithm_baseline,
    genetic_algorithm_2d_baseline,
    pso_baseline,
    pso_2d_baseline,
)

# ─── Описания параметров ──────────────────────────────────────────────────────

GA_PARAM_DEFS = [
    ("Размер популяции",          "pop_size",       "50",  int),
    ("Число поколений",           "generations",    "100", int),
    ("Вер-ть кроссовера",         "crossover_prob", "0.8", float),
    ("Вер-ть мутации",            "mutation_prob",  "0.1", float),
    ("Масштаб мутации",           "mutation_scale", "0.5", float),
]

PSO_PARAM_DEFS = [
    ("Размер роя",                "swarm_size",  "30",  int),
    ("Число итераций",            "iterations",  "100", int),
    ("c1 (когнитивный)",          "c1",          "1.5", float),
    ("c2 (социальный)",           "c2",          "1.5", float),
    ("Инерция w",                 "w",           "0.7", float),
    ("Макс. скорость Vmax",       "vmax",        "3.0", float),
]

VARIANT_LABELS = {
    "modified": "С модификацией",
    "baseline": "Без модификации",
}
VARIANT_COLORS = {
    "modified": "royalblue",
    "baseline": "darkorange",
}

# ─── Вспомогательные функции ──────────────────────────────────────────────────

def _parse_values(text: str, cast):
    """Парсит строку вида '0.1, 0.3, 0.5' в список значений нужного типа."""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("Пустое поле")
    return [cast(p) for p in parts]


def _run_single(algo: str, dim: str, variant: str, params: dict, seed: int):
    """
    Запускает один прогон алгоритма и возвращает (history, final_best).

    algo    : 'ga' | 'pso'
    dim     : '1d' | '2d'
    variant : 'modified' | 'baseline'
    params  : dict с числовыми значениями параметров
    seed    : int
    """
    np.random.seed(seed)

    if algo == "ga":
        fn_mod = genetic_algorithm if dim == "1d" else genetic_algorithm_2d
        fn_base = genetic_algorithm_baseline if dim == "1d" else genetic_algorithm_2d_baseline
        fn = fn_mod if variant == "modified" else fn_base
        kw = dict(
            pop_size=params["pop_size"],
            generations=params["generations"],
            crossover_prob=params["crossover_prob"],
            mutation_prob=params["mutation_prob"],
            mutation_scale=params["mutation_scale"],
        )
    else:  # pso
        fn_mod = pso if dim == "1d" else pso_2d
        fn_base = pso_baseline if dim == "1d" else pso_2d_baseline
        fn = fn_mod if variant == "modified" else fn_base
        kw = dict(
            swarm_size=params["swarm_size"],
            iterations=params["iterations"],
            c1=params["c1"],
            c2=params["c2"],
            w=params["w"],
            vmax=params["vmax"],
        )

    result = fn(**kw)
    # All functions return (..., best_val, history, snapshots)
    # 1D returns (best_x, best_val, history, snapshots) → len 4
    # 2D returns (best_x, best_y, best_val, history, snapshots) → len 5
    if len(result) == 4:
        _, best_val, history, _ = result
    else:
        _, _, best_val, history, _ = result

    return list(history), float(best_val)


# ─── Основное приложение ──────────────────────────────────────────────────────

class BenchmarkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Сравнение алгоритмов оптимизации — Бенчмарк")
        self.geometry("1280x780")
        self.minsize(900, 600)

        self._stop_flag = threading.Event()
        self._results: list = []          # список результатов экспериментов
        self._param_vars: dict = {}       # StringVar для полей параметров

        self._build()

    # ─── Построение интерфейса ────────────────────────────────────────────────

    def _build(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Левая панель (элементы управления) — прокручиваемая
        left_outer = ttk.Frame(paned, width=330)
        left_outer.pack_propagate(False)
        paned.add(left_outer, weight=0)

        ctrl_canvas = tk.Canvas(left_outer, highlightthickness=0, width=310)
        vsb = ttk.Scrollbar(left_outer, orient=tk.VERTICAL, command=ctrl_canvas.yview)
        ctrl_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        ctrl_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._ctrl_inner = ttk.Frame(ctrl_canvas)
        _win_id = ctrl_canvas.create_window((0, 0), window=self._ctrl_inner, anchor=tk.NW)

        def _on_configure(event):
            ctrl_canvas.configure(scrollregion=ctrl_canvas.bbox("all"))
            ctrl_canvas.itemconfig(_win_id, width=ctrl_canvas.winfo_width())

        self._ctrl_inner.bind("<Configure>", _on_configure)
        ctrl_canvas.bind("<Configure>", _on_configure)

        # Прокрутка колёсиком мыши
        def _on_mousewheel(event):
            ctrl_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        ctrl_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._build_controls(self._ctrl_inner)

        # Правая панель (графики)
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        self._build_plots(right_frame)

    def _build_controls(self, parent):
        pad = {"padx": 6, "pady": 3}

        # ── Целевая функция ───────────────────────────────────────────────────
        grp = ttk.LabelFrame(parent, text="Целевая функция", padding=8)
        grp.pack(fill=tk.X, **pad)

        self.func_var = tk.StringVar(value="1d")
        ttk.Radiobutton(grp, text="1D: f(x) = x·sin(x)  [0, 20]",
                        variable=self.func_var, value="1d").pack(anchor=tk.W)
        ttk.Radiobutton(grp,
                        text="2D: f(x,y) = −0.0001·|sin·sin·exp(…)+1|^0.1",
                        variable=self.func_var, value="2d").pack(anchor=tk.W)

        # ── Алгоритм ──────────────────────────────────────────────────────────
        grp = ttk.LabelFrame(parent, text="Алгоритм", padding=8)
        grp.pack(fill=tk.X, **pad)

        self.algo_var = tk.StringVar(value="ga")
        ttk.Radiobutton(grp, text="Генетический алгоритм (ГА)",
                        variable=self.algo_var, value="ga",
                        command=self._refresh_params).pack(anchor=tk.W)
        ttk.Radiobutton(grp, text="Роевой алгоритм (PSO)",
                        variable=self.algo_var, value="pso",
                        command=self._refresh_params).pack(anchor=tk.W)

        # ── Вариант ───────────────────────────────────────────────────────────
        grp = ttk.LabelFrame(parent, text="Вариант сравнения", padding=8)
        grp.pack(fill=tk.X, **pad)

        self.variant_var = tk.StringVar(value="both")
        ttk.Radiobutton(grp, text="С модификацией",
                        variable=self.variant_var, value="modified").pack(anchor=tk.W)
        ttk.Radiobutton(grp, text="Без модификации (базовый)",
                        variable=self.variant_var, value="baseline").pack(anchor=tk.W)
        ttk.Radiobutton(grp, text="Оба варианта (сравнение)",
                        variable=self.variant_var, value="both").pack(anchor=tk.W)

        # ── Настройки эксперимента ────────────────────────────────────────────
        grp = ttk.LabelFrame(parent, text="Настройки эксперимента", padding=8)
        grp.pack(fill=tk.X, **pad)

        row = ttk.Frame(grp)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Запусков на конфиг:", width=22, anchor=tk.W).pack(side=tk.LEFT)
        self.runs_var = tk.StringVar(value="10")
        ttk.Entry(row, textvariable=self.runs_var, width=7).pack(side=tk.LEFT)

        row2 = ttk.Frame(grp)
        row2.pack(fill=tk.X, pady=2)
        self.fixed_seed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Фикс. начальный seed:",
                        variable=self.fixed_seed_var).pack(side=tk.LEFT)
        self.seed_var = tk.StringVar(value="42")
        ttk.Entry(row2, textvariable=self.seed_var, width=7).pack(side=tk.LEFT)

        ttk.Label(grp,
                  text="(seeds: base, base+1, … base+N−1)",
                  foreground="gray", font=("Arial", 8)).pack(anchor=tk.W)

        # ── Параметры алгоритма ───────────────────────────────────────────────
        self._params_frame = ttk.LabelFrame(
            parent,
            text="Параметры (одно значение или список через запятую)",
            padding=8,
        )
        self._params_frame.pack(fill=tk.X, **pad)
        self._rebuild_params()

        # ── Кнопки управления ─────────────────────────────────────────────────
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, **pad)

        self._start_btn = ttk.Button(
            btn_frame, text="▶ Запустить", command=self._start_experiments,
        )
        self._start_btn.pack(side=tk.LEFT, padx=(0, 4))

        self._stop_btn = ttk.Button(
            btn_frame, text="■ Стоп", command=self._stop_experiments,
            state=tk.DISABLED,
        )
        self._stop_btn.pack(side=tk.LEFT, padx=4)

        self._export_btn = ttk.Button(
            btn_frame, text="⬇ CSV", command=self._export_csv,
            state=tk.DISABLED,
        )
        self._export_btn.pack(side=tk.LEFT, padx=4)

        # ── Прогресс ──────────────────────────────────────────────────────────
        prog_frame = ttk.Frame(parent)
        prog_frame.pack(fill=tk.X, **pad)

        self._progress_var = tk.DoubleVar(value=0.0)
        ttk.Progressbar(
            prog_frame, variable=self._progress_var, maximum=100,
        ).pack(fill=tk.X)

        self._status_var = tk.StringVar(value="Готов к запуску")
        ttk.Label(prog_frame, textvariable=self._status_var,
                  foreground="gray", font=("Arial", 9)).pack(anchor=tk.W, pady=(2, 0))

    def _rebuild_params(self):
        """Перестраивает поля ввода параметров под выбранный алгоритм."""
        for w in self._params_frame.winfo_children():
            w.destroy()
        self._param_vars.clear()

        defs = GA_PARAM_DEFS if self.algo_var.get() == "ga" else PSO_PARAM_DEFS
        for label, key, default, _ in defs:
            row = ttk.Frame(self._params_frame)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=label + ":", width=23, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            ttk.Entry(row, textvariable=var, width=13).pack(side=tk.LEFT)
            self._param_vars[key] = var

    def _refresh_params(self):
        self._rebuild_params()

    # ─── Правая панель (вкладки с графиками) ─────────────────────────────────

    def _build_plots(self, parent):
        self._notebook = ttk.Notebook(parent)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        self._conv_tab = ttk.Frame(self._notebook)
        self._notebook.add(self._conv_tab, text="  Сходимость  ")

        self._box_tab = ttk.Frame(self._notebook)
        self._notebook.add(self._box_tab, text="  Боксплот  ")

        self._heat_tab = ttk.Frame(self._notebook)
        self._notebook.add(self._heat_tab, text="  Тепловая карта  ")

        self._table_tab = ttk.Frame(self._notebook)
        self._notebook.add(self._table_tab, text="  Таблица  ")

        for tab in (self._conv_tab, self._box_tab, self._heat_tab, self._table_tab):
            ttk.Label(
                tab,
                text="Запустите эксперимент для отображения графиков",
                foreground="gray", font=("Arial", 12),
            ).pack(expand=True)

    # ─── Парсинг параметров и запуск ──────────────────────────────────────────

    def _parse_grid(self):
        """
        Считывает поля параметров и возвращает (keys, combos).
        combos — список кортежей значений (одна конфигурация = один кортеж).
        """
        algo = self.algo_var.get()
        defs = GA_PARAM_DEFS if algo == "ga" else PSO_PARAM_DEFS

        param_lists = {}
        for _, key, _, cast in defs:
            text = self._param_vars[key].get()
            try:
                param_lists[key] = _parse_values(text, cast)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Параметр «{key}»: {exc}") from exc

        keys = list(param_lists.keys())
        combos = list(itertools.product(*[param_lists[k] for k in keys]))
        return keys, combos

    def _start_experiments(self):
        try:
            keys, combos = self._parse_grid()
            n_runs = int(self.runs_var.get())
            if n_runs < 1:
                raise ValueError("Число запусков должно быть ≥ 1")
            base_seed = int(self.seed_var.get()) if self.fixed_seed_var.get() else None
        except ValueError as exc:
            messagebox.showerror("Ошибка параметров", str(exc))
            return

        self._stop_flag.clear()
        self._results = []
        self._start_btn.config(state=tk.DISABLED)
        self._stop_btn.config(state=tk.NORMAL)
        self._export_btn.config(state=tk.DISABLED)
        self._progress_var.set(0)
        self._status_var.set("Запуск экспериментов…")

        dim = self.func_var.get()
        algo = self.algo_var.get()
        variant = self.variant_var.get()

        t = threading.Thread(
            target=self._experiment_thread,
            args=(keys, combos, n_runs, dim, algo, variant, base_seed),
            daemon=True,
        )
        t.start()

    def _stop_experiments(self):
        self._stop_flag.set()
        self._status_var.set("Остановка…")

    # ─── Поток экспериментов ──────────────────────────────────────────────────

    def _experiment_thread(
        self, keys, combos, n_runs, dim, algo, variant, base_seed
    ):
        variants = (
            ["modified", "baseline"] if variant == "both" else [variant]
        )
        total = len(combos) * len(variants) * n_runs
        done = 0

        for combo_idx, combo in enumerate(combos):
            if self._stop_flag.is_set():
                break

            params = dict(zip(keys, combo))

            for var_name in variants:
                if self._stop_flag.is_set():
                    break

                histories: list[list] = []
                final_bests: list[float] = []

                for run_i in range(n_runs):
                    if self._stop_flag.is_set():
                        break

                    seed = (
                        base_seed + run_i
                        if base_seed is not None
                        else int(np.random.randint(0, 100_000))
                    )

                    try:
                        history, final = _run_single(algo, dim, var_name, params, seed)
                        histories.append(history)
                        final_bests.append(final)
                    except (ValueError, TypeError, KeyError, ArithmeticError) as exc:
                        tb = traceback.format_exc()
                        msg = f"{exc}\n\n{tb}"
                        self.after(
                            0,
                            functools.partial(messagebox.showerror, "Ошибка прогона", msg),
                        )
                        self._stop_flag.set()
                        break

                    done += 1
                    progress = 100.0 * done / total
                    var_label = VARIANT_LABELS.get(var_name, var_name)
                    status = (
                        f"Конфиг {combo_idx + 1}/{len(combos)}, "
                        f"{var_label}, прогон {run_i + 1}/{n_runs}"
                    )
                    self.after(0, self._set_progress, progress, status)

                if histories:
                    max_len = max(len(h) for h in histories)
                    # Pad shorter histories by repeating last value
                    padded = np.array(
                        [h + [h[-1]] * (max_len - len(h)) for h in histories],
                        dtype=float,
                    )
                    fb = np.array(final_bests, dtype=float)
                    self._results.append(
                        {
                            "params": params.copy(),
                            "variant": var_name,
                            "histories": padded,   # shape (runs, T)
                            "final_bests": fb,
                            "mean_final": float(np.mean(fb)),
                            "std_final": float(np.std(fb)),
                            "min_final": float(np.min(fb)),
                        }
                    )

        if self._stop_flag.is_set():
            self.after(0, self._on_stopped)
        else:
            self.after(0, self._on_done)

    def _set_progress(self, value: float, text: str):
        self._progress_var.set(value)
        self._status_var.set(text)

    def _on_done(self):
        self._progress_var.set(100)
        n = len(self._results)
        self._status_var.set(f"Готово! {n} конфигурация(й) выполнено.")
        self._finish_ui()
        self._update_plots()

    def _on_stopped(self):
        self._status_var.set("Остановлено пользователем.")
        self._finish_ui()
        if self._results:
            self._update_plots()

    def _finish_ui(self):
        self._start_btn.config(state=tk.NORMAL)
        self._stop_btn.config(state=tk.DISABLED)
        if self._results:
            self._export_btn.config(state=tk.NORMAL)

    # ─── Обновление всех графиков ─────────────────────────────────────────────

    def _update_plots(self):
        if not self._results:
            return
        self._draw_convergence()
        self._draw_boxplot()
        self._draw_heatmap()
        self._draw_table()

    @staticmethod
    def _clear_tab(tab: ttk.Frame):
        for w in tab.winfo_children():
            w.destroy()

    # ─── Вкладка «Сходимость» ─────────────────────────────────────────────────

    def _draw_convergence(self):
        self._clear_tab(self._conv_tab)

        by_variant = defaultdict(list)
        for r in self._results:
            by_variant[r["variant"]].append(r)

        fig, ax = plt.subplots(figsize=(8, 5))

        for var_name, res_list in by_variant.items():
            color = VARIANT_COLORS.get(var_name, "green")
            label = VARIANT_LABELS.get(var_name, var_name)

            if len(res_list) == 1:
                # Один конфиг: среднее ± стд по прогонам
                hist_arr = res_list[0]["histories"]
                mean_h = np.mean(hist_arr, axis=0)
                std_h = np.std(hist_arr, axis=0)
                x = np.arange(len(mean_h))
                ax.plot(x, mean_h, color=color, linewidth=2,
                        label=f"{label} (среднее)")
                ax.fill_between(x, mean_h - std_h, mean_h + std_h,
                                alpha=0.2, color=color)
            else:
                # Несколько конфигов: тонкие линии + жирная средняя
                per_config_means = []
                for r in res_list:
                    cfg_mean = np.mean(r["histories"], axis=0)
                    per_config_means.append(cfg_mean)
                    ax.plot(np.arange(len(cfg_mean)), cfg_mean,
                            color=color, alpha=0.25, linewidth=0.9)

                max_len = max(len(m) for m in per_config_means)
                padded = np.array(
                    [m.tolist() + [m[-1]] * (max_len - len(m))
                     for m in per_config_means],
                    dtype=float,
                )
                overall_mean = np.mean(padded, axis=0)
                overall_std = np.std(padded, axis=0)
                x = np.arange(len(overall_mean))
                ax.plot(x, overall_mean, color=color, linewidth=2.5,
                        label=f"{label} (среднее по конфигам)")
                ax.fill_between(x,
                                overall_mean - overall_std,
                                overall_mean + overall_std,
                                alpha=0.15, color=color)

        ax.set_title("Кривые сходимости (среднее ± стд. отклонение)")
        ax.set_xlabel("Итерация / Поколение")
        ax.set_ylabel("Лучшее значение f(x)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._conv_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    # ─── Вкладка «Боксплот» ───────────────────────────────────────────────────

    def _draw_boxplot(self):
        self._clear_tab(self._box_tab)

        by_variant = defaultdict(list)
        for r in self._results:
            by_variant[r["variant"]].append(r)

        # If there are multiple configs, we can group by config label
        n_configs = len(set(
            tuple(sorted(r["params"].items())) for r in self._results
        ))

        fig, ax = plt.subplots(figsize=(8, 5))

        if n_configs == 1 or len(by_variant) > 1:
            # Simple side-by-side boxplot per variant
            data = []
            tick_labels = []
            colors_list = []
            for var_name in sorted(by_variant.keys()):
                all_finals = np.concatenate(
                    [r["final_bests"] for r in by_variant[var_name]]
                )
                data.append(all_finals)
                tick_labels.append(VARIANT_LABELS.get(var_name, var_name))
                colors_list.append(VARIANT_COLORS.get(var_name, "green"))

            bp = ax.boxplot(data, labels=tick_labels, patch_artist=True, notch=False)
            for patch, c in zip(bp["boxes"], colors_list):
                patch.set_facecolor(c)
                patch.set_alpha(0.6)
        else:
            # One variant, multiple configs: one box per config
            sorted_results = sorted(self._results, key=lambda r: r["mean_final"])
            data = [r["final_bests"] for r in sorted_results]
            tick_labels = [
                "\n".join(f"{k}={v}" for k, v in r["params"].items())
                for r in sorted_results
            ]
            var_name = sorted_results[0]["variant"]
            c = VARIANT_COLORS.get(var_name, "steelblue")
            bp = ax.boxplot(data, labels=tick_labels, patch_artist=True)
            for patch in bp["boxes"]:
                patch.set_facecolor(c)
                patch.set_alpha(0.6)
            ax.tick_params(axis="x", labelsize=7)

        ax.set_title("Распределение финальных лучших значений по прогонам")
        ax.set_ylabel("f(x) — лучшее значение")
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._box_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    # ─── Вкладка «Тепловая карта» ─────────────────────────────────────────────

    def _draw_heatmap(self):
        self._clear_tab(self._heat_tab)

        # Найти параметры, по которым велась решётка
        algo = self.algo_var.get()
        defs = GA_PARAM_DEFS if algo == "ga" else PSO_PARAM_DEFS

        swept_keys = []
        for _, key, _, cast in defs:
            try:
                vals = _parse_values(self._param_vars[key].get(), cast)
            except (ValueError, TypeError):
                vals = []
            if len(vals) > 1:
                swept_keys.append(key)

        if len(swept_keys) != 2:
            msg = (
                "Тепловая карта доступна только при переборе ровно 2 параметров.\n"
                f"Сейчас переменных параметров: {len(swept_keys)}."
            )
            ttk.Label(self._heat_tab, text=msg,
                      foreground="gray", font=("Arial", 11),
                      justify=tk.CENTER).pack(expand=True)
            return

        p1, p2 = swept_keys
        variants_present = sorted(set(r["variant"] for r in self._results))
        n_v = len(variants_present)

        fig, axes = plt.subplots(1, n_v, figsize=(6 * n_v + 1, 5))
        if n_v == 1:
            axes = [axes]

        for ax, var_name in zip(axes, variants_present):
            var_res = [r for r in self._results if r["variant"] == var_name]

            p1_vals = sorted({r["params"][p1] for r in var_res})
            p2_vals = sorted({r["params"][p2] for r in var_res})

            matrix = np.full((len(p2_vals), len(p1_vals)), np.nan)
            for r in var_res:
                i = p2_vals.index(r["params"][p2])
                j = p1_vals.index(r["params"][p1])
                matrix[i, j] = r["mean_final"]

            # viridis_r: darker colour = lower (better) value for minimisation tasks
            im = ax.imshow(matrix, aspect="auto", cmap="viridis_r", origin="lower")
            ax.set_xticks(range(len(p1_vals)))
            ax.set_xticklabels([str(v) for v in p1_vals], rotation=45, ha="right")
            ax.set_yticks(range(len(p2_vals)))
            ax.set_yticklabels([str(v) for v in p2_vals])
            ax.set_xlabel(p1)
            ax.set_ylabel(p2)
            title = VARIANT_LABELS.get(var_name, var_name)
            ax.set_title(f"{title}\nСреднее финальное f(x)")
            fig.colorbar(im, ax=ax, shrink=0.85)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self._heat_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    # ─── Вкладка «Таблица» ────────────────────────────────────────────────────

    def _draw_table(self):
        self._clear_tab(self._table_tab)
        if not self._results:
            return

        param_keys = list(self._results[0]["params"].keys())
        cols = param_keys + ["Вариант", "Среднее", "Стд", "Минимум"]

        frame = ttk.Frame(self._table_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set,
        )
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True)

        for col in cols:
            tree.heading(col, text=col,
                         command=lambda c=col: self._sort_tree(tree, c, False))
            tree.column(col, width=100, minwidth=55, anchor=tk.CENTER)

        sorted_results = sorted(self._results, key=lambda r: r["mean_final"])
        for r in sorted_results:
            row_vals = (
                [str(r["params"][k]) for k in param_keys]
                + [
                    VARIANT_LABELS.get(r["variant"], r["variant"]),
                    f"{r['mean_final']:.6f}",
                    f"{r['std_final']:.6f}",
                    f"{r['min_final']:.6f}",
                ]
            )
            tree.insert("", tk.END, values=row_vals)

    @staticmethod
    def _sort_tree(tree: ttk.Treeview, col: str, reverse: bool):
        data = [(tree.set(item, col), item) for item in tree.get_children("")]
        try:
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda x: x[0], reverse=reverse)
        for i, (_, item) in enumerate(data):
            tree.move(item, "", i)
        tree.heading(col, command=lambda: BenchmarkApp._sort_tree(tree, col, not reverse))

    # ─── Экспорт CSV ──────────────────────────────────────────────────────────

    def _export_csv(self):
        if not self._results:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Экспорт результатов в CSV",
        )
        if not path:
            return

        param_keys = list(self._results[0]["params"].keys())
        header = param_keys + ["variant", "mean_final", "std_final", "min_final", "all_finals"]

        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            for r in self._results:
                row = (
                    [r["params"][k] for k in param_keys]
                    + [
                        r["variant"],
                        r["mean_final"],
                        r["std_final"],
                        r["min_final"],
                        ";".join(f"{v:.6f}" for v in r["final_bests"]),
                    ]
                )
                writer.writerow(row)

        self._status_var.set(f"Экспортировано: {path}")
        messagebox.showinfo("Экспорт завершён", f"Результаты сохранены:\n{path}")


# ─── Точка входа ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = BenchmarkApp()
    app.mainloop()
