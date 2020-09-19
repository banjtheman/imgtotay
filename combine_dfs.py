import glob
import logging
import pandas as pd


def combine_dfs():

    dfs = glob.glob("tay_corpus/*")
    df_list = []

    for df in dfs:
        temp_df = pd.read_csv(df, index_col=0)
        df_list.append(temp_df)

    tay_df = pd.concat(df_list, ignore_index=True)
    tay_df.to_csv("tay_hash_df.csv", index=False)


def main():

    logging.info("Combining csvs")
    combine_dfs()


if __name__ == "__main__":
    main()
