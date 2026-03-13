import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os


class ImageToPDFConverter:

    def __init__(self, root):

        self.root = root
        self.root.title("Image to PDF Converter Pro")
        self.root.geometry("650x700")

        self.image_paths = []
        self.preview_image = None

        self.output_pdf_name = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready")

        self.dark_mode = False
        self.compress_images = tk.BooleanVar()

        self.create_ui()

    def create_ui(self):

        title = ttk.Label(self.root, text="Image to PDF Converter Pro", font=("Arial", 18))
        title.pack(pady=10)

        top_frame = ttk.Frame(self.root)
        top_frame.pack()

        ttk.Button(top_frame, text="Select Images", command=self.select_images).grid(row=0, column=0, padx=5)
        ttk.Button(top_frame, text="Clear Images", command=self.clear_images).grid(row=0, column=1, padx=5)
        ttk.Button(top_frame, text="Toggle Dark Mode", command=self.toggle_dark_mode).grid(row=0, column=2, padx=5)

        self.image_listbox = tk.Listbox(self.root, height=10)
        self.image_listbox.pack(fill=tk.BOTH, padx=20, pady=10)

        self.image_listbox.drop_target_register(DND_FILES)
        self.image_listbox.dnd_bind('<<Drop>>', self.drop_files)

        move_frame = ttk.Frame(self.root)
        move_frame.pack()

        ttk.Button(move_frame, text="Move Up", command=self.move_up).grid(row=0, column=0, padx=10)
        ttk.Button(move_frame, text="Move Down", command=self.move_down).grid(row=0, column=1, padx=10)

        self.image_listbox.bind("<<ListboxSelect>>", self.show_preview)

        self.preview_canvas = tk.Canvas(self.root, width=250, height=250)
        self.preview_canvas.pack(pady=10)

        ttk.Checkbutton(
            self.root,
            text="Compress Images",
            variable=self.compress_images
        ).pack()

        ttk.Label(self.root, text="PDF Name").pack()

        ttk.Entry(self.root, textvariable=self.output_pdf_name, width=30).pack(pady=5)

        ttk.Button(self.root, text="Convert to PDF", command=self.convert_images).pack(pady=10)

        ttk.Button(self.root, text="PDF → Images", command=self.pdf_to_images).pack()

        self.progress = ttk.Progressbar(self.root, length=300)
        self.progress.pack(pady=10)

        ttk.Label(self.root, textvariable=self.status_text).pack()

    def select_images(self):

        paths = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )

        for path in paths:

            self.image_paths.append(path)
            self.image_listbox.insert(tk.END, os.path.basename(path))

        self.status_text.set(f"{len(self.image_paths)} images loaded")

    def drop_files(self, event):

        files = self.root.tk.splitlist(event.data)

        for file in files:

            if file.lower().endswith(("png", "jpg", "jpeg", "bmp")):
                self.image_paths.append(file)
                self.image_listbox.insert(tk.END, os.path.basename(file))

    def clear_images(self):

        self.image_paths.clear()
        self.image_listbox.delete(0, tk.END)
        self.preview_canvas.delete("all")

    def move_up(self):

        sel = self.image_listbox.curselection()

        if not sel or sel[0] == 0:
            return

        i = sel[0]

        self.image_paths[i], self.image_paths[i - 1] = self.image_paths[i - 1], self.image_paths[i]

        self.refresh_list()

        self.image_listbox.select_set(i - 1)

    def move_down(self):

        sel = self.image_listbox.curselection()

        if not sel or sel[0] == len(self.image_paths) - 1:
            return

        i = sel[0]

        self.image_paths[i], self.image_paths[i + 1] = self.image_paths[i + 1], self.image_paths[i]

        self.refresh_list()

        self.image_listbox.select_set(i + 1)

    def refresh_list(self):

        self.image_listbox.delete(0, tk.END)

        for path in self.image_paths:
            self.image_listbox.insert(tk.END, os.path.basename(path))

    def show_preview(self, event):

        sel = self.image_listbox.curselection()

        if not sel:
            return

        path = self.image_paths[sel[0]]

        img = Image.open(path)

        img.thumbnail((250, 250))

        self.preview_image = ImageTk.PhotoImage(img)

        self.preview_canvas.delete("all")

        self.preview_canvas.create_image(125, 125, image=self.preview_image)

    def convert_images(self):

        if not self.image_paths:

            messagebox.showerror("Error", "No images selected")

            return

        name = self.output_pdf_name.get().strip()

        if not name:

            messagebox.showerror("Error", "Enter PDF name")

            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf")

        if not save_path:
            return

        try:

            images = []

            total = len(self.image_paths)

            self.progress["maximum"] = total

            for i, path in enumerate(self.image_paths):

                img = Image.open(path)

                if img.mode != "RGB":
                    img = img.convert("RGB")

                if self.compress_images.get():
                    img = img.resize((img.width // 2, img.height // 2))

                images.append(img)

                self.progress["value"] = i + 1

                self.root.update_idletasks()

            images[0].save(save_path, save_all=True, append_images=images[1:])

            messagebox.showinfo("Success", "PDF created!")

            self.output_pdf_name.set("")
            self.clear_images()
            self.progress["value"] = 0

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def pdf_to_images(self):

        pdf_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])

        if not pdf_path:
            return

        output_dir = filedialog.askdirectory()

        if not output_dir:
            return

        try:

            from pdf2image import convert_from_path

            pages = convert_from_path(pdf_path)

            for i, page in enumerate(pages):

                page.save(os.path.join(output_dir, f"page_{i+1}.png"))

            messagebox.showinfo("Success", "PDF converted to images")

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def toggle_dark_mode(self):

        if not self.dark_mode:

            self.root.configure(bg="#2b2b2b")

            self.dark_mode = True

        else:

            self.root.configure(bg="SystemButtonFace")

            self.dark_mode = False


def main():

    root = TkinterDnD.Tk()

    app = ImageToPDFConverter(root)

    root.mainloop()


if __name__ == "__main__":

    main()