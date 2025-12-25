# engine.py
from cleancore.audit import AuditEvent

class CleanEngine:
    def __init__(self, df=None, data=None):
        if df is None and data is None:
            raise ValueError("You must provide data using df or data")

        self.data = df if df is not None else data
        self.audit_log = []

    def run(self):
        event = AuditEvent("No transformations applied.")
        self.audit_log.append(event)
        return self.data, self.audit_log
