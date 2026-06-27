from pathlib import Path

import pandas as pd

from reporting.base import Report



class ComparisonReport:
    def __init__(self, reports):
        self.reports = reports
    
    @property
    def df(self):
        """Convenience property to access the comparison DataFrame."""
        return self.to_dataframe()
    
    @classmethod
    def from_directory(cls, report_dir: str | Path):
        reports = []
        for path in Path(report_dir).glob("*.json"):
            reports.append(
                Report.load_json(path)
            )
        return cls(reports)

    def to_dataframe(self):
        rows = []
        for report in self.reports:
            # Get summary from the first section's summary DataFrame
            # For single-section reports (typical case), this works correctly
            if report.sections:
                summary_row = {
                    'config_name': report.config_name,
                    **report.sections[0].summary.iloc[0].to_dict()
                }
                rows.append(summary_row)
        return pd.DataFrame(rows)

    def save_csv(self, path):
        self.to_dataframe().to_csv(
            path,
            index=False,
        )