# Почему метод µ-analysis based algorithms for probabilistic finite-frequency H₂-performance analysis не подходит для нашей задачи

## Задача (контекст)

**Тема:** Запуск с морской платформы

Морская стартовая платформа находится в экваториальных водах Тихого океана. Пуск ракеты происходит с подвижного основания: платформу слегка качает (период качки 8 секунд, амплитуда наклона платформы до 2 градусов). Система управления ракетой может компенсировать отклонения, но есть задержка в 0,3 секунды между измерением угла наклона и отклонением двигателя (поворотом сопла). Можно ли пренебречь этим смещением для вывода спутника на орбиту (точность выведения ±1 км)?

---

## Таблица цитат из статьи

| Страница | Раздел | Цитата |
|----------|--------|--------|
| 2 | Abstract | "three novel µ-based probabilistic H₂-analysis algorithms, which provide guaranteed upper and lower bounds on the **probability** that an uncertain system violates a desired H₂-performance requirement **on a fixed frequency range**" |
| 3 | II. Problem Statement | "Let us consider the following continuous-time **uncertain linear time-invariant (LTI) system**: ẋ = A(δ)x + B(δ)u; y = C(δ)x + D(δ)u. The real uncertain parameters δ = (δ₁,...,δN) are bounded and without loss of generality normalized ... They are independent **random variables**, whose probability distributions f (typically, but not exclusively, uniform or truncated normal) are supported on the bounded interval [−1 1]." |
| 4 | IV-A. Sufficient conditions | "**Assumption 4.1:** The uncertain system (1) is **Single-Input Single-Output (SISO)**, i.e. u ∈ ℝ and y ∈ ℝ." |
| 4 | IV-A. Sufficient conditions | "**Assumption 4.2:** The transfer function M₂₂(s) is **biproper**, i.e. proper but not strictly proper." |
| 4 | IV-A. Sufficient conditions | "**Work is underway to relax these somewhat strong assumptions.**" |
| 4 | III. Overview | "there are three decisive factors behind the choice to focus on µ-analysis based methods. Firstly, their **computational efficiency**... [but] the dimension of the problem rapidly grows with the number of states." |
| 5 | IV-B. Method 1, Remark 4.2 | "If the uncertain system was **MIMO**, σ(Fᵤ(M(jωᵢ),∆)) would appear instead of |Fᵤ(M(jωᵢ),∆)| in (12)... **This would make the main loop theorem inapplicable.**" |
| 2 | I. Introduction | "it captures the system response to stationary noise ... it measures the **variance of the system output when the input is white noise**, which is for example crucial information for **high-accuracy pointing space missions**." |
| 2 | I. Introduction | "the difficulties encountered when combining classical and modern control techniques led to a shift in focus towards alternative performance criteria, like the currently very mature **worst-case H∞-analysis theory**... attention should be paid to systems with **high peaks in their frequency response**, e.g. with flexible dynamics, for which conservative results can be obtained." |
| 7 | V. Conclusion | "The latter will nevertheless remain **higher than for probabilistic H∞ analysis**. The entire considered frequency interval must indeed be covered accurately, and not only the worst-case frequency, which requires a **significant amount of skew-µ upper bound computations** for each satisfaction or violation test." |
| 7 | V. Conclusion | "extensive work will be carried out to **relax the assumptions** considered in this paper, **so as to make the proposed algorithms applicable to realistic systems**." |

---

## Разбор каждой цитаты и её связь с нашей задачей

---

### Цитата 1 (с. 2, Abstract)
> "three novel µ-based probabilistic H₂-analysis algorithms, which provide guaranteed upper and lower bounds on the **probability** that an uncertain system violates a desired H₂-performance requirement **on a fixed frequency range**"

**Что она говорит:**
Метод решает совершенно другую задачу — он вычисляет **вероятность** того, что H₂-норма системы превысит заданный порог γ. Результатом является вероятностная оценка нарушения нормы в заданном частотном диапазоне.

**Как это относится к нашей ситуации:**
Наша задача состоит не в оценке вероятности нарушения спектральной нормы, а в **детерминированном** вопросе: можно ли пренебречь задержкой в 0,3 с при заданной точности ±1 км? Это вопрос о влиянии конкретной фиксированной задержки на ошибку навигации и устойчивость контура управления. Метод статьи не отвечает на этот вопрос.

