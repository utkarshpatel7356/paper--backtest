import fitz  # PyMuPDF
import PIL.Image
import io

def convert_pdf_to_images(pdf_path, zoom=2.0):
    """
    Converts a PDF into a list of PIL Images.
    Args:
        pdf_path (str): Path to the PDF file.
        zoom (float): Zoom factor. 2.0 = 200% resolution (crucial for math symbols).
    Returns:
        list[PIL.Image]: List of page images.
    """
    try:
        doc = fitz.open(pdf_path)
        images = []
        
        print(f"📄 Processing: {pdf_path} ({len(doc)} pages)")
        
        for i, page in enumerate(doc):
            # Create a transformation matrix for higher resolution
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = PIL.Image.open(io.BytesIO(img_data))
            images.append(img)
            
        return images
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return []