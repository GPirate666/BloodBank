// Chart.js pentru grafic
const ctx = document.getElementById('chart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['10:00 AM', '12:00 PM', '2:00 PM', '4:00 PM', '6:00 PM', '8:00 PM'],
        datasets: [
            {
                label: 'Today',
                data: [10, 20, 15, 25, 30, 20],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
            },
            {
                label: 'Yesterday',
                data: [5, 15, 10, 20, 25, 15],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                fill: true,
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { beginAtZero: true },
            y: { beginAtZero: true }
        }
    }
});
