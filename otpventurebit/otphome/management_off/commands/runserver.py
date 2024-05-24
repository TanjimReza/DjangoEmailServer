import signal
import sys
from subprocess import Popen

from django.core.management.commands.runserver import \
    Command as RunserverCommand

print(f"{'-'*30}\n Custom Startup Command by Tanjim \n{'-'*30}\n")


class Command(RunserverCommand):
    """Run the standard runserver command and start the background task processor in another process."""

    process = None

    def inner_run(self, *args, **options):
        self.start_background_tasks()
        try:
            super().inner_run(*args, **options)
        finally:
            self.stop_background_tasks()

    def start_background_tasks(self):
        """Start the background tasks process."""
        print("Starting background tasks...")
        self.process = Popen([sys.executable, 'manage.py', 'process_tasks'])
        print(f"Started background tasks with PID: {self.process.pid}")

    def stop_background_tasks(self):
        """Stop the background tasks process if it exists."""
        if self.process:
            print("Stopping background tasks...")
            self.process.terminate()
            self.process.wait()
            print("Background tasks stopped.")

    def handle(self, *args, **options):
        signal.signal(signal.SIGINT, self.signal_handler)
        super().handle(*args, **options)

    def signal_handler(self, signal, frame):
        """Handle the shutdown signal by stopping the background tasks."""
        self.stop_background_tasks()
        sys.exit(0)
