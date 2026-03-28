import numpy as np

# ======= Целевые функции (как в main.py) =======

# 1D: f(x) = x·sin(x) на [0, 20]
X_MIN, X_MAX = 0.0, 20.0

def f(x):
    return x * np.sin(x)

# 2D: f(x,y) = -0.0001*(sin(x)*sin(y)*exp(|100 - sqrt(x²+y²)/π|) + 1)^0.1
# на [-10, 10] × [-10, 10]
X2_MIN, X2_MAX = -10.0, 10.0
Y2_MIN, Y2_MAX = -10.0, 10.0

def f2(x, y):
    return -0.0001 * np.abs(
        np.sin(x) * np.sin(y)
        * np.exp(np.abs(100 - (np.sqrt(x**2 + y**2)) / np.pi))
        + 1
    ) ** 0.1


def _snapshot_indices(total, max_snapshots=8):
    """Индексы поколений/итераций для снимков популяции/роя."""
    if total <= max_snapshots:
        return list(range(total))
    step = (total - 1) / (max_snapshots - 1)
    return sorted(set(int(round(i * step)) for i in range(max_snapshots)))


# ======= Baseline GA (без элитизма и без арифметического кроссовера) =======

def genetic_algorithm_baseline(pop_size, generations, crossover_prob, mutation_prob, mutation_scale):
    """
    Минимизирует f(x) на [X_MIN, X_MAX].

    БАЗОВАЯ версия (без модификаций относительно вашего варианта):
    - без элитизма (лучший не переносится гарантированно)
    - без арифметического кроссовера (вместо него: выбрать одного из родителей)
    """
    population = np.random.uniform(X_MIN, X_MAX, pop_size)
    best_history = []
    snap_idx = _snapshot_indices(generations)
    snapshots = []

    for gen in range(generations):
        fitness = f(population)

        if gen in snap_idx:
            snapshots.append((gen, population.copy()))

        # Формируем новое поколение без элиты
        new_pop = []
        while len(new_pop) < pop_size:
            # Турнирный отбор (размер 3) — оставляем как базовый отбор
            idx_a = np.random.choice(pop_size, 3, replace=False)
            idx_b = np.random.choice(pop_size, 3, replace=False)
            parent_a = population[idx_a[np.argmin(fitness[idx_a])]]
            parent_b = population[idx_b[np.argmin(fitness[idx_b])]]

            # Базовый кроссовер: выбрать одного из родителей
            if np.random.rand() < crossover_prob:
                child = parent_a if np.random.rand() < 0.5 else parent_b
            else:
                child = parent_a

            # Мутация (как у вас): гауссовский шум
            if np.random.rand() < mutation_prob:
                child += np.random.normal(0, mutation_scale)

            child = np.clip(child, X_MIN, X_MAX)
            new_pop.append(child)

        population = np.array(new_pop)
        best_history.append(np.min(f(population)))

    best_idx = np.argmin(f(population))
    return population[best_idx], f(population[best_idx]), best_history, snapshots


def genetic_algorithm_2d_baseline(pop_size, generations, crossover_prob, mutation_prob, mutation_scale):
    """
    Минимизирует f2(x, y) на [X2_MIN, X2_MAX] × [Y2_MIN, Y2_MAX].

    БАЗОВАЯ версия:
    - без элитизма
    - без арифметического кроссовера (выбор одного из родителей)
    """
    pop_x = np.random.uniform(X2_MIN, X2_MAX, pop_size)
    pop_y = np.random.uniform(Y2_MIN, Y2_MAX, pop_size)
    best_history = []
    snap_idx = _snapshot_indices(generations)
    snapshots = []

    for gen in range(generations):
        fitness = f2(pop_x, pop_y)

        if gen in snap_idx:
            snapshots.append((gen, pop_x.copy(), pop_y.copy()))

        new_x = []
        new_y = []
        while len(new_x) < pop_size:
            idx_a = np.random.choice(pop_size, 3, replace=False)
            idx_b = np.random.choice(pop_size, 3, replace=False)
            pa_i = idx_a[np.argmin(fitness[idx_a])]
            pb_i = idx_b[np.argmin(fitness[idx_b])]

            if np.random.rand() < crossover_prob:
                if np.random.rand() < 0.5:
                    cx, cy = pop_x[pa_i], pop_y[pa_i]
                else:
                    cx, cy = pop_x[pb_i], pop_y[pb_i]
            else:
                cx, cy = pop_x[pa_i], pop_y[pa_i]

            if np.random.rand() < mutation_prob:
                cx += np.random.normal(0, mutation_scale)
                cy += np.random.normal(0, mutation_scale)

            cx = np.clip(cx, X2_MIN, X2_MAX)
            cy = np.clip(cy, Y2_MIN, Y2_MAX)
            new_x.append(cx)
            new_y.append(cy)

        pop_x = np.array(new_x)
        pop_y = np.array(new_y)
        best_history.append(np.min(f2(pop_x, pop_y)))

    vals = f2(pop_x, pop_y)
    best_idx = np.argmin(vals)
    return pop_x[best_idx], pop_y[best_idx], vals[best_idx], best_history, snapshots


