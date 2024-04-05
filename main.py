from exifread import process_file
from logging import basicConfig, warning, ERROR, error
from sys import exit, version_info, argv

# Set the logging level to ERROR
basicConfig(level=ERROR)


class ShutterCounter:
    """
    A class used to represent a Shutter Counter

    Attributes
    ----------
    image_path : str
        a formatted string to print out the path where the image is located
    shutter_tag : str
        a string representing the shutter tag (default is 'MakerNote TotalShutterReleases')
    supported_models : list
        a list containing the supported camera models (default is ['NIKON D850', 'NIKON D810', 'NIKON D800'])

    Methods
    -------
    get_shutter_count(output_type: int or str = 'int') -> int or str or None:
        Returns the shutter count of the image if possible, else returns None
    """

    def __init__(self, image_path, shutter_tag='MakerNote TotalShutterReleases'):
        """
        Constructs all the necessary attributes for the ShutterCounter object.

        Parameters
        ----------
            image_path : str
                the path where the image is located
            shutter_tag : str
                the shutter tag (default is 'MakerNote TotalShutterReleases')
        """

        self.image_path = image_path
        self.shutter_tag = shutter_tag
        self.supported_models = [
            'NIKON D850',
            'NIKON D810',
            'NIKON D800'
        ]

    def get_shutter_count(self, output_type: int or str = 'int') -> int or str or None:
        """
        Returns the shutter count of the image if possible, else returns None

        Parameters
        ----------
            output_type : int or str
                the type of the output (default is 'int')

        Returns
        -------
            int or str or None
                the shutter count if possible, else None
        """

        try:
            with open(self.image_path, 'rb') as file:
                tags = process_file(file)
                camera_model = str(tags['Image Model'])

                if camera_model not in self.supported_models:
                    error(f"Your camera model {camera_model} is currently not supported.")
                    exit(1)

                if self.shutter_tag in tags:
                    shutter_count_str = str(tags[self.shutter_tag])

                    try:
                        if len(argv) > 2 and argv[2] == 'int':
                            output = int(shutter_count_str)
                        else:
                            output = str(f"Shutter count: {shutter_count_str}")

                        return output

                    except ValueError:
                        error(f"Could not convert shutter count to ${output_type}: {shutter_count_str}")
                        exit(1)
                else:
                    warning(f"The shutter count could not be found in the EXIF data.")
                    exit(1)

        except (FileNotFoundError, IOError):
            error(f"Could not find or open the image file: {self.image_path}")
            exit(1)


# Main execution
if __name__ == "__main__":
    result_type = 'int'

    # Check if the image path is provided as an argument
    if len(argv) < 2:
        print('Please provide an image path as an argument.')
        exit(1)

    # Check if the result type is provided as an argument
    if len(argv) > 2 and argv[2] == 'str':
        result_type = argv[2]
        exit(1)

    # Check if help is requested
    if argv[1] == '-h' or argv[1] == '--help':
        print('Usage: python main.py <image_path> (int|str)')
        exit(1)

    # Check if the Python version is 3 or above
    if version_info[0] < 3:
        error("This script requires Python 3.")
        exit(1)

    # Create a ShutterCounter object
    counter = ShutterCounter(argv[1])

    # Get the shutter count
    shutter_count = counter.get_shutter_count()

    # Print the shutter count
    print(shutter_count)
