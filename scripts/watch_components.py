import time
import sys
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Match folder structure in update_props
COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "components"

# Cooldown tracker per component
last_run = {}

COOLDOWN_SECONDS = 2  # Minimum time between triggers per component


def should_run(component_name):
    now = time.time()
    if component_name not in last_run or now - last_run[component_name] > COOLDOWN_SECONDS:
        last_run[component_name] = now
        return True
    return False


class ComponentChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        changed_path = Path(event.src_path)

        # Only trigger for files relevant to prop generation
        if changed_path.name not in ["example.json", "template.html"]:
            return

        # Resolve component folder relative to COMPONENTS_DIR
        try:
            relative_path = changed_path.relative_to(COMPONENTS_DIR)
            component_name = relative_path.parts[0]
        except ValueError:
            return  # File not inside a valid component

        if not should_run(component_name):
            print(f"[SKIP] Change throttled for: {component_name}")
            return

        print(f"[WATCH] Change detected in: {component_name}")

        try:
            subprocess.run(
                [sys.executable, "manage.py", "update_props", component_name],
                check=True
            )
            print(f"[OK] Updated props for {component_name}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to update props for {component_name}")
            print(e)


def main():
    print("[WATCH] Watching example.json and template.html in components... (Ctrl+C to stop)")
    event_handler = ComponentChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(COMPONENTS_DIR), recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[WATCH] Stopping watcher.")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
