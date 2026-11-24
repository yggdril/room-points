import tkinter as tk
from tkinter import messagebox, scrolledtext
import math

class PointLocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Point Locator")
        self.root.geometry("500x650")

        self.points = []          # list of (x, y, z)
        self.reference_ready = False

        # --- Reference points section ---
        ref_frame = tk.LabelFrame(root, text="1. Define reference points", padx=10, pady=10)
        ref_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(ref_frame, text="Point 1 is always (0, 0, 0)").pack(anchor="w")

        tk.Label(ref_frame, text="Distance point 1 → 2:").pack(anchor="w")
        self.entry_d12 = tk.Entry(ref_frame)
        self.entry_d12.pack(fill="x")

        tk.Label(ref_frame, text="Distance point 1 → 3:").pack(anchor="w")
        self.entry_d13 = tk.Entry(ref_frame)
        self.entry_d13.pack(fill="x")

        tk.Label(ref_frame, text="Distance point 2 → 3:").pack(anchor="w")
        self.entry_d23 = tk.Entry(ref_frame)
        self.entry_d23.pack(fill="x")

        self.side_var = tk.StringVar(value="y")
        tk.Radiobutton(ref_frame, text="Point 3 positive Y", variable=self.side_var, value="y").pack(anchor="w")
        tk.Radiobutton(ref_frame, text="Point 3 negative Y", variable=self.side_var, value="n").pack(anchor="w")

        tk.Button(ref_frame, text="Set reference points", command=self.set_reference).pack(pady=5)

        # --- Add more points section ---
        add_frame = tk.LabelFrame(root, text="2. Add further points", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(add_frame, text="Height (Z):").pack(anchor="w")
        self.entry_z = tk.Entry(add_frame)
        self.entry_z.pack(fill="x")

        tk.Label(add_frame, text="Distance to point 1:").pack(anchor="w")
        self.entry_da = tk.Entry(add_frame)
        self.entry_da.pack(fill="x")

        tk.Label(add_frame, text="Distance to point 2:").pack(anchor="w")
        self.entry_db = tk.Entry(add_frame)
        self.entry_db.pack(fill="x")

        tk.Label(add_frame, text="Distance to point 3:").pack(anchor="w")
        self.entry_dc = tk.Entry(add_frame)
        self.entry_dc.pack(fill="x")

        self.add_button = tk.Button(add_frame, text="Add point", command=self.add_point, state="disabled")
        self.add_button.pack(pady=5)

        # --- Display area ---
        tk.Label(root, text="Points:").pack(anchor="w", padx=10)
        self.output = scrolledtext.ScrolledText(root, height=12, state="disabled")
        self.output.pack(fill="both", expand=True, padx=10, pady=5)

    def log(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.config(state="disabled")

    def set_reference(self):
        try:
            d12 = float(self.entry_d12.get())
            d13 = float(self.entry_d13.get())
            d23 = float(self.entry_d23.get())
            if d12 <= 0 or d13 <= 0 or d23 <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input error", "Please enter positive numbers for the three distances.")
            return

        # Point 1 and 2
        self.points = [(0.0, 0.0, 0.0), (d12, 0.0, 0.0)]

        # Point 3
        x3 = (d13**2 - d23**2 + d12**2) / (2 * d12)
        y3_squared = d13**2 - x3**2
        if y3_squared < 0:
            messagebox.showerror("Geometry error", "Distances do not form a valid triangle.")
            return

        y3 = math.sqrt(y3_squared)
        if self.side_var.get() == "n":
            y3 = -y3

        self.points.append((x3, y3, 0.0))

        # Store values needed later
        self.d = d12
        self.cx = x3
        self.cy = y3

        self.reference_ready = True
        self.add_button.config(state="normal")

        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.config(state="disabled")

        self.log("Reference points set:")
        self.log(f"  Point 1: (0.000, 0.000, 0.000)")
        self.log(f"  Point 2: ({d12:.3f}, 0.000, 0.000)")
        self.log(f"  Point 3: ({x3:.3f}, {y3:.3f}, 0.000)")

    def add_point(self):
        if not self.reference_ready:
            return

        try:
            z = float(self.entry_z.get())
            dA = float(self.entry_da.get())
            dB = float(self.entry_db.get())
            dC = float(self.entry_dc.get())
            if dA <= 0 or dB <= 0 or dC <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid numbers (distances must be positive).")
            return

        rA2 = dA**2 - z**2
        rB2 = dB**2 - z**2
        rC2 = dC**2 - z**2

        if rA2 < 0 or rB2 < 0 or rC2 < 0:
            messagebox.showerror("Impossible", "One of the distances is smaller than the height.")
            return

        x = (rA2 - rB2 + self.d**2) / (2 * self.d)
        y = (rA2 - rC2 + self.cx**2 + self.cy**2 - 2 * self.cx * x) / (2 * self.cy)

        # Consistency check
        computed_dC2 = (x - self.cx)**2 + (y - self.cy)**2 + z**2
        warning = ""
        if abs(computed_dC2 - dC**2) > 0.05:
            warning = f"  (warning: inconsistent by {abs(math.sqrt(computed_dC2) - dC):.3f})"

        self.points.append((x, y, z))
        self.log(f"Point {len(self.points)}: ({x:.3f}, {y:.3f}, {z:.3f}){warning}")

        # Clear the input fields for the next point
        self.entry_z.delete(0, "end")
        self.entry_da.delete(0, "end")
        self.entry_db.delete(0, "end")
        self.entry_dc.delete(0, "end")

if __name__ == "__main__":
    root = tk.Tk()
    app = PointLocatorApp(root)
    root.mainloop()