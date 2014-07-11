function displayMap() {
    var width = 1250,
        height = 830;

    var projection = d3.geo.equirectangular();

    var path = d3.geo.path()
        .projection(projection);

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    d3.json("world.json", function(error, world) {
        if (error) return console.error(error);

        svg.append("path")
            .datum(topojson.feature(world, world.objects.subunits))
            .attr("d", path);
    });
}

// --------------------------------JQUERY/AJAX

// function clickPastQuakes(event, obj){
//     ;
//     }

