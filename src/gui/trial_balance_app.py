"""
Trial Balance Report Automation GUI

PURPOSE:
Unified interface for loading trial balance data from year/month folders and executing
reports via ExecutorFactory (supports both Jupyter notebooks and .NET console apps).

CORE WORKFLOW:
1. Select data source (Local project folder OR Shared Drive X:/Trail Balance)
2. Select Year and Month folders containing trial balance CSVs
3. Choose report from registry (report_registry.json)
4. Click "Run Selected Report" to execute via background thread
5. Monitor execution via progress bar and log output
6. Open results folder after successful completion

OUTPUT STRUCTURE:
- Monthly Reports: {base_path}/{YEAR}/{MONTH}/Trial_Balance.xlsx
- Consolidated: {base_path}/{YEAR}/Trial Balance Monthly/Trial Balance Monthly.xlsx

ARCHITECTURE:
- GUI: tkinter with scrollable canvas (1000x800 fixed window)
- Execution: ExecutorFactory → NotebookExecutor (papermill) or ConsoleExecutor (.NET)
- Threading: Background daemon threads keep GUI responsive during execution
- Configuration: run_config.json (runtime params), report_registry.json (available reports)

CODE ORGANIZATION:
- Section 1: Initialization (GUI setup, state variables)
- Section 2: GUI Layout (widgets, frames, scrollbar)
- Section 3: Event Handlers (year/month selection, validation)
- Section 4: Action Buttons (run, stop, export, refresh, exit)
- Section 5: Report Execution Logic (validation, background threading, ExecutorFactory)
- Section 6: Utility Functions (export folder, logging, connection checks)
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
import shutil
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

class TrialBalanceApp:
    """
    Trial Balance Report Automation GUI
    
    PURPOSE:
    Unified interface for loading trial balance data from year/month folders 
    and executing reports via ExecutorFactory (notebooks or console apps).
    
    WORKFLOW:
    1. User selects data source: Local (project folder) or Shared Drive (X:/Trail Balance)
    2. User selects Year and Month folders containing trial balance CSVs
    3. User chooses report from registry (report_registry.json)
    4. User clicks "Run Selected Report" button
    5. GUI validates selections and updates run_config.json
    6. Background thread executes report via ExecutorFactory
    7. Progress bar shows execution status
    8. Log window displays execution details
    9. "Open Results Folder" button enables after successful completion
    
    OUTPUT LOCATIONS:
    - Local: {project}/data/processed/{YEAR}/{MONTH}/
    - Shared Drive: X:/Trail Balance/data/processed/{YEAR}/{MONTH}/
    - Consolidated reports go to: {base}/{YEAR}/Trial Balance Monthly/
    """
    
    # ========== SECTION 1: INITIALIZATION ==========
    
    def __init__(self, root):
        """Initialize GUI components and state variables"""
        self.root = root
        self.root.title("PEMI REPORT AUTOMATION by RD")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)
        
        # Variables - use absolute paths from project root
        self.project_root = Path(__file__).parent.parent.parent
        self.base_path = self.project_root / 'data' / 'raw' / 'Trial Balance'
        self.selected_year = tk.StringVar()
        self.selected_month = tk.StringVar()
        self.year_folders = []
        self.month_folders = []
        self.data = None
        
        # Load report registry (supports both notebooks and console apps)
        self.report_registry = self.load_report_registry()
        self.selected_report = tk.StringVar()
        
        # Execution control
        self.execution_cancelled = False
        self.current_thread = None
        self.last_error_details = None
        
        # Setup logging to capture in GUI
        self.log_stream = StringIO()
        self.setup_logging()
        
        # Create UI
        self.create_widgets()
        
        # Load available folders
        self.load_year_folders()
        
    def setup_logging(self):
        """Configure logging to capture output to both GUI and file"""
        self.logger = logging.getLogger('PEMI_Reports')
        self.logger.setLevel(logging.INFO)
        
        # Handler for GUI display
        stream_handler = logging.StreamHandler(self.log_stream)
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                     datefmt='%H:%M:%S')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        
        # Handler for file logging
        log_dir = self.project_root / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f'gui_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        self.log_file_path = log_file
        print(f"Logging to: {log_file}")
        
    def load_report_registry(self):
        """Load report registry from config file (supports notebooks and console aspps)"""
        registry_path = self.project_root / 'config' / 'report_registry.json'
        try:
            with open(registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load report registry: {e}")
            return {"reports": []}
    
    def create_widgets(self):
        """Create all GUI widgets with tabbed interface"""
        
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.title_label = ttk.Label(title_frame, text="📊 PEMI Reports Automation",
                               font=('Arial', 16, 'bold'))
        self.title_label.grid(row=0, column=0, sticky=tk.W)
        
        # ========== SECTION 2: GUI LAYOUT ==========
        
        # Main content container with scrollbar
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Main content frame (single unified interface)
        self.tab1 = ttk.Frame(self.scrollable_frame)
        self.tab1.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create the main interface
        self.create_process_tab()
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_process_tab(self):
        """Create main interface for report processing workflow"""
        
        # ========== SECTION 1: DATA SELECTION ==========
        selection_frame = ttk.LabelFrame(self.tab1, text="📁 Step 1: Select Data to Process", padding="10")
        selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Input data location (where to load data from)
        ttk.Label(selection_frame, text="Load Data From:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_location = tk.StringVar(value="local")
        input_combo = ttk.Combobox(selection_frame, textvariable=self.input_location,
                                    state='readonly', width=30)
        input_combo['values'] = ('Local Storage (Project Folder)', 'Shared Drive (X:\\Trail Balance)')
        input_combo.grid(row=0, column=1, padx=10, pady=5)
        input_combo.current(0)  # Default to local
        input_combo.bind('<<ComboboxSelected>>', self.on_input_location_changed)
        
        # Input connection status
        self.input_status_label = ttk.Label(selection_frame, text="", font=('Arial', 9))
        self.input_status_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Year selection
        ttk.Label(selection_frame, text="Year:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.year_combo = ttk.Combobox(selection_frame, textvariable=self.selected_year,
                                       state='readonly', width=30)
        self.year_combo.grid(row=1, column=1, padx=10, pady=5)
        self.year_combo.bind('<<ComboboxSelected>>', self.on_year_selected)
        
        # Month selection
        ttk.Label(selection_frame, text="Month:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.month_combo = ttk.Combobox(selection_frame, textvariable=self.selected_month,
                                        state='readonly', width=30)
        self.month_combo.grid(row=2, column=1, padx=10, pady=5)
        self.month_combo.bind('<<ComboboxSelected>>', self.update_path_display)
        
        # Selected data path display
        ttk.Label(selection_frame, text="Data Path:", font=('Arial', 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.path_label = ttk.Label(selection_frame, text="No selection", 
                                    foreground='gray', font=('Arial', 9))
        self.path_label.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # ========== SECTION 2: REPORT SELECTION ==========
        report_frame = ttk.LabelFrame(self.tab1, text="📊 Step 2: Select Report to Run", padding="10")
        report_frame.grid(row=1, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Report selection
        ttk.Label(report_frame, text="Report:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Load active reports from registry
        active_reports = [r for r in self.report_registry.get('reports', []) if r.get('status') in ('active', 'poc')]
        report_options = [f"{r['name']} [{r.get('executor_type', 'notebook').upper()}]" for r in active_reports]
        
        self.selected_report_index = tk.IntVar(value=0)
        self.report_combo = ttk.Combobox(report_frame, values=report_options,
                                         state='readonly', width=60)
        self.report_combo.grid(row=0, column=1, padx=10, pady=5)
        if report_options:
            self.report_combo.current(0)
        self.report_combo.bind('<<ComboboxSelected>>', self.on_report_combo_changed)
        
        # Report description
        self.report_desc_label = ttk.Label(report_frame, text="", 
                                           font=('Arial', 9), foreground='gray',
                                           wraplength=700)
        self.report_desc_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)
        
        # ========== SECTION 3: OUTPUT SETTINGS ==========
        output_frame = ttk.LabelFrame(self.tab1, text="💾 Step 3: Output Settings", padding="10")
        output_frame.grid(row=2, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Output location selection
        ttk.Label(output_frame, text="Save Results To:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_location = tk.StringVar(value="shared_drive")
        output_combo = ttk.Combobox(output_frame, textvariable=self.output_location,
                                     state='readonly', width=30)
        output_combo['values'] = ('Shared Drive (X:\\Trail Balance)', 'Local Storage (Project Folder)')
        output_combo.grid(row=0, column=1, padx=10, pady=5)
        output_combo.current(0)  # Default to shared drive
        output_combo.bind('<<ComboboxSelected>>', self.on_output_location_changed)
        
        # Output connection status
        self.output_status_label = ttk.Label(output_frame, text="", font=('Arial', 9))
        self.output_status_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Output path display
        self.output_path_label = ttk.Label(output_frame, text="X:\\Trail Balance\\data\\processed\\", 
                                           foreground='blue', font=('Arial', 9))
        self.output_path_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)
        
        # ========== SECTION 4: ACTION BUTTONS ==========
        button_frame = ttk.Frame(self.tab1, padding="10")
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Main action button (Run Report)
        self.process_button = ttk.Button(button_frame, text="▶ Run Selected Report", 
                                      command=self.run_report, state='disabled',
                                      width=25)
        self.process_button.grid(row=0, column=0, padx=5)
        
        # Stop button (initially disabled)
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Process",
                                     command=self.stop_execution, state='disabled',
                                     width=20)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Utility buttons
        self.export_button = ttk.Button(button_frame, text="📂 Open Results Folder", 
                                       command=self.export_results, state='disabled',
                                       width=20)
        self.export_button.grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self.load_year_folders, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Button(button_frame, text="📂 View Logs", 
                  command=self.open_logs_folder, width=15).grid(row=0, column=4, padx=5)
        
        ttk.Button(button_frame, text="❌ Exit", 
                  command=self.root.quit, width=15).grid(row=0, column=5, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.tab1, mode='indeterminate')
        self.progress.grid(row=4, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Generated Reports Frame
        reports_frame = ttk.LabelFrame(self.tab1, text="📊 Generated Reports & COA Mappings", padding="10")
        reports_frame.grid(row=5, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Reports list with scrollbar
        reports_list_frame = ttk.Frame(reports_frame)
        reports_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.reports_listbox = tk.Listbox(reports_list_frame, height=8, width=90,
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
        log_frame.grid(row=6, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log control buttons
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(log_button_frame, text="🗑️ Clear Log", 
                  command=self.clear_log, width=15).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=90,
                                                  font=('Courier', 9))
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for tab1
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.rowconfigure(6, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # Initialize first report selection
        if self.report_combo.get():
            self.on_report_combo_changed(None)
        
        # Load initial reports list
        self.refresh_reports_list()
        
        # Check initial connection status
        self.check_connection(self.base_path, "input")
        output_path = "X:/Trail Balance" if "Shared Drive" in self.output_location.get() else str(self.project_root / 'data' / 'processed' / 'Trail Balance')
        self.check_connection(output_path, "output")
    
    # ========== SECTION 3: EVENT HANDLERS AND VALIDATION ==========
    
    def load_year_folders(self):
        """Load available year folders from selected data source path"""
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
            
            if self.year_folders:
                self.year_combo.current(0)  # Select first (latest) year
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
        
        if self.month_folders:
            self.month_combo.current(0)  # Select first (latest) month
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
    
    def on_report_combo_changed(self, event):
        """Handle report selection change in Process Reports tab"""
        selected_idx = self.report_combo.current()
        if selected_idx < 0:
            return
        
        # Get selected report from registry
        active_reports = [r for r in self.report_registry.get('reports', []) if r.get('status') in ('active', 'poc')]
        if selected_idx < len(active_reports):
            report = active_reports[selected_idx]
            
            # Update description label
            desc = report.get('description', 'No description available')
            executor_type = report.get('executor_type', 'notebook').upper()
            exec_time = report.get('execution_time', 'Unknown')
            
            desc_text = f"[{executor_type}] {desc} • Est. Time: {exec_time}"
            self.report_desc_label.config(text=desc_text, foreground='blue')
            
            self.log_message(f"📋 Selected: {report['name']} ({executor_type})", 'INFO')
    
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
    
    def stop_execution(self):
        """Stop the currently running execution"""
        if self.current_thread and self.current_thread.is_alive():
            self.execution_cancelled = True
            self.log_message("⚠️  STOP REQUESTED - Cancelling execution...", 'WARNING')
            # Don't disable stop button here - let the finally block handle all button states
            
            # Note: Thread will check self.execution_cancelled flag and exit gracefully
            messagebox.showinfo(
                "Stop Requested",
                "Stop signal sent. The process will terminate as soon as possible.\n\n"
                "Note: Some operations may need to complete before stopping."
            )
        else:
            self.log_message("ℹ️  No process is currently running", 'INFO')
    
    # ========== SECTION 5: REPORT EXECUTION LOGIC ==========
    
    def run_report(self):
        """
        Execute the selected report with validated year/month/output configuration
        
        Workflow:
        1. Validate year/month/report selections
        2. Update run_config.json with current selections
        3. Launch background thread for report execution
        4. Update UI to show progress
        """
        print("DEBUG: run_report() CALLED")  # Console debug
        self.log_message("🔘 Run button clicked", 'INFO')
        
        # Get selected report
        selected_idx = self.report_combo.current()
        self.log_message(f"Debug: Report combo index = {selected_idx}", 'INFO')
        
        if selected_idx < 0:
            self.log_message("⚠️  No report selected", 'WARNING')
            messagebox.showwarning("Warning", "Please select a report to run")
            return
        
        active_reports = [r for r in self.report_registry.get('reports', []) if r.get('status') in ('active', 'poc')]
        self.log_message(f"Debug: Found {len(active_reports)} active reports", 'INFO')
        
        if selected_idx >= len(active_reports):
            self.log_message(f"❌ Invalid selection: index {selected_idx} >= {len(active_reports)}", 'ERROR')
            messagebox.showerror("Error", "Invalid report selection")
            return
        
        report = active_reports[selected_idx]
        self.log_message(f"Debug: Selected report = {report.get('name', 'Unknown')}", 'INFO')
        
        # Validate parameters
        year = self.selected_year.get()
        month = self.selected_month.get()
        self.log_message(f"Debug: Year={year}, Month={month}", 'INFO')
        
        if not year or not month:
            self.log_message("❌ Missing year or month", 'ERROR')
            messagebox.showwarning("Warning", "Please select both year and month")
            return
        
        self.log_message("✓ All validations passed, starting execution...", 'INFO')
        
        # Disable run button, enable stop button during execution
        self.process_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.execution_cancelled = False
        self.progress.start()
        self.log_message("✓ Progress bar started", 'INFO')
        self.log_message("✓ Buttons updated (Run disabled, Stop enabled)", 'INFO')
        
        # Execute in background thread
        thread = threading.Thread(target=self._execute_in_background, args=(report, year, month))
        self.current_thread = thread
        thread.daemon = True
        thread.start()
        self.log_message(f"✓ Background thread started (Thread ID: {thread.ident})", 'INFO')
    
    def _execute_in_background(self, report, year, month):
        """
        Background thread: Execute report via ExecutorFactory
        
        This runs in a separate daemon thread to keep GUI responsive.
        Handles both notebook (papermill) and console app execution types.
        
        Args:
            report (dict): Report definition from registry
            year (str): Selected year folder
            month (str): Selected month folder
        
        Process Flow:
        1. Import ExecutorFactory
        2. Validate not cancelled
        3. Determine output path (Local vs Shared Drive)
        4. Execute via ExecutorFactory
        5. Update UI with results
        """
        self.log_message("🚀 Background thread started", 'INFO')
        try:
            self.log_message("Step 1: Importing ExecutorFactory...", 'INFO')
            import sys
            sys.path.insert(0, str(self.project_root))
            from src.orchestration.executor_factory import ExecutorFactory
            self.log_message("✓ ExecutorFactory imported", 'INFO')
            
            # Check cancellation before starting
            if self.execution_cancelled:
                self.log_message("⛔ Execution cancelled before start", 'WARNING')
                return
            
            # Log execution start
            self.log_message("="*60, 'INFO')
            self.log_message(f"🚀 STARTING REPORT EXECUTION: {report['name']}", 'INFO')
            self.log_message("="*60, 'INFO')
            self.log_message(f"📅 Year: {year}", 'INFO')
            self.log_message(f"📅 Month: {month}", 'INFO')
            
            # Get executor type
            executor_type = report.get('executor_type', 'notebook')
            self.log_message(f"🔧 Executor Type: {executor_type.upper()}", 'INFO')
            
            # Check cancellation
            if self.execution_cancelled:
                self.log_message("⛔ Execution cancelled", 'WARNING')
                return
            
            # Prepare parameters
            data_path = self.base_path / year / month
            
            # Determine output path based on user selection
            output_selection = self.output_location.get()
            if "Shared Drive" in output_selection:
                output_base_path = Path("X:/Trail Balance/data/processed")
                self.log_message(f"📍 Output destination: Shared Drive (X:/Trail Balance/data/processed)", 'INFO')
            else:
                output_base_path = self.project_root / 'data' / 'processed'
                self.log_message(f"📍 Output destination: Local Storage ({output_base_path})", 'INFO')
            
            parameters = {
                'year': year,
                'month': month,
                'data_path': str(data_path),
                'output_base_path': str(output_base_path)
            }
            
            # Write run_config.json to ensure notebook uses correct paths
            config_file = self.project_root / 'config' / 'run_config.json'
            try:
                with open(config_file, 'w') as f:
                    json.dump(parameters, f, indent=2)
                self.log_message(f"✓ Updated run_config.json with current settings", 'INFO')
                self.log_message(f"   • data_path: {data_path}", 'INFO')
                self.log_message(f"   • output_base_path: {output_base_path}", 'INFO')
            except Exception as config_err:
                self.log_message(f"⚠️  Warning: Could not write config: {config_err}", 'WARNING')
            
            # Determine executor path
            if executor_type == 'console':
                executor_path = report.get('executor_path')
            else:
                executor_path = f"notebooks/{report.get('notebook')}"
            
            # Create output path for executed notebooks
            output_path = str(self.project_root / 'notebooks' / 'executed' / f"{report['id']}_{year}_{month}.ipynb")
            
            # Define progress callback
            def progress_callback(current, total, message):
                """Callback for progress updates from executor"""
                pct = int((current / total) * 100) if total > 0 else 0
                self.log_message(f"📊 Progress: {message}", 'INFO')
            
            # Create executor with progress callback
            executor = ExecutorFactory.create(executor_type, self.project_root, progress_callback)
            
            # Check cancellation before execution
            if self.execution_cancelled:
                self.log_message("⛔ Execution cancelled", 'WARNING')
                return
            
            self.log_message(f"⚙️  Executing: {executor_path}", 'INFO')
            self.log_message(f"   Parameters: year={year}, month={month}", 'INFO')
            self.log_message(f"   Output: {output_path}", 'INFO')
            self.log_message(f"⏳ Please wait - this may take 1-2 minutes...", 'INFO')
            
            # Execute without stdout capture to avoid papermill conflicts
            try:
                success = executor.execute(executor_path, parameters, output_path)
                self.log_message(f"   Executor returned: {success}", 'INFO')
            except Exception as exec_error:
                error_msg = str(exec_error)
                self.log_message(f"   ❌ Executor exception: {error_msg}", 'ERROR')
                import traceback
                error_trace = traceback.format_exc()
                self.log_message(error_trace, 'ERROR')
                self.last_error_details = f"{error_msg}\n\n{error_trace}"
                success = False
            
            # Check if cancelled during execution
            if self.execution_cancelled:
                self.log_message("⛔ Execution was cancelled", 'WARNING')
                self.root.after(0, lambda: messagebox.showwarning(
                    "Execution Cancelled",
                    f"{report['name']} was cancelled by user."
                ))
                return
            
            if success:
                self.log_message("="*60, 'INFO')
                self.log_message("✅ REPORT EXECUTION COMPLETED SUCCESSFULLY!", 'INFO')
                self.log_message("="*60, 'INFO')
                
                # Show output location
                expected_output = output_base_path / year / month
                self.log_message(f"📂 Output files saved to:", 'INFO')
                self.log_message(f"   {expected_output}", 'INFO')
                
                # Check if files were actually created
                if expected_output.exists():
                    excel_files = list(expected_output.glob('*.xlsx'))
                    if excel_files:
                        self.log_message(f"✓ Found {len(excel_files)} Excel file(s):", 'INFO')
                        for f in excel_files:
                            size_mb = f.stat().st_size / (1024 * 1024)
                            self.log_message(f"   • {f.name} ({size_mb:.2f} MB)", 'INFO')
                    else:
                        self.log_message(f"⚠️  No Excel files found in output folder", 'WARNING')
                else:
                    self.log_message(f"⚠️  Output folder does not exist yet", 'WARNING')
                
                # Enable export button
                self.root.after(0, lambda: self.export_button.config(state='normal'))
                
                # Show success message with location
                location_type = "Shared Drive" if "Shared Drive" in output_selection else "Local Storage"
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"✅ {report['name']} completed successfully!\n\n"
                    f"📂 Output Location: {location_type}\n"
                    f"📁 Path: {expected_output}\n\n"
                    f"Click '📂 Open Results Folder' to view the files."
                ))
                
                # Refresh reports list
                self.root.after(0, self.refresh_reports_list)
            else:
                self.log_message("="*60, 'ERROR')
                self.log_message("❌ REPORT EXECUTION FAILED!", 'ERROR')
                self.log_message("="*60, 'ERROR')
                
                # Get the last few log lines for error context
                log_content = self.log_text.get("end-10l", "end")
                error_lines = [line for line in log_content.split("\n") if "❌" in line or "ERROR" in line or "Traceback" in line]
                error_summary = "\n".join(error_lines[-5:]) if error_lines else "Check Processing Log below for details"
                
                log_location = f"\n\nDetailed log saved to:\n{getattr(self, 'log_file_path', 'logs folder')}"
                
                self.root.after(0, lambda: messagebox.showerror(
                    "Execution Failed",
                    f"{report['name']} failed to execute.\n\nRecent errors:\n{error_summary}{log_location}\n\nClick 'View Logs' button to open logs folder."
                ))
        
        except Exception as e:
            self.log_message(f"❌ EXCEPTION: {str(e)}", 'ERROR')
            import traceback
            self.log_message(traceback.format_exc(), 'ERROR')
            
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Failed to execute report:\n{str(e)}"
            ))
        
        finally:
            # Re-enable run button, disable stop button, stop progress
            self.root.after(0, lambda: self.process_button.config(state='normal'))
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))
            self.root.after(0, self.progress.stop)
            self.execution_cancelled = False
            self.current_thread = None
    
    def run_notebook_processing(self):
        """Run the selected report from Process Reports tab - uses ExecutorFactory"""
        year = self.selected_year.get()
        month = self.selected_month.get()
        
        if not year or not month:
            messagebox.showwarning("Warning", "Please select both year and month")
            return
        
        # Check if a report is selected in Report Selector
        selected_name = self.selected_report.get()
        
        if not selected_name:
            messagebox.showwarning(
                "No Report Selected",
                "Please select a report first:\n\n" +
                "1. Go to 'Report Selector' tab\n" +
                "2. Choose a report from the dropdown\n" +
                "3. Return here to run it"
            )
            return
        
        # Find report in registry
        report = None
        for r in self.report_registry.get('reports', []):
            if r['name'] == selected_name:
                report = r
                break
        
        if not report:
            messagebox.showerror("Error", "Selected report not found in registry")
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
        
        # Execute report in background thread using ExecutorFactory
        thread = threading.Thread(
            target=self._execute_in_background, 
            args=(report, year, month)
        )
        thread.daemon = True
        thread.start()
    
    
    # ========== SECTION 6: UTILITY FUNCTIONS ==========
    
    def open_logs_folder(self):
        """Open the logs folder in Windows Explorer"""
        try:
            logs_dir = self.project_root / 'logs'
            
            if not logs_dir.exists():
                logs_dir.mkdir(parents=True, exist_ok=True)
                self.log_message("📂 Created logs folder", 'INFO')
            
            # Open in Explorer
            import subprocess
            subprocess.run(['explorer', str(logs_dir)])
            self.log_message(f"📂 Opened logs folder: {logs_dir}", 'INFO')
            
        except Exception as e:
            self.log_message(f"❌ Failed to open logs folder: {e}", 'ERROR')
            messagebox.showerror("Error", f"Could not open logs folder:\n{e}")
    
    def export_results(self):
        """
        Open the results folder in Windows Explorer
        
        Opens the year/month specific folder containing the executed report output.
        Respects Local vs Shared Drive selection and validates folder existence.
        """
        try:
            self.log_message("\n💾 Opening results folders...", 'INFO')
            
            # Get the selected year and month from GUI
            year = self.selected_year.get()
            month = self.selected_month.get()
            
            if not year:
                messagebox.showwarning("Warning", "Please select a year first")
                return
            
            # Check BOTH possible locations and open whichever has files
            shared_drive_dir = Path(f"X:/Trail Balance/data/processed/{year}/{month}") if month else Path(f"X:/Trail Balance/data/processed/{year}")
            local_dir = (self.project_root / 'data' / 'processed' / 'Trial Balance' / year / month) if month else (self.project_root / 'data' / 'processed' / 'Trial Balance' / year)
            
            # Check which location has Excel files
            shared_files = list(shared_drive_dir.glob('*.xlsx')) if shared_drive_dir.exists() else []
            local_files = list(local_dir.glob('*.xlsx')) if local_dir.exists() else []
            
            # Open the location that has files (prioritize Shared Drive)
            if shared_files:
                output_dir = shared_drive_dir
                self.log_message(f"  📂 Found {len(shared_files)} file(s) on Shared Drive: {year}/{month if month else ''}", 'INFO')
            elif local_files:
                output_dir = local_dir
                self.log_message(f"  📂 Found {len(local_files)} file(s) in Local Storage: {year}/{month if month else ''}", 'INFO')
            else:
                # Default to output location setting if no files found yet
                selection = self.output_location.get()
                if "Shared Drive" in selection:
                    output_dir = shared_drive_dir
                else:
                    output_dir = local_dir
                self.log_message(f"  📂 No files found yet, opening default location...", 'INFO')
                self.log_message(f"  📂 Opening Local Storage output folder: {year}/{month if month else ''}", 'INFO')
            
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
