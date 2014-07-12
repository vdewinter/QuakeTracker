var width = 1250,
    height = 830;

var projection = d3.geo.mercator();

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

// colors quake points by magnitude
var pathRamp = d3.scale.linear()
    .domain([6,7,8,9])
    .range(["yellow","orange","red","#0x800517"]);

// var siteLabel = svg.aappend("svg:text")
//     .attr("x", 20)
//     .attr("y", 20)
//     .text("Click for details");

function displayMap() {
    d3.json("/static/world.json", function(error, world) {
        if (error) return console.error(error);

        svg.append("path")
            .datum(topojson.feature(world, world.objects.subunits))
            .attr("d", path);
    });

    // overlay fault lines
    // d3.json("/static/plate_boundaries.json", function(error, world) {
    //     if (error) return console.error(error);

    //     svg.append("path") // or insert?
    //         .datum(topojson.object(data, data.objects.tec)) // binds data directly without computing a join
    //         .attr("class", "tectonic")
    //         .attr("d", path);
    // });
}

function displayHistoricalQuakes() {
    d3.json("/read_quakes_from_db", function(error, points) {
    if (error) return console.error(error);
    console.log(points);

    // make pins for historical data
    svg.selectAll(".pin")
        .data(points)
        .enter().append("circle", ".pin")
        // radius proportional to magnitude of quake
        .attr("r", function(d) {
            return d.magnitude/2;
        })
        // lat and lon
        .attr("transform", function(d) {
            return "translate(" + projection ([d.longitude, d.latitude]) + ")";
        })
        .style("fill", function(d) {
            return (pathRamp(d.magnitude));
        });
        // .on("click", function(d) {siteLabel.text(d.magnitude, d.month, d.day, d.year, d.hour, d.minute)});

    // append to svg
    });

    // });

}

function displayRealtimeQuakes() {

}

// $.ajax({
//     url: "/read_quakes_from_db",
//     type : "GET",
//     dataType: "json"
// }).done(function(response) {
//     console.log(response);
