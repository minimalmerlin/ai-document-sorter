"""File system monitoring module using Watchdog.

This module implements the file system watching functionality to detect
new files in the inbox directory and trigger processing workflows.
"""

import logging
import time
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .config import Config

logger = logging.getLogger(__name__)


class DocumentEventHandler(FileSystemEventHandler):
    """Event handler for file system events in the inbox directory.

    This class extends Watchdog's FileSystemEventHandler to process
    new files that appear in the monitored directory.

    Attributes:
        process_callback (Callable): Function to call when a new file is detected.
        stabilization_delay (float): Seconds to wait before processing (file write completion).
    """

    def __init__(
        self,
        process_callback: Callable[[Path], None],
        stabilization_delay: float = Config.FILE_STABILIZATION_DELAY
    ):
        """Initialize the DocumentEventHandler.

        Args:
            process_callback: Function that processes a single file (receives Path).
            stabilization_delay: Time to wait after file creation before processing.
        """
        super().__init__()
        self.process_callback = process_callback
        self.stabilization_delay = stabilization_delay
        logger.info(
            f"DocumentEventHandler initialized with {stabilization_delay}s delay"
        )

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Called by Watchdog when a new file is detected in the monitored directory.

        Args:
            event: The file system event containing information about the created file.
        """
        # Ignore directory creation events
        if event.is_directory:
            logger.debug(f"Ignoring directory creation: {event.src_path}")
            return

        filepath = Path(event.src_path)
        logger.info(f"New file detected: {filepath.name}")

        # Wait for file write to complete (avoid locked files)
        if self.stabilization_delay > 0:
            logger.debug(
                f"Waiting {self.stabilization_delay}s for file stabilization"
            )
            time.sleep(self.stabilization_delay)

        # Trigger the processing callback
        try:
            self.process_callback(filepath)
        except Exception as e:
            logger.error(
                f"Error in process callback for {filepath.name}: {e}",
                exc_info=True
            )


class DirectoryMonitor:
    """Monitors a directory for new files and processes them.

    This class sets up file system watching using Watchdog and handles
    both initial directory scanning and continuous monitoring.

    Attributes:
        inbox_path (Path): Directory to monitor.
        process_callback (Callable): Function to process files.
        observer (Observer): Watchdog observer instance.
        event_handler (DocumentEventHandler): Event handler for file events.
    """

    def __init__(
        self,
        inbox_path: str = Config.INBOX_PATH,
        process_callback: Callable[[Path], None] = None
    ):
        """Initialize the DirectoryMonitor.

        Args:
            inbox_path: Path to the directory to monitor.
            process_callback: Function that processes files (receives Path).
        """
        self.inbox_path = Path(inbox_path)
        self.process_callback = process_callback
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[DocumentEventHandler] = None

        logger.info(f"DirectoryMonitor initialized for: {self.inbox_path}")

    def run_initial_scan(self) -> None:
        """Scan inbox directory for existing files and process them.

        This is called on startup to process any files that arrived while
        the application was not running (catch-up mode).
        """
        logger.info("Starting initial directory scan (catch-up mode)")

        if not self.inbox_path.exists():
            logger.warning(f"Inbox path does not exist: {self.inbox_path}")
            return

        if not self.inbox_path.is_dir():
            logger.error(f"Inbox path is not a directory: {self.inbox_path}")
            return

        # Get list of files in directory
        files = [f for f in self.inbox_path.iterdir() if f.is_file()]
        logger.info(f"Found {len(files)} files in inbox for initial processing")

        # Process each file
        processed_count = 0
        for filepath in files:
            try:
                if self.process_callback:
                    self.process_callback(filepath)
                    processed_count += 1
            except Exception as e:
                logger.error(
                    f"Error processing {filepath.name} during initial scan: {e}",
                    exc_info=True
                )

        logger.info(
            f"Initial scan completed. Processed {processed_count}/{len(files)} files"
        )

    def start_monitoring(self) -> None:
        """Start continuous directory monitoring using Watchdog.

        Sets up the file system observer to watch for new files and
        trigger processing automatically.
        """
        if not self.process_callback:
            logger.error("Cannot start monitoring without a process callback")
            return

        # Create event handler
        self.event_handler = DocumentEventHandler(self.process_callback)

        # Create and configure observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.inbox_path),
            recursive=False  # Don't monitor subdirectories
        )

        # Start the observer
        self.observer.start()
        logger.info(f"Directory monitoring started for: {self.inbox_path}")

    def stop_monitoring(self) -> None:
        """Stop directory monitoring and clean up resources."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Directory monitoring stopped")

    def run(self) -> None:
        """Run the monitor in blocking mode.

        Performs initial scan, starts monitoring, and blocks until interrupted.
        This is the main entry point for the monitoring workflow.
        """
        logger.info("Starting DirectoryMonitor workflow")

        # Step 1: Process existing files
        self.run_initial_scan()

        # Step 2: Start watching for new files
        self.start_monitoring()

        # Step 3: Block and wait for events
        try:
            logger.info("Monitor is now active. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop_monitoring()
            logger.info("DirectoryMonitor shutdown complete")
