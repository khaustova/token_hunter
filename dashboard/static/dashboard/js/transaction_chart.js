let url = "http://127.0.0.1:8000/api/pnlcounts";

async function getJSONData() {
  const response = await fetch(url)
  const json = await response.json();
  return json
}

getJSONData().then(data => {
  createBarChart(data['data_collection'], 'dataCollectionPNL');
  createBarChart(data['simulation'], 'simulationPNL');
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
          label: 'Profit (PNL ≥ 0)',
          data: data.profit,
          backgroundColor: '#00a732',
          borderColor: '#00a732',
          borderWidth: 1
        },
        {
          label: 'Loss (PNL < 0)',
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
          // Убрали stacked для оси X
          grid: {
            display: false
          },
          // Эти настройки помогут расположить столбцы рядом
          stacked: false
        },
        y: {
          stacked: false, // Или true, если хотите stacked по вертикали
          beginAtZero: true,
          ticks: {
            precision: 0,
            stepSize: 1, 
          }
        }
      },
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 12,
            padding: 20,
            font: {
              size: 14
            }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      // Добавляем настройки для группировки столбцов
      datasets: {
        bar: {
          categoryPercentage: 0.8,
          barPercentage: 0.9
        }
      }
    }
  });
}