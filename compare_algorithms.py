import numpy as np
import matplotlib.pyplot as plt
import os
from main import modified_algorithm_1d, modified_algorithm_2d
from baseline_algorithms import baseline_algorithm_1d, baseline_algorithm_2d

# Ensure the output directory exists
output_dir = './comparison_plots'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def run_trials(algo_modified, algo_baseline, n_trials=100, seed=42):
    np.random.seed(seed)
    results_modified = []
    results_baseline = []
    for _ in range(n_trials):
        # Simulate running the algorithms and collecting results
        result_m = algo_modified()  # Placeholder for actual algorithm call
        result_b = algo_baseline()  # Placeholder
        results_modified.append(result_m)
        results_baseline.append(result_b)
    return np.array(results_modified), np.array(results_baseline)

# Compare algorithms for 1D
results_m1d, results_b1d = run_trials(modified_algorithm_1d, baseline_algorithm_1d)

# Compare algorithms for 2D
results_m2d, results_b2d = run_trials(modified_algorithm_2d, baseline_algorithm_2d)

# Plot convergence for 1D
plt.figure()
plt.errorbar(range(len(results_m1d)), np.mean(results_m1d, axis=0), yerr=np.std(results_m1d, axis=0), label='Modified 1D')
plt.errorbar(range(len(results_b1d)), np.mean(results_b1d, axis=0), yerr=np.std(results_b1d, axis=0), label='Baseline 1D')
plt.title('Convergence Comparison - 1D')
plt.xlabel('Iterations')
plt.ylabel('Performance Metric')
plt.legend()
plt.savefig(os.path.join(output_dir, 'convergence_1D.png'))
plt.close()

# Boxplot for 1D
plt.figure()
plt.boxplot([results_m1d, results_b1d], labels=['Modified 1D', 'Baseline 1D'])
plt.title('Boxplot Comparison - 1D')
plt.ylabel('Performance Metric')
plt.savefig(os.path.join(output_dir, 'boxplot_1D.png'))
plt.close()

# Repeat similar plots for 2D
plt.figure()
plt.errorbar(range(len(results_m2d)), np.mean(results_m2d, axis=0), yerr=np.std(results_m2d, axis=0), label='Modified 2D')
plt.errorbar(range(len(results_b2d)), np.mean(results_b2d, axis=0), yerr=np.std(results_b2d, axis=0), label='Baseline 2D')
plt.title('Convergence Comparison - 2D')
plt.xlabel('Iterations')
plt.ylabel('Performance Metric')
plt.legend()
plt.savefig(os.path.join(output_dir, 'convergence_2D.png'))
plt.close()

plt.figure()
plt.boxplot([results_m2d, results_b2d], labels=['Modified 2D', 'Baseline 2D'])
plt.title('Boxplot Comparison - 2D')
plt.ylabel('Performance Metric')
plt.savefig(os.path.join(output_dir, 'boxplot_2D.png'))
plt.close()