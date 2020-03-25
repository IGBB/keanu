# keanu
A tool for viewing the contents of metagenomic samples

<img src="https://github.com/IGBB/keanu/blob/master/logo.png" alt="Keanu Logo" width="200" height="200">

## Files in this repository
* format_input.py: takes a file that contains a single BLAST query and taxon ID per line and formats it correctly as input for Keanu
  * format is `contig_query_name  taxonID_1 [counts], taxonID_2 [count], ...`
* make_db.py: creates Keanu taxonomy database and merged/deleted database from [NCBI taxonomy database ](ftp://ftp.ncbi.nih.gov/pub/taxonomy). Select the taxdmp file and decompress it.
* keanu.py: creates the visualization by taking the output of format_input.py and make_db.py and parsing them
  * output based on http://bl.ocks.org/mbostock/raw/4339083/ or http://bl.ocks.org/vpletzke/raw/c5716da6a021005e7167a9504c6849b2/

## Running Keanu

### Assembly

In order to reduce sequence duplication, the reads can be assembled with some assembler. [ABySS](https://github.com/bcgsc/abyss) was used as Keanu was develeoped. This step is optional.

### BLAST

Use [BLAST](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/) to align the reads (or the assembled reads if the reads were assembled) to a database like the BLAST Nucleotide database. While the choice of output format is up to the user, using `outfmt '6 std staxids'` to include the standard output format 6 with the additional subject taxon ID field is recommended if the BLAST results will be used in with other tools. Then, the query ID field and the subject taxon ID can be extracted from the BLAST results using `cut -f1,13 blast.results.txt > query.staxids.txt`. If the BLAST results aren't needed for anything else, use `outfmt '6 qseqid staxids'` to get the proper format.

If the BLAST alignments have already been completed, the subject taxon ID can be extracted from the database used for the alignments with the `blastdbcmd` from BLAST. To get the file in the proper format, a combination of `paste`, `cut`, and `blastdbcmd` must be used. The command is `paste <(cut -f1 blast.results.txt) <(cut -f2 blast.results.txt | blastdbcmd -db /path/to/db -entry_batch - -outfmt '%T') > query.staxids.txt`.

### Keanu

#### Making the database
The following command is used to create the `taxonomy.dat` and `merged_deleted.dat` databases necessary for running Keanu. There are no optional parameters. The input files - names.dmb, nodes.dmp, delnodes.dmp, and merged.dmp - come from the taxdmp file located at the NCBI Taxonomy FTP site: ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/

`python3 make_db.py -names names.dmp -nodes nodes.dmp -out_db taxonomy.dat -deleted delnodes.dmp -merged merged.dmp -out_md_db merged_deleted.dat`

#### Formatting the input
The following command is used to format data from BLAST into the input file for Keanu. `query.staxids.txt` should contain a single sequence ID and a single taxon ID per line, with the two IDs separated by a tab.

`python3 format_input.py -in query.staxids.txt -out sample_name.keanu.txt`

#### Running Keanu
The following commands are used to create the interactive visualizations based on the input dataset. The first command produces a [bilevel partition graph](http://bl.ocks.org/vpletzke/raw/c5716da6a021005e7167a9504c6849b2/) and the second produces a [collapsible tree](http://bl.ocks.org/mbostock/raw/4339083/).

`python3 keanu.py -db taxonomy.dat -md_db merged_deleted.dat -in input/sample_name.keanu.txt -view bilevel -out output/sample.bilevel.html`

`python3 keanu.py -db taxonomy.dat -md_db merged_deleted.dat -in input/sample_name.keanu.txt -view tree -out output/sample.tree.html`

## Citation

The paper describing Keanu can be found [here](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-019-2629-4).
