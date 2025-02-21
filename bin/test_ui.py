import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def browse_image():
    filename = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    if filename:
        image_entry.delete(0, tk.END)
        image_entry.insert(0, filename)

# Create main window
root = tk.Tk()
root.title("Game Card Creator")

# Convert inches to pixels (96 DPI)
DPI = 96
PREVIEW_WIDTH = int(2.5 * DPI)  # 240 pixels (unchanged)
PREVIEW_HEIGHT = int(3.5 * DPI)  # 336 pixels (unchanged)

# Main container
main_frame = ttk.Frame(root, padding="15")  # Increased padding
main_frame.grid(row=0, column=0, sticky="nsew")

# Left side - Input controls
left_frame = ttk.LabelFrame(main_frame, text="Card Details", padding="15")  # Increased padding
left_frame.grid(row=0, column=0, sticky="nsew")

# Increase font size for all widgets
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12))
style.configure("TCheckbutton", font=("Helvetica", 12))

# Name
ttk.Label(left_frame, text="Name:").grid(row=0, column=0, pady=8, sticky="w")  # Increased pady
name_entry = ttk.Entry(left_frame, width=35, font=("Helvetica", 12))  # Increased width and font
name_entry.grid(row=0, column=1, pady=8)

# Attribute dropdown
ttk.Label(left_frame, text="Attribute:").grid(row=1, column=0, pady=8, sticky="w")
attribute_combo = ttk.Combobox(left_frame, 
                             values=["Fire", "Water", "Earth", "Wind"], 
                             width=32, 
                             font=("Helvetica", 12))  # Increased width and font
attribute_combo.grid(row=1, column=1, pady=8)

# Types checkboxes (added more)
types_frame = ttk.LabelFrame(left_frame, text="Types", padding="8")  # Increased padding
types_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="w")
type_vars = [tk.BooleanVar() for _ in range(5)]
type_labels = ["Warrior", "Spellcaster", "Dragon", "Machine", "Beast"]
for i, label in enumerate(type_labels):
    ttk.Checkbutton(types_frame, text=label, variable=type_vars[i]).grid(
        row=i//3, column=i%3, padx=8, pady=5)  # Arranged in 2 rows

# Level dropdown
ttk.Label(left_frame, text="Level:").grid(row=3, column=0, pady=8, sticky="w")
level_combo = ttk.Combobox(left_frame, 
                          values=[str(i) for i in range(1, 13)], 
                          width=32, 
                          font=("Helvetica", 12))  # Increased width and font
level_combo.grid(row=3, column=1, pady=8)

# Image with browse button
ttk.Label(left_frame, text="Image:").grid(row=4, column=0, pady=8, sticky="w")
image_entry = ttk.Entry(left_frame, width=25, font=("Helvetica", 12))  # Increased font
image_entry.grid(row=4, column=1, pady=8, sticky="w")
browse_btn = ttk.Button(left_frame, text="Browse", command=browse_image)
browse_btn.grid(row=4, column=1, pady=8, sticky="e")

# ATK and DEF
ttk.Label(left_frame, text="ATK:").grid(row=5, column=0, pady=8, sticky="w")
atk_entry = ttk.Entry(left_frame, width=15, font=("Helvetica", 12))  # Increased width and font
atk_entry.grid(row=5, column=1, pady=8, sticky="w")

ttk.Label(left_frame, text="DEF:").grid(row=5, column=1, pady=8, padx=(30, 0), sticky="w")  # Increased padx
def_entry = ttk.Entry(left_frame, width=15, font=("Helvetica", 12))  # Increased width and font
def_entry.grid(row=5, column=1, pady=8, padx=(70, 0), sticky="w")  # Increased padx

# Description
ttk.Label(left_frame, text="Description:").grid(row=6, column=0, pady=8, sticky="w")
desc_entry = tk.Text(left_frame, height=6, width=35, font=("Helvetica", 12))  # Increased size and font
desc_entry.grid(row=6, column=1, pady=8)

# Serial Number (non-editable)
ttk.Label(left_frame, text="Serial #:").grid(row=7, column=0, pady=8, sticky="w")
serial_entry = ttk.Entry(left_frame, width=35, font=("Helvetica", 12))  # Increased width and font
serial_entry.insert(0, "AUTO-GENERATED")
serial_entry.configure(state="disabled")
serial_entry.grid(row=7, column=1, pady=8)

# Right side - Preview window
preview_frame = ttk.LabelFrame(main_frame, text="Card Preview", padding="15")  # Increased padding
preview_frame.grid(row=0, column=1, padx=15, sticky="nsew")  # Increased padx

preview_canvas = tk.Canvas(
    preview_frame,
    width=PREVIEW_WIDTH,
    height=PREVIEW_HEIGHT,
    bg="white",
    highlightthickness=1,
    highlightbackground="black"
)
preview_canvas.grid(row=0, column=0)

# Configure grid weights
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=0)
main_frame.rowconfigure(0, weight=1)

# Force update of geometry and set minimum size
root.update()  # Calculate initial size based on contents
root.minsize(root.winfo_width(), root.winfo_height())  # Set minimum size to initial size

root.mainloop()