---

### Цитата 2 (с. 3, Problem Statement)
> "Let us consider the following continuous-time **uncertain linear time-invariant (LTI) system**... The real uncertain parameters δ = (δ₁,...,δN) are bounded ... They are **independent random variables**, whose probability distributions f (typically, but not exclusively, uniform or truncated normal) are supported on the bounded interval [−1 1]."

**Что она говорит:**
Метод предназначен только для систем, которые:
1. являются **линейными и инвариантными по времени (LTI)**,
2. имеют неопределённости, которые **моделируются как ограниченные случайные параметры** с известными вероятностными распределениями (например, равномерное или усечённое нормальное).

**Как это относится к нашей ситуации:**
Ракета при запуске — это существенно **нелинейная и нестационарная** система: масса убывает по мере сжигания топлива, аэродинамические характеристики меняются с высотой и скоростью, характеристики двигателя изменяются во времени. Неопределённость в нашей задаче — это **фиксированная транспортная задержка** (0,3 с), а не случайный параметр с известным распределением. Задержка не укладывается в стандартный параметрический LFR-фрейм метода без специальной аппроксимации (например, аппроксимации Паде), что вносит дополнительные ошибки.

---

### Цитата 3 (с. 4, Assumption 4.1)
> "**Assumption 4.1:** The uncertain system (1) is **Single-Input Single-Output (SISO)**, i.e. u ∈ ℝ and y ∈ ℝ."

**Что она говорит:**
Метод явно ограничен системами с **одним входом и одним выходом (SISO)**. Это является жёстким ограничением метода, прямо прописанным авторами как допущение.

**Как это относится к нашей ситуации:**
Система управления ракетой при запуске — **многомерная система (MIMO)**. Управление ведётся одновременно по нескольким каналам: крен, тангаж, рыскание. Платформа качается, создавая угловые возмущения сразу в нескольких плоскостях. Измеряются несколько углов (по меньшей мере два — тангаж и рыскание), управляются сразу несколько сопл или рулевые поверхности. Применение метода, разработанного исключительно для SISO-систем, к MIMO-задаче **методологически некорректно**.

---

### Цитата 4 (с. 4, Assumption 4.2)
> "**Assumption 4.2:** The transfer function M₂₂(s) is **biproper**, i.e. proper but not strictly proper."

**Что она говорит:**
Метод требует, чтобы передаточная функция M₂₂(s) была **бипропорной** — то есть не строго правильной: предел при s → ∞ должен быть ненулевым конечным числом. Это необходимо для выполнения инверсии передаточной функции внутри алгоритма.

**Как это относится к нашей ситуации:**
В типичных моделях динамики ракеты угловые передаточные функции (от поворота сопла к углу ракеты) являются **строго правильными** (strictly proper): на бесконечно высоких частотах их усиление стремится к нулю. Транспортная задержка e⁻ˢᵀ, если её аппроксимировать разложением Паде, также нарушает условие бипропорности. Таким образом, условие Assumption 4.2 **скорее всего не выполняется** для реальной модели ракеты, и метод неприменим.

---

### Цитата 5 (с. 4, Assumptions)
> "**Work is underway to relax these somewhat strong assumptions.**"

**Что она говорит:**
Сами авторы признают, что принятые допущения (SISO и бипропорность) являются **чрезмерно ограничительными** и что работа по их ослаблению ещё ведётся.

**Как это относится к нашей ситуации:**
Авторы сами признают, что на момент публикации метод не готов к применению на реалистичных системах. Это прямо означает, что алгоритм **ещё не достиг зрелости**, необходимой для анализа реальной задачи запуска ракеты с морской платформы.

---

### Цитата 6 (с. 4–5, Remark 4.2)
> "If the uncertain system was **MIMO**, σ(Fᵤ(M(jωᵢ),∆)) would appear instead of |Fᵤ(M(jωᵢ),∆)| in (12)... **This would make the main loop theorem inapplicable.**"

**Что она говорит:**
В случае MIMO-системы центральная теорема (main loop theorem), на которой строится весь алгоритм вычисления нижних границ, **перестаёт работать**. Это фундаментальное математическое препятствие, а не просто техническая сложность.

