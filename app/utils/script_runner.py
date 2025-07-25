# app/utils/script_runner.py

import logging
from PyQt6.QtCore import QObject, pyqtSignal, QProcess, QThread

class ScriptRunner(QThread):
    """
    Runs a shell script in a separate thread using QProcess to avoid blocking the GUI.
    It captures output in real-time.
    """
    # Signals to communicate with the GUI thread
    output_ready = pyqtSignal(str)
    finished = pyqtSignal(bool)  # bool indicates success or failure

    def __init__(self, script_path, password, needs_sudo=False, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.password = password
        self.needs_sudo = needs_sudo
        self._success = False

    def run(self):
        """The main logic of the thread."""
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        # Connect QProcess signals to our handlers
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.handle_finish)

        command = []
        if self.needs_sudo:
            # Using 'sudo -S' to read the password from standard input.
            # This is generally safer than putting the password on the command line.
            command.extend(["sudo", "-S", "-p", "''"])
        
        command.extend(["/bin/bash", self.script_path])

        logging.debug(f"Executing command: {' '.join(command)}")
        
        self.process.start(command[0], command[1:])
        
        if self.needs_sudo:
            # Write the password to the process's standard input
            self.process.write(f"{self.password}\n".encode())
            self.process.closeWriteChannel()

        # Start the event loop for this thread
        self.exec()

    def handle_output(self):
        """Reads output from the process and emits it."""
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self.output_ready.emit(data)

    def handle_finish(self, exit_code, exit_status):
        """
        Handles the process finishing, determines success, and emits the finished signal.
        """
        logging.info(f"Script {self.script_path} finished with exit code {exit_code}.")
        self._success = (exit_code == 0 and exit_status == QProcess.ExitStatus.NormalExit)
        self.finished.emit(self._success)
        self.quit() # End the thread's event loop

    def get_success_status(self):
        """Allows retrieving the final status after the thread has finished."""
        return self._success
