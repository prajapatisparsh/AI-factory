"""
Parallel Execution Utility - Run agents concurrently when possible.
"""

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Callable, Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result from a parallel task."""
    task_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class ParallelExecutor:
    """
    Execute multiple agent tasks in parallel.
    
    Usage:
        executor = ParallelExecutor(max_workers=3)
        
        results = executor.run_parallel({
            "backend": lambda: backend_agent.generate_draft(...),
            "frontend": lambda: frontend_agent.generate_draft(...)
        })
        
        backend_result = results["backend"].result
        frontend_result = results["frontend"].result
    """
    
    def __init__(self, max_workers: int = 4, timeout: int = 300):
        """
        Initialize parallel executor.
        
        Args:
            max_workers: Maximum concurrent threads
            timeout: Timeout per task in seconds
        """
        self.max_workers = max_workers
        self.timeout = timeout
    
    def run_parallel(
        self,
        tasks: Dict[str, Callable[[], Any]],
        fail_fast: bool = False
    ) -> Dict[str, TaskResult]:
        """
        Run multiple tasks in parallel.
        
        Args:
            tasks: Dict mapping task names to callable functions
            fail_fast: If True, cancel remaining tasks on first failure
        
        Returns:
            Dict mapping task names to TaskResult objects
        """
        results: Dict[str, TaskResult] = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_task, name, func): name
                for name, func in tasks.items()
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_task):
                task_name = future_to_task[future]
                
                try:
                    result = future.result(timeout=self.timeout)
                    results[task_name] = result
                    
                    if fail_fast and not result.success:
                        logger.warning(f"Task {task_name} failed, cancelling remaining tasks")
                        for f in future_to_task:
                            f.cancel()
                        break
                        
                except FuturesTimeoutError:
                    results[task_name] = TaskResult(
                        task_name=task_name,
                        success=False,
                        result=None,
                        error=f"Task timed out after {self.timeout} seconds"
                    )
                except Exception as e:
                    results[task_name] = TaskResult(
                        task_name=task_name,
                        success=False,
                        result=None,
                        error=str(e)
                    )
        
        return results
    
    def _execute_task(self, name: str, func: Callable) -> TaskResult:
        """Execute a single task and capture result."""
        start_time = time.time()
        
        try:
            logger.info(f"Starting parallel task: {name}")
            result = func()
            execution_time = time.time() - start_time
            
            logger.info(f"Completed task {name} in {execution_time:.2f}s")
            
            return TaskResult(
                task_name=name,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Task {name} failed after {execution_time:.2f}s: {e}")
            
            return TaskResult(
                task_name=name,
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )
    
    def run_sequential_fallback(
        self,
        tasks: Dict[str, Callable[[], Any]]
    ) -> Dict[str, TaskResult]:
        """
        Run tasks sequentially (fallback when parallel fails).
        
        Useful for debugging or when rate limits are an issue.
        """
        results: Dict[str, TaskResult] = {}
        
        for name, func in tasks.items():
            results[name] = self._execute_task(name, func)
        
        return results


def run_agents_parallel(
    tasks: Dict[str, Callable[[], Any]],
    parallel: bool = True,
    max_workers: int = 3
) -> Dict[str, Any]:
    """
    Convenience function to run agent tasks in parallel.
    
    Args:
        tasks: Dict of {name: callable}
        parallel: Whether to run in parallel (False = sequential)
        max_workers: Max concurrent tasks
    
    Returns:
        Dict of {name: result} (unwrapped results)
    """
    executor = ParallelExecutor(max_workers=max_workers)
    
    if parallel:
        task_results = executor.run_parallel(tasks)
    else:
        task_results = executor.run_sequential_fallback(tasks)
    
    # Unwrap results
    results = {}
    for name, task_result in task_results.items():
        if task_result.success:
            results[name] = task_result.result
        else:
            logger.error(f"Task {name} failed: {task_result.error}")
            results[name] = None
    
    return results


# Example usage for the pipeline
def parallel_draft_generation(
    backend_agent,
    frontend_agent,
    context,
    user_stories,
    architecture,
    clarifications,
    feedback=""
) -> Tuple[str, str]:
    """
    Generate backend and frontend drafts in parallel.
    
    Returns:
        Tuple of (backend_draft, frontend_draft)
    """
    tasks = {
        "backend": lambda: backend_agent.generate_backend_draft(
            context, user_stories, architecture, clarifications, feedback
        ),
        "frontend": lambda: frontend_agent.generate_frontend_draft(
            context, user_stories, architecture, clarifications, feedback
        )
    }
    
    results = run_agents_parallel(tasks, parallel=True)
    
    return (
        results.get("backend", ""),
        results.get("frontend", "")
    )
