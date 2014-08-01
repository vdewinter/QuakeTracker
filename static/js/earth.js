// look at performance measuring tools--
// currently changing attrs is time intensive
// to make slider faster, filter by old year- display none; fiter by new year display block
// or
// make hash table with d3 collection by year, track currently displayed year, 
// collection#oldyear display: none; collection#newyear display:block
var mouse = {x: 0, y: 0};

document.addEventListener('mousemove', function(e){
    mouse.x = e.clientX || e.pageX;
    mouse.y = e.clientY || e.pageY;
}, false);

var width = 960,
    height = 500;

var projection = d3.geo.equirectangular();

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("class", "map");

var g = svg.append("g")
    .attr("class", "main-g");

// colors quake points by magnitude
var colorRamp = d3.scale.linear()
    .domain([3,4,5,6,7,8,9])
    .range(["#9B30FF","#003EFF","#00FF00",
        "#FFE600","orange","red","#B81324"]);

var zoom = d3.behavior.zoom()
    .scaleExtent([1,8])
    .on("zoom", move);

function move() {
  var t = d3.event.translate,
      s = d3.event.scale;
  t[0] = Math.min(width / 2 * (s - 1), Math.max(width / 2 * (1 - s), t[0]));
  t[1] = Math.min(height / 2 * (s - 1) + 230 * s, Math.max(height / 2 * (1 - s) - 230 * s, t[1]));
  zoom.translate(t);
  d3.select(".main-g").style("stroke-width", 1 / s).attr("transform", "translate(" + t + ")scale(" + s + ")");
}

function displayHistoricalQuakes() {
    d3.json("/read_quakes_from_db", function(error, points) {
        if (error) return console.error(error);
        dataset = points;
        displayMap(points);
    });
}

// TODO: use queue to async load: https://github.com/mbostock/queue
function displayMap(points) {
    // land
    d3.json("/static/world.json", function(error, world) {
        if (error) return console.error(error);

        svg.append("path")
            .datum(topojson.feature(world, world.objects.subunits))
            .attr("d", path)
            .style("opacity", 0.9);
        
        // create points inside g elt once world.json has loaded
        svg.append("g")
            .attr("class", "historical");
        svg.append("g")
            .attr("class", "recent");
        createHistoricalPoints(points);
        createRecentPoints();
    });

    // fault lines
    d3.json("/static/tectonics.json", function(error, data) {
        if (error) return console.error(error);

        svg.append("path")
            .datum(topojson.feature(data, data.objects.tec))
            .attr("class", "tectonic")
            .attr("d", path)
            .style("stroke", 0.1)
            .style("fill", "#EEEEEE")
            .style("opacity", 0.5);
    });

    //slider 
    var currentYear = new Date().getFullYear();
    d3.select("#slider")
        .call(d3.slider()
            .axis(d3.svg.axis().orient("bottom")
            .ticks(15)
            .tickFormat(function (d) {return d;}))
            .min(1900)
            .max(currentYear)
            .step(1)
            .on("slide", function(event, value) {
                d3.select("#slider-tooltip")
                    .classed("hidden", false)
                    .text(value);

                filterPoints(value);
        }));

    // magnitude filters
    var newsvg = d3.select("#recent-filter")
        .append("svg")
        .attr("class", "newsvg")
        .attr("height", "90px")
        .attr("width", "400px");

    var othersvg = d3.select("#historical-filter")
        .append("svg")
        .attr("class", "othersvg")
        .attr("height", "90px")
        .attr("width", "400px");

    // filter for recent points
    createFilterCircles(newsvg, 3, 10, 21, ".newPoint");
    createFilterCircles(newsvg, 4, 15, 43, ".newPoint");
    createFilterCircles(newsvg, 5, 20, 69, ".newPoint");
    createFilterCircles(newsvg, 6, 25, 100, ".newPoint");
    createFilterCircles(newsvg, 7, 30, 140, ".newPoint");
    createFilterCircles(newsvg, 8, 40, 188, ".newPoint");
    createFilterCircles(newsvg, 9, 40, 250, ".newPoint");

    // filter for historical points
    createFilterCircles(othersvg, 6, 25, 21, ".point");
    createFilterCircles(othersvg, 7, 30, 61, ".point");
    createFilterCircles(othersvg, 8, 40, 105, ".point");
    createFilterCircles(othersvg, 9, 40, 164, ".point");
}

// create a g elt in which circle and text at center will be created

function createFilterCircles(elt, magnitude, divisor, cx, pointType) {
    var rad = Math.pow(10, Math.sqrt(magnitude))/divisor * 1.3;
    var circleG = elt.append("g");

    circleG.append("circle")
        .attr("r", rad)
        .style("fill", function() {
            return (colorRamp(magnitude));
        })
        .attr("cx", cx)
        .attr("cy", "40")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.select("#slider-tooltip")
                .classed("hidden", true);
            d3.selectAll(pointType)
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === magnitude) ? "block" : "none";
                });
        })
        .on("mouseover", function() {
            d3.select(this)
                .transition().duration(300).ease("sine")
                .attr("r", rad/1.2);
        })
        .on("mouseout", function() {
            d3.select(this)
                .transition().duration(500).ease("sine")
                .attr("r", rad);
        });

    circleG.append("text")
        .attr("dy", function() {
            return 44;
        })
        .attr("dx", function() {
            return cx - 3;
        })
        .style("font-size", "11px")
        .style("fill", "white")
        .style("pointer-events", "none")
        .text(function() {
            return magnitude;
        });
}

