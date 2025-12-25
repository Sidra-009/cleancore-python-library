from cleancore.engine import CleanEngine

engine = CleanEngine(df="Groceries_dataset.csv")
cleaned, audit = engine.run()

print(cleaned)
print(audit)
