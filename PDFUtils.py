import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pikepdf
from pdf2image import convert_from_path
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


class PDFUtils:
    """
    Set of comprehensive PDF Utilities
    """

    def __init__(self) -> None:
        self.msgs = [" W e l c o m e   t o   P D F   U t i l i t y "]

    def show_msg(self) -> None:
        # If your OS is Windows, change 'clear' to 'cls'
        os.system("clear")
        for msg in self.msgs:
            print(msg)

    def clean_output_dir(self, output_dir):

        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        os.system(f"rm -rf {output_dir}/*")

    def merge_PDFs(
        self, pdfs_dir="converted_pdf_files/", merged_file_name="output.pdf"
    ):
        """
        Merges all PDFs present in the given directory and saves it as merged_file_name.
        If merged_file_name is not specified, the merged file will be saved as 'output.pdf'.
        :param pdfs_dir: directory containing the PDFs to be merged
        :param merged_file_name: name of the merged file
        """
        self.msgs.append("Started to merge PDFs")
        self.show_msg()
        pdf_list = [
            f"{pdfs_dir}{pdf}"
            for pdf in sorted(
                os.listdir(pdfs_dir), key=lambda x: int(x[:-4].split("-")[-1])
            )
            if pdf[0] != "."
        ]
        merger = pikepdf.Pdf.new()
        for pdf in pdf_list:
            merger.pages.extend(pikepdf.open(pdf).pages)
        merger.save(merged_file_name)
        self.msgs.pop()
        self.msgs.append("Started to merge PDFs...Done")
        self.msgs.append(f"Individual PDFs merged into {merged_file_name}")
        self.show_msg()

    def convert_img_dir_to_pdfs(
        self,
        img_dir="split_images/",
        output_dir="converted_pdf_files/",
        output_prefix="input",
    ):
        """
        Converts all images present in the given directory to pdfs and saves them in the output_dir.
        If output_dir is not specified, the pdfs will be saved in the directory 'converted_pdf_files/'
        :param img_dir: directory containing the images
        :param output_dir: directory to save the converted pdfs
        :param output_prefix: prefix to be used when saving the converted pdfs
        """
        self.msgs.append("Started to convert images to individual PDFs")
        self.show_msg()

        self.clean_output_dir(output_dir)

        def img_to_pdf(image):
            img = Image.open(os.path.join(img_dir, image))
            pdf_file = open(f"{output_dir}{output_prefix}-{image[:-4]}.pdf", "wb")
            canvas = Canvas(pdf_file, pagesize=(img.width, img.height))
            canvas.drawImage(ImageReader(img), 0, 0, img.width, img.height)
            canvas.showPage()
            canvas.save()
            pdf_file.close()

        with ThreadPoolExecutor() as executor:
            future_create_pdf = [
                executor.submit(img_to_pdf, img)
                for img in os.listdir(img_dir)
                if img[0] != "."
            ]
            for future in as_completed(future_create_pdf):
                future.result()

        self.msgs.pop()
        self.msgs.append("Started to convert images to individual PDFs...Done")
        self.msgs.append(f"Images converted to PDF. Output PDFs saved to {output_dir}")
        self.show_msg()

    def split_pdf_to_images(
        self, original_pdf, no_of_slices, output_dir="split_images"
    ):
        """
        Splits the given original_pdf into sliced images and saves them in the directory 'split_images/'.
        :param original_pdf: path to the original pdf
        :param no_of_slices: number of slices to divide the pdf into
        """
        self.msgs.append("Started to split PDF to images")
        self.show_msg()
        pages = convert_from_path(original_pdf, 500)

        self.clean_output_dir(output_dir)

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
                a.save(f"{output_dir}/{i * no_of_slices + 1+ j}.png")

        with ThreadPoolExecutor() as executor:
            future_to_page = [
                executor.submit(process_page, i, page) for i, page in enumerate(pages)
            ]
            for future in as_completed(future_to_page):
                future.result()
        self.msgs.pop()
        self.msgs.append("Started to split PDF to images...Done")
        self.msgs.append(
            f"{original_pdf} split into images. Images saved to split_images/"
        )
        self.show_msg()


if __name__ == "__main__":

    pdf_util = PDFUtils()
    os.system("rm -rf converted_pdf_files/*")
    os.system("rm -rf split_images/*")
    pdf_util.split_pdf_to_images("original.pdf", 3)
    pdf_util.convert_img_dir_to_pdfs()
    pdf_util.merge_PDFs()
