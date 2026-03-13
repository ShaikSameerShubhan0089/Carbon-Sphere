// Initialize Map
// Default: Tirupati (13.6355, 79.4236)
const defaultLat = 13.6355;
const defaultLon = 79.4236;

const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
});

const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

const map = L.map('map', {
    center: [defaultLat, defaultLon],
    zoom: 13,
    layers: [darkLayer] // Default layer
});

let marker = L.marker([defaultLat, defaultLon], { draggable: true }).addTo(map);
let circle = L.circle([defaultLat, defaultLon], {
    color: '#10b981',
    fillColor: '#10b981',
    fillOpacity: 0.2,
    radius: 1000 // 1km
}).addTo(map);

// Update input fields when dragging marker
marker.on('dragend', function (event) {
    var position = marker.getLatLng();
    marker.setLatLng(position, { draggable: 'true' }).bindPopup(position).update();
    circle.setLatLng(position);
    document.getElementById('lat').value = position.lat.toFixed(5);
    document.getElementById('lon').value = position.lng.toFixed(5);
});

// Update map when inputs change
function updateMapFromInput() {
    const lat = parseFloat(document.getElementById('lat').value);
    const lon = parseFloat(document.getElementById('lon').value);
    if (!isNaN(lat) && !isNaN(lon)) {
        const newLatLng = new L.LatLng(lat, lon);
        marker.setLatLng(newLatLng);
        circle.setLatLng(newLatLng);
        map.panTo(newLatLng);
    }
}

document.getElementById('lat').addEventListener('change', updateMapFromInput);
document.getElementById('lon').addEventListener('change', updateMapFromInput);

// Handle File Select visual
document.getElementById('forestImage').addEventListener('change', function () {
    const fileName = this.files[0].name;
    document.querySelector('.fake-btn').innerText = fileName;
});

// Analyze Form Submission
// Update slider value
const sensSlider = document.getElementById('sensitivity');
const sensVal = document.getElementById('sens-val');

if (sensSlider) {
    sensSlider.addEventListener('input', (e) => {
        sensVal.textContent = e.target.value + '%';
    });
}

// Helper function for loading state
function setLoading(isLoading) {
    const btnText = document.querySelector('.btn-text');
    const loader = document.getElementById('loader');
    if (isLoading) {
        btnText.style.display = 'none';
        loader.style.display = 'block';
    } else {
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}

// Analysis Function
async function analyzeForest(e) {
    e.preventDefault();

    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    const imageInput = document.getElementById('forestImage');
    const sensitivity = document.getElementById('sensitivity').value;
    const model = document.getElementById('model-select').value;

    if (!imageInput.files[0]) {
        alert("Please upload a forest image.");
        return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('latitude', lat);
    formData.append('longitude', lon);
    formData.append('image', imageInput.files[0]);
    formData.append('sensitivity', sensitivity);
    formData.append('model', model);

    try {
        const response = await fetch('http://127.0.0.1:2020/api/v1/forest/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server Error (${response.status}): ${errorText}`);
        }

        const result = await response.json();
        displayResults(result);

    } catch (error) {
        console.error("Error:", error);
        alert(`Analysis failed: ${error.message}`);
    } finally {
        resetBtn();
    }
}

// Attach Event Listener
document.getElementById('analysisForm').addEventListener('submit', analyzeForest);

function resetBtn() {
    document.querySelector('.btn-text').style.display = 'block';
    document.getElementById('loader').style.display = 'none';
}

function displayResults(data) {
    document.getElementById('placeholder-text').style.display = 'none';
    document.getElementById('resultsGrid').style.display = 'grid';

    // Animate numbers
    document.getElementById('res-ndvi').textContent = data.satellite_metrics.ndvi_mean.toFixed(3);

    const coverPct = (data.ai_metrics.tree_cover_ratio * 100).toFixed(1) + '%';
    document.getElementById('res-cover').textContent = coverPct;

    document.getElementById('res-credits').textContent = data.carbon_analysis.carbon_credits;

    const conf = (data.carbon_analysis.confidence_score * 100).toFixed(0) + '%';
    document.getElementById('res-conf').textContent = conf;

    // Update Chart with new data point
    addToChart(new Date().toLocaleTimeString(), data.carbon_analysis.carbon_credits, data.ai_metrics.tree_cover_ratio);
}

// --- CHARTS CONFIGURATION ---

Chart.defaults.color = '#71717a';
Chart.defaults.scale.grid.color = '#27272a';

// 1. Trend Chart (Line) - Bottom
const ctxTrend = document.getElementById('historyChart').getContext('2d');
const gradientTrend = ctxTrend.createLinearGradient(0, 0, 0, 400);
gradientTrend.addColorStop(0, 'rgba(16, 185, 129, 0.5)');
gradientTrend.addColorStop(1, 'rgba(16, 185, 129, 0)');

const historyChart = new Chart(ctxTrend, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Carbon Credits (Tons)',
            data: [],
            borderColor: '#10b981',
            backgroundColor: gradientTrend,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#10b981',
            pointRadius: 4,
            pointHoverRadius: 6
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: {
                bottom: 10  // Extra space for x-axis labels
            }
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(24, 24, 27, 0.9)',
                titleColor: '#fff',
                bodyColor: '#a1a1aa',
                borderColor: '#27272a',
                borderWidth: 1
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: '#27272a' },
                ticks: { padding: 5 }
            },
            x: {
                grid: { display: false },
                ticks: {
                    padding: 5,
                    maxRotation: 45,
                    minRotation: 0
                }
            }
        }
    }
});

