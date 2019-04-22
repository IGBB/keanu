import sys
import itertools
import argparse
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument("-db", "--database", help="Formatted taxonomy database")
parser.add_argument("-md_db", "--merged_deleted_database", help="Merged/deleted taxonomy database")
parser.add_argument("-view", "--view", choices=["tree", "bilevel"], help="View choice")
parser.add_argument("-in", "--input", help="Input data set")
parser.add_argument("-out", "--output", help="Output HTML filename")
parser.add_argument("-export", "--export", help="Export node/contig assignments to user-specified file")
parser.add_argument("-ts", "--to_species", action='store_true', help="Assign ambiguous hits without attempting to find deepest common classification")

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()



# HTML selection:
if args.view == "tree":
    before_html = '<!DOCTYPE html><!-- saved from url=(0040)http://bl.ocks.org/mbostock/raw/4339083/ --><html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta charset="utf-8"><meta charset="UTF-8"><meta content="utf-8" http-equiv="encoding"><style>.node {  cursor: pointer;}.node circle {  fill: #fff;  stroke: steelblue;  stroke-width: 1.5px;}.node text {  font: 10px sans-serif;}.link {  fill: none;  stroke: #ccc;  stroke-width: 1.5px;}</style><title></title></head><body><script src="https://d3js.org/d3.v3.min.js"></script><script>var margin = {top: 20, right: 120, bottom: 20, left: 120},    width = 1920 - margin.right - margin.left,    height = 1080 - margin.top - margin.bottom;var i = 0,    duration = 750,    root;var tree = d3.layout.tree()    .size([height, width]);var diagonal = d3.svg.diagonal()    .projection(function(d) { return [d.y, d.x]; });var svg = d3.select("body").append("svg")    .attr("width", width + margin.right + margin.left)    .attr("height", height + margin.top + margin.bottom)  .append("g")    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");root=JSON.parse(\''
    after_html = '\');  root.x0 = height / 2;  root.y0 = 0;  var max = root.size; function collapse(d) {    if (d.children) {      d._children = d.children;      d._children.forEach(collapse);      d.children = null;    }  }  root.children.forEach(collapse);  update(root);d3.select(self.frameElement).style("height", "800px");function update(source) {  var nodes = tree.nodes(root).reverse(),      links = tree.links(nodes);  nodes.forEach(function(d) { d.y = d.depth *180 });  var node = svg.selectAll("g.node")      .data(nodes, function(d) { return d.id || (d.id = ++i); });  var nodeEnter = node.enter().append("g")      .attr("class", "node")      .attr("transform", function(d) { return "translate(" + source.y0+ "," + source.x0 + ")"; })      .on("click", click);  nodeEnter.append("circle")      .attr("r", 1e-6)      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });  nodeEnter.append("text")      .attr("x", function(d) { return d.children || d._children ? -10 - (d.size / max * 10) : 10 + (d.size / max * 10)})      .attr("dy", ".35em")      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })      .text(function(d) { return d.name; })      .style("fill-opacity", 1e-6);  var nodeUpdate = node.transition()      .duration(duration)      .attr("transform", function(d) { return "translate(" +d.y + "," + d.x + ")"; });  nodeUpdate.select("circle")      .attr("r", function(d) { return d.size / max * 10; })      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });  nodeUpdate.select("text")      .style("fill-opacity", 1);  var nodeExit = node.exit().transition()      .duration(duration)      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })      .remove();  nodeExit.select("circle")      .attr("r", 1e-6);  nodeExit.select("text")      .style("fill-opacity", 1e-6);  var link = svg.selectAll("path.link")      .data(links, function(d) { return d.target.id; });  link.enter().insert("path", "g")      .attr("class", "link")      .attr("d", function(d) {        var o = {x: source.x0, y: source.y0};        return diagonal({source: o, target: o});      });  link.transition()      .duration(duration)      .attr("d", diagonal);  link.exit().transition()      .duration(duration)      .attr("d", function(d) {        var o = {x: source.x, y: source.y};        return diagonal({source: o, target: o});      })      .remove();  nodes.forEach(function(d) {    d.x0 = d.x;    d.y0 = d.y;  });}function click(d) {  if (d.children) {    d._children = d.children;    d.children = null;  } else {    d.children = d._children;    d._children = null;  }  update(d);}</script></body></html>'
