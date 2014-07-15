// create array of yrs from object, map slider to years- consider only 300 yrs?

var width = 1200,
    height = width/2;

var projection = d3.geo.equirectangular();

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var drag = d3.behavior.drag()
    .origin(Object)
    .on("drag", dragMove);

// for labeling points
// var tooltip = d3.select("body")
//     .append("div")
//     .style("position", "absolute")
//     .style("z-index", "10")
//     .style("visibility", "hidden")
//     .text("a simple tooltip");

// colors quake points by magnitude
var pathRamp = d3.scale.linear()
    .domain([6,7,8,9])
    .range(["yellow","orange","red","#B81324"]);

function dragMove(d) {
    d3.select(this)
        .attr("cx", d.x = Math.max(r, Math.min(width - r, d3.event.x)))
        .attr("cy", d.y = Math.max(r, Math.min(height - r, d3.event.y)));
}

function displayMap() {
    // land
    d3.json("/static/world.json", function(error, world) {
        if (error) return console.error(error);

        svg.append("path")
            .datum(topojson.feature(world, world.objects.subunits))
            .attr("d", path);
    });

    // fault lines
    d3.json("/static/tectonics.json", function(error, data) {
        if (error) return console.error(error);

        svg.append("path")
            .datum(topojson.feature(data, data.objects.tec))
            .attr("class", "tectonic")
            .attr("d", path)
            .style("stroke", 0.1)
            .style("fill", "white")
            .style("opacity", 0.5);
    });

    //slider 
    d3.select("#slider")
        .call(d3.slider()
            .axis(d3.svg.axis().orient("bottom").ticks(10))
            .min(-2500)
            .max(2014)
            .step(1)
            .on("slide", function(event, value) {
                console.log(value);
                filterPoints(value);
        }));
}

function filterPoints(value) {
    console.log(dataset[value]);
    if (dataset[value] == value) {
        // plot each point in array that is value of year key
        for (i = 0; i < dataset[value].length; i++) {
            displayPoint(dataset[value][i]);
        }
    }
}

function displayPoint(point) {
    // pins for historical data
    svg.selectAll(".pin")
        .data(points)
        .enter().append("circle", ".pin")

        // show info on hover
        // .append("svg:title")
        // .text(function(d) {
        //     return d.magnitude, d.month, d.day, d.year;
        // })

        // radius proportional to magnitude of quake
        .attr("r", function(d) {
            return d.magnitude/2;
        })
        .style("fill", function(d) {
            return (pathRamp(d.magnitude));
        })
        .style("stroke", 0.001)
        // lat and lon
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        });
}

function displayHistoricalQuakes() {
    d3.json("/read_quakes_from_db", function(error, points) {
        if (error) return console.error(error);
        dataset = points;
        return points;
    });
}

function displayRealtimeQuakes() {

}


// ROTATION http://bl.ocks.org/mbostock/5731578
// dragging: http://bl.ocks.org/mbostock/3795040 (globe) and http://bl.ocks.org/mbostock/1557377 (dragging) -- interactive, draggable globe
function globeView() { // orthographic
//     var projection = d3.geo.orthographic();

//     var lambda = d3.scale.linear()
//         .domain([0, height])
//         .range([90, -90]);

//     var phi = d3.scale.linear()
//         .domain([0, height])
//         .range([90, -90]);

//     svg.selectAll("#map")
//         .attr("cx", function(d) {
//             return d.x;
//         })
//         .attr("cy", function(d) {
//             return d.y;
//         })
//         .call(drag);
}


