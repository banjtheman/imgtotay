import os
import requests
import logging
import io


from PIL import Image
from icrawler.builtin import BingImageCrawler
from icrawler import ImageDownloader
import imagehash
import pandas as pd


class CustomLinkPrinter(ImageDownloader):
    file_urls = []

    def get_filename(self, task, default_ext):
        file_idx = self.fetched_num + self.file_idx_offset
        return "{:04d}.{}".format(file_idx, default_ext)

    def download(
        self, task, default_ext, timeout=5, max_retry=3, overwrite=False, **kwargs
    ):
        file_url = task["file_url"]
        filename = self.get_filename(task, default_ext)

        task["success"] = True
        task["filename"] = filename

        if not self.signal.get("reach_max_num"):
            self.file_urls.append(file_url)

        self.fetched_num += 1

        if self.reach_max_num():
            self.signal.set(reach_max_num=True)

        return


logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)


def convert_url(image_url):
    try:
        response = requests.get(image_url, stream=True)
    except Exception as error:
        logging.error(error)
        return None

    # Show current image
    try:
        image = Image.open(io.BytesIO(response.content))
    except Exception as error:
        logging.error(error)
        return None

    return image


def make_hash_df(tay_images, keyword):
    logging.info("Starting imagehash df maker")

    tay_json = {}
    tay_json["image"] = []
    tay_json["hash"] = []

    counter = 1
    num_images = len(tay_images)

    for tay_image in tay_images:
        logging.info(
            "Working on "
            + tay_image
            + " ("
            + str(counter)
            + "/"
            + str(num_images)
            + ")"
        )

        curr_image = convert_url(tay_image)

        try:
            tay_hash = imagehash.average_hash(curr_image)
        except Exception as error:
            counter += 1
            logging.error(error)
            continue

        tay_json["hash"].append(tay_hash)
        tay_json["image"].append(tay_image)
        counter += 1

    tay_df = pd.DataFrame.from_dict(tay_json)
    # tay_df.fillna("NULL")

    df_name = "tay_corpus/" + keyword.replace(" ", "_") + "_tay_hash_df.csv"
    tay_df.to_csv(df_name)


def get_images(keyword):

    bing_crawler = BingImageCrawler(downloader_cls=CustomLinkPrinter)
    bing_crawler.downloader.file_urls = []
    bing_crawler.crawl(keyword=keyword, max_num=50)

    file_urls = bing_crawler.downloader.file_urls

    print(file_urls)
    make_hash_df(file_urls, keyword)


def main():
    keyword = "Taylor Swift gold dress"
    get_images(keyword)


if __name__ == "__main__":
    main()