elif args.view == "bilevel":
    before_html='<!DOCTYPE html><!-- saved from url=http://bl.ocks.org/vpletzke/raw/c5716da6a021005e7167a9504c6849b2/ --><meta charset="utf-8"><style>circle,path{cursor: pointer;}circle{fill: none; pointer-events: all;}#tooltip{background-color: white; padding: 3px 5px; border: 1px solid black; text-align: center;}html{font-family: sans-serif;}</style><body><script src="http://d3js.org/d3.v3.min.js"></script><script>var margin={top: 350, right: 480, bottom: 350, left: 480}, radius=Math.min(margin.top, margin.right, margin.bottom, margin.left) - 10;function filter_min_arc_size_text(d, i){return (d.dx*d.depth*radius/3)>14};var hue=d3.scale.category20c();var luminance=d3.scale.sqrt() .domain([0, 1e6]) .clamp(true) .range([90, 20]);var svg=d3.select("body").append("svg") .attr("width", margin.left + margin.right) .attr("height", margin.top + margin.bottom) .append("g") .attr("transform", "translate(" + margin.left + "," + margin.top + ")");var partition=d3.layout.partition() .sort(function(a, b){return d3.ascending(a.name, b.name);}) .size([2 * Math.PI, radius]);var arc=d3.svg.arc() .startAngle(function(d){return d.x;}) .endAngle(function(d){return d.x + d.dx - .01 / (d.depth + .5);}) .innerRadius(function(d){return radius / 3 * d.depth;}) .outerRadius(function(d){return radius / 3 * (d.depth + 1) - 1;});var tooltip=d3.select("body") .append("div") .attr("id", "tooltip") .style("position", "absolute") .style("z-index", "10") .style("opacity", 0);function format_number(x){return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");}function format_description(d){var description=d.name; return /* \'<b>\' + d.name + \'</b></br>\'+*/ d.name;}function computeTextRotation(d){var angle=(d.x +d.dx/2)*180/Math.PI - 90; return angle;}function mouseOverArc(d){d3.select(this).attr("stroke","black"); tooltip.html(format_description(d)); return tooltip.transition() .duration(50) .style("opacity", 0.9);}function mouseOutArc(){d3.select(this).attr("stroke",""); return tooltip.style("opacity", 0);}function mouseMoveArc (d){return tooltip .style("top", (d3.event.pageY-10)+"px") .style("left", (d3.event.pageX+10)+"px");}var root_=null;root=JSON.parse(\''
    after_html='\'); partition .value(function(d){return d.size;}) .nodes(root) .forEach(function(d){d._children=d.children; d.sum=d.size; d.key=key(d); d.fill=fill(d);});partition .children(function(d, depth){return depth < 2 ? d._children : null;}) .value(function(d){return d.sum;});var center=svg.append("circle") .attr("r", radius / 3) .on("click", zoomOut);center.append("title") .text("zoom out"); var partitioned_data=partition.nodes(root).slice(1);var path=svg.selectAll("path") .data(partitioned_data) .enter().append("path") .attr("d", arc) .style("fill", function(d){return d.fill;}) .each(function(d){this._current=updateArc(d);}) .on("click", zoomIn) .on("mouseover", mouseOverArc) .on("mousemove", mouseMoveArc) .on("mouseout", mouseOutArc);var texts=svg.selectAll("text") .data(partitioned_data) .enter().append("text") .filter(filter_min_arc_size_text) .attr("x", function(d){return radius / 3 * d.depth;}) .attr("dx", "6") .attr("dy", ".35em") .attr("transform", function(d){var rotation=computeTextRotation(d); if (rotation > -180 && rotation < 180){return "rotate(" + rotation + ")";}else{return "rotate(" + (rotation ) + ")";}}) .text(function(d,i){return d.name.split("(")[0]});function zoomIn(p){if (p.depth > 1) p=p.parent; if (!p.children) return; zoom(p, p);}function zoomOut(p){if (!p.parent) return; zoom(p.parent, p);}function zoom(root, p){if (document.documentElement.__transition__) return; var enterArc, exitArc, outsideAngle=d3.scale.linear().domain([0, 2 * Math.PI]); function insideArc(d){return p.key > d.key ?{depth: d.depth - 1, x: 0, dx: 0}: p.key < d.key ?{depth: d.depth - 1, x: 2 * Math.PI, dx: 0}:{depth: 0, x: 0, dx: 2 * Math.PI};}function outsideArc(d){return{depth: d.depth + 1, x: outsideAngle(d.x), dx: outsideAngle(d.x + d.dx) - outsideAngle(d.x)};}center.datum(root); if (root===p) enterArc=outsideArc, exitArc=insideArc, outsideAngle.range([p.x, p.x + p.dx]); var new_data=partition.nodes(root).slice(1); path=path.data(new_data, function(d){return d.key;}); if (root !==p) enterArc=insideArc, exitArc=outsideArc, outsideAngle.range([p.x, p.x + p.dx]); d3.transition().duration(d3.event.altKey ? 7500 : 750).each(function(){path.exit().transition() .style("fill-opacity", function(d){return d.depth===1 + (root===p) ? 1 : 0;}) .attrTween("d", function(d){return arcTween.call(this, exitArc(d));}) .remove(); path.enter().append("path") .style("fill-opacity", function(d){return d.depth===2 - (root===p) ? 1 : 0;}) .style("fill", function(d){return d.fill;}) .on("click", zoomIn) .on("mouseover", mouseOverArc) .on("mousemove", mouseMoveArc) .on("mouseout", mouseOutArc) .each(function(d){this._current=enterArc(d);}); path.transition() .style("fill-opacity", 1) .attrTween("d", function(d){return arcTween.call(this, updateArc(d));});}); texts=texts.data(new_data, function(d){return d.key;}); texts.exit() .remove(); texts.enter() .append("text"); texts.style("opacity", 0) .attr("x", function(d){return radius / 3 * d.depth;}) .attr("dx", "6") .attr("dy", ".35em") .attr("transform", function(d){var rotation=computeTextRotation(d); if (rotation > -180 && rotation < 180){return "rotate(" + rotation + ")";}else{return "rotate(" + (rotation ) + ")";}}) .filter(filter_min_arc_size_text) .transition().delay(750).style("opacity", 1) .text(function(d,i){return d.name.split("(")[0]});};function key(d){var k=[], p=d; while (p.depth) k.push(p.name), p=p.parent; return k.reverse().join(".");}function fill(d){var p=d; while (p.depth > 1) p=p.parent; var c=d3.lab(hue(p.name+d.name)); c.l=luminance(d.sum/1000+p.sum); console.log(d.name+ " "+c); return c;}function arcTween(b){var i=d3.interpolate(this._current, b); this._current=i(0); return function(t){return arc(i(t));};}function updateArc(d){return{depth: d.depth, x: d.x, dx: d.dx};}d3.select(self.frameElement).style("height", margin.top + margin.bottom + "px");</script> '

