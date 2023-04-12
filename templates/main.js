var map = L.map('map').setView([40.9701, -5.6635], 15);  // Salamanca
//var map = L.map('map').setView([28.586905, -17.911115], 15);  // Canary Islands

//$("#map").css("min-height", 200);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


L.marker([40.96611815700082, -5.665447711944581]).addTo(map);
L.marker([40.9654103006922, -5.650899410247804]).addTo(map);
L.marker([40.97473829860183, -5.65047408856507]).addTo(map);
L.marker([40.97077831099318, -5.670963866405486]).addTo(map);
L.marker([40.97474813472539, -5.650411248295003]).addTo(map);

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
            gradient: {0: 'blue', 0.3: 'lime', 0.4: 'yellow', 0.5: 'red', 0.7: 'black'}
        }).addTo(map);
});

/*const ctx = document.getElementById('ts-chart');

new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [{
            data: [650, 590, 800, 810, 560, 550, 400],
            fill: false,
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'CO2'
                },
                suggestedMin: 0,
                suggestedMax: 2000
            }
        }
    }
});
*/
ChartHelper.createEmptyChart("ts-chart", "line", false, 0, 2000);

$.getJSON("/ts.json", function (data) {

    ChartHelper.updateChart("ts-chart", {
        datasets: [{
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgb(255, 99, 132)',
            data: data["means"],
            label: "CO2",
            pointStyle: 'circle',
            pointRadius: 3,
            pointHoverRadius: 5
        }],
        labels: data["labels"]
    });
});
