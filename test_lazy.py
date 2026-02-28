"""Test CleanCore with lazy evaluation on large dataset."""

from cleancore import audit_trail, audit_pipeline
import time

# Generate large dataset lazily
def generate_large_data(n=100000):
    """Generator for large dataset - memory efficient."""
    for i in range(n):
        yield {
            'id': i,
            'name': f'User_{i}',
            'age': i % 50 + 20,
            'email': f'user{i}@example.com'
        }

@audit_trail(rule_id="MASK_EMAILS", lazy=True)
def mask_emails(data):
    """Process lazily."""
    result = []
    for row in data:
        new_row = row.copy()
        if '@' in new_row.get('email', ''):
            new_row['email'] = '***@***.***'
        result.append(new_row)
    return result

@audit_trail(rule_id="FILTER_AGE", lazy=True)
def filter_by_age(data):
    """Filter with generator."""
    for row in data:
        if row.get('age', 0) > 30:
            yield row

# Run with lazy evaluation
print("\n🚀 Testing LAZY mode with 100,000 rows...")

with audit_pipeline("Large_Data_Test", lazy=True, sample_size=1000) as logger:
    # Use generators - memory efficient!
    data = generate_large_data(100000)
    data1 = mask_emails(data, provena_logger=logger)
    data2 = list(filter_by_age(data1, provena_logger=logger))  # Convert to list at end

# Print report
reporter = logger.get_reporter()
reporter.print_report()

print("\n✅ Lazy evaluation test complete!")