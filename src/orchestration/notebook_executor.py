"""
Notebook execution orchestrator with dependency resolution and error handling.

This module provides the NotebookExecutor class for executing Jupyter notebooks
via papermill with support for:
- Parameter injection
- Dependency resolution
- Error handling and retries
- Execution logging and metrics
"""

import papermill as pm
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
import json
from collections import defaultdict


class NotebookExecutor:
    """
    Orchestrates notebook execution with dependency resolution.
    
    This class manages the execution of multiple notebooks in the correct order
    based on their dependencies, handles parameter injection, and provides
    comprehensive logging and error handling.
    
    Attributes:
        registry_path (Path): Path to report registry JSON file
        reports (Dict): Loaded report configurations
        logger (logging.Logger): Logger instance
        execution_log (List[Dict]): History of execution attempts
    
    Example:
        >>> executor = NotebookExecutor()
        >>> 
        >>> # Execute single report
        >>> output = executor.execute_report('trial_balance_mvp', 
        ...                                  parameters={'year': '2025', 'month': 'September'})
        >>> 
        >>> # Execute batch with dependencies
        >>> results = executor.execute_batch(['trial_balance_mvp', 'monthly_consolidation'])
    """
    
    def __init__(self, registry_path: str = 'config/report_registry.json',
                 logger: Optional[logging.Logger] = None):
        """
        Initialize NotebookExecutor.
        
        Args:
            registry_path: Path to report registry JSON (relative to project root)
            logger: Optional logger instance. If None, creates default logger.
        """
        self.registry_path = Path(registry_path)
        self.reports = self._load_registry()
        self.logger = logger or self._create_default_logger()
        self.execution_log = []
        self.project_root = self._find_project_root()
    
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
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for config directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / 'config').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load report registry from JSON file."""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"⚠️ Registry not found: {self.registry_path}")
            return {"reports": []}
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON in registry: {e}")
            return {"reports": []}
    
    def get_report_config(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Get report configuration by ID.
        
        Args:
            report_id: Unique report identifier
        
        Returns:
            Report configuration dict or None if not found
        """
        for report in self.reports.get('reports', []):
            if report['id'] == report_id:
                return report
        return None
    
    def list_reports(self, category: Optional[str] = None,
                    status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all reports, optionally filtered by category or status.
        
        Args:
            category: Filter by category (e.g., 'trial_balance', 'consolidation')
            status: Filter by status (e.g., 'active', 'planned')
        
        Returns:
            List of report configurations
        """
        reports = self.reports.get('reports', [])
        
        if category:
            reports = [r for r in reports if r.get('category') == category]
        
        if status:
            reports = [r for r in reports if r.get('status') == status]
        
        return reports
    
    def execute_report(self, 
                      report_id: str, 
                      parameters: Optional[Dict[str, Any]] = None,
                      output_notebook: Optional[str] = None) -> str:
        """
        Execute a single notebook with papermill.
        
        Args:
            report_id: Unique report identifier from registry
            parameters: Optional parameters to override/add to report defaults
            output_notebook: Optional custom output path. If None, auto-generated.
        
        Returns:
            Path to executed notebook
        
        Raises:
            ValueError: If report not found or invalid configuration
            Exception: If notebook execution fails
        
        Example:
            >>> executor = NotebookExecutor()
            >>> output = executor.execute_report(
            ...     'monthly_consolidation',
            ...     parameters={'year': '2025', 'month': 'October'}
            ... )
        """
        # Get report config
        report = self.get_report_config(report_id)
        if not report:
            raise ValueError(f"Report '{report_id}' not found in registry")
        
        # Check if report is active
        if report.get('status') != 'active':
            self.logger.warning(f"⚠️ Report '{report_id}' status: {report.get('status')}")
        
        # Check dependencies
        if report.get('dependencies'):
            self.logger.info(f"📋 Dependencies: {report['dependencies']}")
            self._check_dependencies(report['dependencies'])
        
        # Prepare paths
        notebook_path = self.project_root / 'notebooks' / report['notebook']
        
        if not notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")
        
        # Prepare output path
        if output_notebook:
            output_path = Path(output_notebook)
        else:
            output_dir = self.project_root / 'notebooks' / 'executed' / datetime.now().strftime('%Y%m%d')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{report_id}_{datetime.now():%H%M%S}.ipynb"
        
        # Merge parameters
        params = report.get('parameters', {}).copy()
        if parameters:
            params.update(parameters)
        
        # Auto-resolve 'auto' parameters
        params = self._resolve_auto_parameters(params)
        
        self.logger.info(f"📊 Executing: {report['name']}")
        self.logger.info(f"   Notebook: {notebook_path.name}")
        self.logger.info(f"   Parameters: {params}")
        
        start_time = datetime.now()
        
        try:
            # Execute notebook with papermill
            pm.execute_notebook(
                str(notebook_path),
                str(output_path),
                parameters=params,
                kernel_name='python3',
                progress_bar=False,
                log_output=True
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"✅ {report_id} completed in {duration:.1f}s")
            self.logger.info(f"   Output: {output_path}")
            
            # Log execution
            self.execution_log.append({
                'report_id': report_id,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'duration': duration,
                'output': str(output_path),
                'parameters': params
            })
            
            return str(output_path)
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            self.logger.error(f"❌ {report_id} failed after {duration:.1f}s: {e}")
            
            # Log execution
            self.execution_log.append({
                'report_id': report_id,
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'duration': duration,
                'error': str(e),
                'parameters': params
            })
            
            raise
    
    def execute_batch(self, 
                     report_ids: List[str], 
                     parameters: Optional[Dict[str, Any]] = None,
                     stop_on_error: bool = True) -> Dict[str, str]:
        """
        Execute multiple reports in dependency order.
        
        This method resolves dependencies and executes reports in the correct
        order to ensure prerequisite reports complete before dependent reports.
        
        Args:
            report_ids: List of report IDs to execute
            parameters: Optional parameters applied to all reports
            stop_on_error: If True, stop batch on first error. If False, continue.
        
        Returns:
            Dictionary mapping report_id to output notebook path
        
        Example:
            >>> results = executor.execute_batch(
            ...     ['trial_balance_mvp', 'monthly_consolidation', 'variance_analysis'],
            ...     parameters={'year': '2025', 'month': 'September'}
            ... )
        """
        # Resolve execution order based on dependencies
        execution_order = self._resolve_dependencies(report_ids)
        
        self.logger.info(f"📋 Batch execution plan: {len(execution_order)} reports")
        self.logger.info(f"   Order: {' → '.join(execution_order)}")
        
        results = {}
        failed = []
        
        for report_id in execution_order:
            try:
                output = self.execute_report(report_id, parameters)
                results[report_id] = output
            except Exception as e:
                failed.append(report_id)
                self.logger.error(f"❌ Batch error at {report_id}: {e}")
                
                if stop_on_error:
                    self.logger.error(f"🛑 Stopping batch execution (stop_on_error=True)")
                    break
                else:
                    self.logger.warning(f"⚠️ Continuing batch execution despite error")
        
        # Summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"📊 Batch Execution Summary")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"✅ Successful: {len(results)}/{len(execution_order)}")
        if failed:
            self.logger.info(f"❌ Failed: {len(failed)}/{len(execution_order)} - {failed}")
        self.logger.info(f"{'='*60}\n")
        
        return results
    
    def _resolve_dependencies(self, report_ids: List[str]) -> List[str]:
        """
        Topological sort of reports based on dependencies.
        
        Args:
            report_ids: List of report IDs to sort
        
        Returns:
            Sorted list with dependencies first
        """
        all_reports = []
        visited = set()
        
        def visit(report_id: str):
            """Recursive dependency resolution."""
            if report_id in visited:
                return
            
            report = self.get_report_config(report_id)
            if not report:
                self.logger.warning(f"⚠️ Report not found: {report_id}")
                return
            
            # Visit dependencies first (depth-first)
            for dep in report.get('dependencies', []):
                visit(dep)
            
            all_reports.append(report_id)
            visited.add(report_id)
        
        # Visit all requested reports
        for report_id in report_ids:
            visit(report_id)
        
        return all_reports
    
    def _check_dependencies(self, dependencies: List[str]) -> None:
        """
        Verify all dependencies exist in registry.
        
        Args:
            dependencies: List of report IDs that are dependencies
        
        Logs warnings for missing dependencies.
        """
        for dep in dependencies:
            if not self.get_report_config(dep):
                self.logger.warning(f"⚠️ Dependency not found: {dep}")
    
    def _resolve_auto_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve 'auto' parameter values to actual values.
        
        Args:
            params: Parameter dictionary possibly containing 'auto' values
        
        Returns:
            Parameters with 'auto' values resolved
        """
        resolved = params.copy()
        
        if resolved.get('year') == 'auto':
            resolved['year'] = str(datetime.now().year)
        
        if resolved.get('month') == 'auto':
            resolved['month'] = datetime.now().strftime('%B')
        
        return resolved
    
    def get_execution_history(self, 
                             report_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get execution history for all reports or specific report.
        
        Args:
            report_id: Optional report ID to filter by
        
        Returns:
            List of execution log entries
        """
        if report_id:
            return [e for e in self.execution_log if e['report_id'] == report_id]
        return self.execution_log
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics summary.
        
        Returns:
            Dictionary with execution statistics
        """
        total = len(self.execution_log)
        successful = sum(1 for e in self.execution_log if e['status'] == 'success')
        failed = total - successful
        
        durations = [e['duration'] for e in self.execution_log if 'duration' in e]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        by_report = defaultdict(lambda: {'success': 0, 'failed': 0})
        for entry in self.execution_log:
            by_report[entry['report_id']][entry['status']] += 1
        
        return {
            'total_executions': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0,
            'average_duration': avg_duration,
            'by_report': dict(by_report)
        }
    
    def save_execution_log(self, output_path: str) -> None:
        """
        Save execution log to JSON file.
        
        Args:
            output_path: Path for output JSON file
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w') as f:
            json.dump({
                'execution_log': self.execution_log,
                'stats': self.get_execution_stats()
            }, f, indent=2)
        
        self.logger.info(f"💾 Execution log saved to: {output}")