# Taxon class
# Stores information about individual nodes in the graph
class Taxon:
    'A class for storing information about taxons'
    
    def __init__(self, taxon, source, rank, name):
        self.taxon = taxon
        self.descendants = []
        self.source = source
        self.name = name
        self.rank = rank
        self.coverage = 0

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
        return(str(self.taxon)+" ("+str(self.coverage)+") "+str(self.descendants))

# Graph class
# Organizes the links between nodes into a tree for ascending/descending
class Graph:
    'A helper class for linking and searching taxonomy information'

    def __init__(self):
        self.vertices = {}

    def add_vertex(self, taxon, source, rank, name, descendants):
        temp = Taxon(taxon, source, rank, name)
        for descendant in descendants:
            temp.add_descendant(descendant)
        self.vertices[taxon] = temp

    def collapse(self):
        collapsed = []
        for taxon in self.vertices:
            collapsed_taxon = self.vertices[taxon]
            if len(collapsed_taxon.descendants) == 1 and collapsed_taxon.taxon != 0:
                collapsed.append(taxon)
                parent_taxon = self.vertices[collapsed_taxon.source]
                descendant = self.vertices[collapsed_taxon.descendants[0]]
                descendant.set_source(collapsed_taxon.source)
                parent_taxon.add_descendant(descendant.taxon)
                parent_taxon.remove_descendant(taxon)
                #parent_taxon.coverage += collapsed_taxon.coverage
        for each in collapsed:
            del self.vertices[each]

    def add_unassigned(self):
        annotated_lineage = ["root", "superkingdom", "kingdom", "phylum", "class", "order", "suborder", "family", "genus", "species"]
        added = {}
        for each in self.vertices:
            number_of_assigned = 0
            if self.vertices[each].rank in annotated_lineage and self.vertices[each].rank != "species":
                for descendant in self.vertices[each].descendants:
                    number_of_assigned+=self.vertices[descendant].coverage
                number_of_unassigned = self.vertices[each].coverage - number_of_assigned
                added[each*-1] = Taxon(each*-1, each, annotated_lineage[annotated_lineage.index(self.vertices[each].rank)+1], "unassigned "+self.vertices[each].name)
                added[each*-1].coverage = number_of_unassigned
                self.vertices[each].descendants.append(each*-1)
        for each in added:
            self.vertices[each] = added[each]
            
    def recursive_depth_first_search(self, taxon, visited_taxons, json):
        annotated_lineage = ["root", "superkingdom", "kingdom", "phylum", "class", "order", "suborder", "family", "genus", "species"]
        vertex = self.vertices[taxon]
        visited_taxons.append(taxon)
        if vertex.coverage != 0:
            if vertex.rank in annotated_lineage or vertex.name == "root":
                if len(vertex.descendants) != 0:
                    json+=("{"+'"name": "{:s} ({:d})", "size": "{:d}", "children": ['.format(vertex.name, vertex.coverage, vertex.coverage))

                    for descendant in vertex.descendants:
                        if descendant not in visited_taxons and descendant != None:
                            (visited_taxons, json) = self.recursive_depth_first_search(descendant, visited_taxons, json)
                    json+="]},"
                else:
                    json+=("{"+'"name": "{:s} ({:d})", "size": "{:d}"'.format(vertex.name, vertex.coverage, vertex.coverage)+"},")
            else:
                for descendant in vertex.descendants:
                    if descendant not in visited_taxons:
                        (visited_taxons, json) = self.recursive_depth_first_search(descendant, visited_taxons, json)
        return visited_taxons, json

