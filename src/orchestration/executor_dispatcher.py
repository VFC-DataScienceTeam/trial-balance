import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any, Tuple, List

class ExecutorDispatcher:
    """Dispatches execution to different kinds of executors: 'notebook', 'dotnet', 'shell'.

    For now we implement 'dotnet' and 'shell'.
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)

    def run_dotnet_project(self, project_path: Path, args: List[str]) -> Dict[str, Any]:
        p = Path(project_path)
        if not p.exists():
            return {"ok": False, "error": f"Project path not found: {p}"}

        cmd = ["dotnet", "run", "--project", str(p), "--"] + args
        return self._run_command(cmd, cwd=self.workspace_root)

    def run_shell(self, command: str) -> Dict[str, Any]:
        cmd = shlex.split(command)
        return self._run_command(cmd, cwd=self.workspace_root)

    def _run_command(self, cmd, cwd: Path) -> Dict[str, Any]:
        try:
            proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
            return {
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
