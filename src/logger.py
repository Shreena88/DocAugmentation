import os
import datetime

class ActivityLogger:
    def __init__(self, log_file="logs/activity_log.md"):
        self.enabled = True
        self.log_file = log_file

        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Initialize file with header if it doesn't exist
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w") as f:
                    f.write("# DocAUG Activity Log\n\n")
                    f.write("| Timestamp | Action | Input | Detection | Enhancement | Status |\n")
                    f.write("|---|---|---|---|---|---|\n")

        except (OSError, PermissionError) as e:
            print(f"WARNING: Could not initialize logging (Permission Denied). Logging disabled. Error: {e}")
            self.enabled = False

    def log_process(self, input_path, detect_mode, enhance_mode, status="Success"):
        """
        Logs a processing event.
        """
        if not self.enabled:
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(input_path) if input_path else "N/A"
        
        entry = f"| {timestamp} | Process Image | {filename} | {detect_mode} | {enhance_mode} | {status} |\n"
        
        try:
            with open(self.log_file, "a") as f:
                f.write(entry)
        except Exception as e:
            print(f"Logging failed: {e}")