tree = Graph()
merged = {}
deleted = []

with open(args.database) as taxa_data_file:
    for line in taxa_data_file:
        data = line.strip("\n").split("|=:=|")
        taxon = int(data[0])
        source = int(data[1])
        rank = data[2]
        name = data[3]
        if data[4] != "[]":
            descendants = [int(descendant[1:-1]) for descendant in data[4][1:-1].split(", ")]
        else:
            descendants = []
        tree.add_vertex(taxon, source, rank, name, descendants)

with open(args.merged_deleted_database) as deleted_data_file:
    for line in deleted_data_file:
        data = line.strip("\n").split("\t")
        if len(data) == 1:
            try:
                deleted.append(int(data[0]))
                del tree.vertices[int(data[0])]
            except:
                pass
        else:
            merged[int(data[0])] = int(data[1])

assignments = {}
with open(args.input) as blast_taxon_coverage_file:
    annotated_lineage = ["root", "superkingdom", "kingdom", "phylum", "class", "order", "suborder", "family", "genus", "species"]
    for line in blast_taxon_coverage_file:
        contig = line.strip("\n").split("\t")[0]
        if "," in line.strip("\n").split("\t")[1]:
            data = line.strip("\n").split("\t")[1].split(",")
        else:
            data = [line.strip("\n").split("\t")[1]]
        parents = []
        for each in data:
            taxon_data = each.split(" [")
            if ";" in taxon_data[0]:
                for each in taxon_data[0].split(";"):
                    if int(each) in merged:
                        each = merged[int(each)]
                    if args.to_species:
                        for i in range(0, int(taxon_data[1].strip("]"))):
                            parents.append(each)
                    else:
                        parents.append(int(each))
            elif taxon_data[0] == "N/A":
                pass
            else:
                taxon_data[0] = taxon_data[0].strip()
                if len(taxon_data[0]) > 0:
                    taxon = int(taxon_data[0])
                    if int(taxon_data[0]) in merged:
                        taxon = merged[int(taxon_data[0])]
                    if args.to_species:
                        for i in range(0, int(taxon_data[1].strip("]"))):
                            parents.append(taxon)
                    else:
                        parents.append(taxon)
        sys.stderr.write(str(parents)+"\n")
        i = 0

        while i < len(parents):
            if parents[i] == 1 and parents[i-1] == 1 and parents[i-2] == 1:
                break
            each = parents[i]
            if each in merged:
                each = merged[each]
            try:
                taxon = tree.vertices[each]
                parents.append(taxon.source)
            except:
                if each in deleted:
                    sys.stderr.write("WARNING: Keanu has encountered a deleted taxon ID ("+str(each)+") in the BLAST results.\n")
                else:
                    sys.stderr.write("WARNING: Keanu has encountered a taxon ID ("+str(each)+") in the BLAST results that is not in the taxonomy database or merged/deleted database.\n")
            i += 1
        parent_counts = Counter(parents)
        sys.stderr.write(str(parent_counts)+"\n")
        
        # print(parent_counts)
        if len(parent_counts) > 0:
            if args.to_species:
                for each in parent_counts:
                    tree.vertices[each].coverage = parent_counts[each]
            else:
                highest = sorted(parent_counts.values())[-2]
                root = sorted(parent_counts.values())[-1]
                if highest == 1 and root != 1:
                    sys.stderr.write(contig+" was assigned to root. Check your BLAST results for "+contig+", especially e-scores.\n")
                    common_candidates = set()
                    taxon = tree.vertices[1]
                    tree.vertices[taxon.taxon].coverage += 1
                else:
                    common_candidates = [k for k,v in parent_counts.items() if v == highest]
                    for i in range(0, len(common_candidates)):
                        each = common_candidates[i]
                        while tree.vertices[each].rank not in annotated_lineage and tree.vertices[each].name != "root":
                            each = tree.vertices[each].source
                        common_candidates[i] = each 
                    # print(common_candidates)
                    depth = -1
                    taxon = 0
                    common_candidates = set(common_candidates)
                    if len(common_candidates) > 1:
                        for each in common_candidates:
                            try:
                                if annotated_lineage.index(tree.vertices[each].rank) > depth:
                                    depth = annotated_lineage.index(tree.vertices[each].rank)
                                    taxon = tree.vertices[each]
                            except:
                                pass
                    else:
                        taxon = tree.vertices[common_candidates.pop()]

                    while "uncultured" in taxon.name or "unidentified" in taxon.name or "synthetic" in taxon.name:
                        taxon = tree.vertices[taxon.source]
                    
                    while taxon.name != "root":
                        if taxon.name not in assignments:
                            assignments[taxon.name] = []
                        assignments[taxon.name].append(contig)
                        tree.vertices[taxon.taxon].coverage += 1
                        taxon = tree.vertices[taxon.source]
                    tree.vertices[taxon.taxon].coverage += 1

  
tree.add_unassigned()
json = tree.recursive_depth_first_search(1, [], "")[1].replace("[,", "[").replace("},]", "}]").replace("'", "\\'").replace(", \"children\": []", "").strip(",")
if json == "{\"name\": \"root (1)\", \"size\": \"1\"}":
    sys.stderr.write("No assignments could be made besides to root node, and no output will be created. Check your BLAST results, especially e-scores.\n")
else:
    with open(args.output, 'w') as output_file:
        output_file.write(before_html+json+after_html)

    if args.export:
        assignment_string = ""
        for each in assignments:
            assignment_string += each+"\t"+str(assignments[each])+"\n"
        with open(args.export, 'w') as output_file:
            output_file.write(assignment_string)