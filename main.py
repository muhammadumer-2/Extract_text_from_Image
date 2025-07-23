from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import pytesseract
import os

# Initialize main window
root = Tk()
root.title('Text Extraction from Image')
root.geometry('800x600')

# Configure scrollable area
canvas = Canvas(root)
scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# UI Elements
uploaded_img = Label(scrollable_frame)
result_frame = Frame(scrollable_frame)
uploaded_img.pack(pady=10)
result_frame.pack(fill="both", expand=True)

def set_tesseract_path():
    """Try to automatically find Tesseract or prompt user"""
    possible_paths = [
        r'C:/Program Files/Tesseract-OCR/tesseract.exe',
        r'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True
    
    # If not found, ask user to locate it
    path = filedialog.askopenfilename(title="Locate Tesseract OCR executable (tesseract.exe)")
    if path and os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        return True
    
    return False

def extract(path):
    """Extract text from image"""
    for widget in result_frame.winfo_children():
        widget.destroy()
    
    try:
        # Verify Tesseract
        if not hasattr(pytesseract.pytesseract, 'tesseract_cmd') or not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            if not set_tesseract_path():
                messagebox.showerror("Error", "Tesseract OCR not found. Please install it first.")
                return

        # Read and process image
        img = cv2.imread(path)
        if img is None:
            raise ValueError("Could not read the image file")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Perform OCR with config for better accuracy
        custom_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
        
        # Display extracted text with formatting
        current_line = []
        prev_bottom = 0
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60:  # Only high confidence results
                text = data['text'][i]
                top = data['top'][i]
                bottom = top + data['height'][i]
                
                # Group by lines
                if abs(bottom - prev_bottom) > 10 and current_line:
                    Label(result_frame, text=' '.join(current_line), 
                         font=('Arial', 12), wraplength=700, justify='left').pack(anchor='w')
                    current_line = []
                
                current_line.append(text)
                prev_bottom = bottom
        
        if current_line:
            Label(result_frame, text=' '.join(current_line), 
                 font=('Arial', 12), wraplength=700, justify='left').pack(anchor='w')
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

def show_extract_button(path):
    """Show extract button after image upload"""
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, Button) and widget['text'] == "Extract Text":
            widget.destroy()
    
    extractBtn = Button(scrollable_frame, text="Extract Text", 
                       command=lambda: extract(path),
                       bg="#2f2f77", fg="white", 
                       font=('Arial', 12, 'bold'))
    extractBtn.pack(pady=10)

def upload():
    """Handle image upload"""
    try:
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if not path:
            return
            
        image = Image.open(path)
        image.thumbnail((600, 400))  # Resize for display
        img = ImageTk.PhotoImage(image)
        
        uploaded_img.configure(image=img)
        uploaded_img.image = img
        show_extract_button(path)
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not open image:\n{str(e)}")

# Initial setup
if not set_tesseract_path():
    messagebox.showwarning("Warning", 
                         "Tesseract OCR not found in default locations.\n"
                         "You'll be prompted to locate it when needed.")

upload_btn = Button(scrollable_frame, text="Upload Image", 
                   command=upload, bg="#2f2f77", fg="white",
                   height=2, width=20, font=('Arial', 12, 'bold'))
upload_btn.pack(pady=20)

root.mainloop()