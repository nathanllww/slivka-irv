import os
import pytest
from . import TEST_CASE_INVALID, WCTestCase


@pytest.fixture()
def duplicate_question_test_case() -> WCTestCase:
    return WCTestCase(os.path.join(TEST_CASE_INVALID, "duplicate_questions.csv"))
