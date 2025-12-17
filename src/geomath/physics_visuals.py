class Visualizer:
    @staticmethod
    def draw_svg(filename, shapes, width=500, height=500):
        header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="background:#f0f0f0;">\n'
        content = ""
        for s in shapes:
            if s["type"] == "circle":
                content += f'  <circle cx="{s["x"]}" cy="{s["y"]}" r="{s["r"]}" fill="{s["color"]}" />\n'
        with open(filename, "w") as f:
            f.write(header + content + "</svg>")
        print(f"SVG saved to {filename}")

class TerminalPlotter:
    @staticmethod
    def plot_path(data, width=50, height=12):
        """Universal Plotter: Works in Colab, Jupyter, and Terminal."""
        if not data: return
        
        BLUE, GRAY, WHITE, RESET = "\033[94m", "\033[90m", "\033[97m", "\033[0m"
        
        max_v, min_v = max(data), min(data)
        v_range = max_v - min_v if max_v != min_v else 1
        
        canvas = [[" " for _ in range(width)] for _ in range(height)]
        
        for i in range(len(data)):
            x = int((i / (len(data) - 1)) * (width - 1)) if len(data) > 1 else 0
            y = (height - 1) - int(((data[i] - min_v) / v_range) * (height - 1))
            if 0 <= y < height and 0 <= x < width:

                canvas[y][x] = f"{BLUE}*{RESET}"

        print("\n" + " " * 10 + f"{WHITE}GEOMATH PHYSICS PLOT{RESET}")
        border = "+" + "-" * width + "+"
        print(f"           {GRAY}{border}{RESET}")
        
        for r in range(height):
            val = max_v - (r * (v_range / (height - 1)))
            row_content = "".join(canvas[r])
            print(f" {WHITE}{val:8.2f} |{RESET}{row_content}{GRAY}|{RESET}")
            
        print(f"           {GRAY}{border}{RESET}")
        print(f"            0{' ' * (width-8)}Time (s) ->\n")

class PhysicsEngine:
    def __init__(self, gravity=9.8):
        self.g = gravity

    def apply_gravity(self, velocity_y, time_step=0.1): 
        """
        Calculates the new velocity after a time step.
        'time_step' is clear for public users.
        """
        return velocity_y + (self.g * time_step)