import sys
from subprocess import Popen

from django.core.management.commands.runserver import \
    Command as RunserverCommand

print(f"{'-'*30}\n Custom Startup Command by Tanjim \n{'-'*30}\n")
class Command(RunserverCommand):
    """Run the standard runserver command and start the background task processor in another process."""

    process = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--no-tasks', action='store_true', help='Do not start the background tasks processor')

    def inner_run(self, *args, **options):
        if not options['no_tasks']:
            self.start_background_tasks()
        super().inner_run(*args, **options)

    def start_background_tasks(self):
        """Start the background tasks process."""
        print("Starting background tasks...")
        self.process = Popen([sys.executable, 'manage.py', 'process_tasks'])

    def inner_stop(self):
        print("Stopping background tasks...")
        if self.process:
            self.process.terminate()
        super().inner_stop()
