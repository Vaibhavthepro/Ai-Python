from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Signal
from terminal import TerminalSession
from powershell import PowerShellProcess
from error_parser import ErrorAnalyzer
from ai_helper import AIHelper
import threading

class MainWindow(QMainWindow):
    ai_fix_ready = Signal(dict, dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Powered Terminal")
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.terminal = TerminalSession()
        layout.addWidget(self.terminal)

        self.error_analyzer = ErrorAnalyzer()
        self.ai_helper = AIHelper()
        self.output_buffer = ""

        self.ps_process = PowerShellProcess()
        self.ps_process.output_received.connect(self.on_output)
        self.ps_process.error_received.connect(self.on_error)
        
        self.terminal.command_entered.connect(self.ps_process.write)

        self.ps_process.start()
        
        self.ai_fix_ready.connect(self._render_ai_fix)

    def on_output(self, text):
        self.terminal.write_output(text, color="#D4D4D4")
        self._process_for_errors(text)

    def on_error(self, text):
        self.terminal.write_output(text, color="#F44336")
        self._process_for_errors(text)
        
    def _process_for_errors(self, text):
        self.output_buffer += text
        while "\n" in self.output_buffer:
            line, self.output_buffer = self.output_buffer.split("\n", 1)
            result = self.error_analyzer.process_line(line)
            if result:
                # Trigger AI in background so UI doesn't freeze
                threading.Thread(target=self.trigger_ai_fix, args=(result,), daemon=True).start()

    def trigger_ai_fix(self, error_info):
        explanation = self.ai_helper.explain_error(error_info["type"], error_info["msg"], error_info["traceback"])
        self.ai_fix_ready.emit(error_info, explanation)

    def _render_ai_fix(self, error_info, explanation):
        block = f"\n────────────────────────────────────────\n\n"
        block += f"❌ Python Error Detected\n\n"
        block += f"Type:\n{error_info['type']}\n\n"
        block += f"Explanation:\n{explanation['explanation']}\n\n"
        block += f"Possible Fix:\n{explanation['fix']}\n\n"
        block += f"Would you like AI to fix this?\n[Y] Yes\n[N] No\n\n"
        block += f"────────────────────────────────────────\n"
        
        self.terminal.write_output(block, color="#FFB300")
        
    def closeEvent(self, event):
        self.ps_process.stop()
        super().closeEvent(event)
