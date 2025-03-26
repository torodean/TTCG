#!/bin/python3

import os
import shutil
from tkinter import Tk, Label, Button, Canvas, messagebox, Frame
from PIL import Image, ImageTk

# Configuration
SOURCE_FOLDER = "../images/unsorted"           # Folders containing images (and subfolders)
FIXED_FOLDER = "../images/needs_fixed"         # Destination folder for images needing fixes
OVERLAY_IMAGE = "../images/card pngs/fire-50.png" # Transparent overlay image (displayed actual size)
EXCLUDE_FOLDERS = ["images/needs_fixed", "images/card pngs", "images/generated_cards", "images/icons", "images/sample cards"]
TYPES = ["earth", "fire", "water", "air", "nature", "electric", "light", "dark"]
UNITS_BASE_FOLDER = "../images/units"
SPELLS_BASE_FOLDER = "../images/spells"

class ImageViewer:
    def __init__(self, root):
        """
        Initialize the ImageViewer application.

        Args: qq
            root (Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Image Viewer")
        
        # Load all image files and overlay image
        self.image_files = self.load_images(SOURCE_FOLDER, False)
        self.current_index = 0
        self.overlay = Image.open(OVERLAY_IMAGE).convert("RGBA")  # Ensure overlay has transparency
        
        if not self.image_files:
            messagebox.showerror("Error", "No images found in the source folder!")
            self.root.quit()
            return
        
        # Create destination directories at startup
        self.ensure_directories_exist()
        
        # Create GUI elements
        self.main_frame = Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Canvas for image display
        self.canvas = Canvas(self.main_frame, width=self.overlay.width, height=self.overlay.height)
        self.canvas.pack(side="left", pady=10)
        
        # Side panel for type selection
        self.side_panel = Frame(self.main_frame)
        self.side_panel.pack(side="right", padx=10, pady=10, fill="y")
        
        # Units column
        self.units_frame = Frame(self.side_panel)
        self.units_frame.pack(side="left", padx=5)
        Label(self.units_frame, text="Units").pack()
        for type_name in TYPES:
            btn = Button(self.units_frame, text=type_name.capitalize(),
                        command=lambda t=type_name: self.move_to_type("units", t))
            btn.pack(fill="x", pady=2)
        # Add Next button under Units with spacing
        self.next_button = Button(self.units_frame, text="Next", command=self.next_image)
        self.next_button.pack(fill="x", pady=(40, 0))  # 10px space above, 0 below
        
        # Spells column
        self.spells_frame = Frame(self.side_panel)
        self.spells_frame.pack(side="left", padx=5)
        Label(self.spells_frame, text="Spells").pack()
        for type_name in TYPES:
            btn = Button(self.spells_frame, text=type_name.capitalize(),
                        command=lambda t=type_name: self.move_to_type("spells", t))
            btn.pack(fill="x", pady=2)
        # Add Needs Fixed button under Spells with spacing
        self.fix_button = Button(self.spells_frame, text="Needs Fixed", command=self.mark_needs_fixed)
        self.fix_button.pack(fill="x", pady=(40, 0))  # 10px space above, 0 below
        
        # Display the first image
        self.display_image()

    def ensure_directories_exist(self):
        """Create all necessary destination directories at startup."""
        os.makedirs(FIXED_FOLDER, exist_ok=True)
        for type_name in TYPES:
            os.makedirs(os.path.join(UNITS_BASE_FOLDER, type_name), exist_ok=True)
            os.makedirs(os.path.join(SPELLS_BASE_FOLDER, type_name), exist_ok=True)

    def load_images(self, folder, exclude_top_level=False):
        """
        Recursively load all image files from the specified folder and its subfolders.

        Args:
            folder (str): Path to the source folder containing images.
            exclude_top_level (bool): If True, exclude images directly in the folder (only use subfolders).

        Returns:
            list: List of full paths to image files.
        """
        image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        image_list = []
        
        for root, _, files in os.walk(folder):
            if any(excluded in root for excluded in EXCLUDE_FOLDERS):
                continue
            if exclude_top_level and root == folder:
                continue
            for file in files:
                if file.lower().endswith(image_extensions):
                    image_list.append(os.path.join(root, file))
        
        return image_list

    def display_image(self):
        """
        Display the current image with a transparent overlay.
        """
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Done", "No more images to display!")
            self.root.quit()
            return
        
        image_path = self.image_files[self.current_index]
        base_img = Image.open(image_path).convert("RGBA")
        
        overlay_width = self.overlay.width
        aspect_ratio = base_img.height / base_img.width
        new_height = int(overlay_width * aspect_ratio)
        base_img_resized = base_img.resize((overlay_width, new_height), Image.Resampling.LANCZOS)
        
        if base_img_resized.height < self.overlay.height:
            padded_img = Image.new("RGBA", (overlay_width, self.overlay.height), (0, 0, 0, 0))
            padded_img.paste(base_img_resized, (0, 0))
            base_img_final = padded_img
        else:
            base_img_final = base_img_resized.crop((0, 0, overlay_width, self.overlay.height))
        
        combined_img = Image.alpha_composite(base_img_final, self.overlay)
        self.photo = ImageTk.PhotoImage(combined_img)
        
        self.canvas.delete("all")
        self.canvas.config(width=combined_img.width, height=combined_img.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        self.root.title(f"Image Viewer - {os.path.basename(image_path)} ({self.current_index + 1}/{len(self.image_files)})")

    def next_image(self):
        """Advance to the next image in the list."""
        self.current_index += 1
        self.display_image()

    def mark_needs_fixed(self):
        """Move the current image to the FIXED_FOLDER and advance to the next image."""
        if self.current_index >= len(self.image_files):
            return
        
        current_image = self.image_files[self.current_index]
        destination = os.path.join(FIXED_FOLDER, os.path.basename(current_image))
        
        try:
            shutil.move(current_image, destination)
            print(f"Moved {current_image} to {destination}")
            self.image_files.pop(self.current_index)
            if self.current_index >= len(self.image_files):
                self.current_index = len(self.image_files) - 1 if self.image_files else 0
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move {current_image}: {e}")

    def move_to_type(self, category, type_name):
        """
        Move the current image to the appropriate units or spells type folder.

        Args:
            category (str): 'units' or 'spells'
            type_name (str): The type (e.g., 'fire', 'water')
        """
        if self.current_index >= len(self.image_files):
            return
        
        current_image = self.image_files[self.current_index]
        base_folder = UNITS_BASE_FOLDER if category == "units" else SPELLS_BASE_FOLDER
        destination_folder = os.path.join(base_folder, type_name)
        destination = os.path.join(destination_folder, os.path.basename(current_image))
        
        try:
            shutil.move(current_image, destination)
            print(f"Moved {current_image} to {destination}")
            self.image_files.pop(self.current_index)
            if self.current_index >= len(self.image_files):
                self.current_index = len(self.image_files) - 1 if self.image_files else 0
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move {current_image}: {e}")

if __name__ == "__main__":
    try:
        import tkinter
        from PIL import Image, ImageTk
    except ImportError:
        print("Required libraries not found. Install them with: pip install pillow")
        exit(1)
    
    if not os.path.exists(OVERLAY_IMAGE):
        print(f"Overlay image {OVERLAY_IMAGE} not found!")
        exit(1)
    
    root = Tk()
    app = ImageViewer(root)
    root.mainloop()
