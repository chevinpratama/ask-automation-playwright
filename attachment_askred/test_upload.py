from pathlib import Path

file_path = Path(__file__).parent.parent / "attachment" / "ktp.jpg"

page.set_input_files('input[type="file"]', str(file_path))