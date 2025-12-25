# engine.py
from cleancore.audit import AuditEvent

class CleanEngine:
    def __init__(self, df=None):
        self.data = df
        self.audit_log = []

    def run(self):
        self.audit_log.append(
            AuditEvent("No transformations applied.")
        )
        return self.data, self.audit_log
