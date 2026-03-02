"""Simple desktop app for local Whisper transcription.

Designed for Windows users who prefer a graphical interface.
"""

from __future__ import annotations

import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import torch
import whisper

MODEL_OPTIONS = ["tiny", "base", "small", "medium", "large", "turbo"]
LANGUAGE_OPTIONS = ["auto", "pt", "en", "es", "fr", "de", "it", "ja"]
TASK_OPTIONS = ["transcribe", "translate"]


class WhisperApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Whisper Local Transcription")
        self.root.geometry("760x520")

        self.audio_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        self.model_name = tk.StringVar(value="turbo")
        self.language = tk.StringVar(value="auto")
        self.task = tk.StringVar(value="transcribe")
        self.status = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="Whisper Local Transcription (CPU/GPU)",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        ttk.Label(frame, text="Audio file:").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.audio_path, width=70).grid(
            row=1, column=1, sticky="ew", pady=6
        )
        ttk.Button(frame, text="Browse", command=self.select_audio).grid(
            row=1, column=2, padx=(8, 0), pady=6
        )

        ttk.Label(frame, text="Output folder:").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.output_dir, width=70).grid(
            row=2, column=1, sticky="ew", pady=6
        )
        ttk.Button(frame, text="Browse", command=self.select_output_dir).grid(
            row=2, column=2, padx=(8, 0), pady=6
        )

        ttk.Label(frame, text="Model:").grid(row=3, column=0, sticky="w", pady=6)
        ttk.Combobox(
            frame,
            textvariable=self.model_name,
            values=MODEL_OPTIONS,
            state="readonly",
            width=16,
        ).grid(row=3, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Language:").grid(row=4, column=0, sticky="w", pady=6)
        ttk.Combobox(
            frame,
            textvariable=self.language,
            values=LANGUAGE_OPTIONS,
            state="readonly",
            width=16,
        ).grid(row=4, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Task:").grid(row=5, column=0, sticky="w", pady=6)
        ttk.Combobox(
            frame,
            textvariable=self.task,
            values=TASK_OPTIONS,
            state="readonly",
            width=16,
        ).grid(row=5, column=1, sticky="w", pady=6)

        ttk.Button(frame, text="Start transcription", command=self.start_transcription).grid(
            row=6, column=0, columnspan=3, sticky="ew", pady=(14, 10)
        )

        ttk.Label(frame, text="Recognized text:").grid(row=7, column=0, sticky="nw", pady=(8, 4))
        self.output_text = tk.Text(frame, height=14, wrap=tk.WORD)
        self.output_text.grid(row=8, column=0, columnspan=3, sticky="nsew")

        ttk.Label(frame, textvariable=self.status).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(10, 0)
        )

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(8, weight=1)

    def select_audio(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.flac *.ogg *.mp4 *.webm"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.audio_path.set(file_path)

    def select_output_dir(self) -> None:
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_dir.set(folder)

    def start_transcription(self) -> None:
        if not self.audio_path.get().strip():
            messagebox.showwarning("Missing audio", "Choose an audio file before starting.")
            return

        audio_file = Path(self.audio_path.get())
        if not audio_file.exists():
            messagebox.showerror("Invalid file", "The selected audio file does not exist.")
            return

        output_dir = Path(self.output_dir.get())
        output_dir.mkdir(parents=True, exist_ok=True)

        self.output_text.delete("1.0", tk.END)
        self.status.set("Running... This can take a while for longer files.")

        thread = threading.Thread(
            target=self._run_transcription,
            args=(audio_file, output_dir),
            daemon=True,
        )
        thread.start()

    def _run_transcription(self, audio_file: Path, output_dir: Path) -> None:
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = whisper.load_model(self.model_name.get(), device=device)

            language = None if self.language.get() == "auto" else self.language.get()
            result = model.transcribe(
                str(audio_file),
                language=language,
                task=self.task.get(),
                fp16=torch.cuda.is_available(),
            )

            text = result.get("text", "").strip()
            txt_file = output_dir / f"{audio_file.stem}.txt"
            txt_file.write_text(text, encoding="utf-8")

            self.root.after(0, self._on_success, text, txt_file)
        except Exception as exc:  # pragma: no cover
            self.root.after(0, self._on_error, str(exc))

    def _on_success(self, text: str, txt_file: Path) -> None:
        self.output_text.insert(tk.END, text)
        self.status.set(f"Done. Saved transcript to: {txt_file}")
        messagebox.showinfo("Finished", f"Transcription complete!\n\nSaved to:\n{txt_file}")

    def _on_error(self, error_message: str) -> None:
        self.status.set("Failed")
        messagebox.showerror(
            "Error",
            "An error occurred while transcribing.\n"
            f"Details: {error_message}\n\n"
            "Tip: make sure ffmpeg is installed and available in PATH.",
        )


def main() -> None:
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
