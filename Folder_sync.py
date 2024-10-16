import os
import time
import shutil
import argparse
import logging

# Function to configure logging to both file and console
def configure_logging(log_file):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ])

# Function to synchronize the source folder to the replica folder
def sync_folders(source, replica):
    # Ensure the replica folder exists
    if not os.path.exists(replica):
        os.makedirs(replica)
        logging.info(f"Created replica folder: {replica}")

    # Copy files and directories from source to replica
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_path)

        for dir_name in dirs:
            replica_dir = os.path.join(replica_root, dir_name)
            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)
                logging.info(f"Created folder: {replica_dir}")

        for file_name in files:
            source_file = os.path.join(root, file_name)
            replica_file = os.path.join(replica_root, file_name)

            # Copy file if it doesn't exist in replica or if it's modified (based on last modified time)
            if not os.path.exists(replica_file) or os.path.getmtime(source_file) > os.path.getmtime(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Copied file: {source_file} to {replica_file}")

    # Remove files and directories from replica that don't exist in source
    for root, dirs, files in os.walk(replica):
        relative_path = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_path)

        for dir_name in dirs:
            source_dir = os.path.join(source_root, dir_name)
            replica_dir = os.path.join(root, dir_name)
            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                logging.info(f"Removed folder: {replica_dir}")

        for file_name in files:
            source_file = os.path.join(source_root, file_name)
            replica_file = os.path.join(root, file_name)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed file: {replica_file}")

# Main function to handle command-line arguments and initiate synchronization
def main():
    parser = argparse.ArgumentParser(description="Folder synchronization script")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Log file path")

    args = parser.parse_args()

    configure_logging(args.log_file)

    source_folder = args.source
    replica_folder = args.replica
    interval = args.interval

    if not os.path.exists(source_folder):
        logging.error(f"Source folder '{source_folder}' does not exist.")
        return

    logging.info(f"Starting folder synchronization every {interval} seconds.")
    try:
        while True:
            sync_folders(source_folder, replica_folder)
            logging.info(f"Synchronization complete. Next sync in {interval} seconds.")
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Synchronization stopped by user.")

if __name__ == "__main__":
    main()