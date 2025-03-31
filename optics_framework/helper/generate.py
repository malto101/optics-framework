import os
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from optics_framework.common.runner.csv_reader import CSVDataReader
from optics_framework.common.logging_config import logger

# Type aliases for clarity
TestCases = Dict[str, List[str]]
Modules = Dict[str, List[Tuple[str, List[str]]]]
Elements = Dict[str, str]


class TestFrameworkGenerator(ABC):
    """Abstract base class for generating test framework code."""

    @abstractmethod
    def generate_header(self, yaml_path: str) -> str:
        pass

    @abstractmethod
    def generate_element_definitions(self, elements: Elements) -> str:
        pass

    @abstractmethod
    def generate_setup(self) -> str:
        pass

    @abstractmethod
    def generate_module_function(self, module_name: str, steps: List[Tuple[str, List[str]]], elements: Elements) -> str:
        pass

    @abstractmethod
    def generate_test_function(self, test_case_name: str, module_names: List[str]) -> str:
        pass


class PytestGenerator(TestFrameworkGenerator):
    """Concrete implementation for generating pytest-compatible test code."""

    def generate_header(self, yaml_path: str) -> str:
        # Use a relative path to config.yaml from the generated file's location
        return '\n'.join([
            "# Auto-generated by generate.py. Do not edit manually.",
            "import pytest",
            "from optics_framework import optics",
            "import os",
            "",
        ])

    def generate_element_definitions(self, elements: Elements) -> str:
        lines = ["# Define elements"]
        for name, value in elements.items():
            var_name = name.upper()
            lines.append(f"{var_name} = '{value}'")
        return '\n'.join(lines) + '\n'

    def generate_setup(self) -> str:
        return '\n'.join([
            "# Fixture for optics instance",
            "@pytest.fixture(scope='session')",
            "def optics_instance():",
            "    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml')",
            "    return optics.setup(yaml_path=config_path)",
            ""
        ])

    def generate_module_function(self, module_name: str, steps: List[Tuple[str, List[str]]], elements: Elements) -> str:
        func_name = '_'.join(module_name.lower().split())
        lines = [f"def {func_name}(optics_instance):"]
        for keyword, params in steps:
            method_name = '_'.join(keyword.lower().split())
            resolved_params = self._resolve_params(params, elements)
            param_str = ', '.join(resolved_params)
            lines.append(f"    optics_instance.{method_name}({param_str})")
        return '\n'.join(lines) + '\n'

    def generate_test_function(self, test_case_name: str, module_names: List[str]) -> str:
        func_name = f"test_{'_'.join(test_case_name.lower().split())}"
        lines = [f"def {func_name}(optics_instance):"]
        for module_name in module_names:
            module_func_name = '_'.join(module_name.lower().split())
            lines.append(f"    {module_func_name}(optics_instance)")
        return '\n'.join(lines) + '\n'

    def _resolve_params(self, params: List[str], elements: Elements) -> List[str]:
        resolved = []
        for param in params:
            if param.startswith('${') and param.endswith('}'):
                var_name = param[2:-1]
                if var_name not in elements:
                    raise ValueError(
                        f"Element '{var_name}' not found in elements.")
                resolved.append(var_name.upper())
            else:
                resolved.append(repr(param))
        return resolved


class FileWriter:
    """Handles writing generated code to a file."""

    def write(self, folder_path: str, filename: str, content: str) -> None:
        os.makedirs(folder_path, exist_ok=True)
        output_file = os.path.join(folder_path, filename)
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Generated file: {output_file}")


def find_csv_files(folder_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Search for CSV files in a folder and categorize them by reading their headers.

    Args:
        folder_path (str): Path to the folder containing CSV files.

    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: Paths to test cases, modules, and elements CSV files.
    """
    test_cases, modules, elements = None, None, None

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            try:
                df = pd.read_csv(file_path, nrows=1)
                headers = [h.strip() for h in df.columns]
            except Exception as e:
                logger.exception(f"Error reading {file_path}: {e}")
                continue

            if "test_case" in headers and "test_step" in headers:
                test_cases = file_path
            elif "module_name" in headers and "module_step" in headers:
                modules = file_path
            elif "Element_Name" in headers and "Element_ID" in headers:
                elements = file_path

    return test_cases, modules, elements


def generate_test_file(
    folder_path: str,
    output_filename: str = 'generated_test.py'
) -> None:
    """
    Generate a test file from CSV files in the specified folder.

    Args:
        folder_path (str): Path to the folder containing CSV files and config.yaml.
        data_reader (CSVDataReader): Reader for CSV data.
        generator (TestFrameworkGenerator): Generator for test framework code.
        writer (FileWriter): Writer for saving the generated file.
        output_filename (str): Name of the output file (default: 'test_optics.py').
    """
    test_cases_file: Optional[str]
    modules_file: Optional[str]
    elements_file: Optional[str]

    data_reader = CSVDataReader()
    test_generator = PytestGenerator()
    writer = FileWriter()

    test_cases_file, modules_file, elements_file = find_csv_files(folder_path)
    config_file = os.path.join(folder_path, 'config.yaml')

    # Validate files exist
    missing_files = []
    if not test_cases_file:
        missing_files.append(
            "test cases CSV (requires 'test_case' and 'test_step' headers)")
    if not modules_file:
        missing_files.append(
            "modules CSV (requires 'module_name' and 'module_step' headers)")
    if not os.path.exists(config_file):
        missing_files.append("config.yaml")

    if missing_files:
        print(f"Error: Missing required files: {', '.join(missing_files)}")
        return

    # Read data
    test_cases: TestCases = data_reader.read_test_cases(test_cases_file) if test_cases_file else {}
    modules: Modules = data_reader.read_modules(modules_file) if modules_file else {}
    elements: Elements = data_reader.read_elements(elements_file) if elements_file else {}

    # Generate code
    code_parts = [
        test_generator.generate_header(config_file),
        test_generator.generate_element_definitions(elements),
        test_generator.generate_setup(),
        "# Module functions\n"
    ]
    for module_name, steps in modules.items():
        code_parts.append(test_generator.generate_module_function(
            module_name, steps, elements))
    code_parts.append("# Test functions\n")
    for test_case_name, module_names in test_cases.items():
        code_parts.append(test_generator.generate_test_function(
            test_case_name, module_names))

    code = ''.join(code_parts)

    # Write to file
    generated_folder = os.path.join(folder_path, 'generated')
    writer.write(generated_folder, output_filename, code)
