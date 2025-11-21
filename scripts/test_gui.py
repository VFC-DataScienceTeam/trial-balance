"""
Quick test to verify tkinter is working
"""
import tkinter as tk
from tkinter import messagebox

def test_tkinter():
    """Test if tkinter GUI works"""
    try:
        root = tk.Tk()
        root.title("Tkinter Test")
        root.geometry("400x200")
        
        label = tk.Label(root, text="✅ Tkinter is working!", font=('Arial', 14, 'bold'))
        label.pack(pady=50)
        
        button = tk.Button(root, text="Close", command=root.quit)
        button.pack()
        
        print("GUI window should be visible now...")
        root.mainloop()
        print("GUI closed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    test_tkinter()
