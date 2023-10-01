from PIL import Image


@staticmethod
def resize_image(image: Image, length: int) -> Image:
    """
    Resize an image to a square length x length. Return the resized image. It also crops
    part of the image; length: Width and height of the output image.
        Resizing strategy :
        1) resize the smallest side to the desired dimension (e.g. 200)
        2) crop the other side so as to make it fit with the same length as the smallest side (e.g. 200)
    """

    # If the height is bigger than width.
    if image.size[0] < image.size[1]:
        # this makes the width fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((length, int(image.size[1] * (length / image.size[0]))))
        # amount of pixels to lose in total on the height of the image.
        required_loss = resized_image.size[1] - length
        # crop the height of the image so as to keep 300 pixels the center part.
        resized_image = resized_image.crop(
            box=(0, required_loss / 2, length, resized_image.size[1] - required_loss / 2)
        )
        # we now have a length x length pixels image.

        return resized_image

    # If the width is bigger than the height.
    else:
        # this makes the height fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((int(image.size[0] * (length / image.size[1])), length))
        # amount of pixels to lose in total on the width of the image.
        required_loss = resized_image.size[0] - length
        # crop the width of the image so as to keep 300 pixels of the center part.
        resized_image = resized_image.crop(
            box=(required_loss / 2, 0, resized_image.size[0] - required_loss / 2, length)
        )
        # we now have a length x length pixels image.

        return resized_image
