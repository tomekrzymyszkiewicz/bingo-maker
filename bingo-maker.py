import argparse
import pathlib
from PIL import Image, UnidentifiedImageError
from math import sqrt
from itertools import product
import random
import os

parser = argparse.ArgumentParser(
    prog="Bingo maker",
    description="This script takes 2^n square photos and makes bingo board from them",
)
parser.add_argument(
    "-d",
    type=pathlib.Path,
    metavar="directory",
    help="Directory containing photos",
    required=True,
)
parser.add_argument(
    "-r",
    type=int,
    metavar="fixed resolution",
    help="Fixed resolution of each photo",
)
parser.add_argument(
    "-n",
    default=1,
    type=int,
    metavar="number of boards",
    help="Number of bingo boards",
)
parser.add_argument(
    "-s",
    default=1,
    type=float,
    metavar="scale",
    help="Scale factor of resolution of largest photo in set",
)
args = parser.parse_args()


def load_images(source_path: pathlib.Path):
    images = []
    for file_path in source_path.iterdir():
        try:
            image = Image.open(file_path)
            if image.size[0] != image.size[1]:
                print(f"Image {file_path} is not squared, skipping file")
                continue
            images.append(image)
            print(f"Image {file_path} loaded")
        except UnidentifiedImageError as e:
            print(f"{e}, skipping file")
    return images


def get_board_size(images):
    max_resolution = max([image.size[0] for image in images])
    number_of_images = len(images)
    if args.r is not None:
        board_size = sqrt(number_of_images) * args.r
    else:
        board_size = sqrt(number_of_images) * max_resolution * args.s
    board_size = int(board_size)
    return (board_size, board_size)


def check_if_board_squared(images):
    if not sqrt(len(images)).is_integer():
        raise ValueError("Number of image files is not square of 2")


def provide_result_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def get_random_positions(board_resolution):
    images_positions = [
        position
        for position in product(range(board_resolution), range(board_resolution))
    ]
    random.shuffle(images_positions)
    print(f"Images positions {images_positions}")
    return images_positions


def dispose_images(board_image, board_resolution, images, image_size) -> Image.Image:
    images_positions = get_random_positions(board_resolution)
    for image, image_position in zip(images, images_positions):
        if args.s != 1 or args.r is not None:
            image = image.resize((image_size, image_size))
        board_image.paste(
            image, (image_size * image_position[0], image_size * image_position[1])
        )
    return board_image


def create_boards():
    source_path = args.d
    images = load_images(source_path)
    check_if_board_squared(images)
    board_size = get_board_size(images)
    board_resolution = int(sqrt(len(images)))
    image_size = int(board_size[0] / board_resolution)
    provide_result_dir("bingo-boards")
    for i in range(1, args.n + 1):
        board_file_name = f"{source_path}_bingo_{i}.png"
        print(f"Board {board_file_name}")
        image = Image.new("RGB", board_size, (250, 250, 250))
        image = dispose_images(image, board_resolution, images, image_size)
        image.show()
        image.save(f"bingo-boards/{board_file_name}")


if __name__ == "__main__":
    try:
        create_boards()
    except Exception as e:
        print(f"Error: {e}")
