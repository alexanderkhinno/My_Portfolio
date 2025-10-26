"""
filename: car_proj.oy
author: Alex k

API for extracting car sales data
selects various parameters
"""

import pandas as pd
import sankey as sk
import panel as pn

class CAR:

    car = None
    def __init__(self):
        self.car = None

    def data_open(self, filename):
        """ This function opens the data
        and saves it as a panda datafile
        """
        self.car = pd.read_csv(filename)
        self.car.dropna(inplace=True)

    def columns(self):
        """ Extracts the columns in order to
        be used for selection later on"""
        return list(self.car.columns)

    def car_models(self):
        """ Gets the make names and its average selling price
        """
        model = list(self.car['make'].unique())
        avg_price_by_make = self.car.groupby('make')['sellingprice'].mean()
        return model, avg_price_by_make

def main():
    car = CAR()
    car.data_open('car_prices.csv')
    #local = car.extract_local_network()
    car.columns()

if __name__ == '__main__':
    main()
