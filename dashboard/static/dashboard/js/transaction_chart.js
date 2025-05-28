let url = "http://127.0.0.1:8000/api/pnlcounts";

async function getJSONData() {
  const response = await fetch(url)
  const json = await response.json();
  return json
}

getJSONData().then(data => {
  createBarChart(data['data_collection'], 'dataCollectionPNL');
  createBarChart(data['emulation'], 'emulationPNL');
  createBarChart(data['real_buy'], 'realBuyPNL');
});

function createBarChart(data, chartId) {
  const ctx = document.getElementById(chartId).getContext('2d');
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.dates,
      datasets: [
        {
          label: 'Profit (PNL ≥ 60)',
          data: data.profit,
          backgroundColor: '#00a732',
          borderColor: '#00a732',
          borderWidth: 1
        },
        {
          label: 'Loss (PNL < 60)',
          data: data.loss,
          backgroundColor: '#b30000',
          borderColor: '#b30000',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          grid: {
            display: false
          }
        },
        y: {
          stacked: true,
          beginAtZero: true,
          ticks: {
            precision: 0, // Убираем десятичные дроби
            stepSize: 1,  // Шаг только целые числа
            callback: function(value) {
              if (value % 1 === 0) { // Показываем только целые числа
                return value;
              }
            }
          }
        }
      },

      legend: {
        position: 'right',
        labels: {
          boxWidth: 12,
          padding: 20,
          font: {
            size: 14
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      }
    }
  });
}