# MathNexus 📐🚀

[![PyPI version](https://badge.fury.io/py/mathnexus.svg)](https://badge.fury.io/py/mathnexus)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**MathNexus** is a powerful yet lightweight Python library built for students, educators, and developers to simplify **Linear Algebra** and **Coordinate Geometry** operations. 🧠✨

---

## 🌟 Why MathNexus?
Traditional math operations in Python can sometimes feel bulky. **MathNexus** provides a clean, human-readable syntax to handle complex calculations in seconds!

---

## 📦 Installation 🛠️

You can install the latest version of MathNexus directly from [PyPI](https://pypi.org/project/mathnexus/):

```bash   pip install mathnexus```

🔥 Key Features 🚀
📍 Coordinate Geometry: Easily calculate distances, slopes, and midpoints.

🔢 Linear Algebra: Built-in support for Vectors and Matrices.

📉 Physics Modeling: Bridge the gap between math and physics visualizations.

⚡ Lightweight: Zero heavy dependencies, keeping your projects fast!

🚀 Quick Start Guide 📖
Check out how easy it is to use MathNexus in your code:

1️⃣ Distance Between Two Points
Python

from mathnexus.coordinate_geometry import calculate_distance

# Coordinates as (x, y)
p1 = (0, 0)
p2 = (3, 4)

distance = calculate_distance(p1, p2)
print(f"The distance is: {distance} 📏") # Output: 5.0
2️⃣ Finding the Slope of a Line
Python

from mathnexus.coordinate_geometry import calculate_slope

slope = calculate_slope((1, 2), (3, 6))
print(f"The slope is: {slope} 📈") # Output: 2.0
3️⃣ Working with Vectors
Python

from mathnexus.linear_datatypes import Vector

v = Vector(5, 12)
print(f"Vector Magnitude: {v.magnitude()} ⚡") # Output: 13.0
🛠 Tech Stack & Requirements 💻
Language: Python 3.6+ 🐍

Dependencies: None (Pure Python) 🛡️

🤝 Contributing 🤝
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

👩‍💻 Author
Sidra Saqlain ✨ 
