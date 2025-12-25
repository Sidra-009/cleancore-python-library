from datetime import datetime
from cleancore.audit import AuditEvent
from cleancore.transform import dataframe_hash


class CleanEngine:
    def __init__(self, df, id_column, age_column="age", salary_column="price"):
        self.df = df
        self.id_column = id_column
        self.age_column = age_column
        self.salary_column = salary_column
        self.audit_log = []
        self.audit_id = "AUD20241219001"

    def run(self):
        self._impute_missing_age()
        self._detect_constant_salary()
        return self.df, self.audit_log

    def _impute_missing_age(self):
        col = self.age_column

        if col not in self.df.columns:
            return

        missing_mask = self.df[col].isna()
        if missing_mask.sum() == 0:
            return

        before_hash = dataframe_hash(self.df)
        median_value = self.df[col].median()

        affected_rows = []
        for idx in self.df[missing_mask].index:
            affected_rows.append({
                "row_index": int(idx),
                "record_id": self.df.loc[idx, self.id_column],
                "before": None,
                "after": median_value
            })

        self.df.loc[missing_mask, col] = median_value
        after_hash = dataframe_hash(self.df)

        self.audit_log.append(
            AuditEvent(
                audit_id=self.audit_id,
                timestamp=datetime.utcnow().isoformat(),
                transformation="Missing values imputation",
                problem=f"{col} has missing values",
                solution=f"Filled with median ({median_value})",
                rule_id="GDPR_COMPLIANT_IMPUTATION_v2",
                affected_rows=affected_rows,
                before_hash=before_hash,
                after_hash=after_hash,
                status="AUTO_FIXED"
            )
        )

    def _detect_constant_salary(self):
        col = self.salary_column

        if col not in self.df.columns:
            return

        if self.df[col].nunique() != 1:
            return

        self.audit_log.append(
            AuditEvent(
                audit_id=self.audit_id,
                timestamp=datetime.utcnow().isoformat(),
                transformation="Constant column detection",
                problem=f"{col} has zero variance",
                solution="Flagged for manual review",
                rule_id="FINANCE_RULE_001",
                affected_rows=[],
                before_hash="",
                after_hash="",
                status="PENDING_REVIEW"
            )
        )
