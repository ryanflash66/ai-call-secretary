/**
 * Appointments module for the AI Call Secretary web interface.
 * Handles the appointments page functionality.
 */

// Global state for appointments page
const appointmentsState = {
  page: 1,
  pageSize: 10,
  total: 0,
  status: 'all',
  date: '',
  appointments: [],
  selectedDate: new Date(),
  calendarView: 'month'
};

// Initialize appointments page
function initAppointmentsPage() {
  // Create appointment modals
  createAppointmentModals();
  
  // Set up event listeners
  setupAppointmentsFilters();
  setupAppointmentsRefresh();
  setupNewAppointmentButton();
  
  // Initialize calendar
  initCalendar();
  
  // Load appointments
  loadAppointments();
}

// Create appointment modals
function createAppointmentModals() {
  // Create appointment detail modal if it doesn't exist
  if (!document.getElementById('appointment-detail-modal')) {
    const detailModal = document.createElement('div');
    detailModal.id = 'appointment-detail-modal';
    detailModal.className = 'modal';
    detailModal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>Appointment Details</h3>
          <button class="close-btn"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <!-- Appointment details will be loaded here -->
        </div>
        <div class="modal-footer">
          <button class="secondary-btn close-modal-btn">Close</button>
          <button class="primary-btn edit-btn"><i class="fas fa-edit"></i> Edit</button>
        </div>
      </div>
    `;
    document.body.appendChild(detailModal);
    
    // Add event listeners
    detailModal.querySelector('.close-btn').addEventListener('click', () => {
      closeModal('appointment-detail-modal');
    });
    
    detailModal.querySelector('.close-modal-btn').addEventListener('click', () => {
      closeModal('appointment-detail-modal');
    });
  }
  
  // Create appointment form modal if it doesn't exist
  if (!document.getElementById('appointment-form-modal')) {
    const formModal = document.createElement('div');
    formModal.id = 'appointment-form-modal';
    formModal.className = 'modal';
    formModal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>New Appointment</h3>
          <button class="close-btn"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <form id="appointment-form" class="appointment-form">
            <div class="form-group">
              <label for="appointment-title">Title</label>
              <input type="text" id="appointment-title" name="title" required>
            </div>
            <div class="form-group">
              <label for="appointment-contact">Contact</label>
              <input type="text" id="appointment-contact" name="contact" required>
            </div>
            <div class="form-group">
              <label for="appointment-date">Date</label>
              <input type="date" id="appointment-date" name="date" required>
            </div>
            <div class="form-group time-group">
              <div class="time-input">
                <label for="appointment-start-time">Start Time</label>
                <input type="time" id="appointment-start-time" name="start_time" required>
              </div>
              <div class="time-input">
                <label for="appointment-end-time">End Time</label>
                <input type="time" id="appointment-end-time" name="end_time" required>
              </div>
            </div>
            <div class="form-group">
              <label for="appointment-status">Status</label>
              <select id="appointment-status" name="status" required>
                <option value="scheduled">Scheduled</option>
                <option value="confirmed">Confirmed</option>
                <option value="cancelled">Cancelled</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div class="form-group">
              <label for="appointment-notes">Notes</label>
              <textarea id="appointment-notes" name="notes" rows="3"></textarea>
            </div>
            <div class="form-error" id="appointment-form-error"></div>
            <input type="hidden" id="appointment-id" name="appointment_id">
          </form>
        </div>
        <div class="modal-footer">
          <button class="secondary-btn close-modal-btn">Cancel</button>
          <button class="primary-btn" id="save-appointment-btn">Save Appointment</button>
        </div>
      </div>
    `;
    document.body.appendChild(formModal);
    
    // Add event listeners
    formModal.querySelector('.close-btn').addEventListener('click', () => {
      closeModal('appointment-form-modal');
    });
    
    formModal.querySelector('.close-modal-btn').addEventListener('click', () => {
      closeModal('appointment-form-modal');
    });
    
    // Add event listener for saving appointment
    formModal.querySelector('#save-appointment-btn').addEventListener('click', saveAppointment);
  }
}

