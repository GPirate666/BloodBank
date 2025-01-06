const hospitals = [
    {
        id: 1,
        name: "Spitalul Universitar de Urgență București",
        address: "Splaiul Independenței 169, Sector 5, București"
    },
    {
        id: 2,
        name: "Spitalul Clinic de Urgență Floreasca",
        address: "Calea Floreasca 8, Sector 1, București"
    },
    {
        id: 3,
        name: "Spitalul Clinic Colțea",
        address: "Bulevardul I.C. Brătianu 1, Sector 3, București"
    },
    {
        id: 4,
        name: "Spitalul Clinic de Urgență Sf. Pantelimon",
        address: "Șoseaua Pantelimon 340-342, Sector 2, București"
    },
    {
        id: 5,
        name: "Spitalul Clinic de Urgență Bagdasar-Arseni",
        address: "Șoseaua Berceni 12, Sector 4, București"
    }
];

function initializeHospitalSelector() {
    const hospitalList = document.getElementById('hospitalList');
    
    hospitals.forEach(hospital => {
        const hospitalCard = document.createElement('div');
        hospitalCard.className = 'hospital-card';
        hospitalCard.dataset.hospitalId = hospital.id;
        
        hospitalCard.innerHTML = `
            <div class="hospital-name">${hospital.name}</div>
            <div class="hospital-address">${hospital.address}</div>
        `;
        
        hospitalCard.addEventListener('click', () => {
            // Remove selection from other hospitals
            document.querySelectorAll('.hospital-card').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Select this hospital
            hospitalCard.classList.add('selected');
        });
        
        hospitalList.appendChild(hospitalCard);
    });
}

// Initialize hospital selector
initializeHospitalSelector();

// Blood type selection functionality
document.querySelectorAll('.blood-type').forEach(button => {
    button.addEventListener('click', () => {
        // Deselect other buttons
        document.querySelectorAll('.blood-type').forEach(btn => btn.classList.remove('selected'));

        // Select this button
        button.classList.add('selected');
    });
});

// Current date setup
const currentDate = new Date(); // Use current date dynamically
const currentMonth = {
    name: currentDate.toLocaleString('default', { month: 'long' }) + ' ' + currentDate.getFullYear(),
    days: new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate(),
    firstDay: new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay() || 7 // Convert Sunday (0) to 7
};

// Week handling functions
let currentWeekStart = new Date(currentDate);
currentWeekStart.setDate(currentWeekStart.getDate() - currentWeekStart.getDay() + 1); // Start from Monday

function formatDateHeader(date) {
    const day = date.toLocaleString('default', { weekday: 'long' });
    return `${day}<br>${date.getDate()}`;
}

function generateTimeSlotGrid(startDate) {
    const timeSlotGrid = document.getElementById('timeSlotGrid');
    timeSlotGrid.innerHTML = ''; // Clear existing content

    const timeSlots = [
        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
        '15:00', '15:30', '16:00', '16:30', '17:00', '17:30'
    ];

    // Generate 7 columns starting from the given date
    for (let i = 0; i < 7; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);

        const column = document.createElement('div');
        column.className = 'date-column';
        
        const header = document.createElement('div');
        header.className = 'date-header';
        header.innerHTML = formatDateHeader(currentDate);
        column.appendChild(header);

        timeSlots.forEach(time => {
            const slot = document.createElement('div');
            slot.className = 'time-slot';
            // Disable past dates and times
            const now = new Date();
            const slotDateTime = new Date(currentDate);
            const [hours, minutes] = time.split(':').map(Number);
            slotDateTime.setHours(hours, minutes, 0, 0);
            if (slotDateTime < now) {
                slot.classList.add('disabled');
            }
            slot.textContent = time;
            slot.addEventListener('click', () => {
                if (!slot.classList.contains('disabled')) {
                    document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                    slot.classList.add('selected');
                }
            });
            column.appendChild(slot);
        });

        timeSlotGrid.appendChild(column);
    }

    // Update navigation month display
    document.querySelector('.week-navigation span').textContent = 
        startDate.toLocaleString('default', { month: 'long', year: 'numeric' });
}

// Navigation event handlers
document.querySelector('.prev-week').addEventListener('click', () => {
    currentWeekStart.setDate(currentWeekStart.getDate() - 7);
    generateTimeSlotGrid(currentWeekStart);
});

