import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from PIL import Image, ImageTk

# ---- Helper Functions ----
def generate_summary(bone_type, severity, is_fractured):
    if is_fractured:
        return f"Fracture detected in the {bone_type} bone. Severity level is {severity}. Immediate medical attention is advised."
    else:
        return f"No fracture detected in the {bone_type} bone. Bone appears normal based on X-ray analysis."

def classify_bone_type(image):
    return "metacarpal"

def classify_severity(contours):
    if len(contours) > 15:
        return "severe"
    elif len(contours) > 7:
        return "moderate"
    else:
        return "mild"

def detect_fracture(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image could not be loaded. Please check the path.")

    blur = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    is_fractured = len(contours) > 10
    return is_fractured, contours, edges

def generate_pdf(image_path, bone_type, severity, is_fractured, summary, contours, patient_data):
    file_name = f"fracture_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 780, "Multiple Bone Fracture Detection")
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(50, 765, "Model built by Pavithra B, Samyuktha C S")

    c.setFont("Helvetica", 11)
    c.drawString(50, 740, f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 720, f"Patient Name: {patient_data['Patient Name']}")
    c.drawString(50, 700, f"Age / Gender: {patient_data['Age']} / {patient_data['Gender']}")
    c.drawString(50, 680, f"Lab Technician: {patient_data['Technician']}")
    c.drawString(50, 660, f"Bone Type: {bone_type}")
    c.drawString(50, 640, f"Fractured: {'Yes' if is_fractured else 'No'}")
    c.drawString(50, 620, f"Severity: {severity}")

    c.drawString(50, 600, "AI Summary:")
    text = c.beginText(50, 580)
    text.setFont("Helvetica-Oblique", 12)
    for line in summary.split('\n'):
        text.textLine(line)
    c.drawText(text)

    img = cv2.imread(image_path)
    cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    temp_img_path = "temp_overlay.jpg"
    cv2.imwrite(temp_img_path, img)

    c.drawImage(temp_img_path, 50, 300, width=400, height=250)
    c.showPage()
    c.save()
    print(f"PDF report saved as {file_name}")

# ---- UI Class ----
class FractureDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fracture Detection System")
        self.root.geometry("700x600")
        self.root.configure(bg="#f5f7fa")

        self.header_frame = tk.Frame(self.root, bg="#f5f7fa")
        self.header_frame.pack(pady=10)
        tk.Label(self.header_frame, text="\U0001F9B4 Multiple Bone Fracture Detection", font=("Helvetica", 20, "bold"), fg="#2e3f4f", bg="#f5f7fa").pack()
        tk.Label(self.header_frame, text="Model built by Pavithra B, Samyuktha C S", font=("Helvetica", 12, "italic"), fg="#555", bg="#f5f7fa").pack()

        self.info_frame = tk.Frame(self.root, bg="#f5f7fa")
        self.info_frame.pack(pady=10)

        self.entries = {}
        for idx, label in enumerate(["Patient Name", "Age", "Gender", "Technician"]):
            tk.Label(self.info_frame, text=label + ":", bg="#f5f7fa").grid(row=idx, column=0, sticky='e', padx=5, pady=5)
            entry = tk.Entry(self.info_frame, width=30)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[label] = entry

        self.img_label = tk.Label(self.root, text="No image selected", bg="#f5f7fa")
        self.img_label.pack(pady=10)

        tk.Button(self.root, text="Choose Image", command=self.choose_image, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=5)

        self.result_label = tk.Label(self.root, text="", bg="#f5f7fa", fg="black", font=("Helvetica", 12))
        self.result_label.pack(pady=10)

    def choose_image(self):
        image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if not image_path:
            return

        self.img_label.config(text=os.path.basename(image_path))
        try:
            is_fractured, contours, edges = detect_fracture(image_path)
            bone_type = classify_bone_type(image_path)
            severity = classify_severity(contours) if is_fractured else "N/A"
            summary = generate_summary(bone_type, severity, is_fractured)

            patient_data = {k: v.get() for k, v in self.entries.items()}
            generate_pdf(image_path, bone_type, severity, is_fractured, summary, contours, patient_data)
            self.result_label.config(text=f"Report generated successfully. Fracture: {'Yes' if is_fractured else 'No'} | Severity: {severity}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ---- Main Execution ----
if __name__ == "__main__":
    root = tk.Tk()
    app = FractureDetectionApp(root)
    root.mainloop()
