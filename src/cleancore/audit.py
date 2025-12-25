# audit.py

class AuditEvent:
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f"AuditEvent(message='{self.message}')"
