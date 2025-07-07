# src/genetic_algorithm/genetic_algorithm.py
import os
import sys
import random
import time
from tqdm import tqdm
import json
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import CONTEXT_PREDICT_PATH, BUILD_DIR, SPREADSHEETS_DIR, STATS_DIR

from src.compression.context_manager import ContextFileManager
from src.compression.baseline import BaselineCompression

class GeneticAlgorithm:
    """
    Genetic Algorithm for optimizing W-OP8 predictor weights.
    """
    
    def __init__(self, run_name, excel_path, train_paths, population_size=30, 
                 generations=24, mutation_rate=0.05, crossover_rate=0.9, 
                 elitism_count=2, tournament_size=3):
        """
        Initialize the genetic algorithm.
        """
        self.run_name = run_name
        self.excel_path = excel_path
        self.train_paths = train_paths
        
        # GA parameters
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        self.tournament_size = tournament_size
        
        # Predictor weights constraints
        self.num_predictors = 8
        self.min_weight = 0
        self.max_weight = 15
        
        # Initialize cache and results tracking
        self.evaluation_cache = {}
        self.processed_candidates = set()  # Track already processed candidates
        self.generation_results = []
        
        # Initialize context manager and baseline compressor
        self.context_manager = ContextFileManager(CONTEXT_PREDICT_PATH, BUILD_DIR)
        self.compressor = BaselineCompression()
        
        # Setup compression output directory
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(self.excel_path)), 
            'compressed', 
            self.run_name, 
            'ga_candidates'
        )
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Ensure stats directory exists
        os.makedirs(STATS_DIR, exist_ok=True)
        
        # Ensure WOP8 is active
        self._switch_to_wop8()  
    
    def _switch_to_wop8(self):
        """Switch to W-OP8 implementation"""
        self.context_manager.ensure_versions_exist()
        success = self.context_manager.use_wop8()
        if not success:
            raise RuntimeError("Failed to switch to W-OP8 implementation")
        
        success = self.context_manager.rebuild_library()
        if not success:
            raise RuntimeError("Failed to rebuild library with W-OP8 implementation")
    
    def _create_candidate(self):
        """Create a random candidate with weights between min_weight and max_weight"""
        return [random.randint(self.min_weight, self.max_weight) 
                for _ in range(self.num_predictors)]
    
    def _initialize_population(self):
        """Initialize the population with random candidates"""
        return [self._create_candidate() for _ in range(self.population_size)]
    
    def _evaluate_candidate(self, candidate):
        """
        Evaluate a candidate by compressing training images and calculating fitness.
        """
        # Convert candidate to tuple for cache lookup
        candidate_tuple = tuple(candidate)
        
        # Check if candidate has already been evaluated
        if candidate_tuple in self.evaluation_cache:
            return self.evaluation_cache[candidate_tuple]
        
        # Update weights in context_predict.h
        success = self.context_manager.update_wop8_weights(candidate)
        if not success:
            print(f"Failed to update weights: {candidate}")
            return {'fitness': float('-inf'), 'total_size': float('inf'), 'results': {}}
        
        # Rebuild library
        success = self.context_manager.rebuild_library()
        if not success:
            print(f"Failed to rebuild library with weights: {candidate}")
            return {'fitness': float('-inf'), 'total_size': float('inf'), 'results': {}}
        
        # Create unique identifier for this candidate
        weight_str = '_'.join(map(str, candidate))
        candidate_dir = os.path.join(self.output_dir, f"w{weight_str}")
        os.makedirs(candidate_dir, exist_ok=True)
        
        # Compress training images
        total_size = 0
        image_results = {}
        
        for input_path in tqdm(self.train_paths, desc=f"Evaluating w{weight_str}", leave=False):
            image_name = os.path.basename(input_path)
            compressed_path = os.path.join(candidate_dir, f"{os.path.splitext(image_name)[0]}.jxl")
            decompressed_path = os.path.join(candidate_dir, f"dec_{image_name}")
            
            # Compress image
            result = self.compressor.compress_image(input_path, compressed_path, decompressed_path)
            if result is None:
                continue
                
            size = result['size']
            mae = result['mae']
            
            total_size += size
            image_results[image_name] = {'size': size, 'mae': mae}
        
        # Calculate fitness as negative of total size (higher is better)
        fitness = -total_size
        
        # Cache the result
        result = {
            'fitness': fitness,
            'total_size': total_size,
            'results': image_results,
            'weights': candidate
        }
        self.evaluation_cache[candidate_tuple] = result
        
        # Add to unique processed candidates for spreadsheet update
        if candidate_tuple not in self.processed_candidates:
            self.processed_candidates.add(candidate_tuple)
        
        return result
    
    def _tournament_selection(self, population, fitnesses):
        """
        Select an individual using tournament selection.
        """
        # Randomly select tournament_size individuals
        tournament_indices = random.sample(range(len(population)), self.tournament_size)
        tournament = [(population[i], fitnesses[i]) for i in tournament_indices]
        
        # Select the best individual from the tournament
        tournament.sort(key=lambda x: x[1], reverse=True)
        return tournament[0][0]
    
    def _crossover(self, parent1, parent2):
        """
        Perform uniform crossover between two parents.
        """
        if random.random() < self.crossover_rate:
            child1 = parent1.copy()
            child2 = parent2.copy()
            
            for i in range(self.num_predictors):
                if random.random() < 0.5:
                    child1[i], child2[i] = child2[i], child1[i]
                    
            return child1, child2
        else:
            return parent1.copy(), parent2.copy()
    
    def _mutate(self, candidate):
        """
        Mutate a candidate by randomly changing weights.
        """
        for i in range(self.num_predictors):
            if random.random() < self.mutation_rate:
                candidate[i] = random.randint(self.min_weight, self.max_weight)
        return candidate
    # In genetic_algorithm.py, replace the update_spreadsheet method with:

    def update_spreadsheet(self):
        """
        Update the training spreadsheet with all evaluated candidates.
        Only adds candidates that haven't been previously added.
        """
        from src.reporting.spreadsheet import update_spreadsheet_with_ga_candidate
        
        for candidate_tuple in self.processed_candidates:
            candidate = list(candidate_tuple)
            result = self.evaluation_cache[candidate_tuple]
            
            # Update spreadsheet with this candidate
            success = update_spreadsheet_with_ga_candidate(
                self.excel_path, 
                candidate, 
                result['results']
            )
            
            if not success:
                print(f"Warning: Failed to update spreadsheet for candidate {candidate}")
        
        # Clear the processed candidates set after updating
        self.processed_candidates = set()
        
        return True
       
    
    def run(self, progress_callback=None):
        """
        Run the genetic algorithm with progress tracking.
        """
        print(f"Starting GA optimization for {self.run_name}")
        print(f"Population size: {self.population_size}, Generations: {self.generations}")
        
        # Initialize population
        population = self._initialize_population()
        
        # Track best candidate
        best_candidate = None
        best_fitness = float('-inf')
        
        # Track generation times
        generation_times = []
        
        # Run for specified number of generations
        for generation in range(self.generations):
            gen_start_time = time.time()
            print(f"Generation {generation+1}/{self.generations}")
            
            # Evaluate current population
            fitnesses = []
            gen_results = {'generation': generation, 'candidates': []}
            
            for candidate in tqdm(population, desc=f"Generation {generation+1}", leave=True):
                result = self._evaluate_candidate(candidate)
                fitness = result['fitness']
                fitnesses.append(fitness)
                
                # Record candidate performance
                gen_results['candidates'].append({
                    'weights': candidate,
                    'fitness': fitness,
                    'total_size': result['total_size']
                })
                
                # Update best candidate if better
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_candidate = candidate.copy()
                    print(f"New best: {best_candidate} (Fitness: {best_fitness})")
            
            # Record generation results
            self.generation_results.append(gen_results)
            
            # Update spreadsheet
            if generation % 3 == 0 or generation == self.generations - 1:
                self.update_spreadsheet()
            
            # Create next generation
            next_population = []
            
            # Elitism: Add best individuals directly to next generation
            sorted_population = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
            elites = [candidate for candidate, _ in sorted_population[:self.elitism_count]]
            next_population.extend(elites)
            
            # Fill the rest of the population
            while len(next_population) < self.population_size:
                parent1 = self._tournament_selection(population, fitnesses)
                parent2 = self._tournament_selection(population, fitnesses)
                
                child1, child2 = self._crossover(parent1, parent2)
                
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                next_population.append(child1)
                if len(next_population) < self.population_size:
                    next_population.append(child2)
            
            # Update population for next generation
            population = next_population
            
            # Save intermediate results
            self._save_results(generation)
            
            # Calculate generation time
            gen_time = time.time() - gen_start_time
            generation_times.append(gen_time)
            
            # Estimate remaining time
            if len(generation_times) > 0:
                avg_time = sum(generation_times) / len(generation_times)
                remaining_generations = self.generations - (generation + 1)
                est_remaining_seconds = avg_time * remaining_generations
                est_remaining = str(timedelta(seconds=int(est_remaining_seconds))).split('.')[0]
            else:
                est_remaining = "Calculating..."
            
            # Call progress callback
            if progress_callback:
                progress_callback(
                    "ga",
                    f"Generation {generation + 1}/{self.generations}",
                    generation + 1,
                    best_candidate,
                    best_fitness,
                    est_remaining
                )
        
        # Final update to spreadsheet
        self.update_spreadsheet()
        
        # Save final best weights to W-OP8 implementation
        if best_candidate:
            self.context_manager.update_wop8_weights(best_candidate)
            print(f"Final best weights: {best_candidate} (Fitness: {best_fitness})")
            
            # Save best candidate to a file
            best_candidate_path = os.path.join(STATS_DIR, f"{self.run_name}_best_weights.json")
            with open(best_candidate_path, 'w') as f:
                json.dump({
                    'weights': best_candidate,
                    'fitness': best_fitness,
                    'total_size': -best_fitness
                }, f, indent=2)
        
        return {
            'best_candidate': best_candidate,
            'best_fitness': best_fitness,
            'total_size': -best_fitness if best_fitness != float('-inf') else float('inf')
        }
    
    def _save_results(self, generation):
        """Save intermediate results to a file"""
        results_path = os.path.join(STATS_DIR, f"{self.run_name}_ga_results.json")
        with open(results_path, 'w') as f:
            json.dump({
                'run_name': self.run_name,
                'generations_completed': generation + 1,
                'best_candidate': self.generation_results[-1]['candidates'][0]['weights'],
                'best_fitness': self.generation_results[-1]['candidates'][0]['fitness'],
                'generation_results': self.generation_results
            }, f, indent=2)