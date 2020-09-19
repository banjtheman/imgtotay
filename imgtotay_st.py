import requests
import time
import json
import io
import logging

from PIL import Image
import streamlit as st
import pandas as pd
import imagehash


def find_sim_hash(row, feats):
    row_hash = imagehash.hex_to_hash(row["hash"])
    return feats - row_hash



def rgb_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image


def get_tay_image_hash(image_url):

    try:
        feats = imagehash.average_hash(image_url)
    except Exception as error:
        st.error("Invalid Image")
        st.error(error)

    df = load_tay_df_hash()
    df["sim"] = df.apply(lambda row: find_sim_hash(row, feats), axis=1)

    final_df = df.sort_values(by=["sim"], ascending=True)


    sim_image = final_df["image"].values[0]

    image = load_url(sim_image)
    images = [image_url,image]
    try:
        st.image(images, width=300)
    except Exception as error:

        #try converting images?
        logging.error(error)

        try:
            new_images = []
            for image in images:
                new_images.append(rgb_image(image))
            st.image(new_images, width=300)
        except Exception as new_error:
            logging.error(new_error)
            st.error(new_error)


    # top3 = final_df["image"].values[0:3]
    # images = []

    # for img in top3:
    #     image = load_url(img)  # Image.open(img)
    #     images.append(image)

    # try:
    #     st.image(images, use_column_width=True)
    # except Exception as error:
    #     st.error(error)


@st.cache(allow_output_mutation=True)
def load_tay_df_hash():
    df = pd.read_csv("tay_hash_df.csv")
    return df


def load_url(image_url):
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

    #check RGB mode?
    # if image.mode != 'RGB':
    #     image = image.convert('RGB')

    return image


def convert_url(image_url):
    image = load_url(image_url)

    # try:
    #     st.image(image, use_column_width=True)
    # except Exception as error:
    #     st.error(error)

    with st.spinner("Converting..."):
        get_tay_image_hash(image)
    st.balloons()


def main():
    st.title("Image to Taylor Swift")

    st.header("Enter in a picture url and watch it turn to Taylor Swift")

    image_url = st.text_input("Image_url")

    if st.button("Convert"):
        convert_url(image_url)


if __name__ == "__main__":
    main()
