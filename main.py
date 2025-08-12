import tkinter as tk
from app import OptimizationApp

def main() -> None:
    root = tk.Tk()
    root.title("Kesim Optimizasyon Uygulaması")
    app = OptimizationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
