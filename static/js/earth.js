// look at performance measuring tools--
// currently changing attrs is time intensive
// to make slider faster, filter by old year- display none; fiter by new year display block
// or
// make hash table with d3 collection by year, track currently displayed year, 
// collection#oldyear display: none; collection#newyear display:block

var width = 1200,
    height = width/2;

var projection = d3.geo.equirectangular();

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var circles = null;

// colors quake points by magnitude
var pathRamp = d3.scale.linear()
    .domain([2,3,4,5,6,7,8,9])
    .range(["purple","blue","teal","green",
        "yellow","orange","red","#B81324"]);

// var drag = d3.behavior.drag()
//     .origin(Object)
//     .on("drag", dragMove);


// function dragMove(d) {
//     d3.select(this)
//         .attr("cx", d.x = Math.max(r, Math.min(width - r, d3.event.x)))
//         .attr("cy", d.y = Math.max(r, Math.min(height - r, d3.event.y)));
// }

function displayHistoricalQuakes() {
    d3.json("/read_quakes_from_db", function(error, points) {
        if (error) return console.error(error);
        dataset = points;
        displayMap(points);
    });
}

function convertObjToArr(points) {
    var keys = Object.keys(points),
        arr = [];
    for (var i=0; i < keys.length; i++) {
        var current_elem = points[keys[i]];
        arr.push(current_elem);
    }
    return arr;
}

// this is diff from create points only in that this sets display: block, circles appended to newg, and class is .newPoint
function displayRecentQuakes() {
    d3.json("/new_earthquake", function(error, points) {
        if (error) return console.error(error);
        console.log(points);
        // do i need to put points in list for below to work?

        points = convertObjToArr(points);
        
        d3.select(".recent")
            .selectAll(".newPoint")
            .data(points)
            .enter().append("circle", ".newPoint")
            .attr("r", function(d) {
                return Math.pow(10, Math.sqrt(d.magnitude))/60;
            })
            .style("fill", function(d) {
                return (pathRamp(d.magnitude));
            })
            // there might be a pt with no lat/long- filter func
            .attr("transform", function(d) {
                return "translate(" + projection ([d.longitude, d.latitude]) + ")";
            })
            .style("display", "block")
            // better to move the following to CSS?
            .on("mouseover", function(d) {
                txt.style("opacity", 1);
                var p = projection([d.longitude, d.latitude]);
                var date = new Date(d.timestamp);
                var str = (date.getUTCMonth() + 1) + "/" + date.getUTCDate() + "/" + date.getUTCFullYear();
                txt.text(parseFloat(d.magnitude).toFixed(1) + ", " + str)
                    .style("fill", "#7D26CD")
                    .style("stroke", "#000000")
                    .style("stroke-width", 0.05)
                    .attr("dy", ".5em")
                    .attr("text-anchor", "middle")
                    .attr("transform", "translate(" + p[0] + "," + (p[1] - 19) + ")");
            })
            .on("mouseout", function() {
                txt.style("opacity", 0);
            });

        circles = d3.selectAll("circle");
        // add point labels here so they are drawn on top of all other layers
        var txt = svg.append("text")
            .attr("class", "txt");
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
        svg.append("g")
            .attr("class", "historical");
        svg.append("g")
            .attr("class", "recent");
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
            .axis(d3.svg.axis().orient("bottom")
            .ticks(15))
            // .tickFormat(d3.format("d"))
            .min(1900)
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

    // points = convertObjToArr(points);
    d3.select("g.historical")
        .selectAll(".point")
        .data(pointsList)
        .enter().append("circle", ".point")
        .attr("r", function(d) {
            return Math.pow(10, Math.sqrt(d.magnitude))/100;
        })
        .style("fill", function(d) {
            return (pathRamp(d.magnitude));
        })
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none")
        // better to move the following to CSS?
        .on("mouseover", function(d) {
            txt.style("opacity", 1);
            var p = projection([d.longitude, d.latitude]);
            var date = new Date(d.timestamp);
            var str = (date.getUTCMonth() + 1) + "/" + date.getUTCDate() + "/" + date.getUTCFullYear();
            txt.text(parseFloat(d.magnitude).toFixed(1) + ", " + str)
                .style("fill", "#7D26CD")
                .style("stroke", "#000000")
                .style("stroke-width", 0.05)
                .attr("dy", ".5em")
                .attr("text-anchor", "middle")
                .attr("transform", "translate(" + p[0] + "," + (p[1] - 19) + ")");
        })
        .on("mouseout", function() {
            txt.style("opacity", 0);
        });

    circles = d3.selectAll("circle");
    // add point labels here so they are drawn on top of all other layers
    var txt = svg.append("text")
        .attr("class", "txt");
}

function filterPoints(value) {
    if (dataset.hasOwnProperty(value)) {
        circles
            .style("display", function(d) {
                year = new Date(d.timestamp).getUTCFullYear();
                return (year === value) ? "block" : "none";
            });
    }
}

function displayAllPoints() {
    circles
        .style("display", "block");
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


