"""
Data loading utilities for Trial Balance automation.

This module provides centralized data loading functions that can be imported
by notebooks for consistent data access patterns.
"""

from pathlib import Path
from typing import Dict, Union, Optional, List
import pandas as pd
from datetime import datetime
import logging


class DataLoader:
    """
    Centralized data loading with consistent patterns and error handling.
    
    This class provides reusable methods for loading trial balance data,
    reference data (COA/Portfolio mappings), and batch CSV processing.
    
    Attributes:
        base_path (Path): Base directory for data operations
        logger (logging.Logger): Logger instance for operation tracking
    
    Example:
        >>> loader = DataLoader(base_path='../data/raw/Trial Balance')
        >>> daily_data = loader.load_all_csv_files(
        ...     folder='2025/September/Trial Balance',
        ...     date_format='%m-%d-%Y'
        ... )
        >>> coa_mapping = loader.load_reference_data('COA Mapping')
    """
    
    def __init__(self, base_path: Union[str, Path], logger: Optional[logging.Logger] = None):
        """
        Initialize DataLoader with base path and optional logger.
        
        Args:
            base_path: Base directory for data operations (can be relative or absolute)
            logger: Optional logger instance. If None, creates a default logger.
        """
        self.base_path = Path(base_path)
        self.logger = logger or self._create_default_logger()
    
    def _create_default_logger(self) -> logging.Logger:
        """Create a default logger if none provided."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                        datefmt='%H:%M:%S')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def load_all_csv_files(self, 
                           folder: Union[str, Path], 
                           date_format: Optional[str] = None,
                           recursive: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files from a folder into a dictionary.
        
        This method scans a folder for CSV files and loads them into DataFrames.
        Optionally parses dates from filenames for use as dictionary keys.
        
        Args:
            folder: Folder path (absolute or relative to base_path)
            date_format: Optional strptime format string for parsing dates from filenames
                        (e.g., '%m-%d-%Y' for '09-15-2025.csv')
            recursive: If True, search subfolders recursively
            
        Returns:
            Dictionary mapping keys to DataFrames:
            - If date_format provided: keys are YYYY-MM-DD date strings
            - Otherwise: keys are filenames without extension
            
        Example:
            >>> # Parse dates from filenames like '09-15-2025.csv'
            >>> data = loader.load_all_csv_files(
            ...     folder='2025/September/Trial Balance',
            ...     date_format='%m-%d-%Y'
            ... )
            >>> print(data.keys())  # ['2025-09-15', '2025-09-16', ...]
        """
        folder_path = Path(folder)
        
        # Handle relative paths
        if not folder_path.is_absolute():
            folder_path = self.base_path / folder_path
        
        if not folder_path.exists():
            self.logger.warning(f"⚠️ Folder not found: {folder_path}")
            return {}
        
        data = {}
        
        # Get CSV files
        if recursive:
            csv_files = sorted(folder_path.rglob("*.csv"))
        else:
            csv_files = sorted(folder_path.glob("*.csv"))
        
        self.logger.info(f"📂 Loading {len(csv_files)} CSV files from {folder_path.name}")
        
        for file in csv_files:
            try:
                # Parse date from filename if format provided
                if date_format:
                    try:
                        file_date = datetime.strptime(file.stem, date_format)
                        key = file_date.strftime("%Y-%m-%d")
                    except ValueError as e:
                        self.logger.warning(f"  ⚠️ Skipped {file.name}: Invalid date format - {e}")
                        continue
                else:
                    key = file.stem
                
                # Load CSV
                df = pd.read_csv(file)
                data[key] = df
                
                self.logger.info(f"  ✓ {file.name}: {len(df):,} records, {len(df.columns)} columns")
                
            except Exception as e:
                self.logger.error(f"  ❌ Error loading {file.name}: {e}")
        
        self.logger.info(f"✅ Loaded {len(data)} files successfully")
        return data
    
    def load_reference_data(self, ref_type: str = 'COA Mapping') -> Optional[pd.DataFrame]:
        """
        Load latest reference file (COA Mapping, Portfolio Mapping, etc.).
        
        This method automatically finds and loads the most recent reference file
        based on file modification time. Supports both CSV and Excel formats.
        
        Args:
            ref_type: Reference data type matching folder name in data/references/
                     (e.g., 'COA Mapping', 'Portfolio Mapping')
        
        Returns:
            DataFrame containing reference data, or None if no files found
            
        Example:
            >>> coa_mapping = loader.load_reference_data('COA Mapping')
            >>> portfolio_mapping = loader.load_reference_data('Portfolio Mapping')
        """
        # Navigate to references folder
        ref_folder = self.base_path.parent / 'references' / ref_type
        
        if not ref_folder.exists():
            self.logger.warning(f"⚠️ Reference folder not found: {ref_folder}")
            return None
        
        # Get latest file by modification time
        files = sorted(
            list(ref_folder.glob('*.csv')) + list(ref_folder.glob('*.xlsx')) + list(ref_folder.glob('*.xls')),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        if not files:
            self.logger.warning(f"⚠️ No files found in {ref_folder}")
            return None
        
        latest_file = files[0]
        
        try:
            # Load based on file extension
            if latest_file.suffix == '.csv':
                df = pd.read_csv(latest_file)
            else:
                df = pd.read_excel(latest_file)
            
            self.logger.info(f"✓ Loaded {ref_type}: {latest_file.name} ({len(df):,} records)")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error loading {latest_file.name}: {e}")
            return None
    
    def load_trial_balance_data(self, year: str, month: str) -> Dict[str, pd.DataFrame]:
        """
        Load all trial balance CSVs for a specific year and month.
        
        This is a convenience wrapper around load_all_csv_files() specifically
        for trial balance data following the standard folder structure.
        
        Args:
            year: Year folder name (e.g., '2025')
            month: Month folder name (e.g., 'September')
        
        Returns:
            Dictionary mapping YYYY-MM-DD dates to DataFrames
            
        Example:
            >>> data = loader.load_trial_balance_data('2025', 'September')
            >>> print(list(data.keys()))  # ['2025-09-01', '2025-09-02', ...]
        """
        folder = self.base_path / year / month / 'Trial Balance'
        return self.load_all_csv_files(folder, date_format='%m-%d-%Y')
    
    def consolidate_data(self, 
                        data_dict: Dict[str, pd.DataFrame],
                        add_date_column: bool = True,
                        date_column_name: str = 'Date') -> pd.DataFrame:
        """
        Consolidate multiple DataFrames into a single DataFrame.
        
        Args:
            data_dict: Dictionary of DataFrames (typically from load_all_csv_files)
            add_date_column: If True, adds a column with the dictionary key (date)
            date_column_name: Name for the date column
        
        Returns:
            Single consolidated DataFrame with all records
            
        Example:
            >>> daily_data = loader.load_all_csv_files(folder, date_format='%m-%d-%Y')
            >>> consolidated = loader.consolidate_data(daily_data)
            >>> print(consolidated.columns)  # [..., 'Date']
        """
        if not data_dict:
            self.logger.warning("⚠️ No data to consolidate")
            return pd.DataFrame()
        
        dfs_to_concat = []
        
        for key, df in data_dict.items():
            if add_date_column:
                df_copy = df.copy()
                df_copy[date_column_name] = key
                dfs_to_concat.append(df_copy)
            else:
                dfs_to_concat.append(df)
        
        consolidated = pd.concat(dfs_to_concat, ignore_index=True)
        
        self.logger.info(f"✅ Consolidated {len(data_dict)} files into {len(consolidated):,} records")
        
        return consolidated
    
    def get_unique_records(self, 
                          df: pd.DataFrame, 
                          columns: List[str],
                          sort_by: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Extract unique combinations of specified columns.
        
        Args:
            df: Source DataFrame
            columns: List of column names to get unique combinations of
            sort_by: Optional list of columns to sort by
        
        Returns:
            DataFrame with unique combinations, index reset
            
        Example:
            >>> unique_accounts = loader.get_unique_records(
            ...     consolidated_df,
            ...     columns=['accountname', 'level1accountname', 'Account Type']
            ... )
        """
        if not all(col in df.columns for col in columns):
            missing = [col for col in columns if col not in df.columns]
            self.logger.error(f"❌ Missing columns: {missing}")
            raise ValueError(f"Columns not found in DataFrame: {missing}")
        
        unique_df = df[columns].drop_duplicates().reset_index(drop=True)
        
        if sort_by:
            unique_df = unique_df.sort_values(by=sort_by).reset_index(drop=True)
        
        self.logger.info(f"✓ Found {len(unique_df):,} unique combinations of {len(columns)} columns")
        
        return unique_df


class ExcelExporter:
    """
    Utility class for exporting DataFrames to Excel with formatting.
    
    Example:
        >>> exporter = ExcelExporter(output_path='output.xlsx')
        >>> exporter.add_sheet(df, 'Summary', freeze_panes=(1, 0))
        >>> exporter.save()
    """
    
    def __init__(self, output_path: Union[str, Path], logger: Optional[logging.Logger] = None):
        """
        Initialize Excel exporter.
        
        Args:
            output_path: Path for output Excel file
            logger: Optional logger instance
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self.writer = None
        self.sheets = []
    
    def add_sheet(self, 
                  df: pd.DataFrame, 
                  sheet_name: str,
                  freeze_panes: Optional[tuple] = None,
                  autofilter: bool = True) -> None:
        """
        Add a DataFrame as a new sheet.
        
        Args:
            df: DataFrame to export
            sheet_name: Name for the Excel sheet
            freeze_panes: Tuple (row, col) for freeze panes (e.g., (1, 0) freezes header)
            autofilter: If True, add autofilter to header row
        """
        self.sheets.append({
            'df': df,
            'name': sheet_name,
            'freeze_panes': freeze_panes,
            'autofilter': autofilter
        })
    
    def save(self) -> str:
        """
        Save all sheets to Excel file.
        
        Returns:
            Path to saved file
        """
        with pd.ExcelWriter(self.output_path, engine='xlsxwriter') as writer:
            for sheet in self.sheets:
                df = sheet['df']
                df.to_excel(writer, sheet_name=sheet['name'], index=False)
                
                # Get worksheet object for formatting
                worksheet = writer.sheets[sheet['name']]
                
                # Apply freeze panes
                if sheet['freeze_panes']:
                    worksheet.freeze_panes(*sheet['freeze_panes'])
                
                # Apply autofilter
                if sheet['autofilter']:
                    worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        
        self.logger.info(f"✅ Exported {len(self.sheets)} sheets to {self.output_path}")
        return str(self.output_path)
