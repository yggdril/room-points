import math

def get_positive_float(prompt):
    """Ask for a number > 0 and keep asking until valid."""
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a number.")

def main():
    print("=== 3D Point Locator ===")
    print("Point 1 is always at the origin (0, 0, 0).")
    points = [(0.0, 0.0, 0.0)]

    # Point 2 on the positive X-axis
    d12 = get_positive_float("Distance from point 1 to point 2: ")
    points.append((d12, 0.0, 0.0))
    print(f"Point 2 placed at ({d12}, 0, 0)")

    # Point 3 on the floor (Z = 0)
    d13 = get_positive_float("Distance from point 1 to point 3: ")
    d23 = get_positive_float("Distance from point 2 to point 3: ")

    # 2D calculation on the XY plane
    # x = (d13² - d23² + d12²) / (2 * d12)
    x3 = (d13**2 - d23**2 + d12**2) / (2 * d12)
    y3_squared = d13**2 - x3**2

    if y3_squared < 0:
        print("Error: distances do not form a valid triangle. Start over.")
        return

    y3_abs = math.sqrt(y3_squared)
    side = input("Is point 3 on the positive Y side of the X-axis? (y/n): ").strip().lower()
    y3 = y3_abs if side == "y" else -y3_abs

    points.append((x3, y3, 0.0))
    print(f"Point 3 placed at ({x3:.3f}, {y3:.3f}, 0)")

    print("\nCurrent points:")
    for i, p in enumerate(points, start=1):
        print(f"  Point {i}: ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f})")

if __name__ == "__main__":
    main()