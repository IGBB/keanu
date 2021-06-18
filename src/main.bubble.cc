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

#include "bubble.html.h"
#include "bubble.style.h"
#include "bubble.script.h"

using namespace std;

typedef unordered_map<uint64_t, list<uint64_t> > tree_t;
typedef unordered_map<uint64_t,uint64_t> counts_t;

string print_tree(kraken2::Taxonomy & tax,
                        tree_t & tree,
                        counts_t & counts,
                        uint64_t id){
    stringstream ss;
    kraken2::TaxonomyNode node = tax.nodes()[id];
    bool need_comma = false;

    ss << "{\"name\": \""<< tax.name_data()+node.name_offset << "\"";
    ss << ",\"id\": "<< node.external_id;
    ss << ",\"rank\": \"" << tax.rank_data() + node.rank_offset<< "\"";
    if(counts[node.external_id])
        ss << ",\"kmers\":" << counts[node.external_id];


    if(!tree[id].empty()){
        ss << ", \"children\": [";

        for (auto& x: tree[id]) {
            if(need_comma)
                ss << ",";
            need_comma = true;
            ss << print_tree(tax, tree, counts, x);
        }

        ss << "]";
    }
    ss << "}";
    return ss.str();
}

int main (int argc, char** argv){
    stringstream json_data;
    // cutoff to combine kmers into "other" category
    float cutoff = 0.1;


    // open tax db
    kraken2::Taxonomy tax(argv[1]);
    tax.GenerateExternalToInternalIDMap();

    // open kraken output
    fstream input;
    input.open(argv[2], ios::in);
    if(!input.is_open())
       return 1;


    json_data << "{ \"children\": [ ";

    set<uint64_t> ranks;

    // loop through kraken output
    string line;
    bool need_comma = false;
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
        counts_t counts;
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

        if(need_comma) json_data << ",";
        need_comma = true;

        json_data << "{"
                  << "\"seq\": \""  << seqid << "\","
                  << "\"taxid\": "  << taxid << ","
                  << "\"id\": "     << tax.GetInternalID(taxid) << ","
                  << "\"length\": " << length << ",";



        if(taxid != 0)
            json_data << "\"name\": \""
                      << tax.name_data() +
                               tax.nodes()[tax.GetInternalID(taxid)].name_offset
                      << "\",";
        else
            json_data << "\"name\": \"Unclassified\",";

        tree_t tree;
        queue<uint64_t> queue;
        for (auto& x: counts) {
            // get kraken internal id for current taxon
            uint64_t id = tax.GetInternalID(x.first);

            // create tree entry (empty list) and queue if not already in tree
            if(tree.emplace(id, list<uint64_t>()).second)
                queue.push(id);


        }

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

            ranks.insert(node.rank_offset);
        }

        json_data << " \"children\": ["
                  << print_tree(tax, tree, counts, 1)
                  << ","
                  << "{\"id\":\"0\", \"kmers\":" << counts[0]
                      << ", \"name\":\"Unclassified\", \"rank\":\"Unclassified\"}"
                  << ","
                  << "{\"id\":\"other\", \"kmers\":" << other
                      << ", \"name\":\"Other\",\"rank\":\"Other\"}"
                  << "]";
        json_data <<  "}";

    }

    json_data << "], \"ranks\":[";

    for(auto& x : ranks){
        json_data << "\"" << tax.rank_data()+x << "\",";
    }

    json_data << "\"Other\", \"Unclassified\"]";
    json_data <<  "}";

    printf((char*) bubble_html,
           json_data.str().c_str(),
           bubble_css,
           bubble_js,
           cutoff);

    return 0;
}
