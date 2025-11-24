"""
Trial Balance Processing Application
A GUI application for loading and processing trial balance data.
This app runs the full notebook (01-rd-trial-balance-mvp.ipynb) using papermill.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import threading
import logging
from io import StringIO
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

class TrialBalanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trial Balance Data Processor")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables - use absolute paths from project root
        self.project_root = Path(__file__).parent.parent.parent
        self.base_path = self.project_root / 'data' / 'raw' / 'Trial Balance'
        self.selected_year = tk.StringVar()
        self.selected_month = tk.StringVar()
        self.year_folders = []
        self.month_folders = []
        self.data = None
        
        # Load notebook registry
        self.notebook_registry = self.load_notebook_registry()
        self.selected_notebook = tk.StringVar()
        
        # Setup logging to capture in GUI
        self.log_stream = StringIO()
        self.setup_logging()
        
        # Create UI
        self.create_widgets()
        
        # Load available folders
        self.load_year_folders()
        
    def setup_logging(self):
        """Configure logging to capture output"""
        self.logger = logging.getLogger('TrialBalanceApp')
        self.logger.setLevel(logging.INFO)
        
        # Handler for GUI display
        handler = logging.StreamHandler(self.log_stream)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                     datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def load_notebook_registry(self):
        """Load notebook registry from config file"""
        registry_path = self.project_root / 'config' / 'notebook_registry.json'
        try:
            with open(registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load notebook registry: {e}")
            return {"notebooks": []}
    
    def create_widgets(self):
        """Create all GUI widgets with tabbed interface"""
        
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.title_label = ttk.Label(title_frame, text="📊 Trial Balance Data Processor",
                               font=('Arial', 16, 'bold'))
        self.title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Main content container
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabbed interface
        self.tab_control = ttk.Notebook(self.main_container)
        self.tab_control.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tab 1: Process Reports (existing functionality)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='  Process Reports  ')
        
        # Tab 2: Notebook Selector (new functionality)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab2, text='  Notebook Selector  ')
        
        # Create widgets for each tab
        self.create_process_tab()
        self.create_notebook_tab()
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
    
    def create_process_tab(self):
        """Create widgets for Process Reports tab (existing functionality)"""
        
        # Folder Selection Frame
        selection_frame = ttk.LabelFrame(self.tab1, text="Select Data Folder", padding="10")
        selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Year selection
        ttk.Label(selection_frame, text="Year:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.year_combo = ttk.Combobox(selection_frame, textvariable=self.selected_year,
                                       state='readonly', width=30)
        self.year_combo.grid(row=0, column=1, padx=10, pady=5)
        self.year_combo.bind('<<ComboboxSelected>>', self.on_year_selected)
        
        # Month selection
        ttk.Label(selection_frame, text="Month:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.month_combo = ttk.Combobox(selection_frame, textvariable=self.selected_month,
                                        state='readonly', width=30)
        self.month_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Input data location selection
        ttk.Label(selection_frame, text="Load Data From:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.input_location = tk.StringVar(value="local")
        input_combo = ttk.Combobox(selection_frame, textvariable=self.input_location,
                                    state='readonly', width=30)
        input_combo['values'] = ('Local Storage (Project Folder)', 'Shared Drive (X:\\Trail Balance)')
        input_combo.grid(row=2, column=1, padx=10, pady=5)
        input_combo.current(0)  # Default to local
        input_combo.bind('<<ComboboxSelected>>', self.on_input_location_changed)
        
        # Input connection status indicator
        self.input_status_label = ttk.Label(selection_frame, text="", font=('Arial', 9))
        self.input_status_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Path display
        ttk.Label(selection_frame, text="Selected Path:", font=('Arial', 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.path_label = ttk.Label(selection_frame, text="No selection", 
                                    foreground='gray', font=('Arial', 9))
        self.path_label.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Output location selection
        ttk.Label(selection_frame, text="Save Output To:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_location = tk.StringVar(value="shared_drive")
        output_combo = ttk.Combobox(selection_frame, textvariable=self.output_location,
                                     state='readonly', width=30)
        output_combo['values'] = ('Shared Drive (X:\\Trail Balance)', 'Local Storage (Project Folder)')
        output_combo.grid(row=4, column=1, padx=10, pady=5)
        output_combo.current(0)  # Default to shared drive
        output_combo.bind('<<ComboboxSelected>>', self.on_output_location_changed)
        
        # Output connection status indicator
        self.output_status_label = ttk.Label(selection_frame, text="", font=('Arial', 9))
        self.output_status_label.grid(row=4, column=2, padx=5, pady=5)
        
        # Output path display
        self.output_path_label = ttk.Label(selection_frame, text="X:\\Trail Balance\\data\\processed\\Trail Balance\\", 
                                           foreground='blue', font=('Arial', 9))
        self.output_path_label.grid(row=5, column=1, sticky=tk.W, padx=10, pady=2)
        
        # Buttons Frame
        button_frame = ttk.Frame(self.tab1, padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Main action button (large and prominent)
        self.process_button = ttk.Button(button_frame, text="📊 Process Report", 
                                      command=self.run_notebook_processing, state='disabled',
                                      width=25)
        self.process_button.grid(row=0, column=0, padx=5)
        
        # Secondary buttons
        self.export_button = ttk.Button(button_frame, text="📂 Open Results Folder", 
                                       command=self.export_results, state='disabled',
                                       width=20)
        self.export_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self.load_year_folders, width=15).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="❌ Exit", 
                  command=self.root.quit, width=15).grid(row=0, column=3, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.tab1, mode='indeterminate')
        self.progress.grid(row=2, column=0, padx=10, sticky=(tk.W, tk.E))
        
        # Generated Reports Frame
        reports_frame = ttk.LabelFrame(self.tab1, text="📊 Generated Reports & COA Mappings", padding="10")
        reports_frame.grid(row=3, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Reports list with scrollbar
        reports_list_frame = ttk.Frame(reports_frame)
        reports_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.reports_listbox = tk.Listbox(reports_list_frame, height=5, width=90,
                                          font=('Courier', 9))
        reports_scrollbar = ttk.Scrollbar(reports_list_frame, orient="vertical",
                                         command=self.reports_listbox.yview)
        self.reports_listbox.config(yscrollcommand=reports_scrollbar.set)
        
        self.reports_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        reports_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        reports_list_frame.columnconfigure(0, weight=1)
        
        # Refresh reports button
        ttk.Button(reports_frame, text="🔄 Refresh Reports List", 
                  command=self.refresh_reports_list, width=20).grid(row=1, column=0, pady=5)
        
        # Status/Log display
        log_frame = ttk.LabelFrame(self.tab1, text="Processing Log", padding="10")
        log_frame.grid(row=4, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log control buttons
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(log_button_frame, text="🗑️ Clear Log", 
                  command=self.clear_log, width=15).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=90,
                                                  font=('Courier', 9))
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for tab1
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # Load initial reports list
        self.refresh_reports_list()
        
        # Check initial connection status
        self.check_connection(self.base_path, "input")
        output_path = "X:/Trail Balance" if "Shared Drive" in self.output_location.get() else str(self.project_root / 'data' / 'processed' / 'Trail Balance')
        self.check_connection(output_path, "output")
    
    def create_notebook_tab(self):
        """Create widgets for Notebook Selector tab"""
        
        # Notebook Selection Frame
        notebook_frame = ttk.LabelFrame(self.tab2, text="Select Notebook to Execute", padding="10")
        notebook_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Notebook dropdown
        ttk.Label(notebook_frame, text="Select Notebook:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Build notebook list from registry
        active_notebooks = [nb for nb in self.notebook_registry.get('notebooks', []) if nb.get('status') == 'active']
        notebook_names = [nb['name'] for nb in active_notebooks]
        
        self.notebook_combo = ttk.Combobox(notebook_frame, textvariable=self.selected_notebook,
                                          state='readonly', width=50)
        self.notebook_combo['values'] = notebook_names
        self.notebook_combo.grid(row=0, column=1, padx=10, pady=5)
        if notebook_names:
            self.notebook_combo.current(0)
        self.notebook_combo.bind('<<ComboboxSelected>>', self.on_notebook_selected)
        
        # Description Frame
        desc_frame = ttk.LabelFrame(self.tab2, text="Notebook Description", padding="10")
        desc_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        self.desc_text = scrolledtext.ScrolledText(desc_frame, height=4, width=90,
                                                   font=('Arial', 9), wrap=tk.WORD)
        self.desc_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.desc_text.config(state='disabled')
        
        # Notebook Details Frame
        details_frame = ttk.LabelFrame(self.tab2, text="Notebook Details", padding="10")
        details_frame.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Details labels
        self.nb_file_label = ttk.Label(details_frame, text="File: -", font=('Arial', 9))
        self.nb_file_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.nb_exec_time_label = ttk.Label(details_frame, text="Estimated Time: -", font=('Arial', 9))
        self.nb_exec_time_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.nb_requires_label = ttk.Label(details_frame, text="Requires: -", font=('Arial', 9), wraplength=700)
        self.nb_requires_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Parameters Frame (reuse year/month/location from tab1)
        params_frame = ttk.LabelFrame(self.tab2, text="Parameters", padding="10")
        params_frame.grid(row=3, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Year
        ttk.Label(params_frame, text="Year:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nb_year_combo = ttk.Combobox(params_frame, textvariable=self.selected_year,
                                          state='readonly', width=15)
        self.nb_year_combo.grid(row=0, column=1, padx=10, pady=5)
        self.nb_year_combo['values'] = self.year_combo['values']
        self.nb_year_combo.bind('<<ComboboxSelected>>', self.on_nb_year_selected)
        
        # Month
        ttk.Label(params_frame, text="Month:", font=('Arial', 10)).grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.nb_month_combo = ttk.Combobox(params_frame, textvariable=self.selected_month,
                                           state='readonly', width=15)
        self.nb_month_combo.grid(row=0, column=3, padx=10, pady=5)
        
        # Input location
        ttk.Label(params_frame, text="Load Data From:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        nb_input_combo = ttk.Combobox(params_frame, textvariable=self.input_location,
                                       state='readonly', width=35)
        nb_input_combo['values'] = ('Local Storage (Project Folder)', 'Shared Drive (X:\\Trail Balance)')
        nb_input_combo.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Input status
        self.nb_input_status = ttk.Label(params_frame, text="", font=('Arial', 9))
        self.nb_input_status.grid(row=1, column=3, padx=5, pady=5)
        
        # Output location
        ttk.Label(params_frame, text="Save Output To:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        nb_output_combo = ttk.Combobox(params_frame, textvariable=self.output_location,
                                        state='readonly', width=35)
        nb_output_combo['values'] = ('Shared Drive (X:\\Trail Balance)', 'Local Storage (Project Folder)')
        nb_output_combo.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Output status
        self.nb_output_status = ttk.Label(params_frame, text="", font=('Arial', 9))
        self.nb_output_status.grid(row=2, column=3, padx=5, pady=5)
        
        # Outputs Frame
        outputs_frame = ttk.LabelFrame(self.tab2, text="Expected Outputs", padding="10")
        outputs_frame.grid(row=4, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        self.outputs_text = scrolledtext.ScrolledText(outputs_frame, height=3, width=90,
                                                      font=('Courier', 9), wrap=tk.WORD)
        self.outputs_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.outputs_text.config(state='disabled')
        
        # Run Button
        run_frame = ttk.Frame(self.tab2, padding="10")
        run_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        self.nb_run_button = ttk.Button(run_frame, text="▶ Run Selected Notebook", 
                                        command=self.run_selected_notebook,
                                        width=30)
        self.nb_run_button.grid(row=0, column=0, padx=5)
        
        # Status display
        self.nb_status_label = ttk.Label(run_frame, text="Ready", font=('Arial', 9), foreground='gray')
        self.nb_status_label.grid(row=0, column=1, padx=20)
        
        # Configure grid weights for tab2
        self.tab2.columnconfigure(0, weight=1)
        
        # Load first notebook details
        if notebook_names:
            self.on_notebook_selected(None)
        
    def on_nb_year_selected(self, event):
        """Handle year selection in notebook tab"""
        self.on_year_selected(event)
        # Update month combo in notebook tab
        self.nb_month_combo['values'] = self.month_combo['values']
    
    def load_year_folders(self):
        """Load available year folders"""
        try:
            if not self.base_path.exists():
                self.log_message(f"❌ Base path not found: {self.base_path}", 'ERROR')
                messagebox.showerror("Error", f"Data folder not found:\n{self.base_path}")
                return
            
            self.year_folders = sorted([f.name for f in self.base_path.iterdir() if f.is_dir()],
                                      reverse=True)
            
            if not self.year_folders:
                self.log_message("❌ No year folders found", 'ERROR')
                messagebox.showwarning("Warning", "No year folders found in data directory")
                return
            
            self.year_combo['values'] = self.year_folders
            # Also update notebook tab year combo if it exists
            if hasattr(self, 'nb_year_combo'):
                self.nb_year_combo['values'] = self.year_folders
            
            if self.year_folders:
                self.year_combo.current(0)  # Select first (latest) year
                if hasattr(self, 'nb_year_combo'):
                    self.nb_year_combo.current(0)
                self.on_year_selected(None)
            
            self.log_message(f"✓ Found {len(self.year_folders)} year folders", 'INFO')
            
        except Exception as e:
            self.log_message(f"❌ Error loading folders: {str(e)}", 'ERROR')
            messagebox.showerror("Error", f"Failed to load folders:\n{str(e)}")
    
    def on_year_selected(self, event):
        """Handle year selection change"""
        year = self.selected_year.get()
        if not year:
            return
        
        year_path = self.base_path / year
        self.month_folders = sorted([f.name for f in year_path.iterdir() if f.is_dir()],
                                    reverse=True)
        
        self.month_combo['values'] = self.month_folders
        # Also update notebook tab month combo if it exists
        if hasattr(self, 'nb_month_combo'):
            self.nb_month_combo['values'] = self.month_folders
        
        if self.month_folders:
            self.month_combo.current(0)  # Select first (latest) month
            if hasattr(self, 'nb_month_combo'):
                self.nb_month_combo.current(0)
            self.update_path_display()
        
        self.log_message(f"📅 Year {year} selected - {len(self.month_folders)} months available", 'INFO')
    
    def update_path_display(self):
        """Update the path display label"""
        year = self.selected_year.get()
        month = self.selected_month.get()
        
        if year and month:
            path = self.base_path / year / month
            self.path_label.config(text=str(path), foreground='black')
            self.process_button.config(state='normal')
        else:
            self.path_label.config(text="No selection", foreground='gray')
            self.process_button.config(state='disabled')
    
    def check_connection(self, path, location_type="input"):
        """Check if a path is accessible and update status indicator"""
        try:
            path_obj = Path(path)
            if path_obj.exists():
                if location_type == "input":
                    self.input_status_label.config(text="✓ Connected", foreground='green')
                else:
                    self.output_status_label.config(text="✓ Connected", foreground='green')
                return True
            else:
                if location_type == "input":
                    self.input_status_label.config(text="✗ Not Found", foreground='orange')
                else:
                    self.output_status_label.config(text="✗ Not Found", foreground='orange')
                return False
        except Exception as e:
            if location_type == "input":
                self.input_status_label.config(text="✗ No Access", foreground='red')
            else:
                self.output_status_label.config(text="✗ No Access", foreground='red')
            return False
    
    def on_output_location_changed(self, event):
        """Handle output location selection change"""
        selection = self.output_location.get()
        
        if "Shared Drive" in selection:
            output_path = "X:\\Trail Balance\\data\\processed\\Trail Balance\\"
            self.output_path_label.config(text=output_path, foreground='blue')
            self.log_message("💾 Output will be saved to: Shared Drive", 'INFO')
            # Check connection
            base_path = "X:/Trail Balance"
            if self.check_connection(base_path, "output"):
                self.log_message("  ✓ Shared drive is accessible", 'INFO')
            else:
                self.log_message("  ⚠️ WARNING: Shared drive not accessible!", 'WARNING')
        else:
            output_path = str(self.project_root / 'data' / 'processed' / 'Trail Balance')
            self.output_path_label.config(text=output_path, foreground='green')
            self.log_message("💾 Output will be saved to: Local Storage", 'INFO')
            # Check connection
            if self.check_connection(output_path, "output"):
                self.log_message("  ✓ Local storage is accessible", 'INFO')
            else:
                self.log_message("  ⚠️ WARNING: Local path not accessible!", 'WARNING')
        
        # Refresh reports list to show files from new location
        self.refresh_reports_list()
    
    def on_input_location_changed(self, event):
        """Handle input data location selection change"""
        selection = self.input_location.get()
        
        if "Shared Drive" in selection:
            self.base_path = Path("X:/Trail Balance/data/raw/Trial Balance")
            self.log_message("📂 Input data will be loaded from: Shared Drive", 'INFO')
            # Check connection
            base_path = "X:/Trail Balance"
            if self.check_connection(base_path, "input"):
                self.log_message("  ✓ Shared drive is accessible", 'INFO')
            else:
                self.log_message("  ⚠️ WARNING: Shared drive not accessible! Check network connection.", 'WARNING')
        else:
            self.base_path = self.project_root / 'data' / 'raw' / 'Trial Balance'
            self.log_message("📂 Input data will be loaded from: Local Storage", 'INFO')
            # Check connection
            if self.check_connection(self.base_path, "input"):
                self.log_message("  ✓ Local storage is accessible", 'INFO')
            else:
                self.log_message("  ⚠️ WARNING: Local path not accessible!", 'WARNING')
        
        # Reload year and month folders from new location
        self.load_year_folders()
    
    def refresh_reports_list(self):
        """Refresh the list of generated reports and COA mappings"""
        try:
            # Clear current list
            self.reports_listbox.delete(0, tk.END)
            
            # Determine output location based on dropdown selection
            selection = self.output_location.get()
            if "Shared Drive" in selection:
                output_base = Path("X:/Trail Balance/data/processed/Trail Balance")
                location_label = "📁 SHARED DRIVE"
            else:
                output_base = self.project_root / 'data' / 'processed' / 'Trail Balance'
                location_label = "💻 LOCAL STORAGE"
            
            # === SECTION 1: Excel Reports ===
            self.reports_listbox.insert(tk.END, f"═══ EXCEL REPORTS ({location_label}) ===")
            
            excel_files = []
            if output_base.exists():
                # Find all Excel files across all year folders
                for year_folder in sorted(output_base.iterdir(), reverse=True):
                    if year_folder.is_dir():
                        for excel_file in year_folder.glob('*.xlsx'):
                            # Get file info
                            stat = excel_file.stat()
                            size_mb = stat.st_size / (1024 * 1024)
                            modified = datetime.fromtimestamp(stat.st_mtime)
                            
                            excel_files.append({
                                'path': excel_file,
                                'year': year_folder.name,
                                'name': excel_file.name,
                                'size': size_mb,
                                'modified': modified
                            })
            
            if excel_files:
                # Sort by modification time (newest first)
                excel_files.sort(key=lambda x: x['modified'], reverse=True)
                
                # Display reports
                for file_info in excel_files:
                    display_text = (
                        f"{file_info['modified'].strftime('%Y-%m-%d %H:%M')} | "
                        f"{file_info['year']} | "
                        f"{file_info['name']} "
                        f"({file_info['size']:.2f} MB)"
                    )
                    self.reports_listbox.insert(tk.END, display_text)
                
                # Add summary
                total_size = sum(f['size'] for f in excel_files)
                self.reports_listbox.insert(tk.END, f"  ✓ Total: {len(excel_files)} files ({total_size:.2f} MB)")
                self.reports_listbox.insert(tk.END, f"  📂 Location: {output_base}")
            else:
                self.reports_listbox.insert(tk.END, "  (No Excel reports found)")
                self.reports_listbox.insert(tk.END, f"  📂 Location: {output_base}")
            
            # === SECTION 2: COA Mappings ===
            self.reports_listbox.insert(tk.END, "")
            self.reports_listbox.insert(tk.END, "═══ COA MAPPINGS ═══")
            
            # Find COA mappings in data/references/COA Mapping/
            coa_base = self.project_root / 'data' / 'references' / 'COA Mapping'
            
            coa_files = []
            if coa_base.exists():
                for coa_file in coa_base.glob('*.xlsx'):
                    stat = coa_file.stat()
                    size_kb = stat.st_size / 1024
                    modified = datetime.fromtimestamp(stat.st_mtime)
                    
                    coa_files.append({
                        'path': coa_file,
                        'name': coa_file.name,
                        'size': size_kb,
                        'modified': modified
                    })
            
            if coa_files:
                # Sort by modification time (newest first)
                coa_files.sort(key=lambda x: x['modified'], reverse=True)
                
                # Display COA mappings (limit to 5 most recent)
                for file_info in coa_files[:5]:
                    display_text = (
                        f"{file_info['modified'].strftime('%Y-%m-%d %H:%M')} | "
                        f"{file_info['name']} "
                        f"({file_info['size']:.1f} KB)"
                    )
                    self.reports_listbox.insert(tk.END, display_text)
                
                if len(coa_files) > 5:
                    self.reports_listbox.insert(tk.END, f"  ... and {len(coa_files) - 5} more")
            else:
                self.reports_listbox.insert(tk.END, "  (No COA mappings found)")
            
            # Show count in status
            total_reports = len(excel_files)
            total_coa = len(coa_files)
            self.log_message(
                f"📊 Found {total_reports} report(s), {total_coa} COA mapping(s)", 
                'INFO'
            )
            
        except Exception as e:
            self.reports_listbox.insert(tk.END, f"Error loading reports: {str(e)}")
            self.log_message(f"⚠️  Error refreshing reports list: {str(e)}", 'WARNING')
    
    def log_message(self, message, level='INFO'):
        """Add message to log display"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("✨ Log cleared", 'INFO')
    
    def on_notebook_selected(self, event):
        """Handle notebook selection - update description and details"""
        selected_name = self.selected_notebook.get()
        
        # Find notebook in registry
        notebook = None
        for nb in self.notebook_registry.get('notebooks', []):
            if nb['name'] == selected_name:
                notebook = nb
                break
        
        if not notebook:
            return
        
        # Update description
        self.desc_text.config(state='normal')
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, notebook.get('description', 'No description available'))
        self.desc_text.config(state='disabled')
        
        # Update details
        self.nb_file_label.config(text=f"File: {notebook.get('file', 'N/A')}")
        self.nb_exec_time_label.config(text=f"Estimated Time: {notebook.get('execution_time', 'N/A')}")
        
        requires = notebook.get('requires', [])
        requires_text = "Requires: " + ", ".join(requires) if requires else "Requires: None"
        self.nb_requires_label.config(text=requires_text)
        
        # Update outputs
        self.outputs_text.config(state='normal')
        self.outputs_text.delete(1.0, tk.END)
        
        outputs = notebook.get('outputs', [])
        if outputs:
            for i, output in enumerate(outputs, 1):
                output_name = output.get('name', 'Unknown')
                output_desc = output.get('description', '')
                output_loc = output.get('location', '')
                self.outputs_text.insert(tk.END, f"{i}. {output_name}\n")
                self.outputs_text.insert(tk.END, f"   {output_desc}\n")
                self.outputs_text.insert(tk.END, f"   📂 {output_loc}\n")
                if i < len(outputs):
                    self.outputs_text.insert(tk.END, "\n")
        else:
            self.outputs_text.insert(tk.END, "No outputs defined")
        
        self.outputs_text.config(state='disabled')
        
        # Update status based on notebook status
        status = notebook.get('status', 'unknown')
        if status == 'active':
            self.nb_status_label.config(text="✅ Ready to run", foreground='green')
            self.nb_run_button.config(state='normal')
        elif status == 'planned':
            self.nb_status_label.config(text="⏳ Planned (not yet implemented)", foreground='orange')
            self.nb_run_button.config(state='disabled')
        else:
            self.nb_status_label.config(text="❓ Status unknown", foreground='gray')
            self.nb_run_button.config(state='disabled')
        
        # Update connection status in notebook tab
        self.nb_input_status.config(text=self.input_status_label.cget("text"), 
                                    foreground=self.input_status_label.cget("foreground"))
        self.nb_output_status.config(text=self.output_status_label.cget("text"),
                                     foreground=self.output_status_label.cget("foreground"))
    
    def run_selected_notebook(self):
        """Run the selected notebook from the notebook selector tab"""
        selected_name = self.selected_notebook.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a notebook")
            return
        
        # Find notebook in registry
        notebook = None
        for nb in self.notebook_registry.get('notebooks', []):
            if nb['name'] == selected_name:
                notebook = nb
                break
        
        if not notebook:
            messagebox.showerror("Error", "Selected notebook not found in registry")
            return
        
        # Check if notebook is active
        if notebook.get('status') != 'active':
            messagebox.showinfo("Info", f"This notebook is not yet implemented.\n\nStatus: {notebook.get('status', 'unknown')}")
            return
        
        # Validate parameters
        year = self.selected_year.get()
        month = self.selected_month.get()
        
        if not year or not month:
            messagebox.showwarning("Warning", "Please select both year and month")
            return
        
        # For now, route to existing processing (only Trial Balance MVP is active)
        notebook_file = notebook.get('file', '')
        if notebook_file == '01-rd-trial-balance-mvp.ipynb':
            # Switch to tab 1 and run
            self.tab_control.select(0)
            self.run_notebook_processing()
        else:
            messagebox.showinfo("Info", f"Execution for '{selected_name}' will be implemented soon!")
    
    def run_notebook_processing(self):
        """Run the full notebook processing - writes config file for notebook to read"""
        year = self.selected_year.get()
        month = self.selected_month.get()
        
        if not year or not month:
            messagebox.showwarning("Warning", "Please select both year and month")
            return
        
        # Disable button during processing
        self.process_button.config(state='disabled')
        
        self.log_message("="*60, 'INFO')
        self.log_message("🚀 STARTING NOTEBOOK EXECUTION", 'INFO')
        self.log_message("="*60, 'INFO')
        self.log_message(f"📅 Year: {year}", 'INFO')
        self.log_message(f"📅 Month: {month}", 'INFO')
        
        # Build absolute path to the selected data folder
        data_path = self.base_path / year / month
        
        # Validate that the selected folder exists
        if not data_path.exists():
            self.log_message(f"❌ ERROR: Folder not found: {data_path}", 'ERROR')
            messagebox.showerror(
                "Folder Not Found",
                f"The selected folder does not exist:\n{data_path}\n\nPlease verify your selection."
            )
            self.process_button.config(state='normal')
            return
        
        # Validate that required subfolders exist
        tb_folder = data_path / "Trial Balance"
        if not tb_folder.exists():
            self.log_message(f"⚠️  WARNING: Trial Balance folder not found: {tb_folder}", 'WARNING')
            result = messagebox.askyesno(
                "Missing Trial Balance Folder",
                f"Trial Balance folder not found:\n{tb_folder}\n\nContinue anyway?",
                icon='warning'
            )
            if not result:
                self.process_button.config(state='normal')
                return
        
        # Determine output path based on user selection
        selection = self.output_location.get()
        if "Shared Drive" in selection:
            output_base_path = "X:\\Trail Balance\\data\\processed\\Trail Balance"
            self.log_message(f"💾 Output Location: Shared Drive", 'INFO')
        else:
            output_base_path = str(self.project_root / 'data' / 'processed' / 'Trail Balance')
            self.log_message(f"💾 Output Location: Local Storage", 'INFO')
        
        # Write config file for notebook to read (with absolute path)
        import json
        config_path = self.project_root / 'config' / 'run_config.json'
        config_path.parent.mkdir(exist_ok=True)
        config = {
            'year': year,
            'month': month,
            'data_path': str(data_path),  # Absolute input path
            'output_base_path': output_base_path  # Output location
        }
        config_path.write_text(json.dumps(config, indent=2))
        self.log_message(f"📝 Config written: {config_path.name}", 'INFO')
        self.log_message(f"   Input Path: {data_path}", 'INFO')
        self.log_message(f"   Output Path: {output_base_path}\\{year}\\", 'INFO')
        
        # Run in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self._execute_notebook, args=(year, month))
        thread.daemon = True
        thread.start()
    
    def _execute_notebook(self, year, month):
        """Execute notebook in background thread"""
        self.progress.start()
        
        try:
            # Paths - use absolute paths from project root
            notebook_path = self.project_root / 'notebooks' / '01-rd-trial-balance-mvp.ipynb'
            output_dir = self.project_root / 'notebooks' / 'executed_trial_balance_reports'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_dir / f"trial_balance_report_{timestamp}.ipynb"
            
            self.log_message(f"\n📓 Notebook: {notebook_path}", 'INFO')
            self.log_message(f"💾 Output: {output_path}", 'INFO')
            self.log_message("\n⚙️  Executing notebook (this may take a few minutes)...", 'INFO')
            
            # Execute notebook with papermill (no parameters - reads config file instead)
            cmd = [
                'papermill',
                str(notebook_path),
                str(output_path)
            ]
            
            self.log_message(f"\n📝 Command: {' '.join(cmd)}", 'INFO')
            self.log_message("\n" + "-"*60, 'INFO')
            
            # Run papermill and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output to log
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.log_message(line.strip(), 'INFO')
            
            process.wait()
            
            if process.returncode == 0:
                self.log_message("\n" + "="*60, 'INFO')
                self.log_message("✅ NOTEBOOK EXECUTION COMPLETE", 'INFO')
                self.log_message("="*60, 'INFO')
                self.log_message(f"\n📊 Executed notebook: {output_path.name}", 'INFO')
                
                # Show output locations
                output_reports_dir = self.project_root / 'data' / 'processed' / 'Trail Balance'
                self.log_message(f"\n📂 OUTPUT LOCATIONS:", 'INFO')
                self.log_message(f"   Excel Reports: {output_reports_dir}", 'INFO')
                self.log_message(f"   Executed Notebooks: {output_dir}", 'INFO')
                
                # Enable export button and refresh reports list
                self.root.after(0, lambda: self.export_button.config(state='normal'))
                self.root.after(0, lambda: self.refresh_reports_list())
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"✅ Processing complete!\n\n"
                    f"📓 Executed Notebook:\n{output_path.name}\n\n"
                    f"📊 Excel Reports saved to:\n{output_reports_dir}\n\n"
                    f"Click '📂 Open Results Folder' to view outputs."
                ))
            else:
                self.log_message("\n" + "="*60, 'ERROR')
                self.log_message("❌ NOTEBOOK EXECUTION FAILED", 'ERROR')
                self.log_message("="*60, 'ERROR')
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Notebook execution failed.\nCheck the log for details."
                ))
        
        except Exception as e:
            self.log_message(f"\n❌ ERROR: {str(e)}", 'ERROR')
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to execute notebook:\n{str(e)}"))
        
        finally:
            self.progress.stop()
            self.root.after(0, lambda: self.process_button.config(state='normal'))
    

    
    
    def export_results(self):
        """Open results folder in Windows Explorer"""
        try:
            self.log_message("\n💾 Opening results folders...", 'INFO')
            
            # Determine output directory based on user selection
            selection = self.output_location.get()
            if "Shared Drive" in selection:
                output_dir = Path("X:/Trail Balance/data/processed/Trail Balance")
                self.log_message("  📂 Opening Shared Drive output folder...", 'INFO')
            else:
                output_dir = self.project_root / 'data' / 'processed' / 'Trail Balance'
                self.log_message("  📂 Opening Local Storage output folder...", 'INFO')
            
            executed_dir = self.project_root / 'notebooks' / 'executed_trial_balance_reports'
            
            # Create directories if they don't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            executed_dir.mkdir(parents=True, exist_ok=True)
            
            # Open both directories in Windows Explorer
            import subprocess
            import os
            
            # Open output directory (where Excel files are saved)
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{output_dir}"')
                self.log_message(f"  ✓ Opened: {output_dir}", 'INFO')
            else:
                subprocess.Popen(['xdg-open', str(output_dir)])
            
            # Check for files
            excel_files = list(output_dir.glob('*.xlsx'))
            notebook_files = list(executed_dir.glob('trial_balance_report_*.ipynb'))
            
            if excel_files:
                latest_excel = max(excel_files, key=lambda p: p.stat().st_mtime)
                self.log_message(f"  ✓ Latest Excel: {latest_excel.name}", 'INFO')
            else:
                self.log_message(f"  ⚠️  No Excel files found yet", 'WARNING')
            
            if notebook_files:
                latest_notebook = max(notebook_files, key=lambda p: p.stat().st_mtime)
                self.log_message(f"  ✓ Latest notebook: {latest_notebook.name}", 'INFO')
            
            # Show info message
            if excel_files:
                messagebox.showinfo(
                    "Results Folder Opened",
                    f"✅ Output folder opened in Explorer!\n\n"
                    f"📊 Excel Reports: {len(excel_files)} file(s)\n"
                    f"📓 Executed Notebooks: {len(notebook_files)} file(s)\n\n"
                    f"Location:\n{output_dir}"
                )
            else:
                messagebox.showinfo(
                    "Results Folder Opened",
                    f"📂 Output folder opened!\n\n"
                    f"⚠️  No Excel files found yet.\n"
                    f"The notebook may still be processing,\n"
                    f"or exports may be saved elsewhere.\n\n"
                    f"Location:\n{output_dir}"
                )
            
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}", 'ERROR')
            messagebox.showerror("Error", f"Failed to open results folder:\n{str(e)}")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = TrialBalanceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
