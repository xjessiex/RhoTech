#!/usr/bin/env python
# coding: utf-8

# Rhodium Group Technical Screen
# Process projected energy system data
# Author: Xiaoxuan (Jessie) Yang
# Data file provided by Rhodium Group

# load packages
import os

import pandas as pd
from pandas import DataFrame
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
plt.style.use("seaborn-white")


class Energydata:
    """
    Description of variables.
    :param cleandf: cleaned dataset in long form
    :param carbondf: dataset used to calculate carbon intensity
    :param gencon: dataset to plot generation energy use in power sector
    :param manucon: dataset to plot ng and renewables in industrial manufacturing
    :param emitdf: emission data to plot stackplot
    """
    # define path
    maindir = os.getcwd()
    datadir = os.path.join(maindir, "data")

    def __init__(self):
        print("Ready to clean the raw dataset for future energy scenario!")

    def directory(self):
        # confirm directories
        print("Directory is : " + self.maindir)
        print("Raw data file is temporarily stored in : " + self.datadir)

    def loaddata(self):
        # load dataset
        self.df = pd.read_excel(os.path.join(self.datadir, 'data_for_tech_screen.xlsx'))
        # print(self.df.head())

    def cleandata(self):
        # drop unnecessary columns
        df = self.df
        df.drop(df.columns[[0, 3, 10]], axis=1, inplace=True)
        # df.head()

        # make sure the columns have enough info to delete GLabel
        # fix missing "total" in "Source" column
        df.loc[df["Source"].isnull(), "Source"] = "total"
        df.loc[df["Sector"].isnull(), "Sector"] = "all"

        # adjust alternative vehicle cell
        df.loc[143, "Source"] = "total vehicle"
        df.loc[144, "Source"] = "total alternative vehicle"

        # manually add information for certain rows (e.g. light water reactor)
        df.loc[99, "SubSrc"] = "at"
        df.loc[121, "SubSrc"] = "light water"
        df.loc[172, "SubSrc"] = "delivered total"
        df.loc[187, "SubSrc"] = "delivered total"

        # convert data to long form
        longform = pd.melt(df, id_vars="GLabel", value_vars=range(2013, 2039))
        df = longform.merge(df.iloc[:, 0:8], how='left', on="GLabel")

        # merge "SubSec" with "SubSrc" - both supplementary info
        cols = ["SubSec", "SubSrc"]
        df = df.fillna('')  # eliminate NAN
        df["SubSrc"] = df[cols].sum(axis=1)  # replace SubSrc

        # now we can drop GLabel, SubSec, SubSrc
        df.drop(df.columns[[0, 7]], axis=1, inplace=True)

        # rename certain columns
        self.cleandf = df.rename({
            "Gunits": "Units",
            "variable": "Year",
            "value": "Value",
            "DaType": "Data Type",
            "SubDat": "Sub Data Type",
            "SubSrc": "Sub Info"}, axis=1)

        print("Saved the cleaned dataset!")
        export_excel = self.cleandf.to_excel(os.path.join(self.datadir, "data_cleaned.xlsx"), index=False)

    def carbonint(self):
        df = self.cleandf
        # filter out total emission data
        df_emit = df[(df.Units == "MMmt CO2") & (df.Source == "total")]
        df_emit = df_emit[["Year", "Value", "Sector"]]
        df_emit = df_emit.rename({"Value": "Emis.mmt"}, axis=1)

        # filter out total consumption data
        df_cons = df[(df["Data Type"] == "consumption") & (df.Source == "total") & (df.Units == "quads")]
        df_cons = df_cons[["Year", "Value", "Sector"]]
        df_cons = df_cons.rename({"Value": "Cons.quads"}, axis=1)

        # merge two dataframe
        df_merg = pd.merge(df_emit, df_cons)

        # calculate carbon intensity (kg/MMBtu)
        df_merg["Cint.kg.MMBTU"] = df_merg["Emis.mmt"] / df_merg["Cons.quads"]
        self.carbondf = df_merg

    def cintvisual(self):
        df = self.carbondf
        df = df.pivot_table(values="Cint.kg.MMBTU",
                            index="Year",
                            columns="Sector")

        fig, ax = plt.subplots(figsize=(6, 4))
        df.plot(linestyle='-', linewidth=3, legend=None,
                color=["yellowgreen", "lightblue", "grey", "gold", "salmon"],
                ax=ax)

        # add axis
        ax.yaxis.grid()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # set the range
        ax.set_ylim(25, 75)
        ax.set_xlim(2013, 2038)

        # make axis ticks larger
        ax.set_yticklabels(range(25, 76, 10), fontsize=14)
        ax.set_xticklabels(range(2013, 2040, 5), fontsize=14)
        ax.set_xlabel("Year", fontsize=16)

        # add outward ticks
        ax.tick_params(axis='x', colors='black', direction='out', length=6, width=1)

        ax.axvline(x=2019, color="black", linewidth=0.5, linestyle="-.")

        # add annotation
        ax.annotate('Transportation', xy=(2038, 62), xytext=(2031, 66.7),
                    color="salmon", fontsize=16)
        ax.annotate('Commercial', xy=(2038, 42), xytext=(2031, 43.6),
                    color="yellowgreen", fontsize=16)
        ax.annotate('Residential', xy=(2038, 42), xytext=(2024, 43.3),
                    color="gold", fontsize=16)
        ax.annotate('Industrial', xy=(2038, 42), xytext=(2013.5, 42),
                    color="grey", fontsize=16)
        ax.annotate('Electric Power', xy=(2038, 42), xytext=(2030.5, 33.2),
                    color="lightblue", fontsize=16)
        ax.annotate('projections', xy=(2019, 70), xytext=(2019.2, 72.5),
                    color="lightgrey", fontsize=14)
        ax.annotate('history', xy=(2019, 70), xytext=(2015.7, 72.5),
                    color="lightgrey", fontsize=14)

        fig.suptitle("U.S. carbon intensity of energy use by sector\n", fontsize=15, y=1.03, x=0.472)
        ax.set_title("Kilogram CO2 per million Btu",
                     color="grey", style='italic', loc='left', fontsize=15, y=1.04)

        plt.text(2013, 8, "Data source: Rhodium Group"
                           "\nNote: Calculated by dividing total emission by "
                           "total consumption for each sector",
                 fontsize=10, color="grey")

        # plt.show()
        plt.savefig("carbon intensity by sector.png", bbox_inches="tight", dpi=100)

    def genconsump(self):
        df = self.cleandf
        # select generation mix data
        df_gen = df[(df.Units == "quads") & (df.Sector == "electric power")]

        # eliminate redundant source
        df_gen = df_gen[df_gen.Source != "distillate fuel oil"]
        df_gen = df_gen[df_gen.Source != "residual fuel oil"]
        df_gen = df_gen[df_gen.Source != "total"]

        df_gen = df_gen[["Year", "Value", "Source"]]

        # create pivot table
        self.gencon = df_gen.pivot_table(values="Value",
                                         index="Year",
                                         columns="Source")

    def genvisual(self):
        df_gent = self.gencon

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.stackplot(df_gent.index,
                     df_gent["natural gas"],
                     df_gent["nuclear"],
                     df_gent["renewable energy"],
                     df_gent["steam coal"],
                     colors=['gold', 'coral', 'purple', "yellowgreen"])

        # set the range
        ax.set_ylim(0, 45)
        ax.set_xlim(2013, 2038)

        # make axis ticks larger
        ax.set_yticklabels(range(0, 46, 5), fontsize=14)
        ax.set_xticklabels(range(2013, 2040, 5), fontsize=14)
        ax.set_xlabel("Year", fontsize=16)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # add outward ticks
        ax.tick_params(axis='x', colors='black', direction='out', length=6, width=1)

        # add separation lines between historical and projections
        ax.axvline(x=2019, color="black", linewidth=0.5, linestyle="-.")

        # add labels
        ax.annotate('Natural gas', xy=(2038, 5), xytext=(2031, 5),
                    color="white", fontsize=16)
        ax.annotate('Nuclear', xy=(2038, 42), xytext=(2020, 15.2),
                    color="white", fontsize=16)
        ax.annotate('Renewable energy', xy=(2038, 42), xytext=(2028, 25),
                    color="white", fontsize=16)
        ax.annotate('Steam coal', xy=(2038, 42), xytext=(2020, 32),
                    color="white", fontsize=16)

        # add labels to distinguish historical and projections
        ax.annotate('projections', xy=(2019, 40), xytext=(2019.2, 43),
                    color="lightgrey", fontsize=14)
        ax.annotate('history', xy=(2019, 40), xytext=(2015.8, 43),
                    color="lightgrey", fontsize=14)

        # add titles
        fig.suptitle("U.S. electric power energy consumption by source\n", fontsize=15, y=1.03, x=0.52)
        ax.set_title("Quads",
                     color="grey", style='italic', loc='left', fontsize=15, y=1.04)

        plt.text(2013, -15, "Data source: Rhodium Group"
                            "\nNote: Non-biogenic municipal waste, liquid fuels,"
                            "\nand electricity imports are not included.",
                 fontsize=10, color="grey")
        # plt.show()
        plt.savefig("power generation mix consumption.png", bbox_inches="tight", dpi=100)

    def manusource(self):
        # select manufacturing data
        df = self.cleandf
        df_mf = df[(df.Sector == "industrial") & (df["Sub Info"] == "manufacturing")]

        selected_sc = ["biofuels heat and coproducts",
                       "coal subtotal",
                       "natural gas",
                       "petroleum subtotal",
                       "purchased electricity",
                       "renewables"]
        df_mf = df_mf[df_mf.Source.isin(selected_sc)]

        # natural gas to liquids heat and power is not included
        df_mf = df_mf[["Year", "Value", "Source"]]

        df_mf = df_mf.pivot_table(values="Value",
                                  index="Year",
                                  columns="Source")

        # drop 2013 data and save
        self.manucon = df_mf.drop(df_mf.index[[0]])

    def manuvisual(self):
        fig, ax = plt.subplots(figsize=(6, 4))

        lines = self.manucon.plot(linestyle='-', linewidth=3, legend=None,
                                  color=["grey", "grey", "gold", "grey", "green"],
                                  ax=ax)

        ax.yaxis.grid()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # set the range
        ax.set_ylim(400, 9100)
        ax.set_xlim(2013, 2038)

        # make axis ticks larger
        ax.set_yticklabels(range(400, 9100, 1000), fontsize=14)
        ax.set_xticklabels(range(2013, 2040, 5), fontsize=14)
        ax.set_xlabel("Year", fontsize=16)

        # add outward ticks
        ax.tick_params(axis='x', colors='black', direction='out', length=6, width=1)

        # add separation line for historical and projections
        ax.axvline(x=2019, color="black", linewidth=0.5, linestyle="-.")

        ax.annotate('Natural gas', xy=(2033, 2050), xytext=(2030, 8360),
                    color="gold", fontsize=16)
        ax.annotate('Renewables', xy=(2033, 1300), xytext=(2030, 3400),
                    color="green", fontsize=16)
        ax.annotate('Other sources', xy=(2033, 2000), xytext=(2030, 1800),
                    color="grey", fontsize=16)

        ax.annotate('projections', xy=(2018.5, 8800), xytext=(2019.3, 8650),
                    color="lightgrey", fontsize=14)
        ax.annotate('history', xy=(2019.5, 8800), xytext=(2015.8, 8650),
                    color="lightgrey", fontsize=14)


        fig.suptitle("Energy consumption in industrial manufacturing\n", fontsize=16, y=1.03, x=0.52)
        ax.set_title("Trillion Btu",
                     color="grey", style='italic', loc='left', fontsize=15, y=1.04)

        # add notes
        plt.text(2013, -2400, "Data source: Rhodium Group"
                              "\nNote: Other sources include biofuels heat and coproducts,"
                              "\ncoal, petroleum, purchased electricity",
                 fontsize=10, color="grey")

        plt.savefig("manufacturing consumption by source.png", bbox_inches="tight", dpi=100)

    def totalemiss(self):
        df = self.cleandf
        # select emission data
        df_emit = df[(df.Source == "total") & (df["Data Type"] == "emissions")]
        df_emit = df_emit[["Year", "Value", "Sector"]]

        self.emitdf = df_emit.pivot_table(values="Value",
                                      index="Year",
                                      columns="Sector")

    def emisvisual(self):
        df_emit = self.emitdf
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.stackplot(df_emit.index,
                     df_emit["commercial"],
                     df_emit["industrial"],
                     df_emit["residential"],
                     df_emit["transportation"],
                     colors=['yellowgreen', 'grey', "gold", "salmon"])

        # set the range
        ax.set_ylim(600, 6800)
        ax.set_xlim(2013, 2038)

        # make axis ticks larger
        ax.set_yticklabels(range(600, 6801, 1000), fontsize=14)
        ax.set_xticklabels(range(2013, 2040, 5), fontsize=14)
        ax.set_xlabel("Year", fontsize=16)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # add separation lines for historical and projections
        ax.axvline(x=2019, color="black", linewidth=0.5, linestyle="-.")

        ax.annotate('projections', xy=(2019, 6700), xytext=(2019.3, 6600),
                    color="lightgrey", fontsize=14)
        ax.annotate('history', xy=(2019, 6700), xytext=(2015.8, 6600),
                    color="lightgrey", fontsize=14)

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)

        # add title
        fig.suptitle("U.S. emission by Sector\n", fontsize=16, y=1.03, x=0.326)
        ax.set_title("Million Btu",
                     color="grey", style='italic', loc='left', fontsize=15, y=1.04)

        # add note
        plt.text(2013, -1400, "Data source: Rhodium Group"
                              "\nNote: Sectors are color coded the same way as figure"
                              "on carbon intensity, excluding electric power",
                 fontsize=10, color="grey")

        plt.savefig("emission by sector.png", bbox_inches="tight", dpi=100)

def main():
    test = Energydata()
    test.directory()
    test.loaddata()
    test.cleandata()

    #figures
    test.carbonint()
    test.cintvisual()
    test.genconsump()
    test.genvisual()
    test.manusource()
    test.manuvisual()
    test.totalemiss()
    test.emisvisual()


if __name__ == "__main__":
    main()