// Set up appointments filters
function setupAppointmentsFilters() {
  // Status filter
  const statusFilter = document.getElementById('appointment-status-filter');
  statusFilter.addEventListener('change', () => {
    appointmentsState.status = statusFilter.value;
    appointmentsState.page = 1;
    loadAppointments();
  });
  
  // Date filter
  const dateFilter = document.getElementById('appointment-date-filter');
  dateFilter.addEventListener('change', () => {
    appointmentsState.date = dateFilter.value;
    appointmentsState.page = 1;
    
    // Update calendar if date is selected
    if (appointmentsState.date) {
      appointmentsState.selectedDate = new Date(appointmentsState.date);
      updateCalendar();
    }
    
    loadAppointments();
  });
  
  // Reset filters
  const resetBtn = document.querySelector('#appointments .filter-reset-btn');
  resetBtn.addEventListener('click', () => {
    statusFilter.value = 'all';
    dateFilter.value = '';
    appointmentsState.status = 'all';
    appointmentsState.date = '';
    appointmentsState.page = 1;
    
    // Reset calendar to current month
    appointmentsState.selectedDate = new Date();
    updateCalendar();
    
    loadAppointments();
  });
}

// Set up appointments refresh
function setupAppointmentsRefresh() {
  const refreshBtn = document.querySelector('#appointments .refresh-btn');
  refreshBtn.addEventListener('click', () => {
    loadAppointments();
    updateCalendar();
  });
}

// Setup new appointment button
function setupNewAppointmentButton() {
  const newAppointmentBtn = document.getElementById('new-appointment-btn');
  newAppointmentBtn.addEventListener('click', () => {
    showNewAppointmentModal();
  });
}

// Initialize calendar
function initCalendar() {
  const calendarContainer = document.getElementById('appointments-calendar');
  
  // Create calendar header
  const calendarHeader = document.createElement('div');
  calendarHeader.className = 'calendar-header';
  calendarHeader.innerHTML = `
    <div class="calendar-navigation">
      <button class="nav-btn prev-month-btn"><i class="fas fa-chevron-left"></i></button>
      <h4 class="current-month">Loading...</h4>
      <button class="nav-btn next-month-btn"><i class="fas fa-chevron-right"></i></button>
    </div>
    <div class="calendar-view-options">
      <button class="view-btn month-view-btn active">Month</button>
      <button class="view-btn week-view-btn">Week</button>
      <button class="view-btn day-view-btn">Day</button>
    </div>
  `;
  
  // Create calendar grid
  const calendarGrid = document.createElement('div');
  calendarGrid.className = 'calendar-grid';
  
  // Add to container
  calendarContainer.innerHTML = '';
  calendarContainer.appendChild(calendarHeader);
  calendarContainer.appendChild(calendarGrid);
  
  // Set up event listeners
  const prevMonthBtn = calendarHeader.querySelector('.prev-month-btn');
  const nextMonthBtn = calendarHeader.querySelector('.next-month-btn');
  const monthViewBtn = calendarHeader.querySelector('.month-view-btn');
  const weekViewBtn = calendarHeader.querySelector('.week-view-btn');
  const dayViewBtn = calendarHeader.querySelector('.day-view-btn');
  
  prevMonthBtn.addEventListener('click', () => {
    const date = appointmentsState.selectedDate;
    appointmentsState.selectedDate = new Date(date.getFullYear(), date.getMonth() - 1, 1);
    updateCalendar();
  });
  
  nextMonthBtn.addEventListener('click', () => {
    const date = appointmentsState.selectedDate;
    appointmentsState.selectedDate = new Date(date.getFullYear(), date.getMonth() + 1, 1);
    updateCalendar();
  });
  
  monthViewBtn.addEventListener('click', () => {
    appointmentsState.calendarView = 'month';
    monthViewBtn.classList.add('active');
    weekViewBtn.classList.remove('active');
    dayViewBtn.classList.remove('active');
    updateCalendar();
  });
  
  weekViewBtn.addEventListener('click', () => {
    appointmentsState.calendarView = 'week';
    monthViewBtn.classList.remove('active');
    weekViewBtn.classList.add('active');
    dayViewBtn.classList.remove('active');
    updateCalendar();
  });
  
  dayViewBtn.addEventListener('click', () => {
    appointmentsState.calendarView = 'day';
    monthViewBtn.classList.remove('active');
    weekViewBtn.classList.remove('active');
    dayViewBtn.classList.add('active');
    updateCalendar();
  });
  
  // Initial calendar render
  updateCalendar();
}

