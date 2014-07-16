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

var circles = null;

// colors quake points by magnitude
var pathRamp = d3.scale.linear()
    .domain([6,7,8,9])
    .range(["yellow","orange","red","#B81324"]);

function dragMove(d) {
    d3.select(this)
        .attr("cx", d.x = Math.max(r, Math.min(width - r, d3.event.x)))
        .attr("cy", d.y = Math.max(r, Math.min(height - r, d3.event.y)));
}

function displayHistoricalQuakes() {
    d3.json("/read_quakes_from_db", function(error, points) {
        if (error) return console.error(error);
        dataset = points;
        displayMap(points);
    });
}

function displayMap(points) {
    // land
    d3.json("/static/world.json", function(error, world) {
        if (error) return console.error(error);

        svg.append("path")
            .datum(topojson.feature(world, world.objects.subunits))
            .attr("d", path);
        
        // create points inside g elt once world.json has loaded
        svg.append("g");
        createPoints(points);
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
    var currentYear = new Date().getFullYear();
    d3.select("#slider")
        .call(d3.slider()
            .axis(d3.svg.axis().orient("bottom").ticks(10))
            .min(currentYear - 500)
            .max(currentYear)
            .step(1)
            .on("slide", function(event, value) {
                filterPoints(value);
        }));
}

function createPoints(points) {
    var pointsList = [];
    for (var year in points) {
        var yearPoints = points[year];
        for (var i = 0; i < yearPoints.length; i++) {
            pointsList.push(yearPoints[i]);
        }
    }

    d3.select("g")
        .selectAll(".point")
        .data(pointsList)
        .enter().append("circle", ".point")
        .attr("class", function(d) {
            return d.year;
        })
        .attr("r", function(d) {
            return d.magnitude;
        })
        .style("fill", function(d) {
            return (pathRamp(d.magnitude));
        })
        .style("stroke", 0.001)
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none")
        .on("mouseover", function() {
            focus.style("opacity", 1);
        });
        // .on("mousemove", function(d) {
        //     var o = projection(d.geometry.coordinates);
        //     focus
        //         .text(d.magnitude + ' ' + moment(+d.properties.time).calendar())
        //         .attr("dy", +20)
        //         .attr("text-anchor", "middle")
        //         .attr("transform", "translate(" + o[0] + "," + o[1] + ")");
        // });
        circles = d3.selectAll("circle");
}

function filterPoints(value) {
    // as slider moves, see if value in dataset; show circles with class value
    if (dataset.hasOwnProperty(value)) {
        circles
            .style("display", function(d) {
                return (d.year === value) ? "block" : "none";
            });
    }
}

function displayAllPoints() {
    console.log("running");
    circles
        .style("display", "block");
}

function displayRealtimeQuakes() {
// http://comcat.cr.usgs.gov/fdsnws/event/1/[METHOD[?PARAMETERS]]
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


