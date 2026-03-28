import os
import numpy as np
import matplotlib.pyplot as plt
from genetic_algorithm import pso as ga_pso
from genetic_algorithm_2d import pso_2d as ga2d_pso
from baseline_algorithms import baseline_ga, baseline_pso

# Function to run the experiments
def run_experiment(algorithm, dimension, seed):
    np.random.seed(seed)
    # Simulate the optimization process (this is a placeholder, replace with actual calls to the algorithm)
    best_values = []
    # Assuming your algorithm returns a best value after some evaluation; replace the logic as needed
    for _ in range(10):  # Repeat 10 times
        best_value = algorithm(dimension)  # Replace with the actual function
        best_values.append(best_value)
    return best_values

# Function to save plots
def save_plots(results, title, filename):
    mean_values = np.mean(results, axis=0)
    std_values = np.std(results, axis=0)

    plt.figure()
    plt.errorbar(range(len(mean_values)), mean_values, yerr=std_values, label='Convergence')
    plt.title(title)
    plt.xlabel('Iterations')
    plt.ylabel('Best Value')
    plt.legend()
    plt.savefig(filename)
    plt.close()

def main():
    seeds = np.random.randint(0, 10000, size=10)  # Fixed base seed variation
    results_1d_ga = [run_experiment(ga_pso, 1, seed) for seed in seeds]
    results_1d_baseline = [run_experiment(baseline_pso, 1, seed) for seed in seeds]

    results_2d_ga = [run_experiment(ga2d_pso, 2, seed) for seed in seeds]
    results_2d_baseline = [run_experiment(baseline_ga, 2, seed) for seed in seeds]

    # Ensure plots directory exists
    os.makedirs('comparison_plots', exist_ok=True)

    # Save plots
    save_plots(results_1d_ga, '1D GA Convergence', 'comparison_plots/1d_ga_convergence.png')
    save_plots(results_1d_baseline, '1D Baseline PSO Convergence', 'comparison_plots/1d_baseline_convergence.png')
    save_plots(results_2d_ga, '2D GA Convergence', 'comparison_plots/2d_ga_convergence.png')
    save_plots(results_2d_baseline, '2D Baseline PSO Convergence', 'comparison_plots/2d_baseline_convergence.png')

if __name__ == "__main__":
    main()