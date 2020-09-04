from gitstats.dataframe import aggregate_generator
import pandas as pd


class TestDataFrame:

    def _generator(self, dataframes):
        for d in dataframes:
            yield d

    def test_no_dataframes(self):
        dataframes = []
        aggregated = aggregate_generator(self._generator(dataframes))
        assert len(aggregated) == 0

    def test_one_dataframe(self):
        data = {'col_1': [3, 2, 1, 0], 'col_2': ['a', 'b', 'c', 'd']}
        df = pd.DataFrame.from_dict(data)
        aggregated = aggregate_generator(self._generator([df]))
        assert len(aggregated) == 4

    def test_two_dataframes(self):
        data = {'col_1': [3, 2, 1, 0], 'col_2': ['a', 'b', 'c', 'd']}
        df = pd.DataFrame.from_dict(data)

        data2 = {'col_1': [4, 5, 6, 7], 'col_2': ['e', 'f', 'g', 'h']}
        df2 = pd.DataFrame.from_dict(data2)

        aggregated = aggregate_generator(self._generator([df, df2]))
        assert len(aggregated) == 8
