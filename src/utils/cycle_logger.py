"""
Cycle Logger - Logs each retry cycle's data for debugging.
Saves detailed logs to logs/<project>_<timestamp>/cycle_<N>/
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, Optional, List


class CycleLogger:
    """Logs retry cycle data for debugging and analysis."""
    
    def __init__(self, project_name: str = "project"):
        """Initialize logger with project name."""
        self.project_name = self._sanitize_name(project_name)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "logs",
            f"{self.project_name}_{self.timestamp}"
        )
        self.current_cycle = 0
        self._ensure_base_dir()
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize project name for filesystem."""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:50]
    
    def _ensure_base_dir(self):
        """Create base log directory."""
        os.makedirs(self.base_dir, exist_ok=True)
    
    def _get_cycle_dir(self, cycle: int) -> str:
        """Get directory for a specific cycle."""
        cycle_dir = os.path.join(self.base_dir, f"cycle_{cycle}")
        os.makedirs(cycle_dir, exist_ok=True)
        return cycle_dir
    
    def start_cycle(self, cycle: int):
        """Start a new cycle."""
        self.current_cycle = cycle
        cycle_dir = self._get_cycle_dir(cycle)
        
        # Write cycle start info
        with open(os.path.join(cycle_dir, "start.txt"), "w") as f:
            f.write(f"Cycle {cycle} started at {datetime.now().isoformat()}\n")
    
    def log_backend(self, spec: str, feedback: str = ""):
        """Log backend specification."""
        cycle_dir = self._get_cycle_dir(self.current_cycle)
        
        content = f"# Backend Specification - Cycle {self.current_cycle}\n\n"
        if feedback:
            content += f"## Previous Feedback\n{feedback}\n\n"
        content += f"## Specification\n{spec}"
        
        with open(os.path.join(cycle_dir, "backend.md"), "w", encoding="utf-8") as f:
            f.write(content)
    
    def log_frontend(self, spec: str, feedback: str = ""):
        """Log frontend specification."""
        cycle_dir = self._get_cycle_dir(self.current_cycle)
        
        content = f"# Frontend Specification - Cycle {self.current_cycle}\n\n"
        if feedback:
            content += f"## Previous Feedback\n{feedback}\n\n"
        content += f"## Specification\n{spec}"
        
        with open(os.path.join(cycle_dir, "frontend.md"), "w", encoding="utf-8") as f:
            f.write(content)
    
    def log_qa_report(self, report: Dict[str, Any]):
        """Log QA report as JSON."""
        cycle_dir = self._get_cycle_dir(self.current_cycle)
        
        with open(os.path.join(cycle_dir, "qa_report.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
    
    def log_evaluation(self, score: int, status: str, issues: List[str], scolding: str = ""):
        """Log PM evaluation."""
        cycle_dir = self._get_cycle_dir(self.current_cycle)
        
        data = {
            "cycle": self.current_cycle,
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "status": status,
            "issues": issues,
            "scolding": scolding
        }
        
        with open(os.path.join(cycle_dir, "evaluation.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def log_summary(self, score: int, passed: bool, issues_fixed: int = 0, remaining_issues: int = 0):
        """Log cycle summary."""
        cycle_dir = self._get_cycle_dir(self.current_cycle)
        
        summary = {
            "cycle": self.current_cycle,
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "passed": passed,
            "issues_fixed": issues_fixed,
            "remaining_issues": remaining_issues
        }
        
        with open(os.path.join(cycle_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        
        # Also append to master summary
        master_summary_path = os.path.join(self.base_dir, "all_cycles.json")
        all_cycles = []
        if os.path.exists(master_summary_path):
            with open(master_summary_path, "r") as f:
                all_cycles = json.load(f)
        all_cycles.append(summary)
        with open(master_summary_path, "w") as f:
            json.dump(all_cycles, f, indent=2)
    
    def get_log_path(self) -> str:
        """Get the base log directory path."""
        return self.base_dir


def create_logger(project_name: str = "project") -> CycleLogger:
    """Create a new cycle logger instance."""
    return CycleLogger(project_name)
