import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pikepdf
from pdf2image import convert_from_path
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


class PDFUtils:
    def merge_PDFs(self, pdfs_dir, merged_file_name="output.pdf"):
        """
        Merges all PDFs present in the given directory and saves it as merged_file_name.
        If merged_file_name is not specified, the merged file will be saved as 'output.pdf'.
        :param pdfs_dir: directory containing the PDFs to be merged
        :param merged_file_name: name of the merged file
        """
        print("Started to merge PDFs")
        pdf_list = [
            f"{pdfs_dir}{pdf}"
            for pdf in sorted(os.listdir(pdfs_dir), key=lambda x: int(x[:-4]))
        ]
        merger = pikepdf.Pdf.new()
        for pdf in pdf_list:
            merger.pages.extend(pikepdf.open(pdf).pages)
        merger.save(merged_file_name)
        print(f"Individual PDFs merged into {merged_file_name}")

    def convert_img_dir_to_pdfs(self, img_dir, output_dir="converted_pdf_files/"):
        """
        Converts all images present in the given directory to pdfs and saves them in the output_dir.
        If output_dir is not specified, the pdfs will be saved in the directory 'converted_pdf_files/'
        :param img_dir: directory containing the images
        :param output_dir: directory to save the converted pdfs
        """
        print("Started to convert images to PDFs")
        images_list = sorted(os.listdir(img_dir), key=lambda x: int(x[:-4]))

        def img_to_pdf(image):
            img = Image.open(os.path.join(img_dir, image))
            pdf_file = open(f"{output_dir}{image[:-4]}.pdf", "wb")
            canvas = Canvas(pdf_file, pagesize=(img.width, img.height))
            canvas.drawImage(ImageReader(img), 0, 0, img.width, img.height)
            canvas.showPage()
            canvas.save()
            pdf_file.close()

        with ThreadPoolExecutor() as executor:
            future_create_pdf = [
                executor.submit(img_to_pdf, img) for img in images_list
            ]
            for future in as_completed(future_create_pdf):
                future.result()
        print(f"Images converted to PDF. Output PDFs saved to {output_dir}")

    def split_pdf_to_images(self, original_pdf, no_of_slices):
        """
        Splits the given original_pdf into sliced images and saves them in the directory 'split_images/'.
        :param original_pdf: path to the original pdf
        :param no_of_slices: number of slices to divide the pdf into
        """
        print("Started to split PDF to images")
        pages = convert_from_path(original_pdf, 500)

        def process_page(i, page):
            im = page.convert("RGB")
            width, height = im.size
            for j in range(no_of_slices):
                a = im.crop(
                    (
                        0,
                        j * (height / no_of_slices),
                        width,
                        (j + 1) * height / no_of_slices,
                    )
                )
                a.save(f"split_images/{i * no_of_slices + 1+ j}.png")

        with ThreadPoolExecutor() as executor:
            future_to_page = [
                executor.submit(process_page, i, page) for i, page in enumerate(pages)
            ]
            for future in as_completed(future_to_page):
                future.result()
        print(f"{original_pdf} split into images. Images saved to split_images/")


if __name__ == "__main__":
    os.system("rm -rf output.pdf")
    os.system("mkdir converted_pdf_files")
    os.system("mkdir split_images")
    pdf_util = PDFUtils()
    pdf_util.split_pdf_to_images("original.pdf", 5)
    pdf_util.convert_img_dir_to_pdfs("split_images")
    pdf_util.merge_PDFs("converted_pdf_files/")
