import csv

class IRVElection:
    """
    WIP IRV
    Design decisions/known limitations:
        - Only supports one election

    Ballot format refrence:
        - CSV with each line a ballot, ranking candidates from left to right
        -Example:
            A,B,C
            C,B
    """

    # TODO list:
    #   - implement functions
    #   - determine if run should return to another helper or write itself

    def __init__(self, file):
        """
        Reads ballot format file into TODO

        Parameters
        ----------
        file : string
            Path to the file, which should be in ballot format
        """
        self.ballots = pd.read_csv(file, header=None, index_col=False)
        self.candidates = set()
        for col in self.ballots:
            self.candidates.update(self.ballots[col].unique())
        self.candidates.remove(np.nan)

    def run(self):
        """
        Runs the election

        Returns
        -------
        winner : string
            Winner of the election
        steps : np.array #TODO: figure out what data type!
            Array (matrix?) of election results from each step of the IRV process
        """
        raise NotImplementedError()

    def write_results(self, winner, steps, winner_file, steps_file):
        """
        Writes winner and steps to winner_file and steps_file

        Parameters
        ----------
        winner : string
            Winner of the election
        steps : TODO (see above)
            TODO
        winner_file : string
            File to write the winner to
        steps_file : string
            File to write the steps to
        """
        raise NotImplementedError()

    def run_and_write(self, winner_file="winner.txt", steps_file="steps.txt"):
        """
        Wrapper around run and write_results that runs and then writes results to
        winner.txt and steps.txt

        Parameters
        ----------
        winner_file : string, optional
            File to write the winner to. Default winner.txt
        steps_file : string, optional
            File to write the steps to. Default steps.txt
        """
        winner_data, steps_data = self.run()
        self.write_results(winner_data, steps_data, winner_data, winner_file)

