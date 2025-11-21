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
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="📊 Trial Balance Data Processor",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Folder Selection Frame
        selection_frame = ttk.LabelFrame(self.root, text="Select Data Folder", padding="10")
        selection_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
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
        
        # Path display
        ttk.Label(selection_frame, text="Selected Path:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.path_label = ttk.Label(selection_frame, text="No selection", 
                                    foreground='gray', font=('Arial', 9))
        self.path_label.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Buttons Frame
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
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
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.grid(row=3, column=0, padx=10, sticky=(tk.W, tk.E))
        
        # Generated Reports Frame
        reports_frame = ttk.LabelFrame(self.root, text="📊 Generated Reports & COA Mappings", padding="10")
        reports_frame.grid(row=4, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
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
        log_frame = ttk.LabelFrame(self.root, text="Processing Log", padding="10")
        log_frame.grid(row=5, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log control buttons
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(log_button_frame, text="🗑️ Clear Log", 
                  command=self.clear_log, width=15).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=90,
                                                  font=('Courier', 9))
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # Load initial reports list
        self.refresh_reports_list()
        
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
    
    def refresh_reports_list(self):
        """Refresh the list of generated reports and COA mappings"""
        try:
            # Clear current list
            self.reports_listbox.delete(0, tk.END)
            
            # === SECTION 1: Excel Reports ===
            self.reports_listbox.insert(tk.END, "═══ EXCEL REPORTS ═══")
            
            # Find Excel reports in data/processed/Trail Balance/{year}/
            output_base = self.project_root / 'data' / 'processed' / 'Trail Balance'
            
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
            else:
                self.reports_listbox.insert(tk.END, "  (No Excel reports found)")
            
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
        
        # Write config file for notebook to read (with absolute path)
        import json
        config_path = self.project_root / 'config' / 'run_config.json'
        config_path.parent.mkdir(exist_ok=True)
        config = {
            'year': year,
            'month': month,
            'data_path': str(data_path)  # Absolute path
        }
        config_path.write_text(json.dumps(config, indent=2))
        self.log_message(f"📝 Config written: {config_path.name}", 'INFO')
        self.log_message(f"   Data Path: {data_path}", 'INFO')
        
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
            
            # Find the output directories - use absolute paths
            # Notebook saves Excel files to: data/processed/Trail Balance/{year}/
            output_dir = self.project_root / 'data' / 'processed' / 'Trail Balance'
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
