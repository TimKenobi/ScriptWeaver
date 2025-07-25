# app/core/script_executor.py

from app.core.script_loader import ScriptLoader

class ScriptExecutor(QObject):
    def __init__(self):
        super().__init__()
        self.script_loader = ScriptLoader()

    def execute_scripts(self, scripts: List[Dict]):
        """Execute selected scripts securely"""
        try:
            total_scripts = len(scripts)

            for i, script in enumerate(scripts, 1):
                if self.current_process is None:
                    break

                self.status.emit(f"Running: {script['name']}")
                logger.info(f"Executing script: {script['name']}")

                try:
                    # Execute encrypted script
                    result = self.script_loader.execute_secure_script(script['id'])

                    if result.returncode != 0:
                        raise Exception(f"Script failed: {result.stderr}")

                    # Update progress
                    progress = int((i / total_scripts) * 100)
                    self.progress.emit(progress)
                    self.status.emit(f"Completed: {script['name']}")
                    logger.info(f"Successfully completed script: {script['name']}")

                except Exception as e:
                    logger.error(f"Error executing script {script['name']}: {str(e)}")
                    self.error.emit(f"Error in {script['name']}: {str(e)}")
                    return

            self.finished.emit()

        except Exception as e:
            logger.error(f"Script execution failed: {str(e)}")
            self.error.emit(f"Execution failed: {str(e)}")