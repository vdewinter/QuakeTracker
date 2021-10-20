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

// scale to color earthquake points by magnitude
var colorRamp = d3.scale.linear()
    .domain([3,4,5,6,7,8,9])
    .range(["#9b30ff","#003eff","#00ff00",
        "#ffe600","#ffa500","#ff0000","#b81324"]);

// track which magnitudes/colors occur in new reports
var recentColObj = {
    "#9b30ff": false,
    "#003eff": false,
    "#00ff00": false,
    "#ffe600": false,
    "#ffa500": false,
    "#ff0000": false,
    "#b81324": false
};

// draw all static elements on page
function displayMap(points) {
    d3.json("/static/world.json", function(error, world) {
        if (error) {
            return console.error(error);
        }

        svg.append("path")
            .datum(topojson.feature(world, world.objects.subunits))
            .attr("d", path)
            .style("opacity", 0.8);
        
        svg.append("g")
            .attr("class", "historical");
        svg.append("g")
            .attr("class", "recent");

        // draw map points with display: none
        prepareHistoricalPoints(points);
        readRecentQuakes();
    });

    // fault lines
    d3.json("/static/tectonics.json", function(error, data) {
        if (error) {
            return console.error(error);
        }

        svg.append("path")
            .datum(topojson.feature(data, data.objects.tec))
            .attr("class", "tectonic")
            .attr("d", path)
            .style("stroke", 0.1)
            .style("fill", "#6b6b6b")
            .style("opacity", 0.5);
    });

    //slider 
    var currentYear = new Date().getFullYear();
    d3.select("#slider")
        .call(d3.slider()
            .axis(d3.svg.axis().orient("bottom")
            .ticks(15)
            .tickFormat(function(d) {
                return d;
            }))
            .min(1900)
            .max(currentYear)
            .step(1)
            .on("slide", function(event, value) {
                d3.select("#slider-tooltip")
                    .classed("hidden", false)
                    .text(value);

                filterPoints(value);
    }));

    // set up svg's for magnitude filters
    d3.select("#recent-filter")
        .append("svg")
        .attr("class", "rsvg")
        .attr("height", "90px")
        .attr("width", "400px");

    d3.select("#historical-filter")
        .append("svg")
        .attr("class", "hsvg")
        .attr("height", "90px")
        .attr("width", "400px");
}

