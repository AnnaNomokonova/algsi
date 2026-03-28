import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use('TkAgg')

# Assuming the existing algorithm functions are defined above


def genetic_algorithm_baseline():
    # Existing code for genetic_algorithm_baseline
    pass

def genetic_algorithm_2d_baseline():
    # Existing code for genetic_algorithm_2d_baseline
    pass

def pso_baseline():
    # Existing code for pso_baseline
    pass

def pso_2d_baseline():
    # Existing code for pso_2d_baseline
    pass

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Baseline Algorithms GUI')

    def run_algorithms():
        genetic_algorithm_baseline()
        genetic_algorithm_2d_baseline()
        pso_baseline()
        pso_2d_baseline()
        messagebox.showinfo('Info', 'Algorithms executed successfully')

    run_button = tk.Button(root, text='Run Algorithms', command=run_algorithms)
    run_button.pack(pady=20)

    root.mainloop()