// Update calendar
function updateCalendar() {
  const calendarContainer = document.getElementById('appointments-calendar');
  const currentMonthTitle = calendarContainer.querySelector('.current-month');
  const calendarGrid = calendarContainer.querySelector('.calendar-grid');
  
  // Format month title
  const options = { year: 'numeric', month: 'long' };
  currentMonthTitle.textContent = appointmentsState.selectedDate.toLocaleDateString(undefined, options);
  
  // Clear previous calendar content
  calendarGrid.innerHTML = '';
  
  // Render calendar based on view
  switch (appointmentsState.calendarView) {
    case 'month':
      renderMonthView(calendarGrid);
      break;
    case 'week':
      renderWeekView(calendarGrid);
      break;
    case 'day':
      renderDayView(calendarGrid);
      break;
  }
  
  // Add event listeners to calendar day cells
  const dayCells = calendarGrid.querySelectorAll('.calendar-day');
  dayCells.forEach(cell => {
    cell.addEventListener('click', () => {
      const dateStr = cell.getAttribute('data-date');
      if (dateStr) {
        appointmentsState.selectedDate = new Date(dateStr);
        appointmentsState.date = dateStr;
        document.getElementById('appointment-date-filter').value = dateStr;
        
        // If day view is not already active, switch to it
        if (appointmentsState.calendarView !== 'day') {
          appointmentsState.calendarView = 'day';
          calendarContainer.querySelector('.month-view-btn').classList.remove('active');
          calendarContainer.querySelector('.week-view-btn').classList.remove('active');
          calendarContainer.querySelector('.day-view-btn').classList.add('active');
          updateCalendar();
        }
        
        // Update appointments list
        loadAppointments();
      }
    });
  });
}

// Render month view
function renderMonthView(calendarGrid) {
  const date = appointmentsState.selectedDate;
  const year = date.getFullYear();
  const month = date.getMonth();
  
  // Get first day of month and last day
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  
  // Get the day of week for the first day (0 is Sunday)
  let firstDayOfWeek = firstDay.getDay();
  
  // Create header with weekday names
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const headerRow = document.createElement('div');
  headerRow.className = 'calendar-header-row';
  
  weekdays.forEach(day => {
    const dayCell = document.createElement('div');
    dayCell.className = 'calendar-header-cell';
    dayCell.textContent = day;
    headerRow.appendChild(dayCell);
  });
  
  calendarGrid.appendChild(headerRow);
  
  // Create calendar grid
  let currentDay = new Date(firstDay);
  currentDay.setDate(firstDay.getDate() - firstDayOfWeek); // Start from last month if needed
  
  // Create 6 rows (to account for all possible month layouts)
  for (let row = 0; row < 6; row++) {
    const weekRow = document.createElement('div');
    weekRow.className = 'calendar-row';
    
    // Create 7 columns (days of the week)
    for (let col = 0; col < 7; col++) {
      const dayCell = document.createElement('div');
      dayCell.className = 'calendar-day';
      
      // Format date for data attribute
      const yyyy = currentDay.getFullYear();
      const mm = String(currentDay.getMonth() + 1).padStart(2, '0');
      const dd = String(currentDay.getDate()).padStart(2, '0');
      const dateStr = `${yyyy}-${mm}-${dd}`;
      dayCell.setAttribute('data-date', dateStr);
      
      // Check if the day is in the current month
      if (currentDay.getMonth() !== month) {
        dayCell.classList.add('outside-month');
      }
      
      // Check if the day is today
      const today = new Date();
      if (currentDay.getDate() === today.getDate() && 
          currentDay.getMonth() === today.getMonth() && 
          currentDay.getFullYear() === today.getFullYear()) {
        dayCell.classList.add('today');
      }
      
      // Check if the day is selected
      if (currentDay.getDate() === appointmentsState.selectedDate.getDate() && 
          currentDay.getMonth() === appointmentsState.selectedDate.getMonth() && 
          currentDay.getFullYear() === appointmentsState.selectedDate.getFullYear()) {
        dayCell.classList.add('selected');
      }
      
      // Add the day number
      const dayNumber = document.createElement('div');
      dayNumber.className = 'day-number';
      dayNumber.textContent = currentDay.getDate();
      dayCell.appendChild(dayNumber);
      
      // Add day content container for appointments
      const dayContent = document.createElement('div');
      dayContent.className = 'day-content';
      dayCell.appendChild(dayContent);
      
      // Add to week row
      weekRow.appendChild(dayCell);
      
      // Move to next day
      currentDay.setDate(currentDay.getDate() + 1);
    }
    
    calendarGrid.appendChild(weekRow);
    
    // Stop if we've gone past the end of the month
    if (currentDay.getMonth() > month && currentDay.getDate() > 7) break;
  }
  
  // Add appointments to calendar
  addAppointmentsToCalendar();
}

