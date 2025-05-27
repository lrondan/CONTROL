// Static sample data
const data = [
    { time: "08:00", temperature: 22, humidity: 60 },
    { time: "10:00", temperature: 24, humidity: 58 },
    { time: "12:00", temperature: 26, humidity: 55 },
    { time: "14:00", temperature: 28, humidity: 50 },
    { time: "16:00", temperature: 25, humidity: 53 },
];

// Extract values
const tempValues = data.map(d => d.temperature);
const humValues = data.map(d => d.humidity);

// Statistical calculations
const mean = arr => (arr.reduce((a, b) => a + b, 0) / arr.length);
const median = arr => {
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};

// Update stats
document.getElementById("temp-mean").textContent = `${mean(tempValues).toFixed(1)} °C`;
document.getElementById("temp-median").textContent = `${median(tempValues).toFixed(1)} °C`;
document.getElementById("temp-range").textContent = `${Math.max(...tempValues)}° / ${Math.min(...tempValues)}°`;

document.getElementById("hum-mean").textContent = `${mean(humValues).toFixed(1)} %`;
document.getElementById("hum-median").textContent = `${median(humValues).toFixed(1)} %`;
document.getElementById("hum-range").textContent = `${Math.max(...humValues)}% / ${Math.min(...humValues)}%`;

// Charts (no animations)
const tempCtx = document.getElementById('tempChart').getContext('2d');
const humCtx = document.getElementById('humChart').getContext('2d');

new Chart(tempCtx, {
    type: 'line',
    data: {
        labels: data.map(d => d.time),
        datasets: [{
            label: 'Temperature (°C)',
            data: tempValues,
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.05)',
            borderWidth: 2,
            tension: 0.1,
            fill: true
        }]
    },
    options: {
        responsive: true,
        animation: { duration: 0 }, // Disable animations
        plugins: {
            legend: { display: false },
            title: { 
                display: true, 
                text: `Temperature (Avg: ${mean(tempValues).toFixed(1)}°C)` 
            }
        },
        scales: { y: { beginAtZero: false } }
    }
});

new Chart(humCtx, {
    type: 'line',
    data: {
        labels: data.map(d => d.time),
        datasets: [{
            label: 'Humidity (%)',
            data: humValues,
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.05)',
            borderWidth: 2,
            tension: 0.1,
            fill: true
        }]
    },
    options: {
        responsive: true,
        animation: { duration: 0 }, // Disable animations
        plugins: {
            legend: { display: false },
            title: { 
                display: true, 
                text: `Humidity (Avg: ${mean(humValues).toFixed(1)}%)` 
            }
        },
        scales: { y: { beginAtZero: false } }
    }
});