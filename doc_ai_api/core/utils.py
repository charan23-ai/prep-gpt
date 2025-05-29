import os
import traceback
from PyPDF2 import PdfReader
from django.conf import settings as config

from PIL import Image, ImageDraw, ImageFont
import textwrap

import json
from dotenv import load_dotenv  
from googleapiclient.discovery import build  


# Simple cleaning for this specific task(To be impoved upon)
def clean_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.strip().isdigit():
            continue
        if any(
            keyword in line.upper()
            for keyword in [
                "CHAPTER",
                "PHYSICS",
                "MECHANICAL PROPERTIES",
                "REPRINT",
                "SUMMARY",
                "POINTS TO PONDER",
                "EXERCISES",
                "==START OF OCR",
                "==END OF OCR",
            ]
        ):
            if not any(
                keyword in line.upper()
                for keyword in [
                    "INTRODUCTION",
                    "STRESS",
                    "HOOK",
                    "CURVE",
                    "MODULI",
                    "APPLICATIONS",
                    "POISSON",
                    "8.1",
                    "8.2",
                    "8.3",
                    "8.4",
                    "8.5",
                    "8.6",
                ]
            ):
                continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)



def convert_pdf_to_text_util(pdf_file):
    if pdf_file is None:
        return "Please upload a PDF file.", None

    try:
        os.makedirs(config.PDF_TEMP_DIR, exist_ok=True)
        pdf_path = pdf_file.name
        file_name = os.path.basename(pdf_path)
        base_name, _ = os.path.splitext(file_name)
        output_text_path = os.path.join(config.PDF_TEMP_DIR, f"{base_name}.txt")

        print(f"Converting PDF: {pdf_path} to {output_text_path}")
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            print("Extracted text is empty or only whitespace.")
            return (
                "Error: Could not extract text from the PDF. It might be an image-based PDF without OCR.",
                None,
            )

        with open(output_text_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Successfully converted PDF to text: {output_text_path}")
        return (
            f"Successfully converted '{file_name}' to text. Text file saved temporarily as '{os.path.basename(output_text_path)}'.",
            output_text_path,
        )

    except Exception as e:
        error_message = f"Error during PDF conversion: {e}\n{traceback.format_exc()}"
        print(error_message)
        return f"An error occurred during conversion: {e}", None



def render_text_with_custom_handwriting(
    text_content: str,
    output_image_path: str,
    custom_font_path: str,
    font_size: int = 40,
    text_color: tuple = (50, 50, 50),  
    background_color: tuple = (255, 255, 255),  
    line_spacing_factor: float = 1.3, 
    max_width_pixels: int = 800,  
    padding: int = 50,  
):
    
    if not os.path.exists(custom_font_path):
        print(f"Error: Custom font file not found at '{custom_font_path}'.")
        print("Please ensure CUSTOM_HANDWRITING_FONT_PATH in config.py is correct.")
        return False

    try:
        font = ImageFont.truetype(custom_font_path, font_size)
    except IOError:
        print(f"Error: Could not load font from '{custom_font_path}'.")
        print(
            "Please ensure the font file exists and the path is correct, and it's a valid TTF file."
        )
        return False
    except Exception as e:
        print(f"An unexpected error occurred loading font: {e}")
        return False

    avg_char_width_estimate = font_size * 0.55
    chars_per_line = int(max_width_pixels / avg_char_width_estimate) - 5

    wrapped_lines = []
    for paragraph in text_content.split("\n"):
        if paragraph.strip() == "":
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(
                textwrap.wrap(paragraph, width=chars_per_line, break_long_words=False)
            )

    if not wrapped_lines:
        print("No text to render for handwriting.")
        return False

    line_height = int(font_size * line_spacing_factor)
    total_text_height = len(wrapped_lines) * line_height

    img_width = max_width_pixels + 2 * padding
    img_height = total_text_height + 2 * padding

    if img_height < 100:
        img_height = 100
    if img_width < 200:
        img_width = 200

    img = Image.new("RGB", (img_width, img_height), color=background_color)
    draw = ImageDraw.Draw(img)

    y_offset = padding
    for line in wrapped_lines:
        draw.text((padding, y_offset), line, font=font, fill=text_color)
        y_offset += line_height

    try:
        img.save(output_image_path)
        print(
            f"Text rendered to image successfully! Output saved to: '{output_image_path}'"
        )
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def _google_custom_search_raw(query: str, num_results: int = 5):
    load_dotenv()  

    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        return "Error: GOOGLE_API_KEY or GOOGLE_CSE_ID not found in .env file. Google Custom Search is disabled."

    try:
        service = build("customsearch", "v1", developerKey=api_key)

        res = service.cse().list(q=query, cx=cse_id, num=num_results).execute()

        if "items" in res and res["items"]:
            formatted_results = []
            for i, item in enumerate(res["items"]):
                title = item.get("title", "N/A")
                link = item.get("link", "N/A")
                snippet = item.get("snippet", "N/A")
                formatted_results.append(
                    f"Title: {title}\nLink: {link}\nSnippet: {snippet}"
                )
            return "\n\n---\n\n".join(formatted_results)
        else:
            return "No relevant search results found."

    except Exception as e:
        return f"An error occurred during Google Custom Search: {e}. Ensure API key and CSE ID are correct and billing is enabled."


def google_custom_search_tool_wrapper(query: str) -> str:
    return _google_custom_search_raw(
        query, num_results=5
    )  
