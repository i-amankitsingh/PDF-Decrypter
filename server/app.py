import os
from PyPDF2 import PdfReader, PdfWriter
from Crypto.Cipher import AES
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Import CORS

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS for all routes (you can also specify specific origins)
CORS(app)  # This will allow CORS for all origins by default

# Folder where PDFs will be saved/uploaded
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def process_pdf(file_path, folder_name, password=None):
    """
    Processes a PDF file:
    - Checks if the PDF is encrypted
    - Unlocks it (if encrypted and password provided)
    - Saves both original and unlocked copies to the upload folder

    Args:
    - file_path (str): Path to the input PDF file
    - upload_folder (str): Path to the upload folder
    - password (str, optional): Password to decrypt the PDF (if encrypted)

    Returns:
    - dict: Information about the operation
    """
    try:
        # Create the upload folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        # Define file paths
        original_pdf_path = os.path.join(folder_name, os.path.basename(file_path))
        unlocked_pdf_path = os.path.join(folder_name, f"unlocked_{os.path.basename(file_path)}")

        # Read the PDF
        reader = PdfReader(file_path)
        writer = PdfWriter()

        # Check if the PDF is encrypted
        if reader.is_encrypted:
            if password:
                # Try decrypting with the provided password
                if not reader.decrypt(password):
                    return {"status": "error", "message": "Failed to decrypt PDF with the provided password.", "isUnlocked": False}
                print("PDF decrypted successfully.")
            else:
                return {"status": "error", "message": "PDF is encrypted. A password is required to decrypt it.", "isUnlocked": False}

        # Write all pages to the unlocked PDF
        for page in reader.pages:
            writer.add_page(page)

        # Save the unlocked copy
        with open(unlocked_pdf_path, "wb") as f:
            writer.write(f)

        # Save the original copy
        os.rename(file_path, original_pdf_path)

        return {
            "status": "success",
            "message": "PDF processed successfully.",
            "original_pdf": original_pdf_path,
            "unlocked_pdf": unlocked_pdf_path,
            "isUnlocked": True,
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to process PDF: {str(e)}"}


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """
    Route to handle the PDF upload and decryption.
    """
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']
    password = request.form.get('password', None)  # Get password from form data if provided

    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Process the PDF
    result = process_pdf(file_path, app.config['UPLOAD_FOLDER'], password)
    print("Result ", result)
    
    if result["status"] == "success":
        download_file_path = result["unlocked_pdf"]
        filename = "Unlocked_PDF"
        return send_file(download_file_path, as_attachment=True, download_name=filename, mimetype='application/pdf')
    else:
        return jsonify(result), 400


if __name__ == "__main__":
    app.run(debug=True)
