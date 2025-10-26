"""

GAD API for extracting data from the gad.csv file
based on various selection parameters.

"""

import pandas as pd
import sankey as sk
from collections import Counter


class GADAPI:

    # state variables
    gad = None  # Dataframe containing the gad data (gad.csv)

    def load_gad(self, filename):
        """ Load the GAD data into the object.
        filename - the name of the csv file containing the gad data
        """
        self.gad = pd.read_csv(filename)


    def get_phenotypes(self):
        """ Retrieves from the GAD dataset a list of all
        distinct disease names which will then populate
        the phenotype dashboard widgewt """

        gady = self.gad[self.gad.association == 'Y']
        gady.phenotype = gady.phenotype.str.lower() # make all phenotypes lowercase
        phen = gady.phenotype.unique() # extract unique phenotypes
        phen = [str(p) for p in phen if ";" not in str(p)] # discard LISTS of phenotypes
        return sorted(phen) # sorting the phenotypes in alphabetical order



    def extract_local_network(self, phenotype, min_pub, singular=True):
        """ Extracts the part of the gad data around a specified
        phenotype.
        phenotype - the disease/phenotype of interest
        min_pub - the min # of confirming publications """

        # postive associations only! ('Y')
        local = self.gad[self.gad.association == 'Y']

        # select out just two columns
        local = local[['phenotype', 'gene']]

        # Convert phenotype to lowercase (for consistency)
        local.phenotype = local.phenotype.str.lower()

        # Count the publications (rows) for each phenotype/gene combination
        local = local.groupby(['phenotype', 'gene']).size().reset_index(name='npubs')

        # Sort table by npubs descending
        local.sort_values('npubs', ascending=False, inplace=True)

        # Filter by minimum # of publications
        local = local[local.npubs >= min_pub]

        # phenotype of interest
        local_pheno = local[local.phenotype == phenotype]

        # 2nd-to-Last step:  Map back to diseases that are connected to these genes
        local = local[local.gene.isin(local_pheno.gene)]

        # Last step: discard singular disease-gene associations if required
        if not singular:
            counter = Counter(local.phenotype)
            exclude = [k for k, v in counter.items() if v == 1]
            local = local[~local.phenotype.isin(exclude)]

        return local


def main():
    """ Test methods for the API """

    gadapi = GADAPI()
    gadapi.load_gad("gad.csv")
    local = gadapi.extract_local_network("diabetes, type 1", 2)
    print(local)
    sk.show_sankey(local, 'phenotype', 'gene', vals='npubs', width=1500, height=1000)


# don't run main if gadapi is imported into another file
# only run main if you are running "gadapi.py" as your "main" program.

if __name__ == '__main__':
    main()
