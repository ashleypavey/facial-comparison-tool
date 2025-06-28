import os
import shutil
import face_recognition
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import uuid

HEADSHOT_FOLDER = r"..." # Location of existing images
DEFAULT_OPEN_PATH = r"..."  # Default path when choosing new image

def load_known_encodings(folder):
    encodings = []
    filepaths = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(folder, filename)
            image = face_recognition.load_image_file(path)
            faces = face_recognition.face_encodings(image)
            if faces:
                encodings.append(faces[0])
                filepaths.append(path)
    return encodings, filepaths

def compare_faces_to_all(new_image_path, known_encodings, known_filepaths):
    image = face_recognition.load_image_file(new_image_path)
    faces = face_recognition.face_encodings(image)
    if not faces:
        return []
    new_encoding = faces[0]

    matched_pairs = []
    for i, encoding in enumerate(known_encodings):
        match = face_recognition.compare_faces([encoding], new_encoding)[0]
        if match:
            matched_pairs.append((known_filepaths[i], new_image_path))
    return matched_pairs

def create_scrollable_review_window(matched_pairs, saved_path):
    top = tk.Toplevel()
    top.title("Matched Images") 

    if matched_pairs:
        window_width = 900
        window_height = 700
    else:
        window_width = 400
        window_height = 200

    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    top.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    if matched_pairs:
        canvas = tk.Canvas(top)
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            if os.name == 'nt':
                canvas.yview_scroll(-1 * (event.delta // 120), "units")
            elif os.name == 'darwin':
                canvas.yview_scroll(-1 * int(event.delta), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        IMG_SIZE = 200
        PAD_X = 10
        PAD_Y = 10

        for match_path, new_path in matched_pairs:
            frame = tk.Frame(scroll_frame, padx=PAD_X, pady=PAD_Y)
            frame.pack(fill="x", pady=PAD_Y)

            img1 = Image.open(match_path).resize((IMG_SIZE, IMG_SIZE))
            img2 = Image.open(new_path).resize((IMG_SIZE, IMG_SIZE))

            tk_img1 = ImageTk.PhotoImage(img1)
            tk_img2 = ImageTk.PhotoImage(img2)

            img_label1 = tk.Label(frame, image=tk_img1)
            img_label1.image = tk_img1
            img_label1.grid(row=0, column=0, padx=PAD_X)

            img_label2 = tk.Label(frame, image=tk_img2)
            img_label2.image = tk_img2
            img_label2.grid(row=0, column=1, padx=PAD_X)

            file_label1 = tk.Label(frame, text=os.path.basename(match_path))
            file_label1.grid(row=1, column=0, pady=(5,0))

            file_label2 = tk.Label(frame, text=os.path.basename(new_path))
            file_label2.grid(row=1, column=1, pady=(5,0))

        rename_frame_parent = scroll_frame
    else:
        rename_frame_parent = top

    rename_frame = tk.Frame(rename_frame_parent, pady=15)
    rename_frame.pack(fill="x")

    tk.Label(rename_frame, text="Rename new image as (without extension):").pack(side="left", padx=5)
    rename_entry = tk.Entry(rename_frame, width=30)
    rename_entry.pack(side="left", padx=5)

    def rename_file():
        new_name = rename_entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Please enter a new name.")
            return
        new_path = os.path.join(HEADSHOT_FOLDER, new_name + os.path.splitext(saved_path)[-1])
        if os.path.exists(new_path):
            messagebox.showerror("Error", "A file with that name already exists.")
            return
        try:
            os.rename(saved_path, new_path)
            messagebox.showinfo("Rename Complete", f"File renamed to {new_name + os.path.splitext(saved_path)[-1]}") 
            top.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Rename failed: {e}")

    tk.Button(rename_frame, text="Rename", command=rename_file).pack(side="left", padx=5)
    rename_entry.bind("<Return>", lambda event: rename_file())

def save_image_to_folder(src_path, folder):
    ext = os.path.splitext(src_path)[-1]
    unique_name = str(uuid.uuid4()) + ext
    dst_path = os.path.join(folder, unique_name)
    shutil.copy2(src_path, dst_path)
    return dst_path

def process_image():
    filepath = filedialog.askopenfilename(
        initialdir=DEFAULT_OPEN_PATH,
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if not filepath:
        return

    known_encodings, known_paths = load_known_encodings(HEADSHOT_FOLDER)
    matched_pairs = compare_faces_to_all(filepath, known_encodings, known_paths)

    saved_path = save_image_to_folder(filepath, HEADSHOT_FOLDER)

    if matched_pairs:
        messagebox.showinfo("Matches Found", f"{len(matched_pairs)} match(es) found. Showing images for review.")
        updated_pairs = [(old, saved_path) for old, _ in matched_pairs]
        create_scrollable_review_window(updated_pairs, saved_path)
    else:
        messagebox.showinfo("No Match", "No match found. Image has been saved for future comparisons.")
        create_scrollable_review_window([], saved_path)

def ensure_headshot_folder():
    if not os.path.exists(HEADSHOT_FOLDER):
        os.makedirs(HEADSHOT_FOLDER)

def main():
    ensure_headshot_folder()

    root = tk.Tk()
    root.title("Face Comparison Tool")

    window_width = 400
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    label = tk.Label(root, text="Select an image to compare:")
    label.pack(pady=10)

    button = tk.Button(root, text="Choose Image", command=process_image, height=2, width=20)
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
