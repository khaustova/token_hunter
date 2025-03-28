let url = "http://127.0.0.1:8000/api/pnlcounts";

async function getJSONData() {
  const response = await fetch(url)
  const json = await response.json();
  return json
}

getJSONData().then(data => {
  data;
  chartPNL(data['data_collection'], 'dataCollectionPNL');
  chartPNL(data['emulation'], 'emulationPNL');
  chartPNL(data['real_buy'], 'realBuyPNL');
});


async function chartPNL(data, chartId) {
  new Chart(
    document.getElementById(chartId),
    {
      type: 'pie',
      options: {
        maintainAspectRatio: false,
        responsive: true,
      },
      data: {
        labels: ['Профит', 'Потеря'],
        datasets: [
          {
            data: data,
            backgroundColor: ['#00a732', '#b30000'],
          }
        ],
      }
    }
  );
};