import os
import shutil
import tempfile
import unittest

from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.run_python_file import run_python_file
from functions.write_file import write_file


class TestGetFileContent(unittest.TestCase):
    def test_get_file_content(self):
        result = get_file_content("calculator", "main.py")
        self.assertIsInstance(result, str)

        result = get_file_content("calculator", "pkg/calculator.py")
        self.assertIsInstance(result, str)

        result = get_file_content("calculator", "/bin/cat")
        self.assertIsInstance(result, str)


class TestGetFilesInfo(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create test files
        os.makedirs(os.path.join(self.test_dir, "subdir"))
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f:
            f.write("test content")
        with open(os.path.join(self.test_dir, "subdir", "file2.txt"), "w") as f:
            f.write("test content 2")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_files_info_root(self):
        result = get_files_info(self.test_dir)
        self.assertIsInstance(result, str)
        self.assertIn("file1.txt", result)
        self.assertIn("subdir", result)
        self.assertIn("is_dir=True", result)
        self.assertIn("is_dir=False", result)

    def test_get_files_info_subdirectory(self):
        result = get_files_info(self.test_dir, "subdir")
        self.assertIsInstance(result, str)
        self.assertIn("file2.txt", result)
        self.assertIn("is_dir=False", result)

    def test_get_files_info_nonexistent_directory(self):
        result = get_files_info(self.test_dir, "nonexistent")
        self.assertIn("Error:", result)
        self.assertIn("not a directory", result)

    def test_get_files_info_outside_working_directory(self):
        result = get_files_info(self.test_dir, "/tmp")
        self.assertIn("Error:", result)
        self.assertIn("outside the permitted working directory", result)


class TestWriteFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_write_file_success(self):
        content = "Hello, World!"
        result = write_file(self.test_dir, "test.txt", content)
        self.assertIn("Successfully wrote", result)

        # Verify file was created with correct content
        with open(os.path.join(self.test_dir, "test.txt"), "r") as f:
            self.assertEqual(f.read(), content)

    def test_write_file_create_directory(self):
        content = "Test content"
        result = write_file(self.test_dir, "new_dir/test.txt", content)
        self.assertIn("Successfully wrote", result)

        # Verify directory was created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "new_dir")))

        # Verify file was created with correct content
        with open(os.path.join(self.test_dir, "new_dir", "test.txt"), "r") as f:
            self.assertEqual(f.read(), content)

    def test_write_file_overwrite(self):
        # Create initial file
        initial_content = "Initial content"
        write_file(self.test_dir, "test.txt", initial_content)

        # Overwrite with new content
        new_content = "New content"
        result = write_file(self.test_dir, "test.txt", new_content)
        self.assertIn("Successfully wrote", result)

        # Verify file was overwritten
        with open(os.path.join(self.test_dir, "test.txt"), "r") as f:
            self.assertEqual(f.read(), new_content)

    def test_write_file_outside_working_directory(self):
        content = "Test content"
        result = write_file(self.test_dir, "/tmp/test.txt", content)
        self.assertIn("Error:", result)
        self.assertIn("outside the permitted working directory", result)

    def test_write_file_empty_content(self):
        result = write_file(self.test_dir, "empty.txt", "")
        self.assertIn("Successfully wrote", result)

        # Verify empty file was created
        with open(os.path.join(self.test_dir, "empty.txt"), "r") as f:
            self.assertEqual(f.read(), "")

    def test_write_file_unicode_content(self):
        content = "Hello, 世界! 🌍"
        result = write_file(self.test_dir, "unicode.txt", content)
        self.assertIn("Successfully wrote", result)

        # Verify unicode content was written correctly
        with open(
            os.path.join(self.test_dir, "unicode.txt"), "r", encoding="utf-8"
        ) as f:
            self.assertEqual(f.read(), content)

    def test_write_file_no_file_path(self):
        content = "Test content"
        result = write_file(self.test_dir, "", content)
        self.assertIn("Error", result)

    def test_write_file_calculator_cases(self):
        # Test case 1: Write to calculator directory
        result = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
        print(f"Test 1 result: {result}")
        self.assertIsInstance(result, str)

        # Test case 2: Write to subdirectory in calculator
        result = write_file(
            "calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"
        )
        print(f"Test 2 result: {result}")
        self.assertIsInstance(result, str)

        # Test case 3: Attempt to write outside working directory (should fail)
        result = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
        print(f"Test 3 result: {result}")
        self.assertIn("Error:", result)
        self.assertIn("outside the permitted working directory", result)


class TestRunPythonFile(unittest.TestCase):
    def test_calculator_usage_instructions(self):
        result = run_python_file("calculator", "main.py")
        self.assertIn("usage:", result)

    def test_calculator_run_with_args(self):
        result = run_python_file("calculator", "main.py", ["3 + 5"])
        print(result)  # This will print the result of running the calculator with args
        self.assertIsInstance(result, str)

    def test_calculator_file_not_found(self):
        result = run_python_file("calculator", "tests.py")
        self.assertIn("Error:", result)
        self.assertIn('File "tests.py" not found.', result)

    def test_calculator_path_outside_working_directory(self):
        result = run_python_file("calculator", "../main.py")
        self.assertIn("Error:", result)
        self.assertIn("Cannot execute", result)

    def test_calculator_nonexistent_file(self):
        result = run_python_file("calculator", "nonexistent.py")
        self.assertIn("Error:", result)
        self.assertIn('File "nonexistent.py" not found.', result)

    def test_calculator_invalid_file_type(self):
        result = run_python_file("calculator", "lorem.txt")
        self.assertIn("Error:", result)
        self.assertIn("is not a Python file.", result)


if __name__ == "__main__":
    _ = unittest.main()
