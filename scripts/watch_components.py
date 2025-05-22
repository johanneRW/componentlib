import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "componentlib" / "components"


class ComponentChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and "metadata.yaml" in event.src_path or "component.py" in event.src_path:
            changed_path = Path(event.src_path)
            component_dir = changed_path.parent

            component_name = component_dir.name
            print(f"[WATCH] 🔁 Change detected in: {component_dir}")

            try:
                subprocess.run(
                    [sys.executable, "manage.py", "generate_component_model", component_name],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to generate model for {component_name}")
                print(e)


def main():
    print("[WATCH] Watching component metadata and logic...")
    event_handler = ComponentChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(COMPONENTS_DIR), recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
