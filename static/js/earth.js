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
var pathRamp = d3.scale.linear()
    .domain([2,3,4,5,6,7,8,9])
    .range(["#9B30FF","#003EFF","teal","#00FF00",
        "yellow","orange","red","#B81324"]);

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
            .style("opacity", 0.7);
        
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

    // recent filter
    var newsvg = d3.select("#recent-filter")
        .append("svg")
        .attr("class", "newsvg")
        .attr("height", "60px")
        .attr("width", "400px");

    newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(2))/10;
        })
        .style("fill", function() {
            return (pathRamp(2));
        })
        .attr("cx", "11")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 2) ? "block" : "none";
                });
        });
        
    newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(3))/10;
        })
        .style("fill", function() {
            return (pathRamp(3));
        })
        .attr("cx", "27")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 3) ? "block" : "none";
                });
        });

    newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(4))/15;
        })
        .style("fill", function() {
            return (pathRamp(4));
        })
        .attr("cx", "47")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 4) ? "block" : "none";
                });
        });

    newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(5))/20;
        })
        .style("fill", function() {
            return (pathRamp(5));
        })
        .attr("cx", "70")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 5) ? "block" : "none";
                });
        });

    newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(6))/25;
        })
        .style("fill", function() {
            return (pathRamp(6));
        })
        .attr("cx", "97")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 6) ? "block" : "none";
                });
        });

   newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(7))/30;
        })
        .style("fill", function() {
            return (pathRamp(7));
        })
        .attr("cx","130")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 7) ? "block" : "none";
                });
        });

    newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(8))/40;
        })
        .style("fill", function() {
            return (pathRamp(8));
        })
        .attr("cx", "168")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 8) ? "block" : "none";
                });
        });

    newsvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(9))/40;
        })
        .style("fill", function() {
            return (pathRamp(9));
        })
        .attr("cx", "219")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".newPoint")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 9) ? "block" : "none";
                });
        });

    // historical filter
    var othersvg = d3.select("#historical-filter")
        .append("svg")
        .attr("class", "othersvg")
        .attr("height", "60px")
        .attr("width", "400px");

    othersvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(6))/25;
        })
        .style("fill", function() {
            return (pathRamp(6));
        })
        .attr("cx", "11")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".point")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 6) ? "block" : "none";
                });
        });

   othersvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(7))/30;
        })
        .style("fill", function() {
            return (pathRamp(7));
        })
        .attr("cx", "45")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".point")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 7) ? "block" : "none";
                });
        });

    othersvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(8))/40;
        })
        .style("fill", function() {
            return (pathRamp(8));
        })
        .attr("cx", "85")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".point")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 8) ? "block" : "none";
                });
        });

    othersvg.append("circle")
        .attr("r", function() {
        return Math.pow(10, Math.sqrt(9))/40;
        })
        .style("fill", function() {
            return (pathRamp(9));
        })
        .attr("cx", "135")
        .attr("cy", "30")
        .on("click", function() {
            d3.selectAll(".circle")
                .style("display", "none");
            d3.selectAll(".point")
                .style("display", function(d) {
                    return (Math.floor(d.magnitude) === 9) ? "block" : "none";
                });
        });

}

var createRecentPoints = function () {
    d3.json("/new_earthquake", function(error, points) {
        if (error) return console.error(error);
        console.log(points);
        data = points;
        refreshPoints();
    });
};

var refreshPoints = function() {
    var recentPoints = d3.select(".recent")
        .selectAll(".newPoint")
        .data(data);

    recentPoints.enter().append("circle", ".newPoint")
        .attr("class", "newPoint circle")
        // .attr("r", 0).transition()
        // .duration(1000) // these lines is making mouseover be considered an undefined func
        .attr("r", function(d) {
            return Math.pow(10, Math.sqrt(d.magnitude))/40;
        })
        .style("fill", function(d) {
            return (pathRamp(Math.floor(d.magnitude)));
        })
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none")
        .on("mouseover", function(d) {
            console.log(d);
            var date = new Date(parseInt(d.timestamp));
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

    recentPoints.exit()
        .remove();
};

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
        .data(pointsList)
        .enter().append("circle", ".point")
        .attr("class", "point circle")
        .attr("r", function(d) {
            return Math.pow(10, Math.sqrt(d.magnitude))/90;
        })
        .style("fill", function(d) {
            return (pathRamp(Math.floor(d.magnitude)));
        })
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none")

        .on("mouseover", function(d) {
            var tooltip = d3.select("#tooltip");
            console.log(d);
            var date = new Date(parseInt(d.timestamp));
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
                year = new Date(d.timestamp).getUTCFullYear();
                return (year === value) ? "block" : "none";
            });
    }
}

function displayHistoricalPoints() {
    d3.selectAll(".point")
        .style("display", "block");
    d3.selectAll(".newPoint")
        .style("display", "none");
}

function displayRecentPoints() {
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