// 2. Performance Bar Chart (Bar) - Top Right
const ctxBar = document.getElementById('barChart').getContext('2d');
const performanceChart = new Chart(ctxBar, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        datasets: [{
            label: 'Tree Cover %',
            data: [65, 70, 75, 72, 80], // Mock start
            backgroundColor: '#3b82f6',
            borderRadius: 6,
            barThickness: 30
        }, {
            label: 'Benchmark',
            data: [60, 60, 60, 60, 60],
            type: 'line',
            borderColor: '#a1a1aa',
            borderDash: [5, 5],
            tension: 0,
            pointRadius: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { font: { size: 10 }, color: '#a1a1aa' }
            }
        },
        scales: {
            y: { beginAtZero: true, max: 100, grid: { color: '#27272a' } },
            x: { grid: { display: false } }
        }
    }
});

// 3. Distribution Donut Chart (Donut) - Top Left
const ctxDist = document.getElementById('distributionChart').getContext('2d');
const distributionChart = new Chart(ctxDist, {
    type: 'doughnut',
    data: {
        labels: ['Tree Cover', 'Non-Forest'],
        datasets: [{
            data: [0, 100], // Initial
            backgroundColor: ['#10b981', '#27272a'],
            borderWidth: 0,
            hoverOffset: 4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
            legend: {
                position: 'bottom',
                labels: { usePointStyle: true, font: { size: 10 } }
            }
        }
    }
});

function updateCharts(label, credits, coverRatio) {
    // 1. Update Trend
    historyChart.data.labels.push(label);
    historyChart.data.datasets[0].data.push(credits);

    if (historyChart.data.labels.length > 10) {
        historyChart.data.labels.shift();
        historyChart.data.datasets[0].data.shift();
    }
    historyChart.update();

    const coverPct = (coverRatio * 100);

    // 2. Update Bar Chart
    performanceChart.data.labels.push(label);
    performanceChart.data.datasets[0].data.push(coverPct);
    performanceChart.data.datasets[1].data.push(65); // Benchmark

    if (performanceChart.data.labels.length > 5) {
        performanceChart.data.labels.shift();
        performanceChart.data.datasets[0].data.shift();
        performanceChart.data.datasets[1].data.shift();
    }
    performanceChart.update();

    // 3. Update Donut Chart (LATEST Snapshot)
    distributionChart.data.datasets[0].data = [coverPct, 100 - coverPct];
    distributionChart.update();
}

function addToChart(label, value, coverRatio = 0.5) {
    // Legacy support wrapper - now accepts actual cover ratio
    updateCharts(label, value, coverRatio);
}

// Fetch History from MongoDB
async function loadHistory() {
    try {
        const response = await fetch('http://127.0.0.1:2020/api/v1/history');
        if (!response.ok) return;

        const data = await response.json();
        const tableBody = document.getElementById('historyTableBody');
        tableBody.innerHTML = ''; // Clear

        // Sort by timestamp desc (newest first)
        data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        data.forEach(item => {
            // Populate Table
            // Helper: Determine Model Name (Default to ResNet/HSV if not saved)
            let modelName = "ResNet50";
            if (item.ai_metrics && item.ai_metrics.segmentation_method) {
                // Heuristic to match model name
                const method = item.ai_metrics.segmentation_method.toLowerCase();
                if (method.includes('unet') || method.includes('deeplab')) modelName = "U-Net";
                else if (method.includes('hsv')) modelName = "HSV";
            }

            const coverVal = (item.ai_metrics.tree_cover_ratio * 100).toFixed(1);

            const row = document.createElement('tr');
            row.className = "history-row";
            row.innerHTML = `
                <td>
                    <div class="date-cell">
                        <span class="date-main">${date}</span>
                        <span class="date-sub">${time}</span>
                    </div>
                </td>
                <td>
                    <div class="progress-wrapper">
                        <div class="progress-bg">
                            <div class="progress-fill" style="width: ${coverVal}%"></div>
                        </div>
                        <span class="progress-text">${coverVal}%</span>
                    </div>
                </td>
                <td>
                    <div class="credits-val">
                        <span>${credits}</span>
                        <span style="font-size:0.7em; opacity:0.7">t</span>
                    </div>
                </td>
                <td>
                    <span class="badge badge-model">${modelName}</span>
                </td>
            `;
            tableBody.appendChild(row);

            // Populate Chart (Oldest to Newest for Line Chart)
            // Note: In real app, we'd process this better. For now, just adding recent ones.
        });

        // Populate Chart with last 5 items reversed (so oldest is left)
        const recentItems = data.slice(0, 10).reverse();
        historyChart.data.labels = [];
        historyChart.data.datasets[0].data = [];

        recentItems.forEach(item => {
            addToChart(
                new Date(item.timestamp).toLocaleTimeString(),
                item.carbon_analysis.carbon_credits,
                item.ai_metrics.tree_cover_ratio
            );
        });

    } catch (e) {
        console.error("Failed to load history:", e);
    }
}

// Load on startup
loadHistory();

// Simulation: Load 2-Year History from "GEE"
async function loadSatelliteHistory() {
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;

    // Show loading state
    const btn = document.querySelector('button[onclick="loadSatelliteHistory()"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = "⏳ Loading...";
    btn.disabled = true;

    try {
        const response = await fetch(`http://127.0.0.1:2020/api/v1/forest/history-simulation?lat=${lat}&lon=${lon}`);
        const data = await response.json();

        // Update Chart with specific simulated data
        historyChart.data.labels = data.map(d => d.date); // Dates
        historyChart.data.datasets[0].data = data.map(d => d.carbon_credits);
        historyChart.data.datasets[0].label = "Simulated 2-Year Trend (Carbon Tons)";
        historyChart.update();

        alert("✅ Retrieved 2-Year Historical Data from Satellite Archive (Simulated).");

    } catch (e) {
        alert("Failed to load history.");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

/* ===========================
   NAVIGATION & UI LOGIC
   =========================== */

const navLinks = {
    dashboard: document.getElementById('nav-dashboard'),
    satellite: document.getElementById('nav-satellite'),
    settings: document.getElementById('nav-settings'),
    developer: document.getElementById('nav-developer')
};

const views = {
    dashboard: document.getElementById('view-dashboard'),
    settings: document.getElementById('view-settings'),
    developer: document.getElementById('view-developer')
};

// State to track if we are in satellite mode (which is just dashboard with map maximized)
let isSatelliteMode = false;

function switchView(viewName) {
    // 1. Update Nav Active State
    Object.values(navLinks).forEach(link => link.classList.remove('active'));
    if (navLinks[viewName]) navLinks[viewName].classList.add('active');

    // 2. Handle Views
    if (viewName === 'settings') {
        views.dashboard.style.display = 'none';
        views.settings.style.display = 'block';
        views.developer.style.display = 'none';
        isSatelliteMode = false;
        disableSatelliteMode();
    } else if (viewName === 'developer') {
        views.dashboard.style.display = 'none';
        views.settings.style.display = 'none';
        views.developer.style.display = 'block';
        isSatelliteMode = false;
        disableSatelliteMode();
    } else if (viewName === 'satellite') {
        // Just toggle satellite layer, keep dashboard visible
        views.dashboard.style.display = 'grid';
        views.settings.style.display = 'none';
        views.developer.style.display = 'none';
        enableSatelliteMode();
    } else {
        // Dashboard - normal dark map
        views.dashboard.style.display = 'grid';
        views.settings.style.display = 'none';
        views.developer.style.display = 'none';
        disableSatelliteMode();
    }

    // Force map resize calc after visibility change
    setTimeout(() => map.invalidateSize(), 100);
}

function enableSatelliteMode() {
    if (isSatelliteMode) return;
    isSatelliteMode = true;

    // ONLY switch map layer - no layout changes
    map.removeLayer(darkLayer);
    map.addLayer(satelliteLayer);
    map.invalidateSize();
}

function disableSatelliteMode() {
    if (!isSatelliteMode) return;
    isSatelliteMode = false;

    // Switch map layer back to Dark
    map.removeLayer(satelliteLayer);
    map.addLayer(darkLayer);
    map.invalidateSize();
}

function resetMapLayout() {
    disableSatelliteMode();
}

// Settings Logic
let currentUnit = 'Metric'; // Default

function saveSettings() {
    const unitSelect = document.getElementById('unit-select');
    if (unitSelect) {
        currentUnit = unitSelect.value.split(' ')[0]; // "Metric" or "Imperial"
    }
    alert(`Settings Saved!\n- Unit: ${currentUnit}\n- AI Model: ResNet50 (Active)`);

    // Switch view back to dashboard
    switchView('dashboard');
}

// Add Event Listeners
if (navLinks.dashboard) navLinks.dashboard.addEventListener('click', () => switchView('dashboard'));
if (navLinks.satellite) navLinks.satellite.addEventListener('click', () => switchView('satellite'));
if (navLinks.settings) navLinks.settings.addEventListener('click', () => switchView('settings'));
if (navLinks.developer) navLinks.developer.addEventListener('click', () => switchView('developer'));
