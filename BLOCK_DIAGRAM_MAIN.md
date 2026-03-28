# Блок-схема main.py

```mermaid
%%{init: {"theme": "default"}}%%
flowchart TD
    A([Старт]) --> B{Запуск как __main__?}
    B -- нет --> C[Импорт модуля:\nдоступны функции/классы]
    B -- да --> D[Создать App()]  
    D --> E[App._build_main():\nглавное окно выбора]

    E --> F{Выбор целевой\nфункции}
    F -->|1D| F1[Режим 1D:\nf(x)=x·sin(x)\nX∈[0,20]]
    F -->|2D| F2[Режим 2D:\nf(x,y)\nX,Y∈[-10,10]]

    E --> G{Выбор метода\nоптимизации}
    G -->|GA| H[Открыть ParamWindow(method='ga')]
    G -->|PSO| I[Открыть ParamWindow(method='pso')]

    H --> J[ParamWindow._build():\nполя параметров + ▶ Запустить]
    I --> J

    J --> K{Нажата ▶ Запустить?}
    K -- нет --> J
    K -- да --> L[ParamWindow._run():\nсчитать параметры]

    L --> M{func == '2d'?}

    M -->|нет (1D)| N{method == 'ga'?}
    N -->|да| N1[genetic_algorithm():\nэлитизм + турнир\nарифм. кроссовер\nмутация]
    N -->|нет| N2[pso():\nобновление скорости\nvelocity clamping\nуменьшение vmax]
    N1 --> O1[_draw():\nграфик f(x)\nточки популяции/роя\nграфик сходимости]
    N2 --> O1

    M -->|да (2D)| P{method == 'ga'?}
    P -->|да| P1[genetic_algorithm_2d():\nэлитизм + турнир\nарифм. кроссовер\nмутация]
    P -->|нет| P2[pso_2d():\nvelocity clamping\nуменьшение vmax]
    P1 --> O2[_draw_2d():\nконтуры f(x,y)\nточки популяции/роя\nграфик сходимости]
    P2 --> O2

    O1 --> Q[Ожидание действий\nпользователя]
    O2 --> Q
    Q --> R([Конец])
```
