from pathlib import Path
from typing import Union
import subprocess
import os

class PyToTxtConverter:

    def __init__(self):
        pass

    @staticmethod
    def convert_py_to_txt(py_file_path: Union[str, Path], txt_file_path: Union[str, Path]) -> None:
        """
        Converts a Python (.py) file to a text (.txt) file by copying its content.

        Args:
            py_file_path (Union[str, Path]): The path to the source Python file.
            txt_file_path (Union[str, Path]): The path to the destination text file.

        Raises:
            ValueError: If the provided Python file path is invalid or not a .py file.

        Example:
            >>> PyToTxtConverter.convert_py_to_txt('script.py', 'script.txt')
            >>> # This will create 'script.txt' with the same content as 'script.py'
        """

        py_file_path = Path(py_file_path)
        txt_file_path = Path(txt_file_path)

        if not py_file_path.is_file() or py_file_path.suffix != '.py':
            raise ValueError("The provided Python file path is invalid or not a .py file.")
        
        with py_file_path.open('r', encoding='utf-8') as py_file:
            code_content = py_file.read()

        with txt_file_path.open('w', encoding='utf-8') as txt_file:
            txt_file.write(code_content)

        print(f"Converted {py_file_path} to {txt_file_path}.")

    
    def convert_py_to_txt_by_dir(self, target_dir: Union[str, Path], txt_dir: Union[str, Path]) -> None:
        """
        Converts all Python (.py) files in the specified directory to text (.txt) files.

        Args:
            target_dir (Union[str, Path]): The path to the target directory containing Python files.
            txt_dir (Union[str, Path]): The path to the directory where text files will be saved.
        
        Raises:
            ValueError: If the provided target directory path is invalid or not a directory.

        Example:
            >>> converter = PyToTxtConverter()
            >>> converter.convert_py_to_txt_by_dir('/path/to/directory')
            >>> # This will convert all .py files in the specified directory to .txt files
        """

        target_dir = Path(target_dir)
        txt_dir = Path(txt_dir)

        os.makedirs(txt_dir, exist_ok=True)

        if not target_dir.is_dir():
            raise ValueError("The provided target directory path is invalid or not a directory.")

        for py_file in target_dir.glob('*.py'):
            txt_file = Path(txt_dir) / py_file.with_suffix('.txt').name
            self.convert_py_to_txt(py_file, txt_file)

if __name__ == "__main__":
    print(f"Running Dir : {os.getcwd()}")
    target_directory = input("Enter the target directory path containing .py files: ")
    txt_directory = input("Enter the directory path to save .txt files: ")
    converter = PyToTxtConverter()
    converter.convert_py_to_txt_by_dir(target_directory, txt_directory)
    print("Conversion completed.")
    subprocess.run("pause", shell=True)