from typing import List, Optional
import pandas as pd


class Formatter:

    def format(self, df: pd.DataFrame) -> str:
        raise NotImplementedError

    def print(self, df):
        print(self.format(df, **kwargs))


class StringFormatter(Formatter):

    def format(self, df: pd.DataFrame) -> str:
        result = []
        for house, g in df.groupby(level=0):
            result.append(f"------------------------------- {house}-------------------------------")
            result.append(g.to_string(header=False, index=False))

        return "\n".join(result)


class LatexFormatter(Formatter):

    def __init__(self):
        self._buf: List[str] = []

    def reset(self):
        self._buf = []

    def __add__(self, other: str) -> "LatexFormatter":
        self._buf.append(other)
        return self

    def format(self, df: pd.DataFrame, alignment: Optional[str] = None) -> str:
        self.reset()
        item_idx = df.index.levels[1]
        columns = [item_idx.name] + df.columns.tolist()
        column_count = len(columns)

        if alignment is None:
            alignment = "|" + "c|" * column_count

        # Header
        self += r"\begin{tabular}{" + alignment + "}"
        self += r"\hline"
        self += r"   &  ".join(map(self._bold, columns)) + r" \\ \hline"

        # Houses
        for house, g in df.groupby(level=0):
            self += r"\multicolumn{" + str(column_count) + r"}{|c|}{\textbf{" + house + r"}} \\ \hline"
            # Items
            for idx, values in g.iterrows():
                self += f"{idx[1]}   &    " + "   &   ".join(map(self._escape, map(str, values))) + r" \\ \hline"

        # End
        self += r"\end{tabular}"

        return "\n".join(self._buf)

    def _bold(self, s: str) -> str:
        """
        Add latex textbf to given string
        :param s: String
        :return:
        """
        return r"\textbf{" + s + "}"

    def _escape(self, s: str) -> str:
        """
        Escape given strings for latex
        :param s: String
        :return:
        """
        if s == "{}":
            return s

        return (
            s.replace("\\", "\\textbackslash ")
            .replace("~", "\\textasciitilde ")
            .replace("^", "\\textasciicircum ")
            .replace("_", "\\_")
            .replace("%", "\\%")
            .replace("$", "\\$")
            .replace("#", "\\#")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace("&", "\\&")
        )
