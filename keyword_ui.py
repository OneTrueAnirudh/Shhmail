import tkinter as tk
from tkinter import messagebox
from keyword_mgr import KeywordManager

class KeywordTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyword Tracker")
        self.keyword_manager = KeywordManager()

        # Display currently tracked keywords
        self.current_keywords_label = tk.Label(root, text="Currently Tracked Keywords:")
        self.current_keywords_label.pack()

        self.keywords_listbox = tk.Listbox(root, height=10, width=50)
        self.keywords_listbox.pack()
        self.refresh_keywords()

        # Add keyword
        self.add_label = tk.Label(root, text="Enter a keyword to track:")
        self.add_label.pack()
        self.add_entry = tk.Entry(root, width=30)
        self.add_entry.pack()
        self.add_button = tk.Button(root, text="Add Keyword", command=self.add_keyword)
        self.add_button.pack()

        # Remove keyword
        self.remove_label = tk.Label(root, text="Enter a keyword to remove:")
        self.remove_label.pack()
        self.remove_entry = tk.Entry(root, width=30)
        self.remove_entry.pack()
        self.remove_button = tk.Button(root, text="Remove Keyword", command=self.remove_keyword)
        self.remove_button.pack()

        # Submit button
        self.submit_button = tk.Button(root, text="Submit", command=root.destroy)
        self.submit_button.pack()

    def refresh_keywords(self):
        self.keywords_listbox.delete(0, tk.END)
        keywords = self.keyword_manager.load_keywords()
        for keyword in keywords:
            self.keywords_listbox.insert(tk.END, keyword)

    def add_keyword(self):
        keyword = self.add_entry.get().strip()
        if keyword:
            self.keyword_manager.add_keyword(keyword)
            self.refresh_keywords()
            messagebox.showinfo("Success", f"Keyword '{keyword}' added.")
        else:
            messagebox.showwarning("Warning", "No keyword entered.")

    def remove_keyword(self):
        keyword = self.remove_entry.get().strip()
        if keyword:
            self.keyword_manager.remove_keyword(keyword)
            self.refresh_keywords()
            messagebox.showinfo("Success", f"Keyword '{keyword}' removed.")
        else:
            messagebox.showwarning("Warning", "No keyword entered.")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = KeywordTrackerApp(root)
#     root.mainloop()
