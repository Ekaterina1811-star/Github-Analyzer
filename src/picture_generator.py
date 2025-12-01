import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator


class PictureGenerator:
    @staticmethod
    def generate_histogram_picture(
            data: pd.DataFrame,
            title: str,
            x_title: str,
            y_title: str,
    ):
        plt.figure(figsize=(10, 6), dpi=300)
        plt.bar(data.index, data, color="skyblue", edgecolor="blue", alpha=0.8)
        plt.title(title, fontsize=16)
        plt.xlabel(x_title, fontsize=14)
        plt.ylabel(y_title, fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout() # для отступов
        plt.savefig(f"hist_{title}.png")


    @staticmethod
    def generate_pie_picture(data: pd.DataFrame, title: str):
        fig, ax = plt.subplots(
            figsize=(20, 15),
            subplot_kw=dict(aspect="equal"),
            dpi=300,
        )
        wedges, texts, autotexts = ax.pie(
            data,
            autopct=lambda pct: f"{pct:.1f}%", # Формат подписи процентов
            textprops=dict(color="w", rotation=0), # Текст внутри
            colors=plt.cm.Set2.colors,
            startangle=45,
        )
        ax.legend(
            wedges,
            data.index,
            title="Языки",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1), # Координаты: справа от графика
            fontsize=24, # Размер шрифта названий
            title_fontsize=28, # Размер шрифта заголовка "Языки"
        )
        plt.setp(autotexts, size=18, weight=700) # подписи внутри
        ax.set_title(title, fontsize=46)
        plt.tight_layout()
        plt.savefig(f"pie_{title}.png")



    @staticmethod
    def generate_picture(
            data1: pd.DataFrame,
            data2: pd.DataFrame,
            title: str,
            label1: str,
            label2: str,
    ):
        fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=18))
        plt.plot(data1["year"], data1["count"], label=label1)
        plt.plot(data2["year"], data2["count"], label=label2)
        plt.title(title, fontsize=14)
        plt.xlabel("Время", fontsize=12)
        plt.ylabel("Количество репозиториев", fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{title}.png")