#!/bin/python3

import os
import shutil
from tkinter import Tk, Label, Button, Canvas, messagebox
from PIL import Image, ImageTk

# Configuration
SOURCE_FOLDER = "../images/units"          # Folder containing images (and subfolders)
FIXED_FOLDER = "../images/needs_fixed"     # Destination folder for images needing fixes
OVERLAY_IMAGE = "../images/card pngs/fire.png"  # Transparent overlay image (displayed actual size)

class ImageViewer:
    def __init__(self, root):
        """
        Initialize the ImageViewer application.

        Args:
            root (Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Image Viewer")
        
        # Load all image files and overlay image
        self.image_files = self.load_images(SOURCE_FOLDER)
        self.current_index = 0
        self.overlay = Image.open(OVERLAY_IMAGE).convert("RGBA")  # Ensure overlay has transparency
        
        if not self.image_files:
            messagebox.showerror("Error", "No images found in the source folder!")
            self.root.quit()
            return
        
        # Create GUI elements
        self.canvas = Canvas(root, width=self.overlay.width, height=self.overlay.height)  # Match overlay size
        self.canvas.pack(pady=10)
        
        self.next_button = Button(root, text="Next", command=self.next_image)
        self.next_button.pack(side="left", padx=10, pady=10)
        
        self.fix_button = Button(root, text="Needs Fixed", command=self.mark_needs_fixed)
        self.fix_button.pack(side="left", padx=10, pady=10)
        
        # Ensure the fixed folder exists
        os.makedirs(FIXED_FOLDER, exist_ok=True)
        
        # Display the first image
        self.display_image()

    def load_images(self, folder):
        """
        Recursively load all image files from the specified folder and its subfolders.

        Args:
            folder (str): Path to the source folder containing images.

        Returns:
            list: List of full paths to image files.
        """
        image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        image_list = []
        
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(image_extensions):
                    image_list.append(os.path.join(root, file))
        
        return image_list

    def display_image(self):
        """
        Display the current image with a transparent overlay.

        Resizes the source image to match the overlay's width while preserving aspect ratio,
        then composites the overlay image on top using alpha compositing for transparency.
        """
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Done", "No more images to display!")
            self.root.quit()
            return
        
        # Load base image
        image_path = self.image_files[self.current_index]
        base_img = Image.open(image_path).convert("RGBA")
        
        # Resize base image to match overlay width, preserving aspect ratio
        overlay_width = self.overlay.width
        aspect_ratio = base_img.height / base_img.width
        new_height = int(overlay_width * aspect_ratio)
        base_img_resized = base_img.resize((overlay_width, new_height), Image.Resampling.LANCZOS)
        
        # Ensure base image matches overlay size (pad or crop)
        if base_img_resized.height < self.overlay.height:
            # Pad bottom with transparent pixels if base is shorter
            padded_img = Image.new("RGBA", (overlay_width, self.overlay.height), (0, 0, 0, 0))
            padded_img.paste(base_img_resized, (0, 0))
            base_img_final = padded_img
        else:
            # Crop base image to match overlay height if taller
            base_img_final = base_img_resized.crop((0, 0, overlay_width, self.overlay.height))
        
        # Composite overlay on top of base image using alpha compositing
        combined_img = Image.alpha_composite(base_img_final, self.overlay)
        
        # Convert to PhotoImage for tkinter
        self.photo = ImageTk.PhotoImage(combined_img)
        
        # Clear previous content and display new image
        self.canvas.delete("all")
        self.canvas.config(width=combined_img.width, height=combined_img.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        # Update window title with current file name
        self.root.title(f"Image Viewer - {os.path.basename(image_path)} ({self.current_index + 1}/{len(self.image_files)})")

    def next_image(self):
        """
        Advance to the next image in the list.

        Increments the current index and refreshes the display.
        """
        self.current_index += 1
        self.display_image()

    def mark_needs_fixed(self):
        """
        Move the current image to the FIXED_FOLDER and advance to the next image.

        Moves the file to the specified needs_fixed folder and updates the image list.
        """
        if self.current_index >= len(self.image_files):
            return
        
        current_image = self.image_files[self.current_index]
        destination = os.path.join(FIXED_FOLDER, os.path.basename(current_image))
        
        try:
            shutil.move(current_image, destination)
            print(f"Moved {current_image} to {destination}")
            
            # Remove the moved image from the list and adjust index
            self.image_files.pop(self.current_index)
            if self.current_index >= len(self.image_files):
                self.current_index = len(self.image_files) - 1 if self.image_files else 0
            
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move {current_image}: {e}")

if __name__ == "__main__":
    # Check for required libraries
    try:
        import tkinter
        from PIL import Image, ImageTk
    except ImportError:
        print("Required libraries not found. Install them with: pip install pillow")
        exit(1)
    
    # Verify overlay image exists
    if not os.path.exists(OVERLAY_IMAGE):
        print(f"Overlay image {OVERLAY_IMAGE} not found!")
        exit(1)
    
    # Initialize and run the application
    root = Tk()
    app = ImageViewer(root)
    root.mainloop()
