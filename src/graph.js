
var data;

var graph = {};
var tree = {};


function setup (){

    data = JSON.parse(document.getElementById("data").innerHTML)

    graph_tree(data);
    graph_classification(data, Object.keys(data.labels));



    update_tree(tree.root)
}


function graph_tree(data){
    tree.size = {width:  1000, height: 600}
    tree.margin = {top: 100, right: 30, bottom: 20, left: 70}

    tree.svg = d3.select("#tree")
                 .attr("height", tree.size.height+120)
                 .attr("viewBox", [-tree.margin.left, -tree.margin.top, tree.size.width, tree.size.height])
                .attr("preserveAspectRatio", "xMidYMid meet")
                .append("g")
                .attr("transform",
                      "translate(" + tree.margin.left + "," + tree.margin.top + ")");

    // Give the data to this cluster layout:
    tree.root = d3.hierarchy(data.tree);
    tree.all = tree.root.copy();

    tree.dx = 50
    tree.dy = tree.size.height / (tree.root.height + 1);

    tree.root.x0 = tree.dy / 2;
    tree.root.y0 = 0;

    // copy children to _children, remove children if depth > 3
    tree.root.descendants().forEach((d, i) => {
        d.nodeid = i;
        d._children = d.children;
        if (d.depth > 3) d.children = null;
    });


    tree.group = {
        link: tree.svg.append("g")
                  .attr("fill", "none")
                  .attr("stroke", "#555")
                  .attr("stroke-opacity", 0.4)
                  .attr("stroke-width", 1.5),
        node: tree.svg.append("g")
                  .attr("cursor", "pointer")
                  .attr("pointer-events", "all")
    }

}


function update_tree(source) {

    diagonal = d3.linkHorizontal().x(d => d.y).y(d => d.x)

    var duration = d3.event && d3.event.altKey ? 2500 : 250;
    var nodes = tree.root.descendants().reverse();
    var links = tree.root.links();



    // Compute the new tree layout.
    d3.tree().nodeSize([tree.dx, tree.dy])(tree.root);

    var limits = {left: tree.root, right:tree.root};
    tree.root.eachBefore(node => {
        if (node.x < limits.left.x) limits.left = node;
        if (node.x > limits.right.x) limits.right = node;
    });

    var height = limits.right.x - limits.left.x + tree.margin.top + tree.margin.bottom;

    var transition = tree.svg.transition()
        .duration(duration)
        .attr("viewBox", [-tree.margin.left, limits.left.x - tree.margin.top, tree.size.width, height])
        .tween("resize", window.ResizeObserver ? null : () => () => svg.dispatch("toggle"));

    // Update the nodes…
    var node = tree.group.node.selectAll("g")
      .data(nodes, d => d.nodeid);

    // Enter any new nodes at the parent's previous position.
    var nodeEnter = node.enter().append("g")
        .attr("transform", d => `translate(${source.y0},${source.x0})`)
        .attr("fill-opacity", 0)
        .attr("stroke-opacity", 0)
        .on("click", (event, d) => {
          d.children = d.children ? null : d._children;
          update_tree(d);
        });

    nodeEnter.append("circle")
        .attr("r", 2.5)
        .attr("fill", d => d._children ? "#555" : "#999")
        .attr("stroke-width", 10);

    nodeEnter.append("text")
        .attr("dy", "0.31em")
        .attr("x", d => d._children ? -6 : 6)
        .attr("text-anchor", d => d._children ? "end" : "start")
        .text(d => d.data.name)
      .clone(true).lower()
        .attr("stroke-linejoin", "round")
        .attr("stroke-width", 3)
        .attr("stroke", "white");

    // Transition nodes to their new position.
    var nodeUpdate = node.merge(nodeEnter).transition(transition)
        .attr("transform", d => `translate(${d.y},${d.x})`)
        .attr("fill-opacity", 1)
        .attr("stroke-opacity", 1);

    // Transition exiting nodes to the parent's new position.
    var nodeExit = node.exit().transition(transition).remove()
        .attr("transform", d => `translate(${source.y},${source.x})`)
        .attr("fill-opacity", 0)
        .attr("stroke-opacity", 0);

    // Update the links…
    var link = tree.group.link.selectAll("path")
      .data(links, d => d.target.id);

    // Enter any new links at the parent's previous position.
    var linkEnter = link.enter().append("path")
        .attr("d", d => {
          const o = {x: source.x0, y: source.y0};
          return diagonal({source: o, target: o});
        });

    // Transition links to their new position.
    link.merge(linkEnter).transition(transition)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition(transition).remove()
        .attr("d", d => {
          const o = {x: source.x, y: source.y};
          return diagonal({source: o, target: o});
        });

    // Stash the old positions for transition.
    tree.root.eachBefore(d => {
      d.x0 = d.x;
      d.y0 = d.y;
    });

    update_graph();
}


    