// Render week view
function renderWeekView(calendarGrid) {
  const date = appointmentsState.selectedDate;
  
  // Get the first day of the week (Sunday)
  const dayOfWeek = date.getDay();
  const firstDay = new Date(date);
  firstDay.setDate(date.getDate() - dayOfWeek);
  
  // Create time labels column
  const timeLabels = document.createElement('div');
  timeLabels.className = 'time-labels';
  
  // Add header for time column
  const timeHeader = document.createElement('div');
  timeHeader.className = 'time-header';
  timeLabels.appendChild(timeHeader);
  
  // Add time slots
  for (let hour = 8; hour < 18; hour++) {
    const timeSlot = document.createElement('div');
    timeSlot.className = 'time-slot';
    timeSlot.textContent = `${hour}:00`;
    timeLabels.appendChild(timeSlot);
  }
  
  calendarGrid.appendChild(timeLabels);
  
  // Create columns for each day of the week
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  
  for (let i = 0; i < 7; i++) {
    const dayCol = document.createElement('div');
    dayCol.className = 'day-column';
    
    // Get the date for this column
    const currentDay = new Date(firstDay);
    currentDay.setDate(firstDay.getDate() + i);
    
    // Format date for data attribute
    const yyyy = currentDay.getFullYear();
    const mm = String(currentDay.getMonth() + 1).padStart(2, '0');
    const dd = String(currentDay.getDate()).padStart(2, '0');
    const dateStr = `${yyyy}-${mm}-${dd}`;
    dayCol.setAttribute('data-date', dateStr);
    
    // Check if the day is today
    const today = new Date();
    if (currentDay.getDate() === today.getDate() && 
        currentDay.getMonth() === today.getMonth() && 
        currentDay.getFullYear() === today.getFullYear()) {
      dayCol.classList.add('today');
    }
    
    // Add day header
    const dayHeader = document.createElement('div');
    dayHeader.className = 'day-header';
    dayHeader.innerHTML = `
      <div class="day-name">${weekdays[i]}</div>
      <div class="day-number">${currentDay.getDate()}</div>
    `;
    dayCol.appendChild(dayHeader);
    
    // Add time slots
    for (let hour = 8; hour < 18; hour++) {
      const timeSlot = document.createElement('div');
      timeSlot.className = 'time-slot';
      timeSlot.setAttribute('data-hour', hour);
      dayCol.appendChild(timeSlot);
    }
    
    calendarGrid.appendChild(dayCol);
  }
  
  // Add appointments to calendar
  addAppointmentsToCalendar();
}

// Render day view
function renderDayView(calendarGrid) {
  const date = appointmentsState.selectedDate;
  
  // Format date display
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const dateDisplay = date.toLocaleDateString(undefined, options);
  
  // Create day header
  const dayHeader = document.createElement('div');
  dayHeader.className = 'day-view-header';
  dayHeader.textContent = dateDisplay;
  calendarGrid.appendChild(dayHeader);
  
  // Create day schedule
  const daySchedule = document.createElement('div');
  daySchedule.className = 'day-schedule';
  
  // Format date for data attribute
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  const dateStr = `${yyyy}-${mm}-${dd}`;
  daySchedule.setAttribute('data-date', dateStr);
  
  // Create schedule slots for each hour
  for (let hour = 8; hour < 18; hour++) {
    const hourSlot = document.createElement('div');
    hourSlot.className = 'hour-slot';
    
    const hourLabel = document.createElement('div');
    hourLabel.className = 'hour-label';
    hourLabel.textContent = `${hour}:00`;
    
    const hourContent = document.createElement('div');
    hourContent.className = 'hour-content';
    hourContent.setAttribute('data-hour', hour);
    
    hourSlot.appendChild(hourLabel);
    hourSlot.appendChild(hourContent);
    daySchedule.appendChild(hourSlot);
  }
  
  calendarGrid.appendChild(daySchedule);
  
  // Add appointments to calendar
  addAppointmentsToCalendar();
}

// Add appointments to calendar
function addAppointmentsToCalendar() {
  // Get appointments for the currently displayed period
  const displayedAppointments = getDisplayedAppointments();
  
  if (displayedAppointments.length === 0) return;
  
  // Add appointments based on the current view
  switch (appointmentsState.calendarView) {
    case 'month':
      addAppointmentsToMonthView(displayedAppointments);
      break;
    case 'week':
      addAppointmentsToWeekView(displayedAppointments);
      break;
    case 'day':
      addAppointmentsToDayView(displayedAppointments);
      break;
  }
}

