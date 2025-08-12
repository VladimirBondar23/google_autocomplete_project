import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence  # you need pillow installed
import asyncio
from ai_model import AiModel

MOCK_USERNAME = "mock user"


class AutoCompleteGUI:
    def __init__(self, root, model):
        self.model = model
        self.root = root
        self.current_task = None
        self.debounce_after_id = None

        root.title("AI Text Completion")
        root.geometry("500x400")
        root.resizable(False, False)

        self.label = ttk.Label(root, text="Enter text to complete:")
        self.label.pack(pady=5)

        self.entry = ttk.Entry(root, width=50)
        self.entry.pack(pady=5)
        self.entry.bind("<KeyRelease>", self.on_text_change)

        self.listbox = tk.Listbox(root, width=70, height=15)
        self.listbox.pack(pady=10)

        # Spinner label (overlayed on listbox)
        self.spinner_label = ttk.Label(root)
        self.spinner_frames = []
        self.spinner_index = 0
        self.load_spinner_gif("spinner.gif")
        self.spinner_animation_id = None

        # Hide spinner initially
        self.spinner_label.place_forget()

        self.exit_button = ttk.Button(root, text="Exit", command=root.destroy)
        self.exit_button.pack(pady=5)

        # Setup asyncio event loop integration
        self.loop = asyncio.get_event_loop()
        self.check_asyncio_loop()

    def load_spinner_gif(self, path):
        from PIL import Image, ImageTk, ImageSequence
        img = Image.open(path)
        self.spinner_frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(img)]
        self.spinner_label.config(image="")
        self.spinner_label.image = None

    def animate_spinner(self):
        if not self.spinner_frames:
            return
        frame = self.spinner_frames[self.spinner_index]
        self.spinner_label.config(image=frame)
        self.spinner_label.image = frame
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_frames)
        self.spinner_animation_id = self.root.after(100, self.animate_spinner)

    def start_spinner(self):
        self.spinner_index = 0
        self.animate_spinner()
        # Calculate listbox position relative to root window
        x = self.listbox.winfo_rootx() - self.root.winfo_rootx()
        y = self.listbox.winfo_rooty() - self.root.winfo_rooty()
        w = self.listbox.winfo_width()
        h = self.listbox.winfo_height()
        # Place spinner centered over listbox
        self.spinner_label.place(x=x + w // 2, y=y + h // 2, anchor="center")

    def stop_spinner(self):
        if self.spinner_animation_id:
            self.root.after_cancel(self.spinner_animation_id)
            self.spinner_animation_id = None
        self.spinner_label.place_forget()
        self.spinner_label.config(image="")
        self.spinner_label.image = None

    def check_asyncio_loop(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.root.after(50, self.check_asyncio_loop)

    def on_text_change(self, event):
        if self.debounce_after_id:
            self.root.after_cancel(self.debounce_after_id)
        self.debounce_after_id = self.root.after(400, self.start_fetch_completions)

    def start_fetch_completions(self):
        text_to_complete = self.entry.get().strip()
        if not text_to_complete:
            self.listbox.delete(0, tk.END)
            self.stop_spinner()
            return

        if self.current_task and not self.current_task.done():
            self.current_task.cancel()

        self.listbox.delete(0, tk.END)
        self.start_spinner()

        self.current_task = asyncio.ensure_future(self.fetch_completions(text_to_complete))

    async def fetch_completions(self, text):
        try:
            completions = await self.model.get_best_completions(text, MOCK_USERNAME)
        except asyncio.CancelledError:
            self.stop_spinner()
            return
        except Exception as e:
            self.root.after(0, lambda: self.listbox.insert(tk.END, f"Error: {e}"))
            self.stop_spinner()
            return

        def update_gui():
            self.stop_spinner()
            self.listbox.delete(0, tk.END)
            for c in completions.splitlines():
                stripped = c.strip()
                if stripped:
                    self.listbox.insert(tk.END, stripped)

        self.root.after(0, update_gui)


def main():
    model = AiModel()

    async def setup_and_run():
        await model.add_user(MOCK_USERNAME)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_and_run())

    root = tk.Tk()
    app = AutoCompleteGUI(root, model)
    root.mainloop()


if __name__ == "__main__":
    main()
