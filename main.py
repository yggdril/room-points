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

def get_float(prompt):
    """Ask for any number (positive, zero or negative)."""
    while True:
        try:
            return float(input(prompt))
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

    # Reference values for later points
    d = d12          # distance A to B
    cx, cy = x3, y3  # coordinates of C

    # Add more points (from point 4 onward)
    while True:
        more = input("\nAdd another point? (y/n): ").strip().lower()
        if more != "y":
            break

        print(f"\n--- Point {len(points) + 1} ---")
        z = get_float("Height (Z value) of the point: ")
        dA = get_positive_float("Distance to point 1: ")
        dB = get_positive_float("Distance to point 2: ")
        dC = get_positive_float("Distance to point 3: ")

        # Horizontal distances squared (distance in the XY plane)
        rA2 = dA**2 - z**2
        rB2 = dB**2 - z**2
        rC2 = dC**2 - z**2

        if rA2 < 0 or rB2 < 0 or rC2 < 0:
            print("Impossible: one of the distances is smaller than the height.")
            continue

        # Solve for x and y using the horizontal distances
        x = (rA2 - rB2 + d**2) / (2 * d)
        y = (rA2 - rC2 + cx**2 + cy**2 - 2 * cx * x) / (2 * cy)

        # Check how well the result matches the third distance
        computed_dC2 = (x - cx)**2 + (y - cy)**2 + z**2
        if abs(computed_dC2 - dC**2) > 0.05:   # 5 cm tolerance
            print(f"Warning: distances are inconsistent (expected {dC:.3f}, calculated {math.sqrt(computed_dC2):.3f})")
            print(f"The Error is: {abs(dC - math.sqrt(computed_dC2)):.3f}m")

        points.append((x, y, z))
        print(f"Point {len(points)} placed at ({x:.3f}, {y:.3f}, {z:.3f})")

    # Final summary
    print("\n=== All points ===")
    for i, p in enumerate(points, start=1):
        print(f"  Point {i}: ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f})")

if __name__ == "__main__":
    main()