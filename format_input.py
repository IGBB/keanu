import argparse
import sys

parser = argparse.ArgumentParser(description="A tool to format BLAST qseqid/staxid files into Keanu's input")
parser.add_argument("-in", "--input", help="BLAST query/taxon data")
parser.add_argument("-out", "--output", help="Output filename")

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

counts = {}
with open(args.input) as query_taxid_file:
    for line in query_taxid_file:
        data = line.strip("\n").split("\t")
        if data[0] in counts:
            if data[1] in counts[data[0]]:
                counts[data[0]][data[1]] += 1
            else:
                counts[data[0]][data[1]] = 1
        else:
            counts[data[0]] = {data[1]: 1}

with open(args.output, 'w') as output_file:
    for each in counts:
        taxid_counts = counts[each]
        line=each+"\t"
        for taxid in taxid_counts:
            line+=taxid+" ["+str(taxid_counts[taxid])+"], "
        output_file.write(line.strip(" ,")+"\n")