function graph_classification (data, classes){
    graph.pointSize = 25;
    graph.size = {width:  graph.pointSize*classes.length ,
                  height: graph.pointSize*data.contigs.length}
    graph.margin = {top: 100, right: 30, bottom: 20, left: 70}

    graph.svg = d3.select("#graph")
                  .attr("height", graph.size.height+120)
                  .attr("viewBox", [-graph.margin.left, -graph.margin.top,
                                    graph.size.width + graph.margin.left,
                                    graph.size.height + graph.margin.top])

    graph.scale = { y: d3.scaleBand()
                         .domain(d3.map(data.contigs, d=>d.seq))
                         .range([0, graph.size.height])
                         .padding(0.1),
                    x: d3.scaleBand()
                         .domain(classes)
                         .range([0, graph.size.width])
                         .padding(0.1),
                    color: d3.scaleOrdinal()
                             .domain(classes)
                             .range(d3.schemeTableau10)
                  }


    graph.scale.yAxis = graph.svg.append("g")
                             .call(d3.axisLeft(graph.scale.y))
                             .selectAll("text")
                             .attr("id", (d) => `tick-${d}`)

    graph.scale.xAxis =  graph.svg.append("g")
                              .call(d3.axisTop(graph.scale.x).tickFormat((d)=>data.labels[d]))
   graph.scale.xAxis
                              .selectAll("text")
                              .attr("dy", "1")
                              .attr("dx", "10")
                              .attr("transform", "rotate(-45)")
                              .style("text-anchor", "start")
                              .attr("id", (d)=> `tick-${d}`)



    graph.elements = graph.svg.append('g')

    graph.data = d3.map(data.contigs,
                        d => d3.map(Object.entries(d.class),
                                    e => {
                                        shape = d3.symbol()
                                        if(e[0] == d.taxid) shape.type(d3.symbolSquare);
                                        else                shape.type(d3.symbolCircle);

                                        shape.size(graph.pointSize*15)

                                        return {seq: d.seq , id: e[0],
                                                count: e[1], length: d.length,
                                                shape: shape}
                                    })).flat()
}


function update_graph(){

    var classes = {"other":"other", "0":"0"};

    tree.root.eachBefore( (d) => {
        classes[d.data.id.toString()] = d.data.id.toString();
    })

    graph.show = {}
    Object.keys(classes).forEach( (d) => { graph.show[d] = {} })


    tree.root.leaves().forEach( (d) => {
        tree.all.find((e) => e.data.id.toString() == d.data.id.toString())
            .descendants()
            .forEach((e) => classes[e.data.id.toString()]=d.data.id.toString())
    } )


    graph.data.forEach( (d) => {
        id = classes[d.id];
        if(graph.show[id][d.seq])
            graph.show[id][d.seq].count += d.count;
        else
            graph.show[id][d.seq] = {
                seq: d.seq , id: id,
                count: d.count, length: d.length,
                shape: d.shape
            };
    } )



    // Recreate classes to include only entries that have count, in tree DFS order

    classes = ['other', '0'];
    tree.root.eachBefore( (d) => {
        if(Object.keys(graph.show[d.data.id.toString()]).length)
            classes.push(d.data.id.toString());
    })

    graph.size.width = graph.pointSize*classes.length;

    graph.scale.x = d3.scaleBand()
                      .domain(classes)
                         .range([0, graph.size.width])
                         .padding(0.1),

    graph.scale.xAxis.call(d3.axisTop(graph.scale.x).tickFormat((d)=>data.labels[d]))
                              .selectAll("text")
                              .attr("dy", "1")
                              .attr("dx", "10")
                              .attr("transform", "rotate(-45)")
                              .style("text-anchor", "start")
                              .attr("id", (d)=> `tick-${d}`)


    graph.show = Object.values(graph.show).map(Object.values).flat()

    graph.elements
        .selectAll("path")
        .data(graph.show)
        .join("path")
        .classed('data', true)
        // .attr("cx", (d) => graph.scale.x(d.id) + graph.scale.x.bandwidth()/2 )
        // .attr("cy", (d) => graph.scale.y(d.seq) + graph.scale.y.bandwidth()/2 )
        // .attr("x", (d) => graph.scale.x(d.id) )
        // .attr("y", (d) => graph.scale.y(d.seq) )
        .attr("transform", (d) => `translate(${graph.scale.x(d.id)+12.5} ${graph.scale.y(d.seq)+12.5}) ` )
        .attr("d", (d) => d.shape())
        .attr('stroke', (d) => graph.scale.color(d.id))
         .attr('stroke-width', 1)
         .attr('fill', (d) => graph.scale.color(d.id))
         .attr("fill-opacity", (d) => d.count/d.length)
         // .attr("r", graph.scale.x.bandwidth()/2)
         // .attr("width", graph.scale.x.bandwidth())
         // .attr("height", graph.scale.y.bandwidth())
         .on("mouseover", function(elem, data){
             // data = d3.select(this).data()[0]
             d3.select(`[id="tick-${data.seq}"]`).classed('highlight', true)
             d3.select(`[id="tick-${data.id}"]`).classed('highlight', true)
         })
         .on("mouseout", function(elem, data){
             // data = d3.select(this).data()[0]
             d3.select(`[id="tick-${data.seq}"]`).classed('highlight', false)
             d3.select(`[id="tick-${data.id}"]`).classed('highlight', false)
         })

}


window.addEventListener('load', setup)
