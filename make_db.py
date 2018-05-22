import sys
import argparse

parser = argparse.ArgumentParser(description="A tool to format NCBI taxonomy data for Keanu")
parser.add_argument("-names", help="Location of names.dmp")
parser.add_argument("-nodes", help="Location of nodes.dmp")
parser.add_argument("-merged", help="Location of merged.dmp")
parser.add_argument("-deleted", help="Location of delnodes.dmp")
parser.add_argument("-out_db", help="Name of output taxonomy database")
parser.add_argument("-out_md_db", help="Name of output merged/deleted database")

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()


class Taxon:
    'A class for storing information about taxons'
    
    def __init__(self, taxon, name):
        self.taxon = taxon
        self.name = name
        self.rank = None
        self.source = None
        self.descendants = []

    def set_source(self, target):
        self.source = target
            
    def add_descendant(self,target):
        if target not in self.descendants:
            self.descendants.append(target)

    def remove_source(self, target):
        if target == self.source:
            self.source == None

    def remove_descendant(self, target):
        if target in self.descendants:
            self.descendants.remove(target)
    
    def __repr__(self):
        return("|=:=|".join([str(self.taxon), str(self.source), self.rank, self.name, str(self.descendants)]))

# Taxonomy database

taxonomy = {}

with open(args.names) as names_file:
    for line in names_file:
        if "scientific name" in line:
            data = line.split("\t|\t")
            temp = Taxon(int(data[0]), data[1])
            taxonomy[int(data[0])] = temp

with open(args.nodes) as nodes_file:
    for line in nodes_file:
        data = line.split("\t|\t")
        taxon = int(data[0])
        source = int(data[1])
        rank = data[2]
        taxonomy[taxon].source = source
        taxonomy[taxon].rank = rank
        taxonomy[source].descendants.append(str(taxon))

with open(args.out_db, 'w') as taxonomy_data_file:
    for each in taxonomy:
        taxonomy_data_file.write(str(taxonomy[each])+"\n")

# Merged and deleted database

deleted = []
merged = {}
with open(args.deleted) as deleted_file:
    for line in deleted_file:
        deleted.append(line.strip("\t|\n"))

with open(args.merged) as merged_file:
    for line in merged_file:
        data = line.strip("\t|\n").split("\t|\t")
        merged[data[0]] = data[1]

with open(args.out_md_db, 'w') as merged_deleted_db_file:
    for each in deleted:
        merged_deleted_db_file.write(each+"\n")
    for each in merged:
        merged_deleted_db_file.write(each+"\t"+merged[each]+"\n")


