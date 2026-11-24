import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import math

class PointLocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Point Locator")
        self.root.geometry("520x720")

        self.points = []
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

        # --- Buttons ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Clear all", command=self.clear_all).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save to .txt", command=self.save_points).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Load from .txt", command=self.load_points).pack(side="left", padx=5)

        # --- Display area ---
        tk.Label(root, text="Points:").pack(anchor="w", padx=10)
        self.output = scrolledtext.ScrolledText(root, height=14, state="disabled", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=10, pady=5)

    def log(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.config(state="disabled")

    def refresh_display(self):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.config(state="disabled")
        if not self.points:
            return
        self.log("Points:")
        for i, p in enumerate(self.points, start=1):
            self.log(f"Point {i:2d}: ({p[0]:8.3f}, {p[1]:8.3f}, {p[2]:8.3f})")

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

        x3 = (d13**2 - d23**2 + d12**2) / (2 * d12)
        y3_squared = d13**2 - x3**2
        if y3_squared < 0:
            messagebox.showerror("Geometry error", "Distances do not form a valid triangle.")
            return

        y3 = math.sqrt(y3_squared)
        if self.side_var.get() == "n":
            y3 = -y3

        # Update only the first three points; keep any points that were added later
        new_first_three = [(0.0, 0.0, 0.0), (d12, 0.0, 0.0), (x3, y3, 0.0)]
        if len(self.points) < 3:
            self.points = new_first_three
        else:
            self.points[0:3] = new_first_three

        self.d = d12
        self.cx = x3
        self.cy = y3
        self.reference_ready = True
        self.add_button.config(state="normal")

        self.refresh_display()

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

        computed_dC2 = (x - self.cx)**2 + (y - self.cy)**2 + z**2
        warning = ""
        if abs(computed_dC2 - dC**2) > 0.05:
            warning = f"   (inconsistent by {abs(math.sqrt(computed_dC2) - dC):.3f})"

        self.points.append((x, y, z))
        self.refresh_display()
        if warning:
            self.log(f"  (last point){warning}")

        self.entry_z.delete(0, "end")
        self.entry_da.delete(0, "end")
        self.entry_db.delete(0, "end")
        self.entry_dc.delete(0, "end")

    def clear_all(self):
        self.points = []
        self.reference_ready = False
        self.add_button.config(state="disabled")
        self.entry_d12.delete(0, "end")
        self.entry_d13.delete(0, "end")
        self.entry_d23.delete(0, "end")
        self.entry_z.delete(0, "end")
        self.entry_da.delete(0, "end")
        self.entry_db.delete(0, "end")
        self.entry_dc.delete(0, "end")
        self.refresh_display()

    def save_points(self):
        if not self.points:
            messagebox.showinfo("Nothing to save", "No points have been entered yet.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save points"
        )
        if not filename:
            return
        try:
            with open(filename, "w") as f:
                for p in self.points:
                    f.write(f"{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n")
            messagebox.showinfo("Saved", f"Saved {len(self.points)} points to\n{filename}")
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def load_points(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Load points"
        )
        if not filename:
            return
        try:
            loaded = []
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) >= 3:
                        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                        loaded.append((x, y, z))
            if not loaded:
                messagebox.showwarning("Empty file", "No valid points found in the file.")
                return

            self.points = loaded
            self.refresh_display()

            # If we have at least the three reference points, enable adding
            if len(self.points) >= 3:
                self.d = self.points[1][0] - self.points[0][0]
                self.cx = self.points[2][0]
                self.cy = self.points[2][1]
                self.reference_ready = True
                self.add_button.config(state="normal")
                # Fill the reference fields so the user can see them
                self.entry_d12.delete(0, "end")
                self.entry_d12.insert(0, f"{self.d:.3f}")
                # d13 and d23 are not stored; leave them blank or calculate if you want
            else:
                self.reference_ready = False
                self.add_button.config(state="disabled")

            messagebox.showinfo("Loaded", f"Loaded {len(self.points)} points.")
        except Exception as e:
            messagebox.showerror("Load error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PointLocatorApp(root)
    root.mainloop()