function createRecentPoints() {
    d3.json("/new_earthquake", function(error, points) {
        if (error) return console.error(error);
        console.log(points);
        data = points;
        refreshPoints();
    });
}

function refreshPoints() {
    var recentPoints = d3.select(".recent")
        .selectAll(".newPoint")
        .data(data.filter(function(d) {
            return d.magnitude >= 3;
        }));

    // only create circles if magnitude >= 3
    recentPoints.enter().append("circle", ".newPoint")
        .attr("class", "newPoint circle")
        .attr("r", function(d) {
            return Math.pow(10, Math.sqrt(d.magnitude))/40;
        })
        .style("fill", function(d) {
            return (colorRamp(Math.floor(d.magnitude)));
        })
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none")
        .style("opacity", 0.9)
        .on("mouseover", function(d) {
            console.log(d);
            var date = new Date(parseInt(d.timestamp, 10));
            var str = (date.getUTCMonth() + 1) + "/" + date.getUTCDate() + "/" + date.getUTCFullYear(); //also show time/place?
            console.log(str);
            d3.select("#p1").text("M" + parseFloat(d.magnitude).toFixed(1));
            d3.select("#p2").text(str);
            
            var xPos = mouse["x"] + 10;
            var yPos = mouse["y"] + 5;

            d3.select("#tooltip")
                .classed("hidden", false)
                .style("left", + xPos + "px")
                .style("top", + yPos + "px");
        })
        .on("mouseout", function() {
            d3.select("#tooltip")
                .classed("hidden", true);
        });

    // remove recent points > 1 week old
    recentPoints.exit()
        .remove();

    // also add new earthquakes with magnitude >= 6 to historical points
    var historicalPoints = d3.selectAll(".historical")
        .data(data.filter(function(d) {
            return d.magnitude >= 6;
        }));

    // does this create duplicate points, and does that matter? would affect opacity
    historicalPoints.enter().append("circle", ".newPoint")
        .attr("class", "newPoint circle")
        .attr("r", function(d) {
            return Math.pow(10, Math.sqrt(d.magnitude))/90;
        })
        .style("fill", function(d) {
            return (colorRamp(Math.floor(d.magnitude)));
        })
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none")
        .style("opacity", 0.9)
        .on("mouseover", function(d) {
            console.log(d);
            var date = new Date(parseInt(d.timestamp, 10));
            var str = (date.getUTCMonth() + 1) + "/" + date.getUTCDate() + "/" + date.getUTCFullYear(); //also show time?
            console.log(str);
            d3.select("#p1").text("M" + parseFloat(d.magnitude).toFixed(1));
            d3.select("#p2").text(str);
            
            var xPos = mouse["x"] + 10;
            var yPos = mouse["y"] + 5;

            d3.select("#tooltip")
                .classed("hidden", false)
                .style("left", + xPos + "px")
                .style("top", + yPos + "px");
        })
        .on("mouseout", function() {
            d3.select("#tooltip")
                .classed("hidden", true);
        });
}

function createHistoricalPoints(points) {
    var pointsList = [];
    for (var year in points) {
        var yearPoints = points[year];
        for (var i = 0; i < yearPoints.length; i++) {
            pointsList.push(yearPoints[i]);
        }
    }

    d3.select("g.historical")
        .selectAll(".point")
        .data(pointsList.filter(function(d) {
            return d.magnitude >= 6;
        }))
        .enter().append("circle", ".point")
        .attr("class", "point circle")
        .attr("r", function(d) {
            return Math.pow(10, Math.sqrt(d.magnitude))/90;
        })
        .style("fill", function(d) {
            return (colorRamp(Math.floor(d.magnitude)));
        })
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none")
        .style("opacity", 0.9)
        .on("mouseover", function(d) {
            var tooltip = d3.select("#tooltip");
            console.log(d);
            var date = new Date(parseInt(d.timestamp, 10));
            var str = (date.getUTCMonth() + 1) + "/" + date.getUTCDate() + "/" + date.getUTCFullYear();
            console.log(str);
            d3.select("#p1").text("M" + parseFloat(d.magnitude).toFixed(1));
            d3.select("#p2").text(str);

            var xPos = mouse["x"] + 5;
            var yPos = mouse["y"]+ 5;

            d3.select("#tooltip")
                .classed("hidden", false)
                .style("left", + xPos + "px")
                .style("top", + yPos + "px");
        })
        .on("mouseout", function() {
            d3.select("#tooltip")
                .classed("hidden", true);
        });
}

function filterPoints(value) {
    if (dataset.hasOwnProperty(value)) {
        d3.selectAll(".circle")
            .style("display", function(d) {
                var timestamp = parseInt(d.timestamp, 10);
                year = new Date(timestamp).getUTCFullYear();
                return ((year === value) && (d.magnitude >= 6)) ? "block" : "none";
            });
    }
}

function displayHistoricalPoints() {
    d3.select("#slider-tooltip")
        .classed("hidden", true);
    d3.selectAll(".point")
        .style("display", "block");
    d3.selectAll(".newPoint")
        .style("display", "none");
}

function displayRecentPoints() {
    d3.select("#slider-tooltip")
        .classed("hidden", true);
    d3.selectAll(".newPoint")
        .style("display", "block");
    d3.selectAll(".point")
        .style("display", "none");
}

// add drag behavior
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

