var map = L.map('map').setView([40.9701, -5.6635], 15);  // Salamanca
//var map = L.map('map').setView([28.586905, -17.911115], 15);  // Canary Islands

//$("#map").css("min-height", 200);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


L.marker([40.96611815700082, -5.665447711944581], {
                    icon: new L.AwesomeNumberMarkers({
                      number: 1,
                      markerColor: "blue"
                  })}).addTo(map);
L.marker([40.9654103006922, -5.650899410247804], {
                    icon: new L.AwesomeNumberMarkers({
                      number: 2,
                      markerColor: "blue"
                  })}).addTo(map);
L.marker([40.97473829860183, -5.65047408856507], {
                    icon: new L.AwesomeNumberMarkers({
                      number: 4,
                      markerColor: "blue"
                  })}).addTo(map);
L.marker([40.97077831099318, -5.670963866405486], {
                    icon: new L.AwesomeNumberMarkers({
                      number: 3,
                      markerColor: "blue"
                  })}).addTo(map);
L.marker([40.97474813472539, -5.650411248295003], {
                    icon: new L.AwesomeNumberMarkers({
                      number: 4,
                      markerColor: "blue"
                  })}).addTo(map);


// get JSON data
$.getJSON("/data.json", function (data) {
    //console.log(data);
    var idw = L.idwLayer( // lat, lng, intensity
        data,
        {
            opacity: 0.4,
            cellSize: 10,
            exp: 2,
            max: 1,
            gradient: {0: 'blue', 0.3: 'lime', 0.4: 'yellow', 0.7: 'red', 0.9: 'black'}
        }).addTo(map);
});

ChartHelper.createEmptyChart("ts-chart", "line", true, 0, 2000);

$.getJSON("/ts.json", function (data) {

    datasets = [{
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgb(255, 99, 132)',
            data: data["means"],
            label: "Total",
            pointStyle: 'circle',
            pointRadius: 3,
            pointHoverRadius: 5
        },
        {
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgb(255, 99, 132)',
            data: data["fut_means"],
            label: "Total Predictions",
            //pointStyle: 'circle',
            //pointRadius: 3,
            //pointHoverRadius: 5,
            borderDash: [5, 5]
        }]
    for(let i in data["zones"]) {
        var color = ChartHelper.colors[i];
        let zonedata = {
            data: data["zones"][i],
            label: "Zone " + i,
            pointStyle: 'circle',
            pointRadius: 1,
            pointHoverRadius: 3,
            //borderDash: [5, 5],
            borderColor: color
        }
        datasets.push(zonedata);
        let zonepred = {
            data: data["zones_pred"][i],
            label: "Zone " + i + " Prediction",
            //pointStyle: 'circle',
            //pointRadius: 1,
            //pointHoverRadius: 3,
            borderDash: [5, 5],
            borderColor: color
        }
        datasets.push(zonepred);
    }

    ChartHelper.updateChart("ts-chart", {
        datasets: datasets,
        labels: [...data["labels"], ...data["fut_dates"]]
    });
});
