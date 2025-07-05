import os
import shutil


def check_pycache(root_dir):
    pycache_paths = []

    for root, dirs, _ in os.walk(root_dir):
        if "venv" in dirs:
            dirs.remove("venv")
        for d in dirs:
            if d == "__pycache__":
                pycache_paths.append(os.path.join(root, d))

    return pycache_paths


def delete_pycache(paths):
    deleted_paths = []
    log_entries = []

    for full_path in paths:
        try:
            shutil.rmtree(full_path)
            deleted_paths.append(full_path)
            msg = f"Dihapus: {full_path}"
            print(msg)
            log_entries.append(msg)
        except Exception as e:
            msg = f"⚠️ Gagal menghapus {full_path}: {e}"
            print(msg)
            log_entries.append(msg)

    if not deleted_paths:
        print("Tidak ada folder __pycache__ yang berhasil dihapus.")

    return deleted_paths


if __name__ == "__main__":
    root_dir = os.getcwd()

    if root_dir in ["/", "/home", "/root"]:
        print(f"Root direktori terlalu umum: {root_dir}. Dibatalkan untuk keamanan.")
        exit(1)

    pycache_list = check_pycache(root_dir)
    if not pycache_list:
        print("Tidak ada folder __pycache__ yang ditemukan untuk dihapus.")
        exit(0)

    print("Folder __pycache__ yang ditemukan dan akan dihapus:")
    for path in pycache_list:
        print(f"  - {path}")

    is_production = os.getenv("APP_ENV") == "production"
    if is_production:
        print("MODE PRODUKSI TERDETEKSI")
        confirm = (
            input(
                "Apakah Anda yakin ingin menghapus seluruh folder __pycache__ di direktori ini dan subdirektorinya? (yes/no): "
            )
            .strip()
            .lower()
        )
        if confirm != "yes":
            print("Operasi dibatalkan.")
            exit(0)
    delete_pycache(pycache_list)
