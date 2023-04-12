const ChartHelper = {};

ChartHelper.colors = ["#084081", "#0868ac", "#2b8cbe", "#4eb3d3", "#3ec3c3", "#7bccc4", "#a8ddb5", "#ccebc5", "#e0f3db", "#f7fcf0", "#ffffff"]; // <= Charts defaults colors
ChartHelper.specialColor = "#FF4500"; // <= Special color for contrast
// Colores para las encuestas: Generado con https://coolors.co/
ChartHelper.surveyColors = ["#E76F51", "#EB7C55", "#EE8959", "#F1965D", "#F4A261", "#F2AB64", "#EFB366", "#ECBC68", "#E9C46A", "#BABB74", "#8AB17D", "#5AA786", "#2A9D8F", "#298880", "#287271", "#275C62", "#264653", "#3A5763", "#4C6671", "#5C747E"];
ChartHelper.charts = {}; // <= Created charts maps

Chart.defaults.font.size = 14; // Default font size
Chart.defaults.elements.line.tension = 0.3; // Beizer curves
Chart.defaults.layout.padding = 20; // Margin

// Crea un chart vacio
ChartHelper.createEmptyChart = function(elementId, chartType, showLegend, minScale, maxScale, labelCallback, legendPos = 'top', maintainAspectRatio=false) {
    var plugins = [];
    var opts = {
        maintainAspectRatio: maintainAspectRatio,
        plugins: {
            legend: {
                display: showLegend,
                position: legendPos
            },
            tooltip: {
                callbacks: {
                    label: labelCallback
                }
            },
        }
    };

    var typeStacked = false;
    if (chartType === "stacked") {
        typeStacked = true;
        chartType = "bar";
    }

    if ((chartType != "doughnut") &&  (chartType != "pie")) {
        opts.scales = {
            xAxes: [{
                stacked: typeStacked,
                ticks: {
                    maxRotation: 180
                }
            }],
            yAxes: [{
                stacked: typeStacked,
                ticks: {}
            }]
        };

        if (minScale != null) {
            opts.scales.yAxes[0].ticks.suggestedMin = minScale;
        }

        if (maxScale != null) {
            opts.scales.yAxes[0].ticks.max = maxScale;
        }
    } else {
        // Show data labels
        opts.plugins.datalabels = {
            anchor: 'end',
            align: 'end',
            offset: 5,
            color: 'black',
            formatter: function (value, context) {
                if (value > 0) {
                    var percentage = value / context.dataset.data.reduce(function(a, b) { return a + b; }, 0) * 100;
                    return ChartHelper.formatNumber(percentage) + "%";
                }
                return ''; // No mostrar etiquetas sin datos
            },
            display: function(context) {
                // Ocultamos cuando es menor al 3% porque no cabe
                var total = context.dataset.data.reduce(function(a, b) { return a + b; }, 0);
                var value = context.dataset.data[context.dataIndex];
                if ((value / total) < 0.03) {
                    return false;
                }
                return true;
            }
        }
        plugins.push(ChartDataLabels);
    }

    ChartHelper.charts[elementId] = new Chart(document.getElementById(elementId).getContext("2d"), {
        type: chartType,
        data: {},
        options: opts,
        plugins: plugins
    });
};

// Actualiza los datos de la grafica
ChartHelper.updateChart = function(elementId, new_data) {
    var chart = ChartHelper.charts[elementId];

    if (chart) {
        chart.data = new_data;
        chart.update();
    }
};

// Utils
ChartHelper.formatNumber = function(num) {
    if (isNaN(num)) {
        return 0;
    }

    return Number(num).toLocaleString("es-ES", {minimumFractionDigits: 0, maximumFractionDigits: 2});
};

// Labels basicas
ChartHelper.pieLabel = function(context) {
    var percentage = context.raw / context.dataset.data.reduce(function(a, b) { return a + b; }, 0) * 100;
    return context.label + ': ' + ChartHelper.formatNumber(context.raw) + ' ' + context.dataset.label +  ' (' + ChartHelper.formatNumber(percentage) + '%)';
};

ChartHelper.stackLabel = function(context) {
    var total = context.dataset.data.reduce(function(a, b) { return a + b; }, 0)
    return context.dataset.label + ': ' + ChartHelper.formatNumber(context.raw) +  ' / Total: ' + ChartHelper.formatNumber(total);
};

ChartHelper.lineLabel = function(context) {
    return context.dataset.label + ': ' + ChartHelper.formatNumber(context.raw);
};

//Fix chartjs printing:
window.onbeforeprint = (ev) => {
    for (var id in Chart.instances) {
        let instance = Chart.instances[id];
        let b64 = instance.toBase64Image();
        let i = new Image();
        //Instead of the below, you could save something on the
        //chart that decides what to change this to. This worked for me
        //however:
        i.style.maxWidth = "100vw";
        i.src = b64;
        let parent = instance.canvas.parentNode;
        instance.tempImage = i;
        instance.oldDisplay = instance.canvas.style.display;
        instance.canvas.style.display = "none";
        parent.appendChild(i);
    }
};

window.onafterprint = (ev) => {
    for (var id in Chart.instances) {
        let instance = Chart.instances[id];
        if (instance.tempImage) {
            let parent = instance.canvas.parentNode;
            parent.removeChild(instance.tempImage);
            instance.canvas.style.display = instance.oldDisplay;
            delete instance.oldDisplay;
            delete instance.tempImage;
        }
    }
};