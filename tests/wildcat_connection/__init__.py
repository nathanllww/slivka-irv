import os
from irv.ballots import RankedChoiceBallots

TEST_CASE_FOLDER_WC = str(os.environ.get(
    "TEST_CASE_FOLDER_WC",
    os.path.join(os.path.dirname(__file__), "test_cases")))
TEST_BALLOT_FORMAT_FOLDER = str(os.environ.get(
    "TEST_BALLOT_FORMAT_FOLDER",
    os.path.join(os.path.dirname(__file__), "test_ballot_format")))
TEST_SPOILT_BALLOT_FOLDER = str(os.environ.get(
    "TEST_SPOILT_BALLOT_FOLDER",
    os.path.join(os.path.dirname(__file__), "test_spoilt")))
TEST_CASE_INVALID = str(os.environ.get(
    "TEST_CASE_INVALID",
    os.path.join(os.path.dirname(__file__), "test_invalid")))


class WCTestCase:
    """Test Case containing data for WC test cases"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.__basename = os.path.basename(filepath).split('.')[0]

    @property
    def ballot_format(self) -> dict[str, RankedChoiceBallots]:
        """Gets formatted ballot answers"""
        folder = os.path.join(TEST_BALLOT_FORMAT_FOLDER, self.__basename)
        ballot_formats = {}
        for path in os.listdir(folder):
            question = os.path.basename(path).split('.')[0]
            with open(os.path.join(folder, path)) as file:
                string_ballot_format = file.read()
                # This converts the old string format into the new RankedChoiceBallots format
                ballot_formats[question] = RankedChoiceBallots([
                    row.split(",") for row in string_ballot_format.split("\n")
                    if not row.strip().startswith("#")
                ])
        return ballot_formats

    @property
    def spoilt_ballots(self) -> dict[str, list[int]]:
        """Gets spoilt ballot answers"""
        folder = os.path.join(TEST_SPOILT_BALLOT_FOLDER, self.__basename)
        spoilt_ballots = {}
        for path in os.listdir(folder):
            question = os.path.basename(path).split('.')[0]
            with open(os.path.join(folder, path)) as file:
                spoilt_ballots[question] = [
                    int(line) for line in file.readlines()
                ]

        return spoilt_ballots


def get_test_cases() -> list[WCTestCase]:
    return [
        WCTestCase(f) for f in
        [os.path.join(TEST_CASE_FOLDER_WC, p) for p in os.listdir(TEST_CASE_FOLDER_WC)]
    ]


def invalid_ranks_test_cases() -> list[WCTestCase]:
    return [
        WCTestCase(f) for f in
        [
            os.path.join(TEST_CASE_INVALID, p) for p in
            ["invalid_ranks.csv", "invalid_ranks2.csv"]
        ]
    ]