// Get appointments that should be displayed in the current calendar view
function getDisplayedAppointments() {
  // Check if appointments are loaded
  if (!appointmentsState.appointments || appointmentsState.appointments.length === 0) {
    return [];
  }
  
  // Filter appointments based on the current view
  const date = appointmentsState.selectedDate;
  
  if (appointmentsState.calendarView === 'month') {
    // For month view, get all appointments in the selected month
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    return appointmentsState.appointments.filter(appointment => {
      const appointmentDate = new Date(appointment.date);
      return appointmentDate >= firstDay && appointmentDate <= lastDay;
    });
  } else if (appointmentsState.calendarView === 'week') {
    // For week view, get all appointments in the selected week
    const dayOfWeek = date.getDay();
    const firstDay = new Date(date);
    firstDay.setDate(date.getDate() - dayOfWeek);
    
    const lastDay = new Date(firstDay);
    lastDay.setDate(firstDay.getDate() + 6);
    
    return appointmentsState.appointments.filter(appointment => {
      const appointmentDate = new Date(appointment.date);
      return appointmentDate >= firstDay && appointmentDate <= lastDay;
    });
  } else {
    // For day view, get all appointments on the selected day
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = date.getDate();
    
    return appointmentsState.appointments.filter(appointment => {
      const appointmentDate = new Date(appointment.date);
      return appointmentDate.getFullYear() === year && 
             appointmentDate.getMonth() === month && 
             appointmentDate.getDate() === day;
    });
  }
}

// Add appointments to month view
function addAppointmentsToMonthView(appointments) {
  const calendarGrid = document.querySelector('.calendar-grid');
  
  // Loop through each appointment
  appointments.forEach(appointment => {
    // Find the corresponding day cell
    const dayCell = calendarGrid.querySelector(`.calendar-day[data-date="${appointment.date}"]`);
    if (!dayCell) return;
    
    // Add appointment to day content
    const dayContent = dayCell.querySelector('.day-content');
    
    // Create appointment element
    const appointmentEl = document.createElement('div');
    appointmentEl.className = `appointment-item ${appointment.status}`;
    appointmentEl.setAttribute('data-appointment-id', appointment.appointment_id);
    
    // Format time
    const startTime = formatTime(appointment.start_time);
    
    appointmentEl.innerHTML = `
      <span class="appointment-time">${startTime}</span>
      <span class="appointment-title">${appointment.title}</span>
    `;
    
    // Add click event to view appointment details
    appointmentEl.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent triggering the day cell click
      viewAppointment(appointment.appointment_id);
    });
    
    dayContent.appendChild(appointmentEl);
  });
}

// Add appointments to week view
function addAppointmentsToWeekView(appointments) {
  const calendarGrid = document.querySelector('.calendar-grid');
  
  // Loop through each appointment
  appointments.forEach(appointment => {
    // Find the corresponding day column
    const dayColumn = calendarGrid.querySelector(`.day-column[data-date="${appointment.date}"]`);
    if (!dayColumn) return;
    
    // Get appointment times
    const startTime = new Date(`${appointment.date}T${appointment.start_time}`);
    const endTime = new Date(`${appointment.date}T${appointment.end_time}`);
    
    // Get hour and calculate duration
    const startHour = startTime.getHours();
    const endHour = endTime.getHours();
    const startMinutes = startTime.getMinutes();
    const endMinutes = endTime.getMinutes();
    
    // Calculate position and height
    const hourHeight = 60; // height in pixels for one hour
    const topPosition = (startHour - 8) * hourHeight + (startMinutes / 60) * hourHeight;
    const height = (endHour - startHour) * hourHeight + ((endMinutes - startMinutes) / 60) * hourHeight;
    
    // Create appointment element
    const appointmentEl = document.createElement('div');
    appointmentEl.className = `appointment-item ${appointment.status}`;
    appointmentEl.setAttribute('data-appointment-id', appointment.appointment_id);
    appointmentEl.style.top = `${topPosition}px`;
    appointmentEl.style.height = `${height}px`;
    
    appointmentEl.innerHTML = `
      <span class="appointment-title">${appointment.title}</span>
      <span class="appointment-time">${formatTime(appointment.start_time)} - ${formatTime(appointment.end_time)}</span>
    `;
    
    // Add click event to view appointment details
    appointmentEl.addEventListener('click', () => {
      viewAppointment(appointment.appointment_id);
    });
    
    // Find relevant time slot and append
    dayColumn.appendChild(appointmentEl);
  });
}

