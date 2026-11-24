import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import math

class PointLocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Point Locator")
        self.root.geometry("540x780")

        self.points = []
        self.ref_indices = [0, 1, 2]   # indices of points used as references
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

        # Dynamic distance fields live in this frame
        self.dist_frame = tk.Frame(add_frame)
        self.dist_frame.pack(fill="x")
        self.dist_labels = []
        self.dist_entries = []
        self.reset_distance_fields()

        self.use_as_ref = tk.BooleanVar(value=False)
        tk.Checkbutton(add_frame, text="Use as reference point", variable=self.use_as_ref).pack(anchor="w", pady=2)

        self.add_button = tk.Button(add_frame, text="Add point", command=self.add_point, state="disabled")
        self.add_button.pack(pady=5)

        # --- Buttons ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Delete last point", command=self.delete_last).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear all", command=self.clear_all).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save to .txt", command=self.save_points).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Load from .txt", command=self.load_points).pack(side="left", padx=5)

        # --- Display area ---
        tk.Label(root, text="Points:").pack(anchor="w", padx=10)
        self.output = scrolledtext.ScrolledText(root, height=14, state="disabled", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=10, pady=5)

    def add_dist_entry(self, label_text):
        lbl = tk.Label(self.dist_frame, text=label_text)
        lbl.pack(anchor="w")
        ent = tk.Entry(self.dist_frame)
        ent.pack(fill="x")
        self.dist_labels.append(lbl)
        self.dist_entries.append(ent)

    def reset_distance_fields(self):
        for lbl in self.dist_labels:
            lbl.destroy()
        for ent in self.dist_entries:
            ent.destroy()
        self.dist_labels = []
        self.dist_entries = []
        self.add_dist_entry("Distance to point 1:")
        self.add_dist_entry("Distance to point 2:")
        self.add_dist_entry("Distance to point 3:")
        self.ref_indices = [0, 1, 2]

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
            marker = " *" if (i-1) in self.ref_indices else ""
            self.log(f"Point {i:2d}: ({p[0]:8.3f}, {p[1]:8.3f}, {p[2]:8.3f}){marker}")

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
        self.reset_distance_fields()
        self.refresh_display()

    def calculate_xy(self, z, distances):
        """Least-squares 2D solution using all current reference points."""
        refs = [self.points[i] for i in self.ref_indices]
        if len(refs) < 3:
            return None

        r2s = []
        for d in distances:
            r2 = d * d - z * z
            if r2 < -1e-6:
                return None
            r2s.append(max(0.0, r2))

        x0, y0 = refs[0][0], refs[0][1]
        r0 = r2s[0]

        s11 = s12 = s22 = 0.0
        t1 = t2 = 0.0

        for i in range(1, len(refs)):
            xi, yi = refs[i][0], refs[i][1]
            ri = r2s[i]
            a1 = 2 * (xi - x0)
            a2 = 2 * (yi - y0)
            rhs = (r0 - ri) - (x0*x0 - xi*xi) - (y0*y0 - yi*yi)
            s11 += a1 * a1
            s12 += a1 * a2
            s22 += a2 * a2
            t1 += a1 * rhs
            t2 += a2 * rhs

        det = s11 * s22 - s12 * s12
        if abs(det) < 1e-8:
            return None

        x = (s22 * t1 - s12 * t2) / det
        y = (-s12 * t1 + s11 * t2) / det
        return x, y

    def add_point(self):
        if not self.reference_ready:
            return

        try:
            z = float(self.entry_z.get())
            distances = []
            for ent in self.dist_entries:
                d = float(ent.get())
                if d <= 0:
                    raise ValueError
                distances.append(d)
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid positive distances and a numeric height.")
            return

        result = self.calculate_xy(z, distances)
        if result is None:
            messagebox.showerror("Calculation error", "Impossible geometry or reference points are collinear.")
            return

        x, y = result
        self.points.append((x, y, z))

        # Optional residual warning
        max_err = 0.0
        refs = [self.points[i] for i in self.ref_indices]
        for (rx, ry, _), d in zip(refs, distances):
            horiz = math.sqrt(max(0.0, d*d - z*z))
            actual = math.hypot(x - rx, y - ry)
            max_err = max(max_err, abs(actual - horiz))
        warning = f"   (max residual {max_err:.3f})" if max_err > 0.05 else ""

        if self.use_as_ref.get():
            new_idx = len(self.points) - 1
            self.ref_indices.append(new_idx)
            self.add_dist_entry(f"Distance to point {new_idx + 1}:")
            self.use_as_ref.set(False)

        self.refresh_display()
        if warning:
            self.log(f"  (last point){warning}")

        # Clear input fields
        self.entry_z.delete(0, "end")
        for ent in self.dist_entries:
            ent.delete(0, "end")

    def delete_last(self):
        if len(self.points) <= 3:
            messagebox.showwarning("Cannot delete", "The first three reference points cannot be deleted.")
            return
        last_idx = len(self.points) - 1
        if last_idx in self.ref_indices:
            self.dist_entries[-1].destroy()
            self.dist_labels[-1].destroy()
            self.dist_entries.pop()
            self.dist_labels.pop()
            self.ref_indices.pop()
        self.points.pop()
        self.refresh_display()

    def clear_all(self):
        self.points = []
        self.reference_ready = False
        self.add_button.config(state="disabled")
        self.entry_d12.delete(0, "end")
        self.entry_d13.delete(0, "end")
        self.entry_d23.delete(0, "end")
        self.entry_z.delete(0, "end")
        self.reset_distance_fields()
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
            self.reset_distance_fields()
            self.refresh_display()

            if len(self.points) >= 3:
                self.d = self.points[1][0] - self.points[0][0]
                self.cx = self.points[2][0]
                self.cy = self.points[2][1]
                self.reference_ready = True
                self.add_button.config(state="normal")
                self.entry_d12.delete(0, "end")
                self.entry_d12.insert(0, f"{self.d:.3f}")
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