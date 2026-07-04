"""Queue-based thread-safe JSONL persistence for query results.

Workers put completed QueryResult objects into a queue, and a dedicated writer thread
consumes the queue and writes to JSONL files. This provides:
- Thread-safe writes without file locking
- Natural ordering control via queue processing
- Resume capability by tracking completed indices
- Separation of concerns (workers don't touch files)
"""

import json
import queue
import threading
from pathlib import Path
from typing import Optional

from rag.models.query_result import QueryResult


class JSONLWriter:
    """Thread-safe JSONL writer using a queue-based architecture.
    
    Workers put QueryResult objects into a queue, and a dedicated writer thread
    consumes the queue and writes to JSONL files.
    """
    
    def __init__(
        self,
        output_path: Path,
        sort_by_index: bool = False,
        fsync: bool = False
    ):
        """Initialize the JSONL writer.
        
        Args:
            output_path: Path to the JSONL file
            sort_by_index: If True, sort queue items by query_index before writing
            fsync: If True, call fsync after each write for maximum crash safety
        """
        self.output_path = Path(output_path)
        self.sort_by_index = sort_by_index
        self.fsync = fsync
        
        # Queue for worker results
        self._queue: queue.Queue = queue.Queue()
        
        # Track completed indices for resume capability
        self._completed_indices: set[int] = set()
        self._lock = threading.Lock()
        
        # Writer thread control
        self._writer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._started = False
        
        # Statistics
        self._total_written = 0
        self._highest_continuous_index = -1
        
        # Load existing indices if file exists
        self._load_existing_indices()
    
    def _load_existing_indices(self):
        """Load already-completed indices from existing JSONL file."""
        if not self.output_path.exists():
            return
        
        try:
            with open(self.output_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        metadata = record.get('metadata', {})
                        query_index = metadata.get('query_index')
                        status = metadata.get('status')
                        if query_index is not None and status == 'success':
                            self._completed_indices.add(query_index)
                    except json.JSONDecodeError:
                        continue
            
            # Calculate highest continuous index
            if self._completed_indices:
                sorted_indices = sorted(self._completed_indices)
                self._highest_continuous_index = sorted_indices[0]
                for i in range(1, len(sorted_indices)):
                    if sorted_indices[i] == self._highest_continuous_index + 1:
                        self._highest_continuous_index = sorted_indices[i]
                    else:
                        break
            
            self._total_written = len(self._completed_indices)
        except Exception as e:
            # If we can't read existing file, start fresh
            self._completed_indices = set()
            self._highest_continuous_index = -1
            self._total_written = 0
    
    def start(self):
        """Start the writer thread."""
        if self._started:
            return
        
        self._stop_event.clear()
        self._writer_thread = threading.Thread(
            target=self._writer_loop,
            daemon=True
        )
        self._writer_thread.start()
        self._started = True
    
    def stop(self):
        """Stop the writer thread and wait for it to finish."""
        if not self._started:
            return
        
        self._stop_event.set()
        # Put a sentinel to wake up the writer
        self._queue.put(None)
        
        if self._writer_thread:
            self._writer_thread.join(timeout=5.0)
        
        self._started = False
    
    def _writer_loop(self):
        """Writer thread main loop."""
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file in append mode
        with open(self.output_path, 'a') as f:
            while not self._stop_event.is_set():
                try:
                    # Get item from queue with timeout
                    item = self._queue.get(timeout=0.1)
                    
                    # Sentinel to stop
                    if item is None:
                        break
                    
                    query_result = item
                    
                    # Extract query_index from metadata
                    query_index = query_result.metadata.get("query_index", 0)
                    
                    # Skip if already written (resume support)
                    with self._lock:
                        if query_index in self._completed_indices:
                            self._queue.task_done()
                            continue
                    
                    # Write to file
                    json_line = json.dumps(query_result.to_dict(), ensure_ascii=False)
                    f.write(json_line + '\n')
                    f.flush()
                    
                    if self.fsync:
                        import os
                        os.fsync(f.fileno())
                    
                    # Update tracking
                    with self._lock:
                        self._completed_indices.add(query_index)
                        self._total_written += 1
                        
                        # Update highest continuous index
                        if query_index == self._highest_continuous_index + 1:
                            self._highest_continuous_index = query_index
                        elif query_index > self._highest_continuous_index:
                            # Check if we can fill gaps
                            expected = self._highest_continuous_index + 1
                            while expected in self._completed_indices:
                                self._highest_continuous_index = expected
                                expected += 1
                    
                    self._queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    # Log error but continue processing
                    print(f"Error writing to JSONL: {e}")
                    continue
    
    def put(self, query_result: QueryResult):
        """Put a QueryResult into the queue for writing.
        
        Args:
            query_result: QueryResult instance to write
        """
        self._queue.put(query_result)
    
    def get_stats(self) -> dict:
        """Get current statistics about the writer.
        
        Returns:
            Dictionary with statistics:
            - total_written: Total number of records written
            - highest_continuous_index: Highest continuous index written
            - queue_size: Current queue size
            - completed_indices: Set of completed indices
        """
        with self._lock:
            return {
                'total_written': self._total_written,
                'highest_continuous_index': self._highest_continuous_index,
                'queue_size': self._queue.qsize(),
                'completed_indices': self._completed_indices.copy()
            }
    
    def wait_for_queue(self, timeout: Optional[float] = None):
        """Wait for all items in the queue to be processed.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        self._queue.join()
    
    def clear_index(self, query_index: int):
        """Remove a query index from completed set so it can be re-processed.
        
        Args:
            query_index: The index to clear
        """
        with self._lock:
            self._completed_indices.discard(query_index)
    
    def deduplicate(self):
        """Rewrite the JSONL file keeping only the last record per query_index."""
        if not self.output_path.exists():
            return
        
        last_record: dict[int, str] = {}
        order: list[int] = []
        
        with open(self.output_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    qi = record.get('metadata', {}).get('query_index')
                    if qi is not None:
                        if qi not in last_record:
                            order.append(qi)
                        last_record[qi] = line
                except json.JSONDecodeError:
                    continue
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for qi in sorted(order):
                f.write(last_record[qi] + '\n')
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
