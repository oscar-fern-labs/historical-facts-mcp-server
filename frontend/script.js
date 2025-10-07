// Historical Facts Explorer - JavaScript
const API_BASE_URL = 'https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so';

// DOM Elements
const todayFactsBtn = document.getElementById('todayFactsBtn');
const randomFactBtn = document.getElementById('randomFactBtn');
const searchDateBtn = document.getElementById('searchDateBtn');
const monthSelect = document.getElementById('monthSelect');
const daySelect = document.getElementById('daySelect');
const filterTabs = document.getElementById('filterTabs');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const emptyState = document.getElementById('emptyState');
const resultsContainer = document.getElementById('resultsContainer');

// State management
let currentData = null;
let currentFilter = 'all';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    populateDayOptions();
    checkAPIHealth();
});

// Event Listeners
function setupEventListeners() {
    todayFactsBtn.addEventListener('click', loadTodayFacts);
    randomFactBtn.addEventListener('click', loadRandomFact);
    searchDateBtn.addEventListener('click', searchByDate);
    
    monthSelect.addEventListener('change', handleMonthChange);
    daySelect.addEventListener('change', handleDayChange);
    
    // Filter tabs
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('filter-tab')) {
            handleFilterChange(e.target.dataset.type);
        }
    });
}

// API Health Check
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) throw new Error('API not responding');
        
        // Update status indicator
        const statusElement = document.querySelector('.text-green-800');
        if (statusElement) {
            statusElement.textContent = 'API Online';
        }
    } catch (error) {
        console.error('API health check failed:', error);
        const statusElement = document.querySelector('.text-green-800');
        if (statusElement) {
            statusElement.textContent = 'API Offline';
            statusElement.classList.remove('text-green-800', 'bg-green-100');
            statusElement.classList.add('text-red-800', 'bg-red-100');
        }
    }
}

// Load Today's Facts
async function loadTodayFacts() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/historical-facts/today`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        currentData = data;
        currentFilter = 'all';
        
        displayResults(data);
        showFilterTabs();
        scrollToResults();
    } catch (error) {
        console.error('Error loading today\'s facts:', error);
        showError();
    }
}

// Load Random Fact
async function loadRandomFact() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/historical-facts/random`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        displayRandomFact(data);
        hideFilterTabs();
        scrollToResults();
    } catch (error) {
        console.error('Error loading random fact:', error);
        showError();
    }
}

// Search by Date
async function searchByDate() {
    const month = monthSelect.value;
    const day = daySelect.value;
    
    if (!month || !day) {
        alert('Please select both month and day');
        return;
    }
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/historical-facts/${month}/${day}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        currentData = data;
        currentFilter = 'all';
        
        displayResults(data);
        showFilterTabs();
        scrollToResults();
    } catch (error) {
        console.error('Error searching by date:', error);
        showError();
    }
}

// Handle Month Change
function handleMonthChange() {
    const month = parseInt(monthSelect.value);
    populateDayOptions(month);
    updateSearchButton();
}

// Handle Day Change
function handleDayChange() {
    updateSearchButton();
}

// Update Search Button State
function updateSearchButton() {
    const isValid = monthSelect.value && daySelect.value;
    searchDateBtn.disabled = !isValid;
}

// Populate Day Options
function populateDayOptions(month = null) {
    daySelect.innerHTML = '<option value="">Day</option>';
    
    if (!month) return;
    
    const daysInMonth = getDaysInMonth(month);
    for (let day = 1; day <= daysInMonth; day++) {
        const option = document.createElement('option');
        option.value = day;
        option.textContent = day;
        daySelect.appendChild(option);
    }
}

// Get Days in Month
function getDaysInMonth(month) {
    const daysInMonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    return daysInMonth[month - 1];
}

