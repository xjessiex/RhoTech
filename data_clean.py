#!/usr/bin/env python
# coding: utf-8

# load packages
import os

import pandas as pd
import numpy as np

class DataClean:
    """
    Description of functions and variables.


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
        df = pd.read_excel(os.path.join(self.maindir,'data_for_tech_screen.xlsx'))


