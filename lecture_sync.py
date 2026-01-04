"""
 Lecture Sync System
"""
# PLEASE DO NOT MODIFY THIS FOLDER
import os
import sys
import shutil
import json
import urllib.request
import zipfile
from pathlib import Path
from datetime import datetime


class SmartLectureSync:
    def __init__(self):
        # ============ 【DO NOT MODIFY】  ============
        self.github_username = "Boyan419329"  # PLEASE DO NOT MODIFY!
        # =======================================================================
        self.repo_name = "course-lectures"
        self.repo_zip_url = f"https://github.com/{self.github_username}/{self.repo_name}/archive/refs/heads/main.zip"

        # Automatically locate the student's 'toolkit' directory
        self.toolkit_root = Path(__file__).parent.absolute()
        self.lectures_dir = self.toolkit_root / "lectures"
        self.backup_dir = self.toolkit_root / "_lecture_backups"
        self.config_file = self.toolkit_root / ".lecture_sync_config.json"

        print("=" * 60)
        print("SMART LECTURE SYNC SYSTEM v2.0")
        print("=" * 60)
        print(f"Tool Path: {self.toolkit_root}")
        print(f"Lectures will be saved to: {self.lectures_dir}")

    def _load_config(self):
        """Load the local configuration file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # If config file is corrupted, return default
                pass
        # Default configuration
        return {"downloaded_weeks": [], "last_sync": None}

    def _save_config(self, config):
        """Save the local configuration file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _get_remote_weeks(self):
        """Fetch the list of all available week folders from the GitHub repository."""
        print("[INFO] Connecting to GitHub repository...")
        try:
            # Download the repository as a ZIP file to inspect its contents
            temp_zip, _ = urllib.request.urlretrieve(self.repo_zip_url)

            week_folders = set()
            with zipfile.ZipFile(temp_zip) as zipf:
                for file_info in zipf.infolist():
                    # Example path in zip: "course-lectures-main/week01/lecture.py"
                    parts = file_info.filename.split('/')
                    if len(parts) >= 2 and parts[1].startswith('week'):
                        week_folders.add(parts[1])

            os.unlink(temp_zip)  # Delete the temporary ZIP file
            return sorted(list(week_folders))

        except urllib.error.URLError as e:
            print(f"[ERROR] Network issue. Please check your internet connection.")
            return []
        except Exception as e:
            print(f"[ERROR] Could not fetch data from repository. Details: {e}")
            return []

    def smart_sync(self):
        """
        INTELLIGENT SYNC - Core Function
        Downloads ONLY new week folders that the student doesn't have locally.
        Preserves all existing student work.
        """
        print("\n" + "=" * 60)
        print("INTELLIGENT SYNC MODE")
        print("=" * 60)

        # Step 1: Get week lists
        print("[INFO] Scanning remote repository...")
        remote_weeks = self._get_remote_weeks()

        if not remote_weeks:
            print("[WARNING] No 'week' folders found in the remote repository.")
            print("          Please ensure the instructor has uploaded materials.")
            return

        config = self._load_config()
        local_weeks = config.get("downloaded_weeks", [])

        # Step 2: Calculate which weeks are new
        new_weeks = [week for week in remote_weeks if week not in local_weeks]

        if not new_weeks:
            print("[SUCCESS] Your local materials are already up-to-date!")
            print(f"          You have {len(local_weeks)} week(s) of materials.")
            return

        # Step 3: Display sync plan
        print(f"\n[PLAN] Found {len(new_weeks)} new week(s) available:")
        for i, week in enumerate(new_weeks, 1):
            print(f"       {i:2d}. {week}")

        if local_weeks:
            print(f"\n[INFO] Your local materials ({len(local_weeks)} week(s)) will remain UNTOUCHED.")
            print("       Any exercises or modifications you've made are SAFE.")

        # Step 4: Confirm with user
        print("\n" + "-" * 40)
        choice = input("Proceed with download? [Y/n]: ").strip().upper()

        if choice not in ('', 'Y', 'YES'):
            print("[INFO] Sync cancelled by user.")
            return

        # Step 5: Download new weeks
        print("\n[INFO] Starting download...")
        self.lectures_dir.mkdir(exist_ok=True)
        success_count = 0

        for week in new_weeks:
            print(f"\n  Downloading {week}...", end=' ', flush=True)
            try:
                # Download the repository ZIP
                temp_zip, _ = urllib.request.urlretrieve(self.repo_zip_url)

                # Extract only the specific week folder
                with zipfile.ZipFile(temp_zip) as zipf:
                    # Find all files belonging to this week
                    for file_info in zipf.infolist():
                        if file_info.filename.startswith(f"{self.repo_name}-main/{week}/"):
                            # Remove the leading path prefix
                            rel_path = file_info.filename[len(f"{self.repo_name}-main/{week}/"):]
                            if rel_path:  # Skip the directory entry itself
                                target_path = self.lectures_dir / week / rel_path
                                target_path.parent.mkdir(parents=True, exist_ok=True)

                                # Extract the file
                                with zipf.open(file_info) as source, open(target_path, 'wb') as target:
                                    shutil.copyfileobj(source, target)

                os.unlink(temp_zip)
                print("✅ SUCCESS")
                success_count += 1

            except Exception as e:
                print(f"❌ FAILED: {str(e)[:50]}...")

        # Step 6: Update local configuration
        if success_count > 0:
            config["downloaded_weeks"] = sorted(list(set(local_weeks + new_weeks)))
            config["last_sync"] = datetime.now().isoformat()
            self._save_config(config)

            print("\n" + "=" * 60)
            print("[SUCCESS] SYNC COMPLETE!")
            print(f"         Downloaded: {success_count} new week(s)")
            print(f"         Total weeks in local library: {len(config['downloaded_weeks'])}")
            print(f"         Location: {self.lectures_dir}")
            print("=" * 60)
        else:
            print("\n[ERROR] All downloads failed. Please check your network connection.")

    def view_library(self):
        """Display the student's local lecture library."""
        config = self._load_config()
        local_weeks = config.get("downloaded_weeks", [])

        if not local_weeks:
            print("\n[INFO] Your lecture library is empty.")
            print("       Run 'Intelligent Sync' to download materials.")
            return

        print("\n" + "=" * 60)
        print("YOUR LECTURE LIBRARY")
        print("=" * 60)
        print(f"Total Weeks: {len(local_weeks)}")

        for week in sorted(local_weeks):
            week_path = self.lectures_dir / week
            if week_path.exists():
                # Count files
                all_files = list(week_path.rglob("*.*"))
                py_files = [f for f in all_files if f.suffix.lower() == '.py']

                # Get last modified time
                if all_files:
                    latest = max(all_files, key=lambda f: f.stat().st_mtime)
                    mtime = datetime.fromtimestamp(latest.stat().st_mtime)
                    time_str = mtime.strftime("%Y-%m-%d %H:%M")
                else:
                    time_str = "N/A"

                print(f"\n  📁 {week}")
                print(f"     Files: {len(all_files)} total ({len(py_files)} Python)")
                print(f"     Path: {week_path}")
                print(f"     Updated: {time_str}")
            else:
                print(f"\n  ⚠️  {week} (Folder missing from disk)")

    def backup_library(self):
        """Create a backup of the entire lecture library."""
        local_weeks = self._load_config().get("downloaded_weeks", [])

        if not local_weeks:
            print("\n[INFO] Nothing to backup. Library is empty.")
            return

        self.backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"lecture_backup_{timestamp}"

        print(f"\n[INFO] Creating backup at: {backup_path}")

        try:
            for week in local_weeks:
                src = self.lectures_dir / week
                dst = backup_path / week
                if src.exists():
                    shutil.copytree(src, dst)
                    print(f"  ✅ Backed up: {week}")

            print(f"\n[SUCCESS] Backup complete!")
            print(f"          Location: {backup_path}")

        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")

    def run(self):
        """Main program loop with English menu."""
        while True:
            print("\n" + "=" * 60)
            print("MAIN MENU")
            print("=" * 60)
            print("1. 🔄 Intelligent Sync (Get new materials, keep my work)")
            print("2. 📂 View My Lecture Library")
            print("3. 💾 Backup My Library (Safe-guard all my exercises)")
            print("4. ℹ️  System Info")
            print("5. 🚪 Exit")
            print("=" * 60)

            choice = input("\nSelect an option [1-5]: ").strip()

            if choice == '1':
                self.smart_sync()
            elif choice == '2':
                self.view_library()
            elif choice == '3':
                self.backup_library()
            elif choice == '4':
                self.system_info()
            elif choice == '5':
                print("\n[INFO] Thank you for using Smart Lecture Sync!")
                print("       Goodbye!")
                break
            else:
                print("\n[ERROR] Invalid selection. Please choose 1-5.")

            input("\nPress Enter to continue...")

    def system_info(self):
        """Display system information and configuration."""
        config = self._load_config()

        print("\n" + "=" * 60)
        print("SYSTEM INFORMATION")
        print("=" * 60)
        print(f"Repository URL: {self.repo_zip_url}")
        print(f"Local Config: {self.config_file}")
        print(f"Lecture Directory: {self.lectures_dir}")
        print(f"Backup Directory: {self.backup_dir}")

        if config.get("last_sync"):
            last_sync = datetime.fromisoformat(config["last_sync"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"Last Successful Sync: {last_sync}")

        print(f"\nConfiguration:")
        print(f"  Downloaded Weeks: {len(config.get('downloaded_weeks', []))}")
        if config.get("downloaded_weeks"):
            print(f"  Weeks List: {', '.join(sorted(config['downloaded_weeks']))}")


# ==================== PROGRAM ENTRY POINT ====================
if __name__ == "__main__":
    print("Initializing Smart Lecture Sync System...")

    # Quick Python version check
    if sys.version_info < (3, 7):
        print("[ERROR] Python 3.7 or higher is required.")
        sys.exit(1)

    try:
        sync_tool = SmartLectureSync()
        sync_tool.run()
    except KeyboardInterrupt:
        print("\n\n[INFO] Program interrupted by user.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] The program encountered an unexpected issue:")
        print(f"                 {e}")
        print("\nPlease ensure:")
        print("  1. You have an active internet connection")
        print(f"  2. The repository exists at: {SmartLectureSync().repo_zip_url}")
        print("  3. You have write permissions in the toolkit directory")
        input("\nPress Enter to exit...")