**Как это относится к нашей ситуации:**
Поскольку система управления ракетой является MIMO, использование данного метода потребует применения сингулярных значений вместо модуля скалярной передаточной функции. Основная теорема алгоритма (main loop theorem) в этом случае неприменима, и весь математический аппарат метода рассыпается. Это делает метод **принципиально неприменимым** без фундаментальной переработки теории.

---

### Цитата 7 (с. 2, Introduction)
> "it captures the system response to stationary noise ... it measures the **variance of the system output when the input is white noise**, which is for example crucial information for **high-accuracy pointing space missions**."

**Что она говорит:**
H₂-норма характеризует **дисперсию выхода системы при белом шуме на входе**. Именно поэтому метод разрабатывался для задач **прецизионного ориентирования космических аппаратов** (pointing missions) — где важна статистическая характеристика устойчивого движения.

**Как это относится к нашей ситуации:**
Задача запуска ракеты с морской платформы — это **переходный процесс**, а не стационарный режим. Нас интересует не дисперсия выхода при шуме, а влияние конкретной задержки 0,3 с на **точность выведения** (±1 км). H₂-норма отвечает на вопрос «как система реагирует на стационарный шум?», а наш вопрос: «как накапливается ошибка из-за задержки в системе управления за время активного участка?» — это принципиально иная постановка.

---

### Цитата 8 (с. 7, Conclusion)
> "The latter will nevertheless remain **higher than for probabilistic H∞ analysis**. The entire considered frequency interval must indeed be covered accurately, and not only the worst-case frequency, which requires a **significant amount of skew-µ upper bound computations** for each satisfaction or violation test."

**Что она говорит:**
Метод является **вычислительно дорогим**: для него требуется покрыть весь частотный диапазон с высокой плотностью, а не только наихудшую частоту. Авторы прямо указывают, что вычислительная стоимость выше, чем у аналогичного метода для H∞.

**Как это относится к нашей ситуации:**
Задача запуска ракеты — критичная по времени оперативная задача. Использование вычислительно дорогого метода для получения оценки, которую можно получить гораздо проще (например, через анализ запаса по задержке или прямое моделирование), нецелесообразно с инженерной точки зрения. Задержка 0,3 с легко анализируется через запас устойчивости по фазе (phase margin) или через метод предельного запаса по задержке (delay margin), не требующие столь сложного аппарата.

---

### Цитата 9 (с. 7, Conclusion)
> "extensive work will be carried out to **relax the assumptions** considered in this paper, **so as to make the proposed algorithms applicable to realistic systems**."

**Что она говорит:**
Авторы прямо **признают, что метод пока неприменим к реалистичным системам**. Это итоговый вывод самой статьи.

**Как это относится к нашей ситуации:**
Ракета-носитель с морской платформы — безусловно реалистичная (и более того, ответственная) система. Авторы сами подтверждают, что их алгоритмы нуждаются в доработке прежде, чем они смогут применяться к таким объектам. Использование незрелого метода для принятия решения о безопасности запуска и точности выведения спутника было бы методологически неоправданным.

---

## Общий вывод

Метод µ-analysis based algorithms for probabilistic finite-frequency H₂-performance analysis **не подходит** для нашей задачи по совокупности следующих причин:

| № | Причина | Подтверждение в статье |
|---|---------|----------------------|
| 1 | Метод работает только для **SISO-систем** | Assumption 4.1, Remark 4.2 |
| 2 | Метод требует **LTI-системы**, ракета нелинейна и нестационарна | Problem Statement (с. 3) |
| 3 | Неопределённость моделируется как **случайные параметры**, а не как фиксированная задержка | Problem Statement (с. 3) |
| 4 | Требование **бипропорности** M₂₂(s), которое нарушается при задержке | Assumption 4.2 (с. 4) |
| 5 | Метод измеряет **H₂-норму** (отклик на шум), а не накопленную ошибку из-за задержки | Introduction (с. 2) |
| 6 | Метод **вычислительно дорогой** и чрезмерен для данной задачи | Conclusion (с. 7) |
| 7 | Сами авторы признают, что **метод ещё не применим к реалистичным системам** | Conclusion (с. 7) |

Для нашей задачи более подходящими подходами являются: анализ запаса устойчивости по задержке (delay margin analysis), частотный анализ с построением диаграммы Боде (проверка запаса по фазе при частоте качки 0,125 Гц), или прямое численное моделирование динамики активного участка с задержкой управления.
