import pytest
from mkr import filter_lines, process_file


@pytest.fixture
def sample_lines():
    return [
        "Двері до першої кімнати відчинені\n",
        "Для цих дверей потрібен КЛЮЧ\n",
        "Тут дверей немає\n",
        "Тут також потрібен КЛЮЧ\n"
    ]


@pytest.fixture
def sample_file(tmp_path):
    """Фікстура для створення тимчасового вхідного файлу."""
    file_path = tmp_path / "test_input.txt"
    file_path.write_text("apple\nbanana\napple pie\norange", encoding="utf-8")
    return file_path


@pytest.mark.parametrize("keyword, expected_count", [
    ("КЛЮЧ", 2),
    ("немає", 1),
    ("Америка", 0)
])
def test_filter_lines(sample_lines, keyword, expected_count):
    """Тестування функції фільтрації з параметризацією."""
    result = filter_lines(sample_lines, keyword)
    assert len(result) == expected_count


def test_process_file(sample_file, tmp_path):
    """Тестування зчитування та запису файлу."""
    output_path = tmp_path / "filtered.txt"

    process_file(str(sample_file), str(output_path), "apple")

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")

    assert "apple" in content
    assert "apple pie" in content
    assert "banana" not in content