// format data for display in tooltip, control mouseover and mouseout events
function handleMouseEvents(selection) {
    selection.on("mouseover", function(d) {
        var date = new Date(parseInt(d.timestamp, 10));
        var dateString = (date.getUTCMonth() + 1) + "/" + date.getUTCDate() + "/" + date.getUTCFullYear();
        var t = date.getUTCHours() + ":" + ((date.getUTCMinutes() < 10 ? "0":"") + date.getUTCMinutes()) + " GMT";
        d3.select("#p1").text("M " + d.magnitude);
        d3.select("#p2").text(dateString);
        d3.select("#p3").text(t);
        
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

// request points from the backend to display on the map
function readHistoricalQuakes() {
    d3.json("/read_quakes_from_db", function(error, points) {
        if (error) {
            return console.error(error);
        }

        dataset = points;
        displayMap(points);
    });
}

// put points from backend into array, select the correct g element to append historical points to, call drawing function
function prepareHistoricalPoints(points) {
    var pointsList = [];
    for (var year in points) {
        var yearPoints = points[year];
        for (var i = 0; i < yearPoints.length; i++) {
            pointsList.push(yearPoints[i]);
        }
    }

    var historicalPoints = d3.selectAll(".historical")
        .selectAll(".point")
        .data(pointsList);

    drawHistoricalPoints(historicalPoints);
}

// draw circles for historical points
function drawHistoricalPoints(selection) {
    selection.enter().append("circle", ".point")
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
        .style("display", "none");

    handleMouseEvents(selection);
}

// read array of objects emitted by backend every minute
function readRecentQuakes() {
    d3.json("/new_earthquake", function(error, points) {
        if (error) {
            return console.error(error);
        }
        refreshPoints(points);
    });
}

// dynamically add recent points for new earthquakes, remove recent points for earthquakes older than one week,
// add new points to the historical points collection, and update filter circles
function refreshPoints(points) {
    var recentPoints = d3.selectAll(".recent")
        .selectAll(".newPoint")
        .data(points.filter(function(d) {
            return d.magnitude >= 3;
        }));

    // remove recent circles older than one week
    recentPoints.exit()
        .remove();

    recentPoints.enter().append("circle", ".newPoint")
        .attr("class", "newPoint circle")
        .each(function(d) {
            // pulsing behavior
            var that = this;
            setInterval(function() {
                d3.select(that)
                    .attr("r", function(d) {
                        return Math.pow(10, Math.sqrt(d.magnitude))/40;
                })
                .transition()
                .duration(1500).ease("sine")
                .attr("r", function(d) {
                    return Math.pow(10, Math.sqrt(d.magnitude))/25;
                })
                .transition()
                .duration(1500).ease("sine")
                .attr("r", function(d) {
                    return Math.pow(10, Math.sqrt(d.magnitude))/40;
                });
            }, 3000);
        })
        .style("fill", function(d) {
            // track magnitudes of earthquakes in new reports to determine which filters to deactivate
            var col = colorRamp(Math.floor(d.magnitude));
            if (recentColObj.hasOwnProperty(col)) {
                recentColObj[col] = true;
            }
            return col;
        })
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("display", "none");

    handleMouseEvents(recentPoints);

    // create historical circles if magnitude >= 6
    var historicalPoints = d3.selectAll(".historical")
        .selectAll(".point")
        .data(points.filter(function(d) {
            return d.magnitude >= 6;
        }));

    drawHistoricalPoints(historicalPoints);

    // update magnitude filters
    updateLegend();
}

function updateLegend() {
    // create magnitude filters for recent points
    drawFilterCircles(".rsvg", 3, 10, 21, ".newPoint");
    drawFilterCircles(".rsvg", 4, 15, 43, ".newPoint");
    drawFilterCircles(".rsvg", 5, 20, 69, ".newPoint");
    drawFilterCircles(".rsvg", 6, 25, 100, ".newPoint");
    drawFilterCircles(".rsvg", 7, 30, 140, ".newPoint");
    drawFilterCircles(".rsvg", 8, 40, 188, ".newPoint");
    drawFilterCircles(".rsvg", 9, 40, 250, ".newPoint");

    // create magnitude filters for historical points
    drawFilterCircles(".hsvg", 6, 25, 15, ".point");
    drawFilterCircles(".hsvg", 7, 30, 55, ".point");
    drawFilterCircles(".hsvg", 8, 40, 99, ".point");
    drawFilterCircles(".hsvg", 9, 40, 158, ".point");

    // dynamically disable recent point labels for which no events exist
    for (var color in recentColObj) {
        if (!recentColObj[color]) {
            d3.selectAll(".newPoint" + color.replace("#",""))
                .style("fill", "gray")
                .attr("pointer-events", "none");
        }
    }
}

// draw and label circles for filtering by magnitude
function drawFilterCircles(elt, magnitude, divisor, cx, pointType) {
    var rad = Math.pow(10, Math.sqrt(magnitude))/divisor * 1.3;
    var circleG = d3.select(elt).append("g");
    var col = colorRamp(magnitude);

    circleG.append("circle")
        .attr("class", pointType.replace(".","") + col.replace("#",""))
        .attr("r", rad)
        .style("fill", col)
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
                .attr("r", rad/1.1);
        })
        .on("mouseout", function() {
            d3.select(this)
                .transition().duration(300).ease("sine")
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

// show M6+ earthquakes in year of slider value
function filterPoints(value) {
    d3.selectAll(".circle")
        .style("display", "none");
    if (dataset.hasOwnProperty(value)) {
        d3.selectAll(".point")
            .style("display", function(d) {
                var timestamp = parseInt(d.timestamp, 10);
                year = new Date(timestamp).getUTCFullYear();
                return ((year === value) && (d.magnitude >= 6)) ? "block" : "none";
            });
    }
}

// control which set of points are displayed when buttons are pressed
function displayPoints(pointsToDisplay, pointsToHide) {
    d3.select("#slider-tooltip")
        .classed("hidden", true);
    d3.selectAll(pointsToDisplay)
        .style("display", "block");
    d3.selectAll(pointsToHide)
        .style("display", "none");
}