document.querySelector('.next-week').addEventListener('click', () => {
    currentWeekStart.setDate(currentWeekStart.getDate() + 7);
    generateTimeSlotGrid(currentWeekStart);
});

// Initialize the grid with current week
generateTimeSlotGrid(currentWeekStart);

// Generate small calendar
function generateCalendar() {
    const calendarBody = document.getElementById('calendarBody');
    calendarBody.innerHTML = ''; // Clear existing content
    
    let date = 1;
    let firstDay = currentMonth.firstDay;

    for (let i = 0; i < 6; i++) {
        const row = document.createElement('tr');
        for (let j = 0; j < 7; j++) {
            const cell = document.createElement('td');
            if (i === 0 && j < firstDay - 1) {
                cell.textContent = '';
            } else if (date > currentMonth.days) {
                cell.textContent = '';
            } else {
                cell.textContent = date;
                // Add active class for current week
                const cellDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), date);
                if (cellDate >= currentWeekStart && 
                    cellDate < new Date(currentWeekStart.getTime() + 7 * 24 * 60 * 60 * 1000)) {
                    cell.classList.add('active');
                }
                // Highlight current date
                const today = new Date();
                if (date === today.getDate() && currentDate.getMonth() === today.getMonth() && currentDate.getFullYear() === today.getFullYear()) {
                    cell.classList.add('selected');
                }
                date++;
            }
            row.appendChild(cell);
        }
        calendarBody.appendChild(row);
        if (date > currentMonth.days) break;
    }
}

generateCalendar();

// Update month display in small calendar
document.querySelector('.month-navigation span').textContent = currentMonth.name;

// ------------------ Consolidated Submit Button Handler ------------------ //

// Select the submit button
const submitBtn = document.querySelector('.submit-btn');

// Ensure the submit button exists
if (submitBtn) {
    submitBtn.addEventListener('click', async (event) => {
        event.preventDefault(); // Prevent the default form submission

        // Get selected blood type
        const selectedBloodType = document.querySelector('.blood-type.selected')?.dataset.bloodType;
        
        // Get selected time slot element and text
        const selectedTimeElement = document.querySelector('.time-slot.selected');
        const selectedTime = selectedTimeElement?.textContent;
        
        // Get selected hospital
        const selectedHospital = document.querySelector('.hospital-card.selected .hospital-name')?.textContent;
        
        // Get selected date header from the parent of the selected time slot
        const selectedDateHeader = selectedTimeElement ? selectedTimeElement.parentElement.querySelector('.date-header')?.innerHTML : null;
        
        // Extract the day from the date header
        const selectedDay = selectedDateHeader ? selectedDateHeader.split('<br>')[1].trim() : null;

        // Form Validations
        if (!selectedBloodType) {
            alert('Please select your blood type.');
            return;
        }

        if (!selectedDay) {
            alert('Please select a date.');
            return;
        }

        if (!selectedTime) {
            alert('Please select a time slot.');
            return;
        }

        if (!selectedHospital) {
            alert('Please select a hospital.');
            return;
        }

        // Determine the selected date's month and year based on currentWeekStart
        const selectedMonth = currentWeekStart.getMonth() + 1; // Months are zero-based
        const selectedYear = currentWeekStart.getFullYear();
        const day = selectedDay.padStart(2, '0');

        // Format the date as YYYY-MM-DD
        const formattedDate = `${selectedYear}-${String(selectedMonth).padStart(2, '0')}-${day}`;

        try {
            // Fetch userId from the server/session
            const userResponse = await fetch('/get_user', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!userResponse.ok) {
                throw new Error('User not logged in.');
            }

            const userData = await userResponse.json();
            const userId = userData.user_id;

            if (!userId) {
                alert('Unable to fetch user information. Please log in.');
                return;
            }

            // Prepare the payload
            const payload = {
                user_id: userId,
                blood_type: selectedBloodType,
                date: formattedDate,
                time: selectedTime,
                hospital_name: selectedHospital,
            };

            // Send JSON data to the backend
            const response = await fetch('/schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                // Redirect to gamification.html
                window.location.href = result.redirect_url;
            } else {
                // Handle errors returned by the backend
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while submitting the form.');
        }
    });
}
