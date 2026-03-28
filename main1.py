import tkinter as tk
from baseline_algorithms import (genetic_algorithm_baseline, genetic_algorithm_2d_baseline, pso_baseline, pso_2d_baseline)

# Create the main window
root = tk.Tk()
root.title('Baseline Algorithms GUI')
root.geometry('400x300')

# Function to execute genetic_algorithm_baseline
def execute_genetic_algorithm_baseline():
    result = genetic_algorithm_baseline()
    result_label.config(text=result)

# Function to execute genetic_algorithm_2d_baseline
def execute_genetic_algorithm_2d_baseline():
    result = genetic_algorithm_2d_baseline()
    result_label.config(text=result)

# Function to execute pso_baseline
def execute_pso_baseline():
    result = pso_baseline()
    result_label.config(text=result)

# Function to execute pso_2d_baseline
def execute_pso_2d_baseline():
    result = pso_2d_baseline()
    result_label.config(text=result)

# Create buttons for each algorithm
btn1 = tk.Button(root, text='Genetic Algorithm Baseline', command=execute_genetic_algorithm_baseline)
btn1.pack(pady=10)

btn2 = tk.Button(root, text='Genetic Algorithm 2D Baseline', command=execute_genetic_algorithm_2d_baseline)
bt2.pack(pady=10)

btn3 = tk.Button(root, text='PSO Baseline', command=execute_pso_baseline)
bt3.pack(pady=10)

btn4 = tk.Button(root, text='PSO 2D Baseline', command=execute_pso_2d_baseline)
bt4.pack(pady=10)

# Label to display results
result_label = tk.Label(root, text='Results will be shown here')
result_label.pack(pady=20)

# Run the application
root.mainloop()