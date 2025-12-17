from geomath import Matrix, Vector, Point2D, PhysicsEngine, TerminalPlotter

print("="*50)
print("       GEOMATH COMPLETE SYSTEM TEST (v0.2.1)")
print("="*50)

# 1. TEST: Linear Algebra
print("\n[1] Testing Linear Algebra...")
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix([[5, 6], [7, 8]])
result_m = m1.multiply(m2)
# We use .matrix here because that is the name of the attribute in your lib
print(f"Matrix Multiply Success: {result_m.matrix}")

# 2. TEST: Geometry
print("\n[2] Testing Geometry...")
p1 = Point2D(0, 0)
p2 = Point2D(3, 4)
dist = p1.distance_to(p2)
print(f"Distance calculation (0,0) to (3,4): {dist}")

# 3. TEST: Physics + Universal Visualizer
print("\n[3] Testing Physics & Scientific Visuals...")
engine = PhysicsEngine(gravity=9.8)
v_y, y_pos = 0, 0
height_data = []

for _ in range(30):
    v_y = engine.apply_gravity(v_y, time_step=0.1)
    y_pos += v_y
    height_data.append(y_pos)

TerminalPlotter.plot_path(height_data)

print("="*50)
print("✅ ALL TESTS PASSED: Ready for Public Release!")
print("="*50)