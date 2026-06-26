"""
Comprehensive pipeline tracking service.

Provides real-time monitoring of scraping and analysis progress
with detailed API call tracking and performance metrics.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..models.pipelines import (
    APIStatus, 
    DetailedPipelineResponse, 
    Phase, 
    TaskStatus
)

logger = logging.getLogger(__name__)


class PipelineTracker:
    """
    Real-time pipeline progress tracking with detailed API monitoring.
    """
    
    def __init__(self):
        self.active_pipelines: Dict[str, Dict[str, Any]] = {}
        self.pipeline_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_pipeline(self, report_id: str, game_name: str) -> None:
        """Initialize a new pipeline tracking session."""
        self.active_pipelines[report_id] = {
            "report_id": report_id,
            "game_name": game_name,
            "started_at": datetime.utcnow(),
            "current_phase": Phase.SCRAPING,
            "overall_progress": 0.0,
            "phases": {
                Phase.SCRAPING: {
                    "status": TaskStatus.WAITING,
                    "progress": 0.0,
                    "started_at": None,
                    "completed_at": None,
                    "tasks": [],
                    "api_calls": []
                },
                Phase.ANALYSIS: {
                    "status": TaskStatus.WAITING,
                    "progress": 0.0,
                    "started_at": None,
                    "completed_at": None,
                    "tasks": [],
                    "api_calls": []
                },
                Phase.SYNTHESIS: {
                    "status": TaskStatus.WAITING,
                    "progress": 0.0,
                    "started_at": None,
                    "completed_at": None,
                    "tasks": [],
                    "api_calls": []
                },
                Phase.STORAGE: {
                    "status": TaskStatus.WAITING,
                    "progress": 0.0,
                    "started_at": None,
                    "completed_at": None,
                    "tasks": [],
                    "api_calls": []
                }
            },
            "api_calls": {},
            "logs": [],
            "metrics": {
                "total_records_processed": 0,
                "scraping_durations": {},
                "analysis_durations": {}
            }
        }
        
        logger.info(f"Pipeline tracker created for {report_id}: {game_name}")
    
    async def start_phase(self, report_id: str, phase: Phase) -> None:
        """Mark a phase as started."""
        if report_id not in self.active_pipelines:
            logger.warning(f"Pipeline {report_id} not found for phase start")
            return
        
        pipeline = self.active_pipelines[report_id]
        pipeline["current_phase"] = phase
        pipeline["phases"][phase]["status"] = TaskStatus.RUNNING
        pipeline["phases"][phase]["started_at"] = datetime.utcnow()
        pipeline["phases"][phase]["progress"] = 0.0
        
        await self.add_log(report_id, f"Started {phase.value} phase", "info")
        
    async def update_phase_progress(self, report_id: str, progress: float, message: str = "") -> None:
        """Update progress for the current phase."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        current_phase = pipeline["current_phase"]
        
        if current_phase:
            phase_data = pipeline["phases"][current_phase]
            phase_data["progress"] = min(100.0, max(0.0, progress))
            if phase_data["status"] == TaskStatus.WAITING and phase_data["progress"] > 0.0:
                phase_data["status"] = TaskStatus.RUNNING
            
            # Calculate overall progress
            pipeline["overall_progress"] = self._calculate_overall_progress(pipeline)
        
        if message:
            await self.add_log(report_id, message, "info")
    
    async def complete_phase(self, report_id: str, phase: Phase) -> None:
        """Mark a phase as completed."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        pipeline["phases"][phase]["status"] = TaskStatus.COMPLETED
        pipeline["phases"][phase]["progress"] = 100.0
        pipeline["phases"][phase]["completed_at"] = datetime.utcnow()
        
        # Calculate phase duration
        if pipeline["phases"][phase]["started_at"]:
            started = pipeline["phases"][phase]["started_at"]
            completed = pipeline["phases"][phase]["completed_at"]
            duration = (completed - started).total_seconds()
            
            if phase == Phase.SCRAPING:
                pipeline["metrics"]["scraping_durations"]["total"] = duration
            elif phase == Phase.ANALYSIS:
                pipeline["metrics"]["analysis_durations"]["total"] = duration
        
        # Recalculate overall progress now that a phase finished
        pipeline["overall_progress"] = self._calculate_overall_progress(pipeline)
        
        await self.add_log(report_id, f"Completed {phase.value} phase", "success")
    
    async def start_subtask(self, report_id: str, parent_phase: Phase, subtask_name: str) -> None:
        """Start tracking a specific subtask within a phase."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        # Ensure tasks list exists
        if "tasks" not in pipeline["phases"][parent_phase]:
            pipeline["phases"][parent_phase]["tasks"] = []
        
        # Create or update subtask
        subtask_id = f"{parent_phase.value}_{subtask_name.lower().replace(' ', '_')}"
        
        # Look for existing subtask
        existing_task = None
        for task in pipeline["phases"][parent_phase]["tasks"]:
            if task.get("name") == subtask_name:
                existing_task = task
                break
        
        if existing_task:
            existing_task["status"] = TaskStatus.RUNNING.value
            existing_task["started_at"] = datetime.utcnow()
            existing_task["progress"] = 0.0
        else:
            # Create new subtask
            new_task = {
                "id": subtask_id,
                "name": subtask_name,
                "status": TaskStatus.RUNNING.value,
                "progress": 0.0,
                "started_at": datetime.utcnow(),
                "completed_at": None
            }
            pipeline["phases"][parent_phase]["tasks"].append(new_task)
        
        await self.add_log(report_id, f"Started subtask: {subtask_name}", "info")
    
    async def update_subtask_progress(self, report_id: str, parent_phase: Phase, subtask_name: str, progress: float, status: TaskStatus = None) -> None:
        """Update progress of a specific subtask."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        if "tasks" not in pipeline["phases"][parent_phase]:
            return
        
        # Find the subtask
        for task in pipeline["phases"][parent_phase]["tasks"]:
            if task.get("name") == subtask_name:
                task["progress"] = progress
                if status:
                    task["status"] = status.value
                
                # If completed, mark completion time
                if progress >= 100.0 or status == TaskStatus.COMPLETED:
                    task["status"] = TaskStatus.COMPLETED.value
                    task["progress"] = 100.0
                    task["completed_at"] = datetime.utcnow()
                    await self.add_log(report_id, f"Completed subtask: {subtask_name}", "success")
                break
    
    async def pause_subtask(self, report_id: str, parent_phase: Phase, subtask_name: str, reason: str = "") -> None:
        """Mark a subtask as paused."""
        await self.update_subtask_status(report_id, parent_phase, subtask_name, TaskStatus.PAUSED, reason)
    
    async def block_subtask(self, report_id: str, parent_phase: Phase, subtask_name: str, reason: str = "") -> None:
        """Mark a subtask as blocked."""
        await self.update_subtask_status(report_id, parent_phase, subtask_name, TaskStatus.BLOCKED, reason)
    
    async def fail_subtask(self, report_id: str, parent_phase: Phase, subtask_name: str, error: str = "") -> None:
        """Mark a subtask as failed."""
        await self.update_subtask_status(report_id, parent_phase, subtask_name, TaskStatus.FAILED, error)
    
    async def update_subtask_status(self, report_id: str, parent_phase: Phase, subtask_name: str, status: TaskStatus, message: str = "") -> None:
        """Update status of a specific subtask."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        if "tasks" not in pipeline["phases"][parent_phase]:
            return
        
        # Find the subtask
        for task in pipeline["phases"][parent_phase]["tasks"]:
            if task.get("name") == subtask_name:
                task["status"] = status.value
                
                if status == TaskStatus.COMPLETED:
                    task["progress"] = 100.0
                    task["completed_at"] = datetime.utcnow()
                
                if message:
                    await self.add_log(report_id, f"{subtask_name}: {message}", "warning" if status in [TaskStatus.FAILED, TaskStatus.BLOCKED] else "info")
                break
    
    async def start_api_call(self, report_id: str, api_name: str, details: Dict[str, Any] = None, timeout_seconds: int = 10) -> None:
        """Track the start of an API call with timeout monitoring."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        api_status = APIStatus(
            name=api_name,
            status=TaskStatus.RUNNING,
            started_at=datetime.utcnow(),
            details=details or {}
        )
        
        pipeline["api_calls"][api_name] = api_status
        
        # Add to current phase API calls
        current_phase = pipeline["current_phase"]
        if current_phase:
            pipeline["phases"][current_phase]["api_calls"].append(api_status)
        
        await self.add_log(report_id, f"Started {api_name} API call (timeout: {timeout_seconds}s)", "info")
        
        # Schedule timeout check
        asyncio.create_task(self._check_api_timeout(report_id, api_name, timeout_seconds))
    
    async def _check_api_timeout(self, report_id: str, api_name: str, timeout_seconds: int) -> None:
        """Check if API call exceeds timeout and mark as failed/blocked."""
        await asyncio.sleep(timeout_seconds)
        
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        # Check if API call is still running
        if api_name in pipeline["api_calls"]:
            api_status = pipeline["api_calls"][api_name]
            if api_status.status == TaskStatus.RUNNING:
                # Mark as failed due to timeout
                api_status.status = TaskStatus.FAILED
                api_status.error = f"Timeout after {timeout_seconds} seconds"
                api_status.completed_at = datetime.utcnow()
                
                # Calculate duration
                if api_status.started_at:
                    api_status.duration_seconds = (
                        api_status.completed_at - api_status.started_at
                    ).total_seconds()
                
                await self.add_log(
                    report_id, 
                    f"{api_name} API call failed: timeout after {timeout_seconds}s", 
                    "warning"
                )
    
    async def complete_api_call(
        self, 
        report_id: str, 
        api_name: str, 
        items_found: int = 0, 
        error: str = None
    ) -> None:
        """Track the completion of an API call."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        if api_name in pipeline["api_calls"]:
            api_status = pipeline["api_calls"][api_name]
            api_status.completed_at = datetime.utcnow()
            api_status.data_items_found = items_found
            api_status.duration_seconds = (
                api_status.completed_at - api_status.started_at
            ).total_seconds()
            
            if error:
                api_status.status = TaskStatus.FAILED
                api_status.error = error
                await self.add_log(report_id, f"{api_name} API call failed: {error}", "error")
            else:
                api_status.status = TaskStatus.COMPLETED
                await self.add_log(
                    report_id, 
                    f"{api_name} API call completed: {items_found} items found", 
                    "success"
                )
    
    async def add_task(self, report_id: str, phase: Phase, task_name: str, description: str = "") -> None:
        """Add a sub-task to track."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        task = {
            "name": task_name,
            "description": description,
            "status": TaskStatus.WAITING,
            "started_at": None,
            "completed_at": None,
            "progress": 0.0
        }
        
        pipeline["phases"][phase]["tasks"].append(task)
        await self.add_log(report_id, f"Added task: {task_name}", "info")
    
    async def update_task_status(
        self, 
        report_id: str, 
        phase: Phase, 
        task_name: str, 
        status: TaskStatus, 
        progress: float = 0.0,
        error: str = None
    ) -> None:
        """Update status of a specific task."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        phase_data = pipeline["phases"][phase]
        
        for task in phase_data["tasks"]:
            if task["name"] == task_name:
                task["status"] = status
                task["progress"] = progress
                
                if status == TaskStatus.RUNNING and not task["started_at"]:
                    task["started_at"] = datetime.utcnow()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task["completed_at"] = datetime.utcnow()
                
                if error:
                    task["error"] = error
                
                log_msg = f"Task {task_name}: {status.value}"
                if error:
                    log_msg += f" - {error}"
                await self.add_log(report_id, log_msg, "info" if status != TaskStatus.FAILED else "error")
                break
    
    def _calculate_overall_progress(self, pipeline: Dict[str, Any]) -> float:
        phase_weights = {
            Phase.SCRAPING: 0.30,
            Phase.ANALYSIS: 0.40,
            Phase.SYNTHESIS: 0.20,
            Phase.STORAGE: 0.10,
        }
        overall_progress = 0.0
        for phase, weight in phase_weights.items():
            phase_progress = pipeline["phases"][phase]["progress"]
            overall_progress += weight * phase_progress
        return min(100.0, overall_progress)

    async def add_log(self, report_id: str, message: str, level: str = "info") -> None:
        """Add a log entry to the pipeline."""
        if report_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[report_id]
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        }
        
        pipeline["logs"].append(log_entry)
        logger.info(f"Pipeline {report_id} [{level}]: {message}")
    
    def get_pipeline_status(self, report_id: str) -> Optional[DetailedPipelineResponse]:
        """Get detailed status of a pipeline."""
        if report_id not in self.active_pipelines:
            return None
        
        pipeline = self.active_pipelines[report_id]
        current_phase = pipeline["current_phase"]
        
        # Calculate task counts
        tasks_total = 0
        tasks_succeeded = 0
        tasks_failed = 0
        tasks_skipped = 0
        
        for phase_data in pipeline["phases"].values():
            for task in phase_data["tasks"]:
                tasks_total += 1
                if task["status"] == TaskStatus.COMPLETED:
                    tasks_succeeded += 1
                elif task["status"] == TaskStatus.FAILED:
                    tasks_failed += 1
                elif task["status"] == TaskStatus.SKIPPED:
                    tasks_skipped += 1
        
        # Determine overall status
        if any(phase_data["status"] == TaskStatus.FAILED for phase_data in pipeline["phases"].values()):
            overall_status = TaskStatus.FAILED
        elif pipeline["overall_progress"] >= 100.0:
            overall_status = TaskStatus.COMPLETED
        elif any(phase_data["status"] == TaskStatus.RUNNING for phase_data in pipeline["phases"].values()):
            overall_status = TaskStatus.RUNNING
        elif any(phase_data["status"] == TaskStatus.COMPLETED for phase_data in pipeline["phases"].values()) or pipeline["overall_progress"] > 0.0:
            overall_status = TaskStatus.RUNNING
        else:
            overall_status = TaskStatus.WAITING
        
        # Calculate elapsed time
        started_at = pipeline["started_at"]
        seconds_elapsed = (datetime.utcnow() - started_at).total_seconds() if started_at else 0.0
        
        # Get recent logs (last 20)
        recent_logs = pipeline["logs"][-20:] if pipeline["logs"] else []
        
        return DetailedPipelineResponse(
            report_id=report_id,
            phase=current_phase or Phase.SCRAPING,
            status=overall_status,
            is_complete=overall_status == TaskStatus.COMPLETED,
            message=(
                "Pipeline completed successfully" if overall_status == TaskStatus.COMPLETED else
                f"Pipeline running - {current_phase.value if current_phase else 'initializing'} phase"
            ),
            
            # Progress tracking
            seconds_elapsed=seconds_elapsed,
            seconds_remaining=None,
            current_phase_progress=pipeline["phases"][current_phase]["progress"] if current_phase else 0.0,
            overall_progress=pipeline["overall_progress"],
            result=pipeline.get("result"),
            
            # Task counts
            tasks_succeeded=tasks_succeeded,
            tasks_failed=tasks_failed,
            tasks_skipped=tasks_skipped,
            tasks_total=tasks_total,
            
            # Detailed breakdown
            phases=pipeline["phases"],
            api_calls=list(pipeline["api_calls"].values()),
            current_task=None,  # Could be enhanced to track current active task
            logs=recent_logs,
            
# Performance metrics
            scraping_durations=pipeline["metrics"]["scraping_durations"],
            analysis_durations=pipeline["metrics"]["analysis_durations"],
            total_records_processed=pipeline["metrics"]["total_records_processed"],
            
            # Database integration
            db_report_id=pipeline.get("db_report_id")
        )
    
    def archive_pipeline(self, report_id: str) -> None:
        """Move pipeline from active to history."""
        if report_id in self.active_pipelines:
            pipeline = self.active_pipelines.pop(report_id)
            
            if report_id not in self.pipeline_history:
                self.pipeline_history[report_id] = []
            
            self.pipeline_history[report_id].append(pipeline)
            logger.info(f"Archived pipeline {report_id}")
    
    async def archive_pipeline_async(self, report_id: str) -> None:
        """Asynchronous version of archive_pipeline."""
        self.archive_pipeline(report_id)
        await self.add_log(report_id, "Pipeline archived", "info")
    
    def get_pipeline_logs(self, report_id: str, level: str = None) -> List[Dict[str, Any]]:
        """Get logs for a pipeline, optionally filtered by level."""
        if report_id not in self.active_pipelines:
            return []
        
        logs = self.active_pipelines[report_id]["logs"]
        
        if level:
            logs = [log for log in logs if log["level"] == level]
        
        return logs


# Global pipeline tracker instance
pipeline_tracker = PipelineTracker()