class Vector:
    def __init__(self, *values):
        if len(values) == 0:
            raise Exception("Vectors cannot be empty")
        self.values = values

    def dimension(self):
        return len(self.values)

    def dot(self, other):
        if self.dimension() != other.dimension():
            raise Exception("Vector dimensions do not match")
        return sum(self.values[i] * other.values[i] for i in range(self.dimension()))

    def __str__(self):
        return f"Vector{self.values}"

class Matrix:
    def __init__(self, rows):
        if len(rows) == 0:
            raise Exception("Matrix cannot be empty")
        
        row_len = len(rows[0])
        for r in rows:
            if len(r) != row_len:
                raise Exception("All rows must have same length")
        
        self.matrix = rows 
        self.r = len(rows)
        self.c = row_len

    def multiply(self, other):
        if self.c != other.r:
            raise Exception("Matrix multiplication not possible")

        result = []
        for i in range(self.r):
            row = []
            for j in range(other.c):
                total = 0
                for k in range(self.c):
                    total += self.matrix[i][k] * other.matrix[k][j]
                row.append(total)
            result.append(row)
        return Matrix(result)

    def __str__(self):
        return f"Matrix{self.matrix}"