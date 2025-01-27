"""
PDF to Audio Converter
======================

This script converts PDF files to audio using PyPDF4, pyttsx3, and pydub libraries with a GUI built with tkinter.

Modules:
- PyPDF4: For reading PDF files
- pyttsx3: For text-to-speech conversion
- tkinter: For creating the GUI
- pydub: For audio format conversion

Functions:
- convert_pdf_to_audio: Reads the PDF, converts its text to audio, and saves it as an MP3 file
- select_pdf: Opens file dialogs to select the PDF and the save location for the audio file
- main: Initializes and hides the main Tkinter window, then runs the file selection process
"""

import fitz  # PyMuPDF
import pyttsx3
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import logging
import time
import pygame
import os

logging.basicConfig(level=logging.DEBUG)

def convert_pdf_to_audio(pdf_path, audio_path, progress_var, status_label, open_button, selected_voice, voice_index_map):
    try:
        pdf_document = fitz.open(pdf_path)
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[voice_index_map[selected_voice.get()]].id)
        text = ""
        num_pages = len(pdf_document)
        delay_per_page = 0.1  # Adjust this value to control the delay per page
        total_delay = num_pages * delay_per_page
        for page_num in range(num_pages):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
            progress_var.set((page_num + 1) / num_pages * 100)
            status_label.config(text=f"Processing page {page_num + 1} of {num_pages}")
            status_label.update_idletasks()
            time.sleep(delay_per_page)  # Add delay for progress bar
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        logging.info("Converted successfully!")
        status_label.config(text=f"Conversion successful! Playing audio: {audio_path}")
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        open_button.config(state=tk.NORMAL, command=lambda: os.startfile(audio_path))
    except Exception as e:
        logging.error(f"Error during conversion: {e}")
        status_label.config(text=f"Error: {e}")

def select_pdf(progress_var, status_label, open_button, view_button):
    try:
        pdf_path = filedialog.askopenfilename()
        if not pdf_path:
            logging.warning("No PDF file selected.")
            status_label.config(text="No PDF file selected.")
            return None
        view_button.config(state=tk.NORMAL, command=lambda: os.startfile(pdf_path))
        return pdf_path
    except Exception as e:
        logging.error(f"Error during file selection: {e}")
        status_label.config(text=f"Error: {e}")
        return None

def save_audio(pdf_path, progress_var, status_label, open_button, selected_voice, voice_index_map):
    try:
        audio_path = filedialog.asksaveasfilename(defaultextension=".mp3")
        if not audio_path:
            logging.warning("No save location selected.")
            status_label.config(text="No save location selected.")
            return
        convert_pdf_to_audio(pdf_path, audio_path, progress_var, status_label, open_button, selected_voice, voice_index_map)
    except Exception as e:
        logging.error(f"Error during file selection: {e}")
        status_label.config(text=f"Error: {e}")

def main():
    def on_select_pdf():
        pdf_path = select_pdf(progress_var, status_label, open_button, view_button)
        if pdf_path:
            convert_button.config(state=tk.NORMAL, command=lambda: save_audio(pdf_path, progress_var, status_label, open_button, selected_voice, voice_index_map))

    def clear():
        progress_var.set(0)
        status_label.config(text="Status: Waiting for user action")
        open_button.config(state=tk.DISABLED)
        view_button.config(state=tk.DISABLED)
        convert_button.config(state=tk.DISABLED)

    root = tk.Tk()
    root.title("PDF to Audio Converter")
    root.configure(bg="#f0f0f0")

    header_label = tk.Label(root, text="PDF to Audio Converter", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
    header_label.grid(row=0, column=0, columnspan=3, pady=10)

    select_button = tk.Button(root, text="Select PDF", command=on_select_pdf, font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
    select_button.grid(row=1, column=0, padx=10, pady=10)

    convert_button = tk.Button(root, text="Convert", state=tk.DISABLED, font=("Helvetica", 12), bg="#2196F3", fg="white", padx=10, pady=5)
    convert_button.grid(row=1, column=1, padx=10, pady=10)

    clear_button = tk.Button(root, text="Clear", command=clear, font=("Helvetica", 12), bg="#f44336", fg="white", padx=10, pady=5)
    clear_button.grid(row=1, column=2, padx=10, pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.grid(row=2, column=0, columnspan=3, pady=10, padx=20, sticky="ew")

    status_label = tk.Label(root, text="Status: Waiting for user action", font=("Helvetica", 10), bg="#f0f0f0")
    status_label.grid(row=3, column=0, columnspan=3, pady=10)

    open_button = tk.Button(root, text="Open Generated Audio", state=tk.DISABLED, font=("Helvetica", 12), bg="#FF9800", fg="black", padx=10, pady=5)
    open_button.grid(row=4, column=0, padx=10, pady=10)

    view_button = tk.Button(root, text="View PDF", state=tk.DISABLED, font=("Helvetica", 12), bg="#9C27B0", fg="white", padx=10, pady=5)
    view_button.grid(row=4, column=1, padx=10, pady=10)

    close_button = tk.Button(root, text="Close", command=root.quit, font=("Helvetica", 12), bg="#607D8B", fg="white", padx=10, pady=5)
    close_button.grid(row=4, column=2, padx=10, pady=10)

    voices = pyttsx3.init().getProperty('voices')
    voice_options = [f"{voice.name} ({voice.languages[0] if voice.languages else 'Unknown'})" for voice in voices]
    voice_index_map = {voice_options[i]: i for i in range(len(voice_options))}
    selected_voice = tk.StringVar(value=voice_options[0])
    voice_label = tk.Label(root, text="Select Voice:", font=("Helvetica", 12), bg="#f0f0f0")
    voice_label.grid(row=5, column=0, padx=10, pady=10)
    voice_menu = tk.OptionMenu(root, selected_voice, *voice_options)
    voice_menu.config(font=("Helvetica", 12), bg="#f0f0f0")
    voice_menu.grid(row=5, column=1, columnspan=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
