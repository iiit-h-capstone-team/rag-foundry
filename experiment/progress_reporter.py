"""Progress reporting for experiment execution.

Displays live execution statistics including completion status,
latencies, throughput, and ETA.
"""

import threading
import time
from typing import Optional


class ProgressReporter:
    """Live progress reporter for experiment execution."""
    
    def __init__(
        self,
        total_queries: int,
        jsonl_writer,
        show_progress: bool = True,
        update_interval: float = 1.0
    ):
        """Initialize progress reporter.
        
        Args:
            total_queries: Total number of queries to execute
            jsonl_writer: JSONLWriter instance to get statistics from
            show_progress: Whether to display progress
            update_interval: Seconds between progress updates
        """
        self.total_queries = total_queries
        self.jsonl_writer = jsonl_writer
        self.show_progress = show_progress
        self.update_interval = update_interval
        
        self._start_time = time.time()
        self._stop_event = threading.Event()
        self._reporter_thread: Optional[threading.Thread] = None
        self._started = False
    
    def start(self):
        """Start the progress reporter thread."""
        if not self.show_progress or self._started:
            return
        
        self._stop_event.clear()
        self._reporter_thread = threading.Thread(
            target=self._report_loop,
            daemon=True
        )
        self._reporter_thread.start()
        self._started = True
    
    def stop(self):
        """Stop the progress reporter thread."""
        if not self._started:
            return
        
        self._stop_event.set()
        if self._reporter_thread:
            self._reporter_thread.join(timeout=2.0)
        
        self._started = False
        # Print final progress
        if self.show_progress:
            self._print_progress(final=True)
    
    def _report_loop(self):
        """Reporter thread main loop."""
        while not self._stop_event.is_set():
            self._print_progress()
            time.sleep(self.update_interval)
    
    def _print_progress(self, final: bool = False):
        """Print current progress statistics."""
        stats = self.jsonl_writer.get_stats()
        completed = stats["total_written"]
        total = self.total_queries
        
        if total == 0:
            return
        
        elapsed = time.time() - self._start_time
        progress_pct = (completed / total) * 100
        
        # Calculate queries per second
        qps = completed / elapsed if elapsed > 0 else 0
        
        # Calculate ETA
        if qps > 0:
            remaining = total - completed
            eta_seconds = remaining / qps
            eta_str = self._format_time(eta_seconds)
        else:
            eta_str = "Unknown"
        
        # Print progress
        print(
            f"\rProgress: {completed}/{total} ({progress_pct:.1f}%) | "
            f"QPS: {qps:.2f} | "
            f"ETA: {eta_str} | "
            f"Elapsed: {self._format_time(elapsed)}",
            end="\n" if final else "",
            flush=True
        )
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
