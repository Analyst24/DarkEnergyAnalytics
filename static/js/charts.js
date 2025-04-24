/**
 * Energy Anomaly Detection Visualization Scripts
 * This file contains functions for creating charts and visualizations
 * for energy consumption data and anomaly detection results.
 */

// Configure global Chart.js settings for dark theme
Chart.defaults.color = '#b3b3b3';
Chart.defaults.scale.grid.color = '#333333';
Chart.defaults.scale.grid.borderColor = '#444444';
Chart.defaults.scale.ticks.color = '#b3b3b3';

/**
 * Creates an energy consumption time series chart with anomaly highlights
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - Data object containing timestamps and values
 */
function createEnergyConsumptionChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Extract data points and anomalies
    const timestamps = data.timestamps;
    const energyValues = data.energy_consumption;
    const isAnomaly = data.is_anomaly;
    
    // Create datasets for normal and anomaly points
    const normalPoints = [];
    const anomalyPoints = [];
    
    for (let i = 0; i < timestamps.length; i++) {
        if (isAnomaly[i] === 1) {
            anomalyPoints.push({x: timestamps[i], y: energyValues[i]});
            normalPoints.push(null);
        } else {
            normalPoints.push({x: timestamps[i], y: energyValues[i]});
            anomalyPoints.push(null);
        }
    }
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [
                {
                    label: 'Energy Consumption',
                    data: normalPoints,
                    borderColor: '#4da6ff',
                    backgroundColor: 'rgba(77, 166, 255, 0.1)',
                    pointBackgroundColor: '#4da6ff',
                    borderWidth: 2,
                    tension: 0.2,
                    fill: true
                },
                {
                    label: 'Anomalies',
                    data: anomalyPoints,
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.8)',
                    pointBackgroundColor: '#ff6b6b',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    borderWidth: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        font: {
                            family: 'Roboto, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e1e1e',
                    titleColor: '#ffffff',
                    bodyColor: '#b3b3b3',
                    borderColor: '#333333',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const datasetLabel = context.dataset.label;
                            const value = context.parsed.y;
                            return `${datasetLabel}: ${value.toFixed(2)} kWh`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: determineTimeUnit(timestamps),
                        displayFormats: {
                            hour: 'HH:mm',
                            day: 'MMM D',
                            week: 'MMM D',
                            month: 'MMM YYYY'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time',
                        color: '#ffffff'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Energy Consumption (kWh)',
                        color: '#ffffff'
                    },
                    beginAtZero: true
                }
            }
        }
    });
    
    return chart;
}

/**
 * Creates a correlation chart between energy consumption and temperature
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - Data object containing energy and temperature values
 */
function createCorrelationChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Extract energy and temperature data
    const energyValues = data.energy_consumption;
    const temperatureValues = data.temperature || [];
    const isAnomaly = data.is_anomaly;
    
    // Create datasets
    const scatterData = [];
    const anomalyData = [];
    
    // Only create points where both energy and temperature values exist
    for (let i = 0; i < energyValues.length; i++) {
        if (i < temperatureValues.length) {
            const point = {
                x: temperatureValues[i],
                y: energyValues[i]
            };
            
            if (isAnomaly[i] === 1) {
                anomalyData.push(point);
            } else {
                scatterData.push(point);
            }
        }
    }
    
    const chart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Normal Data Points',
                    data: scatterData,
                    backgroundColor: 'rgba(77, 166, 255, 0.7)',
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'Anomalies',
                    data: anomalyData,
                    backgroundColor: 'rgba(255, 107, 107, 0.8)',
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        font: {
                            family: 'Roboto, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e1e1e',
                    titleColor: '#ffffff',
                    bodyColor: '#b3b3b3',
                    borderColor: '#333333',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return `Temperature: ${context.parsed.x.toFixed(1)}°C, Energy: ${context.parsed.y.toFixed(2)} kWh`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                        color: '#ffffff'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Energy Consumption (kWh)',
                        color: '#ffffff'
                    },
                    beginAtZero: true
                }
            }
        }
    });
    
    return chart;
}

/**
 * Creates a model evaluation radar chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} evaluationData - Model evaluation metrics
 */
