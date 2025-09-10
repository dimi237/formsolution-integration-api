import subprocess

def run_download_script(item_id: str):
    """
    Exécute le script download_documents.py avec l'item_id.
    """
    try:
        subprocess.run(
            ["python3", "app/scripts/download_documents.py", str(item_id)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Échec du script pour item_id={item_id}: {e}")
