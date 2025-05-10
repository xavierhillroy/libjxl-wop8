# src/genetic_algorithm/optimizer.py
import os
import sys
import json

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import STATS_DIR

from src.genetic_algorithm.genetic_algorithm import GeneticAlgorithm

def optimize_weights(dataset_name, excel_path, train_paths, 
                    population_size=3, generations=2, 
                    mutation_rate=0.05, crossover_rate=0.9):
    """
    Run GA optimization for W-OP8 weights.
    
    Args:
        dataset_name (str): Name of the dataset
        excel_path (str): Path to Excel spreadsheet
        train_paths (list): List of paths to training images
        population_size (int): Size of the population
        generations (int): Number of generations to run
        mutation_rate (float): Probability of mutation per gene
        crossover_rate (float): Probability of crossover
        
    Returns:
        dict: Optimization results with best weights and fitness
    """
    print(f"\nStarting W-OP8 weight optimization for {dataset_name}")
    print(f"Training set: {len(train_paths)} images")
    print(f"GA parameters: Population={population_size}, Generations={generations}")
    
    # Initialize and run GA
    ga = GeneticAlgorithm(
        dataset_name=dataset_name,
        excel_path=excel_path,
        train_paths=train_paths,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate
    )
    
    # Run optimization
    results = ga.run()
    
    print("\nOptimization completed!")
    print(f"Best weights: {results['best_candidate']}")
    print(f"Best fitness: {results['best_fitness']}")
    print(f"Total compression size: {-results['best_fitness']} bytes")
    
    return results