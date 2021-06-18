
var data;


function setup (){
    var size = {width: 150, height: 150};

  // create a tooltip
  var Tooltip = d3.select("#graph")
    .append("div")
    .attr("class", "tooltip")
    .style("background-color", "white")
    .style("border", "solid")
    .style("border-width", "2px")
    .style("border-radius", "5px")
    .style("padding", "5px")
    .style("display", "none")

  // Three function that change the tooltip when user hover / move / leave a cell
  var mouseover = function(d) {
    Tooltip
      .style("display", "block")
  }
    var mousemove = function(event, d) {
      console.log(d)
    Tooltip
            .html(`<b>${d.data.seq}</b><br><i>${(d.parent)?d.data.name:""}</i><br>${d.data.kmers}`)
      .style("left", (event.pageX+20) + "px")
      .style("top", event.pageY + "px")
  }
  var mouseleave = function(d) {
    Tooltip
      .style("display", "none")
  }


    data = JSON.parse(document.getElementById("data").innerHTML)

    data.children.sort((a,b) => (b.id - a.id)).forEach((d, i) => {
        data.children[i].div = d3.select("#graph")
                                 .append("div")
                                 .attr('id', data.children[i].seq)
                                 .classed('graph', true)

        data.children[i].div
            .append("h3")
            .text(data.children[i].seq)
        data.children[i].div
            .append("h4")
            .text(data.children[i].name)
        data.children[i].svg = data.children[i].div
                        .append("svg")
                        .attr("width", size.width)
                        .attr("height", size.height)
                        .append("g")


        data.children[i].kmers = d.length
        data.children[i].root = d3.hierarchy(d)
        data.children[i].root.sum((d) => d.kmers)


        data.children[i].root.each((d) => d.data.seq=data.children[i].seq)

        var packLayout = d3.pack()
                           .size([size.width, size.height])
        packLayout(data.children[i].root)

        data.children[i].circles = data.children[i].svg
                                       .selectAll('circle')
                                       .data(data.children[i].root.descendants())
                                       .enter()
                                       .append('circle')
                                       .attr('cx', function(d) { return d.x; })
                                       .attr('cy', function(d) { return d.y; })
                                       .attr('r', function(d) { return d.r; })
                                       .attr('class', (d) =>
                                           d.ancestors().map((d) => {
                                               if(d.parent)
                                                   return d.data.name
                                           }).join(' '))
                                       .on("mouseover", mouseover)
                                       .on("mousemove", mousemove)
                                       .on("mouseleave", mouseleave)

        // var treemap = d3.treemap()
        //                 .size([size.width, size.height])
        //                 .paddingOuter(10)
        //                 .tile(d3.treemapSliceDice);
        // treemap(data.children[i].root)

        // data.children[i].circles = data.children[i].svg
        //                                .selectAll('rect')
        //                                .data(data.children[i].root.descendants())
        //                                .enter()
        //                                .append('rect')
        //                                .attr('x', (d) => d.x0)
        //                                .attr('y', (d) => d.y0)
        //                                .attr('width', (d) => d.x1 - d.x0 )
        //                                .attr('height', (d) =>  d.y1 - d.y0 )
        //                                .attr('class', (d) =>
        //                                    d.ancestors().map((d) => {
        //                                        if(d.parent)
        //                                            return d.data.name
        //                                    }).join(' '))
        //                                .on("mouseover", mouseover)
        //                                .on("mousemove", mousemove)
        //                                .on("mouseleave", mouseleave)


    })

}

window.addEventListener('load', setup)
