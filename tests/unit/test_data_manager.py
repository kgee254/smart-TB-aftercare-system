import json

from storage.data_manager import DataManager


def test_data_manager_can_be_created(tmp_path):
    manager = DataManager(tmp_path)

    assert manager.data_directory == tmp_path


def test_data_manager_can_save_data(tmp_path):
    manager = DataManager(tmp_path)

    data = [
        {
            "patient_id": 1,
            "name": "John Kamau"
        }
    ]

    manager.save_data("patients.json", data)

    file_path = tmp_path / "patients.json"

    assert file_path.exists()


def test_data_manager_can_load_data(tmp_path):
    manager = DataManager(tmp_path)

    data = [
        {
            "patient_id": 1,
            "name": "John Kamau"
        }
    ]

    file_path = tmp_path / "patients.json"

    with open(file_path, "w") as file:
        json.dump(data, file)

    loaded_data = manager.load_data("patients.json")

    assert loaded_data == data


def test_saved_data_can_be_loaded_again(tmp_path):
    manager = DataManager(tmp_path)

    data = [
        {
            "patient_id": 1,
            "name": "John Kamau"
        },
        {
            "patient_id": 2,
            "name": "Mary Njeri"
        }
    ]

    manager.save_data("patients.json", data)

    loaded_data = manager.load_data("patients.json")

    assert loaded_data == data


def test_empty_json_file_returns_empty_list(tmp_path):
    manager = DataManager(tmp_path)

    file_path = tmp_path / "patients.json"

    with open(file_path, "w") as file:
        json.dump([], file)

    loaded_data = manager.load_data("patients.json")

    assert loaded_data == []