# ======= Baseline PSO (без линейного уменьшения vmax) =======

def pso_baseline(swarm_size, iterations, c1, c2, w, vmax):
    """
    Минимизирует f(x) на [X_MIN, X_MAX].

    БАЗОВАЯ версия:
    - vmax постоянный (нет линейного уменьшения по итерациям)
    """
    pos = np.random.uniform(X_MIN, X_MAX, swarm_size)
    vel = np.random.uniform(-vmax, vmax, swarm_size)
    pbest_pos = pos.copy()
    pbest_val = f(pos)

    gbest_idx = np.argmin(pbest_val)
    gbest_pos = pbest_pos[gbest_idx]
    best_history = []
    snap_idx = _snapshot_indices(iterations)
    snapshots = []

    for i in range(iterations):
        r1 = np.random.rand(swarm_size)
        r2 = np.random.rand(swarm_size)

        vel = w * vel + c1 * r1 * (pbest_pos - pos) + c2 * r2 * (gbest_pos - pos)
        vel = np.clip(vel, -vmax, vmax)
        pos = np.clip(pos + vel, X_MIN, X_MAX)

        if i in snap_idx:
            snapshots.append((i, pos.copy()))

        val = f(pos)
        improved = val < pbest_val
        pbest_pos[improved] = pos[improved]
        pbest_val[improved] = val[improved]

        gbest_idx = np.argmin(pbest_val)
        gbest_pos = pbest_pos[gbest_idx]
        best_history.append(pbest_val[gbest_idx])

    return gbest_pos, pbest_val[gbest_idx], best_history, snapshots



def pso_2d_baseline(swarm_size, iterations, c1, c2, w, vmax):
    """
    Минимизирует f2(x, y) на [X2_MIN, X2_MAX] × [Y2_MIN, Y2_MAX].

    БАЗОВАЯ версия:
    - vmax постоянный (нет линейного уменьшения)
    """
    pos_x = np.random.uniform(X2_MIN, X2_MAX, swarm_size)
    pos_y = np.random.uniform(Y2_MIN, Y2_MAX, swarm_size)
    vel_x = np.random.uniform(-vmax, vmax, swarm_size)
    vel_y = np.random.uniform(-vmax, vmax, swarm_size)

    pbest_x = pos_x.copy()
    pbest_y = pos_y.copy()
    pbest_val = f2(pos_x, pos_y)

    gbest_idx = np.argmin(pbest_val)
    gbest_x = pbest_x[gbest_idx]
    gbest_y = pbest_y[gbest_idx]
    best_history = []
    snap_idx = _snapshot_indices(iterations)
    snapshots = []

    for i in range(iterations):
        r1 = np.random.rand(swarm_size)
        r2 = np.random.rand(swarm_size)

        vel_x = w * vel_x + c1 * r1 * (pbest_x - pos_x) + c2 * r2 * (gbest_x - pos_x)
        vel_y = w * vel_y + c1 * r1 * (pbest_y - pos_y) + c2 * r2 * (gbest_y - pos_y)

        vel_x = np.clip(vel_x, -vmax, vmax)
        vel_y = np.clip(vel_y, -vmax, vmax)

        pos_x = np.clip(pos_x + vel_x, X2_MIN, X2_MAX)
        pos_y = np.clip(pos_y + vel_y, Y2_MIN, Y2_MAX)

        if i in snap_idx:
            snapshots.append((i, pos_x.copy(), pos_y.copy()))

        val = f2(pos_x, pos_y)
        improved = val < pbest_val
        pbest_x[improved] = pos_x[improved]
        pbest_y[improved] = pos_y[improved]
        pbest_val[improved] = val[improved]

        gbest_idx = np.argmin(pbest_val)
        gbest_x = pbest_x[gbest_idx]
        gbest_y = pbest_y[gbest_idx]
        best_history.append(pbest_val[gbest_idx])

    return gbest_x, gbest_y, pbest_val[gbest_idx], best_history, snapshots
