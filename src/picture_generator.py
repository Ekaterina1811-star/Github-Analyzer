import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator


class PictureGenerator:
    @staticmethod
    def generate_histogram_picture(data: pd.DataFrame, title: str):
        plt.figure(figsize=(10, 6), dpi=300)
        plt.bar(data.index, data, color="skyblue", edgecolor="blue", alpha=0.8)
        plt.title(title, fontsize=16)
        plt.xlabel("Возраст", fontsize=14)
        plt.ylabel("Количество репозиториев", fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout() # для отступов
        plt.savefig(f"hist_{title}.png")
