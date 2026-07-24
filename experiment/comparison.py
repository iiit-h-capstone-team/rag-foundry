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
            if not report.sections:
                continue
            summary_df = report.sections[0].summary
            row = {'config_name': report.config_name}
            for _, m in summary_df.iterrows():
                metric = m.get('metric', '')
                # Handle both column naming conventions
                mean_val = m.get('mean_score', m.get('mean', None))
                mae_val = m.get('mean_abs_error', None)
                if mae_val is None and 'deviation' in m:
                    mae_val = abs(m['deviation'])
                if mean_val is not None:
                    row[f"{metric}__mean"] = round(mean_val, 4)
                if mae_val is not None:
                    row[f"{metric}__mae"] = round(mae_val, 4)
            rows.append(row)
        return pd.DataFrame(rows)

    def save_csv(self, path):
        self.to_dataframe().to_csv(
            path,
            index=False,
        )