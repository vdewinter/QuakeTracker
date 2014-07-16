d3.json("http://www.corsproxy.com/earthquake.usgs.gov/earthquakes/feed/geojson/2.5/day", function(error, data) {
   var newQuakes = svg.append("g")
        .attr("class", "new-quakes") 
        .selectAll(".newQuake")
        .data(data.features.reverse()))
        .enter().append("g")
            .attr("class", "quake")
            .attr("transform", function(d) {
                return "translate(" + projection
            })
});