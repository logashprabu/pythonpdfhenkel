import os
import argparse
from PDFNetPython3.PDFNetPython import *
from typing import Tuple

def sign_file(input_file: str, signatureID: str, x_coordinate: int, 
              y_coordinate: int, cert_file: str, key_file: str, key_password: str = '', 
              pages: Tuple = None, output_file: str = None):
    """Sign a PDF file using an existing certificate and private key."""
    if not output_file:
        output_file = (os.path.splitext(input_file)[0]) + "_signed.pdf"

    # Initialize the library
    PDFNet.Initialize()
    doc = PDFDoc(input_file)

    # Create a signature field
    sigField = SignatureWidget.Create(doc, Rect(
        x_coordinate, y_coordinate, x_coordinate + 100, y_coordinate + 50), signatureID)

    # Iterate throughout document pages
    for page in range(1, (doc.GetPageCount() + 1)):
        if pages and str(page) not in pages:
            continue
        pg = doc.GetPage(page)
        pg.AnnotPushBack(sigField)

    # Signature image
    sign_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "signature.jpg")
    
    # Retrieve the signature field
    approval_field = doc.GetField(signatureID)
    approval_signature_digsig_field = DigitalSignatureField(approval_field)

    # Add appearance to the signature field
    img = Image.Create(doc.GetSDFDoc(), sign_image_path)
    found_approval_signature_widget = SignatureWidget(approval_field.GetSDFObj())
    found_approval_signature_widget.CreateSignatureAppearance(img)

    # Prepare the signature and signature handler for signing
    approval_signature_digsig_field.SignOnNextSave(key_file, key_password)

    # The signing will be done during the following incremental save operation
    doc.Save(output_file, SDFDoc.e_incremental)

    # Develop a process summary
    summary = {
        "Input File": input_file,
        "Signature ID": signatureID,
        "Output File": output_file,
        "Signature Image": sign_image_path,
        "Certificate File": cert_file,
        "Key File": key_file
    }

    print("## Summary ########################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in summary.items()))
    print("###################################################################")
    return True


def sign_folder(input_folder: str, signatureID: str, cert_file: str, key_file: str, 
                key_password: str, x_coordinate: int, y_coordinate: int, 
                pages: Tuple = None, recursive: bool = False):
    """Sign all PDF files within a specified folder using an existing certificate and private key."""
    for foldername, dirs, filenames in os.walk(input_folder):
        for filename in filenames:
            if not filename.endswith('.pdf'):
                continue

            inp_pdf_file = os.path.join(foldername, filename)
            print("Processing file =", inp_pdf_file)
            
            sign_file(input_file=inp_pdf_file, signatureID=signatureID, 
                      x_coordinate=x_coordinate, y_coordinate=y_coordinate, 
                      cert_file=cert_file, key_file=key_file, 
                      key_password=key_password, pages=pages)

        if not recursive:
            break


def is_valid_path(path):
    """Validates the path inputted and checks whether it is a file path or a folder path."""
    if not path:
        raise ValueError("Invalid Path")
    if os.path.isfile(path) or os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid Path {path}")


def parse_args():
    """Get user command line parameters."""
    parser = argparse.ArgumentParser(description="Available Options")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path,
                        required=True, help="Enter the path of the file or folder to process")
    parser.add_argument('-s', '--signatureID', dest='signatureID', type=str, 
                        required=True, help="Enter the ID of the signature")
    parser.add_argument('-c', '--cert_file', dest='cert_file', type=str, required=True, 
                        help="Path to the certificate file (e.g., .cer or .crt)")
    parser.add_argument('-k', '--key_file', dest='key_file', type=str, required=True, 
                        help="Path to the private key file (e.g., .pfx or .pem)")
    parser.add_argument('-p', '--key_password', dest='key_password', type=str, default='', 
                        help="Password for the private key file (if applicable)")
    parser.add_argument('-x', '--x_coordinate', dest='x_coordinate', type=int, required=True, 
                        help="Enter the x-coordinate.")
    parser.add_argument('-y', '--y_coordinate', dest='y_coordinate', type=int, required=True, 
                        help="Enter the y-coordinate.")
    parser.add_argument('--pages', dest='pages', type=tuple, default=None, 
                        help="Enter the pages to consider e.g., (1, 3).")
    
    args = parser.parse_args()

    if os.path.isdir(args.input_path):
        parser.add_argument('-r', '--recursive', dest='recursive', default=False, 
                            type=lambda x: str(x).lower() in ['true', '1', 'yes'], 
                            help="Process recursively or non-recursively")

    return vars(args)


if __name__ == '__main__':
    # Parsing command line arguments entered by user
    args = parse_args()

    if os.path.isfile(args['input_path']):
        sign_file(input_file=args['input_path'], signatureID=args['signatureID'], 
                  x_coordinate=args['x_coordinate'], y_coordinate=args['y_coordinate'], 
                  cert_file=args['cert_file'], key_file=args['key_file'], 
                  key_password=args['key_password'], pages=args['pages'])
    elif os.path.isdir(args['input_path']):
        sign_folder(input_folder=args['input_path'], signatureID=args['signatureID'], 
                    cert_file=args['cert_file'], key_file=args['key_file'], 
                    key_password=args['key_password'], x_coordinate=args['x_coordinate'], 
                    y_coordinate=args['y_coordinate'], pages=args['pages'], 
                    recursive=args.get('recursive', False))
