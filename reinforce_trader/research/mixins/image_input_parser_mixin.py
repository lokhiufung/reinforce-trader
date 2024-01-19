
import base64


class ImageInputParserMixin:
    def parse_local_image(self, file_path: str):
        """Parse a local image file to base64 encoded image"""
        with open(file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_image
    
    def parse_local_images(self, file_paths: list[str]):
        """Parse a list of local image files to base64 encoded images"""
        return [self.parse_local_image(file_path) for file_path in file_paths]