// Add appointments to day view
function addAppointmentsToDayView(appointments) {
  const daySchedule = document.querySelector('.day-schedule');
  
  // Loop through each appointment
  appointments.forEach(appointment => {
    // Get appointment times
    const startTime = new Date(`${appointment.date}T${appointment.start_time}`);
    const endTime = new Date(`${appointment.date}T${appointment.end_time}`);
    
    // Get hour and calculate duration
    const startHour = startTime.getHours();
    const endHour = endTime.getHours();
    const startMinutes = startTime.getMinutes();
    const endMinutes = endTime.getMinutes();
    
    // Calculate position and height
    const hourHeight = 60; // height in pixels for one hour
    const topPosition = (startMinutes / 60) * hourHeight;
    const height = ((endHour - startHour) * 60 + (endMinutes - startMinutes)) / 60 * hourHeight;
    
    // Find the hour content elements that this appointment spans
    for (let hour = startHour; hour <= endHour; hour++) {
      if (hour < 8 || hour >= 18) continue; // Skip hours outside business hours
      
      const hourContent = daySchedule.querySelector(`.hour-content[data-hour="${hour}"]`);
      if (!hourContent) continue;
      
      // Only create the appointment in the first hour slot
      if (hour === startHour) {
        // Create appointment element
        const appointmentEl = document.createElement('div');
        appointmentEl.className = `appointment-item ${appointment.status}`;
        appointmentEl.setAttribute('data-appointment-id', appointment.appointment_id);
        
        // Adjust position and height if spanning multiple hours
        if (endHour > startHour) {
          appointmentEl.style.height = `${height}px`;
          appointmentEl.style.top = `${topPosition}px`;
          appointmentEl.style.position = 'absolute';
          hourContent.style.position = 'relative';
        }
        
        appointmentEl.innerHTML = `
          <span class="appointment-title">${appointment.title}</span>
          <span class="appointment-time">${formatTime(appointment.start_time)} - ${formatTime(appointment.end_time)}</span>
          <span class="appointment-contact">${appointment.contact}</span>
        `;
        
        // Add click event to view appointment details
        appointmentEl.addEventListener('click', () => {
          viewAppointment(appointment.appointment_id);
        });
        
        hourContent.appendChild(appointmentEl);
      }
    }
  });
}

// Load appointments
function loadAppointments() {
  // Build filters
  const filters = {
    page: appointmentsState.page,
    page_size: appointmentsState.pageSize
  };
  
  if (appointmentsState.status !== 'all') {
    filters.status = appointmentsState.status;
  }
  
  if (appointmentsState.date) {
    filters.date = appointmentsState.date;
  }
  
  // Show loading state
  const appointmentsList = document.getElementById('appointments-list');
  appointmentsList.innerHTML = `
    <p class="placeholder-text">Loading appointments...</p>
  `;
  
  // Fetch appointments
  api.getAppointments(filters)
    .then(data => {
      appointmentsState.appointments = data.appointments;
      appointmentsState.total = data.total;
      
      // Update calendar with appointments
      updateCalendar();
      
      // Render appointments list
      renderAppointments();
    })
    .catch(error => {
      console.error('Error loading appointments:', error);
      appointmentsList.innerHTML = `
        <p class="placeholder-text">Error loading appointments</p>
      `;
    });
}

// Render appointments list
function renderAppointments() {
  const appointmentsList = document.getElementById('appointments-list');
  
  if (appointmentsState.appointments.length === 0) {
    appointmentsList.innerHTML = `
      <p class="placeholder-text">No appointments found</p>
    `;
    return;
  }
  
  appointmentsList.innerHTML = '';
  
  appointmentsState.appointments.forEach(appointment => {
    const appointmentItem = document.createElement('div');
    appointmentItem.className = `appointment-item ${appointment.status}`;
    appointmentItem.innerHTML = `
      <div class="appointment-header">
        <div class="appointment-date">${formatDate(appointment.date)}</div>
        <div class="appointment-time">${formatTime(appointment.start_time)} - ${formatTime(appointment.end_time)}</div>
      </div>
      <div class="appointment-title">${appointment.title}</div>
      <div class="appointment-contact">${appointment.contact}</div>
      <div class="appointment-actions">
        <button class="action-btn view-appointment-btn" data-appointment-id="${appointment.appointment_id}">
          <i class="fas fa-eye"></i>
        </button>
        <button class="action-btn edit-appointment-btn" data-appointment-id="${appointment.appointment_id}">
          <i class="fas fa-edit"></i>
        </button>
        <button class="action-btn delete-appointment-btn" data-appointment-id="${appointment.appointment_id}">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    `;
    
    appointmentsList.appendChild(appointmentItem);
  });
  
  // Add event listeners for appointment actions
  setupAppointmentActions();
}

