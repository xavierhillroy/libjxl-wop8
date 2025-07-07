# W-OP8/src/tui/interface.py
import os
import sys
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.spinner import Spinner
from rich.text import Text
import pyfiglet
from rich.markdown import Markdown

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import INPUT_DIR, OUTPUT_DIR, STATS_DIR, SPREADSHEETS_DIR, PROJECT_ROOT

class WOP8Interface:
    def __init__(self):
        self.console = Console()
        self.current_screen = "main"
        self.settings = {}
        self.available_datasets = []
        
    def format_path(self, full_path):
        """Format paths to show relative to libjxl-wop8/ directory"""
        if full_path and os.path.exists(full_path):
            try:
                # Get path relative to project root
                rel_path = os.path.relpath(full_path, PROJECT_ROOT)
                return f"libjxl-wop8/{rel_path}"
            except ValueError:
                # If path is not relative to project root, return full path
                return full_path
        return full_path if full_path else "N/A"
    
    def clear_screen(self):
        """Properly clear the screen"""
        self.console.clear()
        
    def run(self):
        """Main TUI loop"""
        while True:
            if self.current_screen == "main":
                self.show_main_menu()
            elif self.current_screen == "quick_settings":
                self.show_quick_settings()
            elif self.current_screen == "detailed_settings":
                self.show_detailed_settings()
            elif self.current_screen == "instructions":
                self.show_instructions()
            elif self.current_screen == "running":
                self.show_running_screen()
            elif self.current_screen == "results":
                self.show_results()
            elif self.current_screen == "exit":
                break
    
    def show_main_menu(self):
        """Display the main menu (W-OP8 CORE Page)"""
        self.clear_screen()
        
        # Create ASCII art title with a larger font
        title = pyfiglet.figlet_format("W-OP8", font="colossal")
        
        
        # Print the title separately, centered and in bold cyan
        self.console.print(f"[bold cyan]{title}[/bold cyan]", justify="left")
        
        # Create main menu panel (without the title)
        menu_content = """
[bold blue]Welcome to W-OP8: Weight-Optimized JPEG XL Compression[/bold blue]

[link=https://arxiv.org/abs/your-paper-id]📄 Read our paper[/link]

[cyan]1.[/cyan] Start New Analysis
[cyan]2.[/cyan] View Instructions  
[cyan]3.[/cyan] View Previous Results
[cyan]4.[/cyan] Exit

Please select an option:"""
        
        panel = Panel(menu_content, title="W-OP8 CORE", border_style="blue")
        self.console.print(panel)
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            self.current_screen = "quick_settings"
        elif choice == "2":
            self.current_screen = "instructions"
        elif choice == "3":
            self.current_screen = "results"
        elif choice == "4":
            self.current_screen = "exit"
    
    def get_available_datasets(self):
        """Get list of datasets from input directory"""
        if not os.path.exists(INPUT_DIR):
            os.makedirs(INPUT_DIR, exist_ok=True)
            return []
        
        datasets = []
        for item in os.listdir(INPUT_DIR):
            item_path = os.path.join(INPUT_DIR, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                datasets.append(item)
        return datasets
    
    def show_quick_settings(self):
        """Show quick input settings screen"""
        self.clear_screen()
        
        # Get available datasets
        datasets = self.get_available_datasets()
        
        if not datasets:
            self.console.print("[red]No datasets found in input directory![/red]")
            self.console.print(f"Please add datasets to: [cyan]{self.format_path(INPUT_DIR)}[/cyan]")
            input("\nPress Enter to return to main menu...")
            self.current_screen = "main"
            return
        
        # Create quick settings panel
        settings_content = f"""
[bold]Quick Settings[/bold]

Available Datasets (in {self.format_path(INPUT_DIR)}):"""
        
        for i, dataset in enumerate(datasets, 1):
            settings_content += f"\n{i}. {dataset}"
        
        panel = Panel(settings_content, title="Quick Input Sequence", border_style="green")
        self.console.print(panel)
        
        # Get user selections
        dataset_choice = IntPrompt.ask("Select dataset", choices=[str(i) for i in range(1, len(datasets) + 1)])
        selected_dataset = datasets[dataset_choice - 1]
        
        train_ratio = FloatPrompt.ask("Set training ratio", default=0.1)
        max_train = IntPrompt.ask("Set max training images", default=10)
        seed = IntPrompt.ask("Set random seed", default=42)
        
        # Store settings
        self.settings = {
            'dataset': selected_dataset,
            'train_ratio': train_ratio,
            'max_train': max_train,
            'seed': seed,
            # Default GA parameters
            'population_size': 30,
            'generations': 24,
            'mutation_rate': 0.05,
            'crossover_rate': 0.9,
            'elitism_count': 2,
            'tournament_size': 3
        }
        
        # Ask for GA customization
        if Confirm.ask("Do you want to customize GA parameters?"):
            self.current_screen = "detailed_settings"
        else:
            # Show summary and ask to run
            self.show_settings_summary()
    
    def show_detailed_settings(self):
        """Show detailed GA parameter settings"""
        self.clear_screen()
        
        panel_content = """
[bold]Detailed GA Parameters[/bold]

Customize Genetic Algorithm settings:"""
        
        panel = Panel(panel_content, title="GA Parameters", border_style="yellow")
        self.console.print(panel)
        
        # Get GA parameters
        self.settings['population_size'] = IntPrompt.ask("Population size", default=self.settings.get('population_size', 30))
        self.settings['generations'] = IntPrompt.ask("Number of generations", default=self.settings.get('generations', 24))
        self.settings['mutation_rate'] = FloatPrompt.ask("Mutation rate", default=self.settings.get('mutation_rate', 0.05))
        self.settings['crossover_rate'] = FloatPrompt.ask("Crossover rate", default=self.settings.get('crossover_rate', 0.9))
        self.settings['elitism_count'] = IntPrompt.ask("Elitism count", default=self.settings.get('elitism_count', 2))
        self.settings['tournament_size'] = IntPrompt.ask("Tournament size", default=self.settings.get('tournament_size', 3))
        
        # Show summary and ask to run
        self.show_settings_summary()
    
    def show_settings_summary(self):
        """Show settings summary and confirm run"""
        self.clear_screen()
        
        # Create summary table
        table = Table(title="Configuration Summary", show_header=True, header_style="bold magenta")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Dataset", self.settings['dataset'])
        table.add_row("Training Ratio", f"{self.settings['train_ratio']:.2f}")
        table.add_row("Max Training Images", str(self.settings['max_train']))
        table.add_row("Random Seed", str(self.settings['seed']))
        table.add_row("", "")  # Separator
        table.add_row("Population Size", str(self.settings['population_size']))
        table.add_row("Generations", str(self.settings['generations']))
        table.add_row("Mutation Rate", f"{self.settings['mutation_rate']:.3f}")
        table.add_row("Crossover Rate", f"{self.settings['crossover_rate']:.2f}")
        table.add_row("Elitism Count", str(self.settings['elitism_count']))
        table.add_row("Tournament Size", str(self.settings['tournament_size']))
        
        self.console.print(table)
        
        if Confirm.ask("\nRun with these settings?"):
            self.current_screen = "running"
        else:
            self.current_screen = "main"
    
    def show_instructions(self):
        """Show instructions screen"""
        self.clear_screen()
        
        instructions = f"""
[bold]W-OP8 Instructions[/bold]

1. Place your PNG images in the input directory:
   [cyan]{self.format_path(INPUT_DIR)}[/cyan]

2. Select a dataset and configure parameters

3. The system will:
   - Validate PNG files
   - Split into training/testing sets
   - Run baseline JPEG XL compression
   - Optimize predictor weights using GA
   - Apply W-OP8 compression with optimized weights
   - Generate reports

4. Results will be saved to:
   - Spreadsheets: [cyan]{self.format_path(SPREADSHEETS_DIR)}[/cyan]
   - Statistics: [cyan]{self.format_path(STATS_DIR)}[/cyan]
   - Compressed files: [cyan]{self.format_path(OUTPUT_DIR)}[/cyan]

"""
        
        panel = Panel(instructions, title="Instructions", border_style="green")
        self.console.print(panel)
        
        input("\nPress Enter to continue...")
        self.current_screen = "main"
    
    def show_running_screen(self):
        """Show the GA running screen with progress"""
        self.clear_screen()
        
        from src.core.processor import process_dataset
        from config import generate_run_name
        
        # Generate run name with all parameters
        run_name = generate_run_name(
            dataset_name=self.settings['dataset'],
            train_ratio=self.settings['train_ratio'],
            max_train_images=self.settings['max_train'],
            population_size=self.settings['population_size'],
            generations=self.settings['generations'],
            mutation_rate=self.settings['mutation_rate'],
            crossover_rate=self.settings['crossover_rate'],
            elitism_count=self.settings['elitism_count'],
            tournament_size=self.settings['tournament_size'],
            seed=self.settings['seed']
        )
        
        # Create layout for the running screen
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=7),
            Layout(name="main", size=20)
        )
        
        # Header content
        header_content = f"""[bold cyan]W-OP8 Compression Running[/bold cyan]
Dataset: {self.settings['dataset']}
Run: {run_name}

[yellow]⚠️  This process may take several hours. Please do not close the application.[/yellow]"""
        
        layout["header"].update(Panel(header_content, title="Status", border_style="cyan"))
        
        # Initialize GA tracking variables
        self.current_phase = "setup"
        self.ga_generation = 0
        self.ga_best_weights = None
        self.ga_best_fitness = None
        self.ga_time_remaining = "Calculating..."
        
        # Initialize live display
        with Live(layout, refresh_per_second=10, console=self.console) as live:
            try:
                self.update_running_display(layout, "setup", "Starting...")
                result = process_dataset(
                    dataset_name=self.settings['dataset'],
                    train_ratio=self.settings['train_ratio'],
                    max_train_images=self.settings['max_train'],
                    seed=self.settings['seed'],
                    population_size=self.settings['population_size'],
                    ga_generations=self.settings['generations'],
                    mutation_rate=self.settings['mutation_rate'],
                    crossover_rate=self.settings['crossover_rate'],
                    elitism_count=self.settings['elitism_count'],
                    tournament_size=self.settings['tournament_size'],
                    run_ga=True,
                    progress_callback=lambda phase, msg, gen=None, weights=None, fitness=None, time_remaining=None: 
                        self.handle_progress_update(layout, live, phase, msg, gen, weights, fitness, time_remaining)
                )
                # Store results for display
                self.results = result
                self.run_name = run_name
            except Exception as e:
                self.show_error_screen(str(e))
                return  # Exit if error

        # Now, after the Live context is closed, clear and show the final screen
        self.show_completion_screen(self.results, self.run_name)
    
    def handle_progress_update(self, layout, live, phase, message, generation=None, best_weights=None, best_fitness=None, time_remaining=None):
        """Handle progress updates from the processor"""
        self.current_phase = phase
        if generation is not None:
            self.ga_generation = generation
        if best_weights is not None:
            self.ga_best_weights = best_weights
        if best_fitness is not None:
            self.ga_best_fitness = best_fitness
        if time_remaining is not None:
            self.ga_time_remaining = time_remaining
        
        self.update_running_display(layout, phase, message)
        live.refresh()
    
    def update_running_display(self, layout, phase, message):
        """Update the running display based on current phase"""
        self.clear_screen()
        if phase == "setup":
            self.update_setup_display(layout, message)
        elif phase == "baseline":
            self.update_baseline_display(layout, message)
        elif phase == "ga":
            self.update_ga_display(layout, message)
        elif phase == "wop8":
            self.update_wop8_display(layout, message)
    
    def update_setup_display(self, layout, message):
        """Update display for setup phase"""
        setup_table = Table(show_header=False, box=None)
        setup_table.add_column(width=20)
        setup_table.add_column(width=60)
        setup_table.add_row("Setup Phase", Spinner('dots', text=message))
        layout["main"].update(Panel(setup_table, title="Current Phase", border_style="green"))
    
    def update_baseline_display(self, layout, message):
        """Update display for baseline compression phase"""
        baseline_table = Table(show_header=False, box=None)
        baseline_table.add_column(width=20)
        baseline_table.add_column(width=60)
        baseline_table.add_row("Setup Phase", "[green]✓[/green] Completed")
        baseline_table.add_row("Baseline", Spinner('dots', text=message))
        layout["main"].update(Panel(baseline_table, title="Current Phase", border_style="green"))
    
    def update_ga_display(self, layout, message):
        """Update display for GA optimization phase"""
        # Show GA status panel
        ga_panel = self.create_ga_status_panel(
            current_gen=self.ga_generation,
            total_gen=self.settings['generations'],
            best_weights=self.ga_best_weights,
            best_fitness=self.ga_best_fitness,
            time_remaining=self.ga_time_remaining,
            status_message=message,
            is_running=True
        )
        layout["main"].update(ga_panel)
    
    def update_wop8_display(self, layout, message):
        """Update display for W-OP8 application phase"""
        wop8_table = Table(show_header=False, box=None)
        wop8_table.add_column(width=20)
        wop8_table.add_column(width=60)
        wop8_table.add_row("GA Optimization", "[green]✓[/green] Completed")
        wop8_table.add_row("W-OP8 Application", Spinner('dots', text=message))
        layout["main"].update(Panel(wop8_table, title="Current Phase", border_style="green"))
    
    def create_ga_status_panel(self, current_gen, total_gen, best_weights, best_fitness, time_remaining, status_message, is_running=False):
        """Create a clean GA status panel"""
        if is_running:
            status_cell = Spinner('dots', text=status_message)
        else:
            status_cell = f"[green]✓[/green] {status_message}"
        
        # Create main table
        ga_table = Table(show_header=False, box=None, padding=(0, 1))
        ga_table.add_column(width=25)
        ga_table.add_column(width=55)
        
        ga_table.add_row("Status:", status_cell)
        ga_table.add_row("Generation:", f"{current_gen}/{total_gen}")
        ga_table.add_row("Time Remaining:", f"[dim]{time_remaining or 'Estimating...'}[/dim]")
        
        if best_weights and current_gen > 0:
            ga_table.add_row("", "")  # Spacer
            ga_table.add_row("Current Best Weights:", f"[green]{best_weights}[/green]")
            ga_table.add_row("Best Compression Size:", f"[green]{-best_fitness:,} bytes[/green]" if best_fitness else "...")
            ga_table.add_row("Fitness Score:", f"[green]{best_fitness:.2f}[/green]" if best_fitness else "...")
        
        # Progress bar
        if current_gen > 0 and total_gen > 0:
            progress_percent = current_gen / total_gen
            bar_width = 50
            filled = int(bar_width * progress_percent)
            bar = "█" * filled + "░" * (bar_width - filled)
            ga_table.add_row("", "")
            ga_table.add_row("Progress:", f"[green]{bar}[/green] {progress_percent*100:.1f}%")
        
        return Panel(ga_table, title="[bold cyan]Genetic Algorithm Optimization[/bold cyan]", border_style="cyan")
    
    def show_completion_screen(self, result, run_name):
        """Show a clean completion screen"""
        self.clear_screen()
        
        # Create completion summary
        summary_table = Table(title="✓ Processing Complete!", show_header=False, box=None)
        summary_table.add_column(width=25, style="cyan")
        summary_table.add_column(width=55, style="white")
        
        summary_table.add_row("Dataset:", result['dataset'])
        summary_table.add_row("Run Name:", run_name)
        summary_table.add_row("Total Images:", str(result['valid_count']))
        summary_table.add_row("Training Set:", str(result['train_count']))
        summary_table.add_row("Testing Set:", str(result['test_count']))
        
        if 'ga_results' in result and result['ga_results']:
            summary_table.add_row("", "")
            summary_table.add_row("Best Weights:", str(result['ga_results']['best_candidate']))
            
            # Add improvement metrics if available
            improvement_metrics = self.calculate_improvement_metrics(result)
            if improvement_metrics:
                summary_table.add_row("Compression Improvement:", f"{improvement_metrics['improvement_percent']:.2f}%")
                summary_table.add_row("Size Reduction:", f"{improvement_metrics['size_reduction']:,} bytes")
        
        # Output locations
        locations_table = Table(title="Output Locations", show_header=False, box=None)
        locations_table.add_column(width=25, style="cyan")
        locations_table.add_column(width=65, style="white")
        
        locations_table.add_row("Results Spreadsheet:", self.format_path(result.get('excel_path')))
        locations_table.add_row("Compressed Files:", self.format_path(OUTPUT_DIR))
        locations_table.add_row("Statistics:", self.format_path(STATS_DIR))
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(Panel(summary_table, border_style="green"), size=14),
            Layout(Panel(locations_table, border_style="blue"), size=8),
            Layout(Panel("[center][green]Press Enter to continue...[/green][/center]", border_style="green"), size=3)
        )
        
        self.console.print(layout)
        input()
        self.current_screen = "main"
    
    def calculate_improvement_metrics(self, result):
        """Calculate improvement metrics from results"""
        try:
            # Try to extract improvement data from result dictionary
            if 'test_results' in result and 'wop8_results' in result:
                baseline_size = sum(res['size'] for res in result['test_results'].values())
                wop8_size = sum(res['size'] for res in result['wop8_results'].values())
                size_reduction = baseline_size - wop8_size
                improvement_percent = (size_reduction / baseline_size) * 100
                
                return {
                    'baseline_size': baseline_size,
                    'wop8_size': wop8_size,
                    'size_reduction': size_reduction,
                    'improvement_percent': improvement_percent
                }
        except Exception:
            # If we can't calculate metrics, return None
            pass
        
        return None
    
    def show_error_screen(self, error_message):
        """Show a clean, highly visible error screen"""
        self.clear_screen()
        # Create a big, bold, red error panel
        error_panel = Panel(
            f"\n[bold red]ERROR[/bold red]\n\n[white on red]{error_message}[/white on red]\n\n[dim]Press Enter to return to main menu...[/dim]",
            title="[bold red]Error Occurred[/bold red]",
            border_style="red",
            padding=(2, 8),  # More padding for visibility
            expand=True
        )
        self.console.print(error_panel, justify="center")
        input()
        self.current_screen = "main"
    
    def show_results(self):
        """Show results screen"""
        self.clear_screen()
        
        # Check if we have results from a run, otherwise list available results
        if hasattr(self, 'results') and hasattr(self, 'run_name'):
            # Show current run results
            self.show_current_results()
        else:
            # Show available results from previous runs
            self.show_available_results()
    
    def show_current_results(self):
        """Display results from current run"""
        result = self.results
        
        # Create results table
        table = Table(title=f"Results for {self.run_name}", show_header=True, header_style="bold green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Dataset", result['dataset'])
        table.add_row("Valid PNG files", str(result['valid_count']))
        table.add_row("Training images", str(result['train_count']))
        table.add_row("Testing images", str(result['test_count']))
        
        if 'ga_results' in result and result['ga_results']:
            table.add_row("", "")  # Separator
            table.add_row("Best GA weights", str(result['ga_results']['best_candidate']))
            table.add_row("Best fitness", f"{result['ga_results']['best_fitness']:.2f}")
            table.add_row("Compression size", f"{-result['ga_results']['best_fitness']} bytes")
        
        self.console.print(table)
        
        # Show output files with formatted paths
        self.console.print("\n[bold]Output Files:[/bold]")
        self.console.print(f"Spreadsheet: [cyan]{self.format_path(result.get('excel_path'))}[/cyan]")
        self.console.print(f"Statistics: [cyan]{self.format_path(STATS_DIR)}[/cyan]")
        self.console.print(f"Compressed files: [cyan]{self.format_path(OUTPUT_DIR)}[/cyan]")
        
        input("\nPress Enter to return to main menu...")
        self.current_screen = "main"
    
    def show_available_results(self):
        """Show list of available results from previous runs"""
        # Check for saved results in various directories
        spreadsheets = []
        if os.path.exists(SPREADSHEETS_DIR):
            for file in os.listdir(SPREADSHEETS_DIR):
                if file.endswith('_results.xlsx'):
                    spreadsheets.append(file)
        
        if not spreadsheets:
            self.console.print("[yellow]No previous results found.[/yellow]")
            self.console.print(f"Results will be saved to: [cyan]{self.format_path(SPREADSHEETS_DIR)}[/cyan]")
        else:
            table = Table(title="Available Results", show_header=True, header_style="bold green")
            table.add_column("File", style="cyan")
            table.add_column("Path", style="white")
            
            for sheet in spreadsheets:
                full_path = os.path.join(SPREADSHEETS_DIR, sheet)
                table.add_row(sheet, self.format_path(full_path))
            
            self.console.print(table)
        
        input("\nPress Enter to return to main menu...")
        self.current_screen = "main"