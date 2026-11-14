
from backend.app.services.backup_service import create_backup


if __name__ == "__main__":
    try:
        backup_path = create_backup()
        print("Резервная копия создана успешно!")
        print(f"Файл: {backup_path}")

    except Exception as error:
        print("Не удалось создать резервную копию.")
        print(f"Причина: {error}")