// Set up appointment actions
function setupAppointmentActions() {
  // View appointment
  document.querySelectorAll('.view-appointment-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const appointmentId = btn.getAttribute('data-appointment-id');
      viewAppointment(appointmentId);
    });
  });
  
  // Edit appointment
  document.querySelectorAll('.edit-appointment-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const appointmentId = btn.getAttribute('data-appointment-id');
      editAppointment(appointmentId);
    });
  });
  
  // Delete appointment
  document.querySelectorAll('.delete-appointment-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const appointmentId = btn.getAttribute('data-appointment-id');
      deleteAppointment(appointmentId);
    });
  });
  
  // Make entire appointment item clickable
  document.querySelectorAll('#appointments-list .appointment-item').forEach(item => {
    item.addEventListener('click', () => {
      const appointmentId = item.querySelector('.view-appointment-btn').getAttribute('data-appointment-id');
      viewAppointment(appointmentId);
    });
  });
}

// View appointment details
function viewAppointment(appointmentId) {
  api.getAppointment(appointmentId)
    .then(appointment => {
      // Get modal
      const modalId = 'appointment-detail-modal';
      const modal = document.getElementById(modalId);
      
      // Set modal title
      modal.querySelector('.modal-header h3').textContent = 'Appointment Details';
      
      // Populate modal with appointment details
      const modalBody = modal.querySelector('.modal-body');
      
      modalBody.innerHTML = `
        <div class="appointment-details">
          <div class="detail-group">
            <span class="detail-label">Title:</span>
            <span class="detail-value">${appointment.title}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Contact:</span>
            <span class="detail-value">${appointment.contact}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Date:</span>
            <span class="detail-value">${formatDate(appointment.date)}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Time:</span>
            <span class="detail-value">${formatTime(appointment.start_time)} - ${formatTime(appointment.end_time)}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Status:</span>
            <span class="detail-value"><span class="status-badge ${appointment.status}">${appointment.status}</span></span>
          </div>
          ${appointment.notes ? `
            <div class="detail-group">
              <span class="detail-label">Notes:</span>
              <span class="detail-value">${appointment.notes}</span>
            </div>
          ` : ''}
          ${appointment.call_id ? `
            <div class="detail-group">
              <span class="detail-label">Related Call:</span>
              <span class="detail-value">
                <button class="secondary-btn view-related-call-btn" data-call-id="${appointment.call_id}">
                  <i class="fas fa-phone-alt"></i> View Call Details
                </button>
              </span>
            </div>
          ` : ''}
        </div>
      `;
      
      // Add event listener for related call button if it exists
      const relatedCallBtn = modalBody.querySelector('.view-related-call-btn');
      if (relatedCallBtn) {
        relatedCallBtn.addEventListener('click', () => {
          closeModal(modalId);
          viewCall(appointment.call_id);
        });
      }
      
      // Update edit button event listener
      const editBtn = modal.querySelector('.edit-btn');
      if (editBtn) {
        // Remove existing event listeners
        const newEditBtn = editBtn.cloneNode(true);
        editBtn.parentNode.replaceChild(newEditBtn, editBtn);
        
        // Add new event listener
        newEditBtn.addEventListener('click', () => {
          closeModal(modalId);
          editAppointment(appointmentId);
        });
      }
      
      // Show modal
      openModal(modalId);
    })
    .catch(error => {
      console.error('Error loading appointment details:', error);
      showNotification('Error loading appointment details', 'error');
    });
}

// Show new appointment modal
function showNewAppointmentModal() {
  const modalId = 'appointment-form-modal';
  const modal = document.getElementById(modalId);
  
  // Set modal title
  modal.querySelector('.modal-header h3').textContent = 'New Appointment';
  
  // Reset form
  document.getElementById('appointment-form').reset();
  document.getElementById('appointment-id').value = '';
  
  // Set default date to the selected date in the calendar
  const dateInput = document.getElementById('appointment-date');
  const yyyy = appointmentsState.selectedDate.getFullYear();
  const mm = String(appointmentsState.selectedDate.getMonth() + 1).padStart(2, '0');
  const dd = String(appointmentsState.selectedDate.getDate()).padStart(2, '0');
  dateInput.value = `${yyyy}-${mm}-${dd}`;
  
  // Set default times (9 AM - 10 AM)
  document.getElementById('appointment-start-time').value = '09:00';
  document.getElementById('appointment-end-time').value = '10:00';
  
  // Clear error message
  document.getElementById('appointment-form-error').textContent = '';
  
  // Show modal
  openModal(modalId);
}