// Handle Filter Change
function handleFilterChange(filterType) {
    if (!currentData) return;
    
    currentFilter = filterType;
    
    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-type="${filterType}"]`).classList.add('active');
    
    // Re-render results with filter
    displayResults(currentData);
}

// Display Results
function displayResults(data) {
    hideLoading();
    hideError();
    hideEmpty();
    
    resultsContainer.innerHTML = '';
    
    if (!data.event_types || data.event_types.length === 0) {
        showEmpty();
        return;
    }
    
    const filteredEventTypes = currentFilter === 'all' 
        ? data.event_types 
        : data.event_types.filter(eventType => eventType.type === currentFilter);
    
    if (filteredEventTypes.length === 0) {
        resultsContainer.innerHTML = `
            <div class="text-center py-8">
                <p class="text-slate-600">No ${currentFilter} found for this date.</p>
            </div>
        `;
        return;
    }
    
    filteredEventTypes.forEach(eventType => {
        const section = createEventTypeSection(eventType, data.date);
        resultsContainer.appendChild(section);
    });
}

// Display Random Fact
function displayRandomFact(data) {
    hideLoading();
    hideError();
    hideEmpty();
    
    resultsContainer.innerHTML = '';
    
    if (!data.fact) {
        showEmpty();
        return;
    }
    
    const randomFactSection = document.createElement('div');
    randomFactSection.className = 'animate-slide-up';
    
    randomFactSection.innerHTML = `
        <div class="text-center mb-8">
            <h3 class="text-3xl font-bold text-slate-900 mb-2">🎲 Random Historical Discovery</h3>
            <p class="text-slate-600">From ${formatDate(data.date)}</p>
        </div>
        <div class="max-w-4xl mx-auto">
            ${createFactCard(data.fact)}
        </div>
    `;
    
    resultsContainer.appendChild(randomFactSection);
}

// Create Event Type Section
function createEventTypeSection(eventType, date) {
    const section = document.createElement('div');
    section.className = 'animate-slide-up';
    
    const categoryInfo = getCategoryInfo(eventType.type);
    
    section.innerHTML = `
        <div class="category-header">
            <div class="category-title">
                <span class="text-3xl mr-3">${categoryInfo.emoji}</span>
                <div>
                    <h3>${categoryInfo.title}</h3>
                    <p class="text-sm text-slate-500 font-normal">${formatDate(date)}</p>
                </div>
            </div>
            <div class="category-count">${eventType.count} ${eventType.count === 1 ? 'item' : 'items'}</div>
        </div>
        <div class="grid gap-6">
            ${eventType.events.slice(0, 10).map(event => createFactCard(event)).join('')}
        </div>
        ${eventType.events.length > 10 ? `
            <div class="text-center mt-6">
                <button class="text-brand-500 hover:text-brand-600 font-medium">
                    Show ${eventType.events.length - 10} more ${categoryInfo.title.toLowerCase()}
                </button>
            </div>
        ` : ''}
    `;
    
    return section;
}

// Create Fact Card
function createFactCard(event) {
    const page = event.pages && event.pages.length > 0 ? event.pages[0] : null;
    const thumbnail = page?.thumbnail;
    const extract = page?.extract;
    const title = page?.title;
    const url = page?.url;
    
    return `
        <div class="fact-card">
            <div class="flex gap-4">
                ${thumbnail ? `
                    <img src="${thumbnail}" alt="${title || 'Historical fact'}" 
                         class="thumbnail-image" loading="lazy" 
                         onerror="this.style.display='none'">
                ` : `
                    <div class="thumbnail-image flex items-center justify-center">
                        <span class="text-2xl">📚</span>
                    </div>
                `}
                <div class="fact-content">
                    <div class="flex items-start justify-between mb-3">
                        <span class="year-badge">${event.year}</span>
                    </div>
                    <p class="fact-text">${event.text}</p>
                    ${extract ? `
                        <p class="fact-extract">${truncateText(extract, 200)}</p>
                    ` : ''}
                    ${url ? `
                        <div class="fact-meta">
                            <a href="${url}" target="_blank" rel="noopener noreferrer" class="wikipedia-link">
                                Read more on Wikipedia
                                <svg class="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
                                </svg>
                            </a>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// Get Category Info
function getCategoryInfo(type) {
    const categories = {
        all: { title: 'All Events', emoji: '📜' },
        events: { title: 'Historical Events', emoji: '⚔️' },
        births: { title: 'Notable Births', emoji: '👶' },
        deaths: { title: 'Notable Deaths', emoji: '🕊️' },
        holidays: { title: 'Holidays & Observances', emoji: '🎉' }
    };
    
    return categories[type] || categories.all;
}

// Utility Functions
function formatDate(dateString) {
    if (!dateString) return '';
    
    const [month, day] = dateString.split('/');
    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    return `${monthNames[parseInt(month) - 1]} ${parseInt(day)}`;
}

function truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
}

function scrollToResults() {
    setTimeout(() => {
        resultsContainer.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }, 100);
}

// UI State Management
function showLoading() {
    hideError();
    hideEmpty();
    loadingState.classList.remove('hidden');
    resultsContainer.innerHTML = '';
}

function hideLoading() {
    loadingState.classList.add('hidden');
}

function showError() {
    hideLoading();
    hideEmpty();
    errorState.classList.remove('hidden');
    resultsContainer.innerHTML = '';
}

function hideError() {
    errorState.classList.add('hidden');
}

function showEmpty() {
    hideLoading();
    hideError();
    emptyState.classList.remove('hidden');
}

function hideEmpty() {
    emptyState.classList.add('hidden');
}

function showFilterTabs() {
    filterTabs.style.display = 'flex';
}

function hideFilterTabs() {
    filterTabs.style.display = 'none';
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && (monthSelect === document.activeElement || daySelect === document.activeElement)) {
        e.preventDefault();
        if (!searchDateBtn.disabled) {
            searchByDate();
        }
    }
});

// Auto-load today's facts on first visit
const hasVisited = localStorage.getItem('hasVisited');
if (!hasVisited) {
    setTimeout(() => {
        loadTodayFacts();
        localStorage.setItem('hasVisited', 'true');
    }, 1000);
}
