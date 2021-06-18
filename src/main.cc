#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdint>
#include <unordered_map>
#include <set>
#include <queue>
#include <list>
#include "kraken2/taxonomy.h"

using namespace std;

typedef unordered_map<uint64_t, list<uint64_t> > tree_t;

void print_tree(kraken2::Taxonomy & tax, tree_t & tree, uint64_t id){
    kraken2::TaxonomyNode node = tax.nodes()[id];
    int add_comma = 0;

    cout << "{\"name\": \""<< tax.name_data()+node.name_offset << "\"";
    cout << ",\"id\": "<< node.external_id ;


    if(!tree[id].empty()){
        cout << ", \"children\": [";

        for (auto& x: tree[id]) {
            if(add_comma++)
                cout << ",";
            print_tree(tax, tree, x);
        }

        cout << "]";
    }
    cout << "}";

}

int main (int argc, char** argv){
    // cutoff to combine kmers into "other" category
    float cutoff = 1.0;


    // open tax db
    kraken2::Taxonomy tax(argv[1]);
    tax.GenerateExternalToInternalIDMap();

    // open kraken output
    fstream input;
    input.open(argv[2], ios::in);
    if(!input.is_open())
       return 1;


    tree_t tree;
    queue<uint64_t> queue;
    cout << " { \"contigs\": [ ";

    // loop through kraken output
    string line;
    int c = 0;
    while(getline(input, line)){


        // load line into stream
        stringstream ss;
        ss.str(line);

        // read first four columns
        string isclass, seqid, length_string;
        uint64_t taxid, length;
        ss >> isclass >> seqid >> taxid >> length_string;
        length = stoull(length_string);

        // tally kmer counts for each matching taxid
        unordered_map<uint64_t,uint64_t> counts;
        uint64_t other = 0;
        string pair;
        while(getline(ss, pair, ' ')){
            uint64_t taxid = 0, kmers = 0;
            size_t pos = pair.find(':');

            if(pos == string::npos) break;

            kmers = stoull(pair.substr(pos+1));


            if(pair[0] == 'A')
                other += kmers;
            else {
                taxid = stoull(pair);
                if(counts[taxid])
                    counts[taxid] += kmers;
                else
                    counts[taxid] = kmers;
            }
        }

        // combine low count data
        for ( auto it = counts.begin(); it != counts.end();  ) {
            if( 100.0*it->second/length  < cutoff ){
                other += it->second;
                 it = counts.erase(it);
            } else {
                it++;
            }
        }

        if(c++) printf(",");
        printf( "{ \"seq\": \"%s\", \"taxid\": %d, \"length\": %d, \"class\": {",
                seqid.c_str(), taxid, length );

        for (auto& x: counts) {
            // get kraken internal id for current taxon
            uint64_t id = tax.GetInternalID(x.first);

            // create tree entry (empty list) and queue if not already in tree
            if(tree.emplace(id, list<uint64_t>()).second)
                queue.push(id);


            printf("\"%d\":%d,", x.first, x.second);
        }
        printf("\"other\":%d}}", other);


    }

    cout << "], ";

    // build tree
    while(!queue.empty()){
        uint64_t id = queue.front();
        queue.pop();

        kraken2::TaxonomyNode node = tax.nodes()[id];



        if(tree.find(node.parent_id) == tree.end())
            queue.push(node.parent_id);

        // stop cycles
        if(node.parent_id != id)
            tree[node.parent_id].push_back(id);

    }

    // print tree with DFS
    cout << "\"tree\": ";
    print_tree(tax, tree, 1);
    cout << ", ";


    cout << "\"labels\": {";

    for (auto& x: tree) {
        kraken2::TaxonomyNode node = tax.nodes()[x.first];
        string name = tax.name_data() + node.name_offset;

        if(x.first == 0) name = "Unclassified";

        printf("\"%d\":\"%s\",", node.external_id, name.c_str());

    }
    cout << "\"other\":\"Other\"}";



    cout << "}";
    return 0;
}