// Edit appointment
function editAppointment(appointmentId) {
  api.getAppointment(appointmentId)
    .then(appointment => {
      const modalId = 'appointment-form-modal';
      const modal = document.getElementById(modalId);
      
      // Set modal title
      modal.querySelector('.modal-header h3').textContent = 'Edit Appointment';
      
      // Populate form with appointment data
      document.getElementById('appointment-title').value = appointment.title;
      document.getElementById('appointment-contact').value = appointment.contact;
      document.getElementById('appointment-date').value = appointment.date;
      document.getElementById('appointment-start-time').value = appointment.start_time;
      document.getElementById('appointment-end-time').value = appointment.end_time;
      document.getElementById('appointment-status').value = appointment.status;
      document.getElementById('appointment-notes').value = appointment.notes || '';
      document.getElementById('appointment-id').value = appointment.appointment_id;
      
      // Clear error message
      document.getElementById('appointment-form-error').textContent = '';
      
      // Show modal
      openModal(modalId);
    })
    .catch(error => {
      console.error('Error loading appointment for editing:', error);
      showNotification('Error loading appointment', 'error');
    });
}

// Save appointment (create or update)
function saveAppointment() {
  // Get form data
  const appointmentId = document.getElementById('appointment-id').value;
  const title = document.getElementById('appointment-title').value.trim();
  const contact = document.getElementById('appointment-contact').value.trim();
  const date = document.getElementById('appointment-date').value;
  const startTime = document.getElementById('appointment-start-time').value;
  const endTime = document.getElementById('appointment-end-time').value;
  const status = document.getElementById('appointment-status').value;
  const notes = document.getElementById('appointment-notes').value.trim();
  
  // Validate
  const errorEl = document.getElementById('appointment-form-error');
  
  if (!title || !contact || !date || !startTime || !endTime) {
    errorEl.textContent = 'Please fill out all required fields';
    return;
  }
  
  // Validate time range
  const startDateTime = new Date(`${date}T${startTime}`);
  const endDateTime = new Date(`${date}T${endTime}`);
  
  if (endDateTime <= startDateTime) {
    errorEl.textContent = 'End time must be after start time';
    return;
  }
  
  // Prepare data
  const appointmentData = {
    title,
    contact,
    date,
    start_time: startTime,
    end_time: endTime,
    status,
    notes
  };
  
  // Save (create or update)
  let savePromise;
  
  if (appointmentId) {
    // Update existing appointment
    appointmentData.appointment_id = appointmentId;
    savePromise = api.updateAppointment(appointmentId, appointmentData);
  } else {
    // Create new appointment
    savePromise = api.createAppointment(appointmentData);
  }
  
  savePromise
    .then(() => {
      closeModal('appointment-form-modal');
      showNotification('Appointment saved successfully', 'success');
      loadAppointments();
    })
    .catch(error => {
      console.error('Error saving appointment:', error);
      errorEl.textContent = 'Error saving appointment. Please try again.';
    });
}

// Delete appointment
function deleteAppointment(appointmentId) {
  if (confirm('Are you sure you want to delete this appointment?')) {
    api.deleteAppointment(appointmentId)
      .then(() => {
        showNotification('Appointment deleted successfully', 'success');
        loadAppointments();
      })
      .catch(error => {
        console.error('Error deleting appointment:', error);
        showNotification('Error deleting appointment', 'error');
      });
  }
}

// Function to load upcoming appointments for the dashboard
function loadUpcomingAppointments() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const todayStr = `${yyyy}-${mm}-${dd}`;
  
  api.getAppointments({ 
    start_date: todayStr,
    page: 1, 
    page_size: 5,
    status: 'scheduled'
  })
    .then(data => {
      const appointmentsContainer = document.getElementById('upcoming-appointments');
      
      if (!data.appointments || data.appointments.length === 0) {
        appointmentsContainer.innerHTML = `<p class="placeholder-text">No upcoming appointments</p>`;
        return;
      }
      
      appointmentsContainer.innerHTML = '';
      
      data.appointments.forEach(appointment => {
        const appointmentItem = document.createElement('div');
        appointmentItem.className = `appointment-item ${appointment.status}`;
        appointmentItem.innerHTML = `
          <div class="appointment-header">
            <div class="appointment-date">${formatDate(appointment.date)}</div>
            <div class="appointment-time">${formatTime(appointment.start_time)}</div>
          </div>
          <div class="appointment-title">${appointment.title}</div>
          <div class="appointment-contact">${appointment.contact}</div>
        `;
        
        // Add click event to view the appointment
        appointmentItem.addEventListener('click', () => {
          viewAppointment(appointment.appointment_id);
        });
        
        appointmentsContainer.appendChild(appointmentItem);
      });
    })
    .catch(error => {
      console.error('Error loading upcoming appointments:', error);
      document.getElementById('upcoming-appointments').innerHTML = `
        <p class="placeholder-text">Error loading appointments</p>
      `;
    });
}