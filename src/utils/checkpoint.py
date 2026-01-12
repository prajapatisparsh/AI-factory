"""
Checkpoint System - Save and restore pipeline state for resume functionality.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import pickle


@dataclass
class PipelineCheckpoint:
    """Represents a saved pipeline state."""
    checkpoint_id: str
    phase: int
    timestamp: str
    project_name: str
    
    # Phase 1 outputs
    context: Optional[Dict] = None
    
    # Phase 2 outputs
    user_stories: Optional[List[Dict]] = None
    architecture: Optional[str] = None
    
    # Phase 3 outputs
    clarifications: Optional[Dict] = None
    
    # Phase 4-6 outputs
    backend_draft: Optional[str] = None
    frontend_draft: Optional[str] = None
    backend_final: Optional[str] = None
    frontend_final: Optional[str] = None
    
    # Phase 7 outputs
    qa_report: Optional[Dict] = None
    evaluation: Optional[Dict] = None
    
    # Retry info
    retry_attempt: int = 0
    feedback: str = ""
    
    # Model used
    model_provider: str = "groq"
    model_id: str = "llama-3.1-70b-versatile"


class CheckpointManager:
    """
    Manages pipeline checkpoints for resume functionality.
    
    Usage:
        manager = CheckpointManager()
        
        # Save state after each phase
        manager.save_checkpoint(phase=2, context=ctx, user_stories=stories)
        
        # Check for existing checkpoint
        checkpoint = manager.get_latest_checkpoint()
        if checkpoint:
            print(f"Resume from phase {checkpoint.phase}?")
    """
    
    def __init__(self, checkpoint_dir: Optional[str] = None):
        """Initialize checkpoint manager."""
        if checkpoint_dir is None:
            self.checkpoint_dir = Path(__file__).parent.parent.parent / "checkpoints"
        else:
            self.checkpoint_dir = Path(checkpoint_dir)
        
        self.checkpoint_dir.mkdir(exist_ok=True)
        self._current_checkpoint: Optional[PipelineCheckpoint] = None
    
    def _generate_checkpoint_id(self, project_name: str) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in project_name[:20] if c.isalnum() or c in "._-")
        return f"{safe_name}_{timestamp}"
    
    def start_new_pipeline(self, project_name: str = "project") -> PipelineCheckpoint:
        """Start a new pipeline and create initial checkpoint."""
        checkpoint_id = self._generate_checkpoint_id(project_name)
        
        self._current_checkpoint = PipelineCheckpoint(
            checkpoint_id=checkpoint_id,
            phase=0,
            timestamp=datetime.now().isoformat(),
            project_name=project_name
        )
        
        self._save_to_disk()
        return self._current_checkpoint
    
    def save_checkpoint(
        self,
        phase: int,
        **kwargs
    ) -> PipelineCheckpoint:
        """
        Save checkpoint after completing a phase.
        
        Args:
            phase: Completed phase number (1-8)
            **kwargs: Phase-specific data to save
        
        Returns:
            Updated checkpoint
        """
        if self._current_checkpoint is None:
            self._current_checkpoint = self.start_new_pipeline()
        
        self._current_checkpoint.phase = phase
        self._current_checkpoint.timestamp = datetime.now().isoformat()
        
        # Update with provided data
        for key, value in kwargs.items():
            if hasattr(self._current_checkpoint, key):
                # Handle non-serializable objects
                if hasattr(value, '__dict__'):
                    value = self._serialize_object(value)
                elif isinstance(value, list) and value and hasattr(value[0], '__dict__'):
                    value = [self._serialize_object(v) for v in value]
                
                setattr(self._current_checkpoint, key, value)
        
        self._save_to_disk()
        return self._current_checkpoint
    
    def _serialize_object(self, obj: Any) -> Dict:
        """Convert object to serializable dict."""
        if hasattr(obj, 'model_dump'):  # Pydantic v2
            return obj.model_dump()
        elif hasattr(obj, 'dict'):  # Pydantic v1
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return obj
    
    def _save_to_disk(self) -> None:
        """Save current checkpoint to disk."""
        if self._current_checkpoint is None:
            return
        
        checkpoint_path = self.checkpoint_dir / f"{self._current_checkpoint.checkpoint_id}.json"
        
        # Convert to dict for JSON
        data = asdict(self._current_checkpoint)
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Also update the "latest" pointer
        latest_path = self.checkpoint_dir / "latest.txt"
        with open(latest_path, 'w') as f:
            f.write(self._current_checkpoint.checkpoint_id)
    
    def get_latest_checkpoint(self) -> Optional[PipelineCheckpoint]:
        """Get the most recent checkpoint."""
        latest_path = self.checkpoint_dir / "latest.txt"
        
        if not latest_path.exists():
            return None
        
        with open(latest_path, 'r') as f:
            checkpoint_id = f.read().strip()
        
        return self.load_checkpoint(checkpoint_id)
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[PipelineCheckpoint]:
        """Load a specific checkpoint."""
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_path.exists():
            return None
        
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        checkpoint = PipelineCheckpoint(**data)
        self._current_checkpoint = checkpoint
        return checkpoint
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints."""
        checkpoints = []
        
        for path in self.checkpoint_dir.glob("*.json"):
            if path.name == "latest.json":
                continue
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                checkpoints.append({
                    "id": data.get("checkpoint_id"),
                    "project": data.get("project_name"),
                    "phase": data.get("phase"),
                    "timestamp": data.get("timestamp"),
                    "path": str(path)
                })
            except Exception:
                pass
        
        # Sort by timestamp (most recent first)
        checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            return True
        return False
    
    def clear_all_checkpoints(self) -> int:
        """Delete all checkpoints. Returns count deleted."""
        count = 0
        for path in self.checkpoint_dir.glob("*.json"):
            path.unlink()
            count += 1
        
        latest_path = self.checkpoint_dir / "latest.txt"
        if latest_path.exists():
            latest_path.unlink()
        
        self._current_checkpoint = None
        return count
    
    def get_resume_phase(self) -> int:
        """Get the phase to resume from (completed phase + 1)."""
        if self._current_checkpoint:
            return self._current_checkpoint.phase + 1
        return 1
    
    def should_resume(self) -> bool:
        """Check if there's a checkpoint to resume from."""
        checkpoint = self.get_latest_checkpoint()
        return checkpoint is not None and checkpoint.phase > 0 and checkpoint.phase < 8


# Global checkpoint manager
_checkpoint_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager() -> CheckpointManager:
    """Get or create global checkpoint manager."""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
