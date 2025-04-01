/**
 * Charts module for the AI Call Secretary web interface.
 * Handles data visualization for dashboard statistics.
 */

// Initialize charts on dashboard
function initDashboardCharts() {
  createCallVolumeChart();
  createCallDurationChart();
  createMessageDistributionChart();
  createAppointmentScheduleChart();
}

// Create call volume chart (calls per day for last 7 days)
function createCallVolumeChart() {
  // Get the canvas element
  const canvas = document.getElementById('call-volume-chart');
  if (!canvas) return;
  
  // Request data from API
  fetchCallVolumeData()
    .then(data => {
      // Create chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Call Volume',
            data: data.values,
            backgroundColor: 'rgba(79, 70, 229, 0.7)',
            borderColor: 'rgba(79, 70, 229, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `Calls: ${context.parsed.y}`;
                }
              }
            }
          }
        }
      });
    })
    .catch(error => {
      console.error('Error creating call volume chart:', error);
      showChartError(canvas);
    });
}

// Create call duration chart (average duration by hour of day)
function createCallDurationChart() {
  // Get the canvas element
  const canvas = document.getElementById('call-duration-chart');
  if (!canvas) return;
  
  // Request data from API
  fetchCallDurationData()
    .then(data => {
      // Create chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Average Call Duration (seconds)',
            data: data.values,
            backgroundColor: 'rgba(6, 182, 212, 0.2)',
            borderColor: 'rgba(6, 182, 212, 1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    })
    .catch(error => {
      console.error('Error creating call duration chart:', error);
      showChartError(canvas);
    });
}

// Create message distribution chart (by urgency)
function createMessageDistributionChart() {
  // Get the canvas element
  const canvas = document.getElementById('message-distribution-chart');
  if (!canvas) return;
  
  // Request data from API
  fetchMessageDistributionData()
    .then(data => {
      // Create chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: data.labels,
          datasets: [{
            data: data.values,
            backgroundColor: [
              'rgba(16, 185, 129, 0.7)', // Success/low
              'rgba(59, 130, 246, 0.7)',  // Info/normal
              'rgba(245, 158, 11, 0.7)',  // Warning/high
              'rgba(239, 68, 68, 0.7)'    // Danger/critical
            ],
            borderColor: [
              'rgba(16, 185, 129, 1)',
              'rgba(59, 130, 246, 1)',
              'rgba(245, 158, 11, 1)',
              'rgba(239, 68, 68, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right'
            }
          },
          cutout: '65%'
        }
      });
    })
    .catch(error => {
      console.error('Error creating message distribution chart:', error);
      showChartError(canvas);
    });
}

// Create appointment schedule chart (by day of week)
function createAppointmentScheduleChart() {
  // Get the canvas element
  const canvas = document.getElementById('appointment-schedule-chart');
  if (!canvas) return;
  
  // Request data from API
  fetchAppointmentScheduleData()
    .then(data => {
      // Create chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Appointments',
            data: data.values,
            backgroundColor: 'rgba(16, 185, 129, 0.7)',
            borderColor: 'rgba(16, 185, 129, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0
              }
            }
          }
        }
      });
    })
    .catch(error => {
      console.error('Error creating appointment schedule chart:', error);
      showChartError(canvas);
    });
}

// Show error message when chart cannot be loaded
function showChartError(canvas) {
  if (!canvas) return;
  
  // Clear canvas
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Draw error message
  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  ctx.font = '14px sans-serif';
  ctx.fillStyle = '#ef4444';
  ctx.textAlign = 'center';
  ctx.fillText('Error loading chart data', canvas.width / 2, canvas.height / 2);
}

// Fetch call volume data (last 7 days)
function fetchCallVolumeData() {
  return api.get('/statistics/calls/volume')
    .catch(error => {
      console.error('Error fetching call volume data:', error);
      
      // Return mock data for development
      const labels = [];
      const values = [];
      
      // Generate last 7 days
      for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(formatDate(date));
        values.push(Math.floor(Math.random() * 10));
      }
      
      return { labels, values };
    });
}

// Fetch call duration data (by hour of day)
function fetchCallDurationData() {
  return api.get('/statistics/calls/duration')
    .catch(error => {
      console.error('Error fetching call duration data:', error);
      
      // Return mock data for development
      const labels = [];
      const values = [];
      
      // Generate hours 8AM to 8PM
      for (let i = 8; i <= 20; i++) {
        labels.push(`${i}:00`);
        // Random duration between 60 and 300 seconds
        values.push(60 + Math.floor(Math.random() * 240));
      }
      
      return { labels, values };
    });
}

// Fetch message distribution data (by urgency)
function fetchMessageDistributionData() {
  return api.get('/statistics/messages/distribution')
    .catch(error => {
      console.error('Error fetching message distribution data:', error);
      
      // Return mock data for development
      const labels = ['Low', 'Normal', 'High', 'Critical'];
      const values = [
        Math.floor(Math.random() * 10), // Low
        Math.floor(Math.random() * 20) + 10, // Normal
        Math.floor(Math.random() * 5) + 3, // High
        Math.floor(Math.random() * 3) // Critical
      ];
      
      return { labels, values };
    });
}

// Fetch appointment schedule data (by day of week)
function fetchAppointmentScheduleData() {
  return api.get('/statistics/appointments/schedule')
    .catch(error => {
      console.error('Error fetching appointment schedule data:', error);
      
      // Return mock data for development
      const labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      const values = [
        Math.floor(Math.random() * 5) + 2, // Monday
        Math.floor(Math.random() * 5) + 3, // Tuesday
        Math.floor(Math.random() * 5) + 5, // Wednesday
        Math.floor(Math.random() * 5) + 4, // Thursday
        Math.floor(Math.random() * 5) + 2, // Friday
        Math.floor(Math.random() * 3),     // Saturday
        Math.floor(Math.random() * 2)      // Sunday
      ];
      
      return { labels, values };
    });
}