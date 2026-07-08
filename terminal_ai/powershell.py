import subprocess
import threading
import os
import queue
from PySide6.QtCore import QObject, Signal, QTimer

class PowerShellProcess(QObject):
    output_received = Signal(str)
    error_received = Signal(str)
    process_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self._is_running = False
        self._output_queue = queue.Queue()
        self._error_queue = queue.Queue()

        # Timer to flush queues to the main thread safely
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._process_queues)

    def start(self):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE # Hide the console window

        # Run powershell. We use -NoExit so it stays alive.
        # -Command "-" means it reads from stdin.
        self.process = subprocess.Popen(
            ["powershell.exe", "-NoLogo", "-NoExit", "-Command", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1, # Line buffered
            startupinfo=startupinfo,
            encoding='utf-8',
            errors='replace'
        )
        self._is_running = True

        # Start reader threads
        self.stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self.stdout_thread.start()
        self.stderr_thread.start()
        
        self.timer.start(50) # Flush every 50ms

    def _read_stdout(self):
        while self._is_running and self.process and self.process.poll() is None:
            char = self.process.stdout.read(1)
            if char:
                self._output_queue.put(char)
            else:
                break
        if self._is_running:
            self.process_finished.emit()

    def _read_stderr(self):
        while self._is_running and self.process and self.process.poll() is None:
            char = self.process.stderr.read(1)
            if char:
                self._error_queue.put(char)
            else:
                break

    def _process_queues(self):
        # Process stdout
        out_chunk = ""
        while not self._output_queue.empty():
            out_chunk += self._output_queue.get()
        if out_chunk:
            self.output_received.emit(out_chunk)
            
        # Process stderr
        err_chunk = ""
        while not self._error_queue.empty():
            err_chunk += self._error_queue.get()
        if err_chunk:
            self.error_received.emit(err_chunk)

    def write(self, command: str):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except IOError:
                pass

    def stop(self):
        self._is_running = False
        if self.process:
            self.process.terminate()
            self.process = None
        self.timer.stop()
