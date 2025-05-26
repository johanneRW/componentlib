import time
import sys
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "componentlib" / "components"

# Cooldown-måler pr. komponent
last_run = {}

COOLDOWN_SECONDS = 2  # minimum tid mellem triggers pr. komponent


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

        if changed_path.name not in ["metadata.yaml", "component.py"]:
            return  # kun reagér på specifikke filer

        # Find nærmeste komponentmappe
        component_dir = changed_path.parent
        while component_dir.parent != COMPONENTS_DIR and component_dir != COMPONENTS_DIR:
            component_dir = component_dir.parent

        component_name = component_dir.name

        if not should_run(component_name):
            print(f"[SKIP] Change throttled for: {component_name}")
            return

        print(f"[WATCH] 🔁 Change detected in: {component_name}")

        try:
            subprocess.run(
                [sys.executable, "manage.py", "generate_component_model", component_name],
                check=True
            )
            print(f"[OK] Regenerated model for {component_name}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to generate model for {component_name}")
            print(e)


def main():
    print("[WATCH] Watching component metadata and logic... (Ctrl+C to stop)")
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
