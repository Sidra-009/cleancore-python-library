import time
import random
from src.cleancore import audit_trail, ProvenaLogger

# ======================================================================
# 1. BIG DATA TEST (Lazy Evaluation & Chunking)
# ======================================================================
@audit_trail(rule_id="BIG_DATA_FILTER")
def process_large_dataset(data):
    """Simulating a filter on 100,000 rows."""
    # Only keep even IDs to simulate row drops
    return [row for row in data if row['id'] % 2 == 0]

def test_big_data():
    print("\n--- TEST 1: BIG DATA (100,000 ROWS) ---")
    # Generator use kar rahe hain taake memory save ho
    large_data_gen = ({"id": i, "value": random.random()} for i in range(100000))
    
    with ProvenaLogger("Big_Data_Pipeline") as logger:
        result = process_large_dataset(large_data_gen, provena_logger=logger)
    
    print(f"Result Size: {len(result)} rows")

# ======================================================================
# 2. SCHEMA SENTINEL TEST (Type Drift Detection)
# ======================================================================
@audit_trail(rule_id="TYPE_CONVERSION")
def mess_up_types(data):
    """Simulating a bug where 'age' becomes a string instead of int."""
    for row in data:
        row['age'] = str(row['age']) # int -> str (Type Drift!)
    return data

def test_schema_sentinel():
    print("\n--- TEST 2: SCHEMA SENTINEL (TYPE DRIFT) ---")
    sample_data = [{"id": 1, "age": 25}, {"id": 2, "age": 30}]
    
    with ProvenaLogger("Compliance_Check_Pipeline") as logger:
        mess_up_types(sample_data, provena_logger=logger)

# ======================================================================
# 3. PANDAS SUPPORT TEST
# ======================================================================
def test_pandas_support():
    try:
        import pandas as pd
        print("\n--- TEST 3: PANDAS DATAFRAME SUPPORT ---")
        df = pd.DataFrame({
            'name': ['Ali', 'Sara', 'Ahmed'],
            'salary': [50000, 60000, 55000]
        })

        @audit_trail(rule_id="SALARY_BUMP")
        def give_raise(data_frame):
            data_frame['salary'] = data_frame['salary'] + 5000
            return data_frame

        with ProvenaLogger("HR_Pipeline") as logger:
            give_raise(df, provena_logger=logger)
    except ImportError:
        print("\n[SKIP] Pandas not installed. Skipping Test 3.")

# ======================================================================
# 4. ERROR HANDLING TEST
# ======================================================================
def test_error_handling():
    print("\n--- TEST 4: ERROR HANDLING ---")
    
    @audit_trail(rule_id="CRASH_TEST")
    def faulty_step(data):
        raise ValueError("Something went wrong in the pipeline!")

    try:
        with ProvenaLogger("Faulty_Pipeline") as logger:
            faulty_step([{"id": 1}], provena_logger=logger)
    except ValueError as e:
        print(f"Caught expected error: {e}")

# ======================================================================
# RUN ALL TESTS
# ======================================================================
if __name__ == "__main__":
    print("="*60)
    print("CLEANCORE ELITE TEST SUITE")
    print("="*60)
    
    test_big_data()        # 100k rows check
    test_schema_sentinel() # Type drift check
    test_pandas_support()  # Pandas check
    test_error_handling()  # ASCII Box error check
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*60)