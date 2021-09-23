import os
from irv.constants import UNBREAKABLE_TIE_WINNER

TEST_CASE_FOLDER_IRV = str(os.environ.get("TEST_CASE_FOLDER_IRV", "test_cases"))


def real_winner(test_file: str) -> str:
    with open(test_file) as f:
        return f.readline().strip().split(':')[1]


def get_test_case_filepaths() -> list[str]:
    """Gets list of filepaths in `tests/TEST_CASE_FOLDER`"""
    abs_filepath = os.path.join(os.path.dirname(__file__), TEST_CASE_FOLDER_IRV)
    return [
        os.path.join(abs_filepath, f) for f in os.listdir(abs_filepath)
    ]


def non_tie_test_cases() -> list[str]:
    """Gets filepaths for non tie test cases"""
    return [test_file for test_file in get_test_case_filepaths()
            if real_winner(test_file) != UNBREAKABLE_TIE_WINNER]


def tie_test_cases() -> list[str]:
    """Gets filepaths for test cases with ties"""
    return [test_file for test_file in get_test_case_filepaths()
            if real_winner(test_file) == "No Confidence (unbreakable tie)"]