function createModelEvaluationChart(canvasId, evaluationData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score'];
    const values = [
        evaluationData.accuracy || 0,
        evaluationData.precision || 0,
        evaluationData.recall || 0,
        evaluationData.f1_score || 0
    ];
    
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: metrics,
            datasets: [{
                label: 'Model Performance',
                data: values,
                backgroundColor: 'rgba(77, 166, 255, 0.2)',
                borderColor: '#4da6ff',
                borderWidth: 2,
                pointBackgroundColor: '#4da6ff',
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.2,
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: '#333333'
                    },
                    angleLines: {
                        color: '#444444'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        font: {
                            family: 'Roboto, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e1e1e',
                    titleColor: '#ffffff',
                    bodyColor: '#b3b3b3',
                    borderColor: '#333333',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw.toFixed(3)}`;
                        }
                    }
                }
            }
        }
    });
    
    return chart;
}

/**
 * Creates a bar chart comparing multiple model evaluations
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} evaluations - Array of evaluation objects
 */
function createModelComparisonChart(canvasId, evaluations) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Extract model names and metrics
    const modelNames = evaluations.map(eval => eval.algorithm);
    const accuracyValues = evaluations.map(eval => eval.accuracy || 0);
    const precisionValues = evaluations.map(eval => eval.precision || 0);
    const recallValues = evaluations.map(eval => eval.recall || 0);
    const f1Values = evaluations.map(eval => eval.f1_score || 0);
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: modelNames,
            datasets: [
                {
                    label: 'Accuracy',
                    data: accuracyValues,
                    backgroundColor: 'rgba(77, 166, 255, 0.7)'
                },
                {
                    label: 'Precision',
                    data: precisionValues,
                    backgroundColor: 'rgba(0, 204, 153, 0.7)'
                },
                {
                    label: 'Recall',
                    data: recallValues,
                    backgroundColor: 'rgba(255, 209, 102, 0.7)'
                },
                {
                    label: 'F1 Score',
                    data: f1Values,
                    backgroundColor: 'rgba(255, 107, 107, 0.7)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#ffffff',
                        font: {
                            family: 'Roboto, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e1e1e',
                    titleColor: '#ffffff',
                    bodyColor: '#b3b3b3',
                    borderColor: '#333333',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Algorithm',
                        color: '#ffffff'
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 1,
                    title: {
                        display: true,
                        text: 'Score',
                        color: '#ffffff'
                    }
                }
            }
        }
    });
    
    return chart;
}

/**
 * Creates a donut chart showing the proportion of anomalies in a dataset
 * @param {string} canvasId - The ID of the canvas element
 * @param {number} normalCount - Count of normal data points
 * @param {number} anomalyCount - Count of anomaly data points
 */
function createAnomalyProportionChart(canvasId, normalCount, anomalyCount) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Normal Data', 'Anomalies'],
            datasets: [{
                data: [normalCount, anomalyCount],
                backgroundColor: ['rgba(0, 204, 153, 0.7)', 'rgba(255, 107, 107, 0.7)'],
                borderColor: ['#00cc99', '#ff6b6b'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        color: '#ffffff',
                        font: {
                            family: 'Roboto, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e1e1e',
                    titleColor: '#ffffff',
                    bodyColor: '#b3b3b3',
                    borderColor: '#333333',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label;
                            const value = context.raw;
                            const total = normalCount + anomalyCount;
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
    
    return chart;
}

/**
 * Creates a heatmap visualization for anomalies by time of day and day of week
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} anomalies - Array of anomaly objects with timestamps
 */
function createAnomalyHeatmap(canvasId, anomalies) {
    // This function is more complex and requires additional libraries
    // For a simplified version, we can use a placeholder that would be replaced with proper implementation
    const container = document.getElementById(canvasId);
    
    if (!container) {
        console.error(`Canvas element with ID ${canvasId} not found`);
        return;
    }
    
    container.innerHTML = '<div class="text-center p-5">Heatmap visualization requires additional libraries. Please include D3.js for full functionality.</div>';
}

/**
 * Determine the appropriate time unit based on the timestamps range
 * @param {Array} timestamps - Array of timestamp strings
 * @returns {string} Appropriate time unit (hour, day, week, month)
 */
function determineTimeUnit(timestamps) {
    if (!timestamps || timestamps.length < 2) {
        return 'day';
    }
    
    const firstDate = new Date(timestamps[0]);
    const lastDate = new Date(timestamps[timestamps.length - 1]);
    const diffDays = Math.round((lastDate - firstDate) / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 1) {
        return 'hour';
    } else if (diffDays <= 14) {
        return 'day';
    } else if (diffDays <= 90) {
        return 'week';
    } else {
        return 'month';
    }
}

/**
 * Fetches dataset data and creates charts
 * @param {number} datasetId - The ID of the dataset to fetch
 * @param {string} containerSelector - The selector for the container to render charts in
 */
function loadDatasetVisualizations(datasetId, containerSelector) {
    const container = document.querySelector(containerSelector);
    
    if (!container) {
        console.error(`Container element with selector ${containerSelector} not found`);
        return;
    }
    
    // Show loading state
    container.innerHTML = `
        <div class="loader-container">
            <div class="loader"></div>
            <p class="mt-3">Loading dataset visualizations...</p>
        </div>
    `;
    
    // Fetch dataset data
    fetch(`/api/dataset/${datasetId}/data`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Clear loading state
            container.innerHTML = '';
            
            // Create energy consumption chart
            const timeSeriesContainer = document.createElement('div');
            timeSeriesContainer.className = 'card mb-4';
            timeSeriesContainer.innerHTML = `
                <div class="card-header">
                    <h3>Energy Consumption Over Time</h3>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="energy-time-chart"></canvas>
                    </div>
                </div>
            `;
            container.appendChild(timeSeriesContainer);
            
            createEnergyConsumptionChart('energy-time-chart', data);
            
            // Create correlation chart if temperature data exists
            if (data.temperature && data.temperature.length > 0) {
                const correlationContainer = document.createElement('div');
                correlationContainer.className = 'card mb-4';
                correlationContainer.innerHTML = `
                    <div class="card-header">
                        <h3>Energy vs. Temperature Correlation</h3>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="correlation-chart"></canvas>
                        </div>
                    </div>
                `;
                container.appendChild(correlationContainer);
                
                createCorrelationChart('correlation-chart', data);
            }
            
            // Create anomaly proportion chart
            const anomalyCount = data.is_anomaly.filter(val => val === 1).length;
            const normalCount = data.is_anomaly.length - anomalyCount;
            
            if (anomalyCount > 0) {
                const proportionContainer = document.createElement('div');
                proportionContainer.className = 'card mb-4';
                proportionContainer.innerHTML = `
                    <div class="card-header">
                        <h3>Anomaly Distribution</h3>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="chart-container" style="height: 300px;">
                                    <canvas id="anomaly-proportion-chart"></canvas>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="anomaly-stats p-3">
                                    <h4>Anomaly Statistics</h4>
                                    <ul class="list-unstyled">
                                        <li><strong>Total Data Points:</strong> ${data.timestamps.length}</li>
                                        <li><strong>Normal Data Points:</strong> ${normalCount} (${((normalCount / data.timestamps.length) * 100).toFixed(1)}%)</li>
                                        <li><strong>Anomalies Detected:</strong> ${anomalyCount} (${((anomalyCount / data.timestamps.length) * 100).toFixed(1)}%)</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(proportionContainer);
                
                createAnomalyProportionChart('anomaly-proportion-chart', normalCount, anomalyCount);
                
                // Fetch anomaly details for additional visualizations
                fetch(`/api/dataset/${datasetId}/anomalies`)
                    .then(response => response.json())
                    .then(anomalies => {
                        if (anomalies && anomalies.length > 0) {
                            // Add anomaly details table
                            const anomalyTable = document.createElement('div');
                            anomalyTable.className = 'card mb-4';
                            anomalyTable.innerHTML = `
                                <div class="card-header">
                                    <h3>Anomaly Details</h3>
                                </div>
                                <div class="card-body">
                                    <div class="table-container">
                                        <table class="table">
                                            <thead>
                                                <tr>
                                                    <th>Timestamp</th>
                                                    <th>Energy Consumption</th>
                                                    <th>Temperature</th>
                                                    <th>Anomaly Score</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${anomalies.map(a => `
                                                    <tr>
                                                        <td>${a.timestamp}</td>
                                                        <td>${a.energy_consumption.toFixed(2)} kWh</td>
                                                        <td>${a.temperature ? a.temperature.toFixed(1) + '°C' : 'N/A'}</td>
                                                        <td>${a.score.toFixed(3)}</td>
                                                    </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            `;
                            container.appendChild(anomalyTable);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching anomaly details:', error);
                    });
            }
        })
        .catch(error => {
            console.error('Error fetching dataset data:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    Error loading dataset visualizations: ${error.message}
                </div>
            `;
        });
}
