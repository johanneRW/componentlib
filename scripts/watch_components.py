from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import subprocess

COMPONENTS_DIR = Path("componentlib/components")

def is_relevant(file_path):
    return file_path.name in ("metadata.yaml", "component.py")

class MetadataChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if is_relevant(file_path):
            component_name = file_path.parent.name
            print(f"[WATCH] 🔁 Change detected in: {file_path}")
            subprocess.run(["python", "manage.py", "generate_component_model", component_name])

if __name__ == "__main__":
    print("[WATCH] Watching component metadata and logic...")
    event_handler = MetadataChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(COMPONENTS_DIR), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
