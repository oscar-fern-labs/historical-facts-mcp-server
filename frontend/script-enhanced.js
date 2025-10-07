// Historical Facts Explorer - Enhanced JavaScript
const API_BASE_URL = 'https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so';

// DOM Elements
const resultsContainer = document.getElementById('resultsContainer');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const emptyState = document.getElementById('emptyState');
const filterTabs = document.getElementById('filterTabs');
const monthSelect = document.getElementById('monthSelect');
const daySelect = document.getElementById('daySelect');
const searchDateBtn = document.getElementById('searchDateBtn');
const apiStatus = document.getElementById('apiStatus');

// State management
let currentData = null;
let currentFilter = 'all';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    populateDayOptions();
    checkAPIHealth();
    
    // Auto-load today's facts after a delay (for first-time visitors)
    setTimeout(() => {
        if (!localStorage.getItem('hasVisited')) {
            loadTodayFacts();
            localStorage.setItem('hasVisited', 'true');
        }
    }, 2000);
});

// Event Listeners
function setupEventListeners() {
    monthSelect.addEventListener('change', handleMonthChange);
    daySelect.addEventListener('change', handleDayChange);
    
    // Filter tabs event delegation
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('filter-tab')) {
            handleFilterChange(e.target.dataset.type);
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && (monthSelect === document.activeElement || daySelect === document.activeElement)) {
            e.preventDefault();
            if (!searchDateBtn.disabled) {
                searchByDate();
            }
        }
    });
}

// API Health Check
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) throw new Error('API not responding');
        
        updateAPIStatus('online');
    } catch (error) {
        console.error('API health check failed:', error);
        updateAPIStatus('offline');
    }
}

function updateAPIStatus(status) {
    const statusElement = document.querySelector('.status');
    const statusDot = document.querySelector('.status-dot');
    
    if (status === 'online') {
        apiStatus.textContent = 'API Online';
        statusElement.style.background = '#dcfce7';
        statusElement.style.color = '#166534';
        statusDot.style.background = '#22c55e';
    } else {
        apiStatus.textContent = 'API Offline';
        statusElement.style.background = '#fee2e2';
        statusElement.style.color = '#991b1b';
        statusDot.style.background = '#ef4444';
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
        showError('Failed to load today\'s historical facts. Please check your connection and try again.');
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
        showError('Failed to load random historical fact. Please check your connection and try again.');
    }
}

// Search by Date
async function searchByDate() {
    const month = monthSelect.value;
    const day = daySelect.value;
    
    if (!month || !day) {
        showNotification('Please select both month and day', 'warning');
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
        showError(`Failed to load historical facts for ${getMonthName(month)} ${day}. Please try again.`);
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
    searchDateBtn.style.opacity = isValid ? '1' : '0.5';
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
    
    if (!data.event_types || data.event_types.length === 0) {
        showEmpty();
        return;
    }
    
    const filteredEventTypes = currentFilter === 'all' 
        ? data.event_types 
        : data.event_types.filter(eventType => eventType.type === currentFilter);
    
    if (filteredEventTypes.length === 0) {
        showNoResults();
        return;
    }
    
    let html = `<div class="fade-in">`;
    
    // Date header
    html += `
        <div class="section-header">
            <div class="section-title">
                <span style="font-size: 32px;">📜</span>
                <h3>Historical Facts for ${formatDate(data.date)}</h3>
            </div>
        </div>
    `;
    
    // Event type sections
    filteredEventTypes.forEach(eventType => {
        const categoryInfo = getCategoryInfo(eventType.type);
        html += createEventTypeSection(eventType, categoryInfo);
    });
    
    html += `</div>`;
    
    resultsContainer.innerHTML = html;
}

// Display Random Fact
function displayRandomFact(data) {
    hideLoading();
    hideError();
    hideEmpty();
    
    if (!data.fact) {
        showError('No random fact available at the moment. Please try again.');
        return;
    }
    
    const html = `
        <div class="fade-in">
            <div class="section-header">
                <div class="section-title">
                    <span style="font-size: 32px;">🎲</span>
                    <h3>Random Historical Discovery</h3>
                </div>
            </div>
            <div style="background: #f8fafc; border-radius: 15px; padding: 20px; margin-bottom: 20px; text-align: center;">
                <p style="color: #64748b; font-weight: 500;">From ${formatDate(data.date)}</p>
            </div>
            <div class="fact-grid">
                ${createFactCard(data.fact)}
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = html;
}

// Create Event Type Section
function createEventTypeSection(eventType, categoryInfo) {
    let html = `
        <div style="margin-bottom: 50px;">
            <div class="section-header">
                <div class="section-title">
                    <span style="font-size: 28px;">${categoryInfo.emoji}</span>
                    <h3>${categoryInfo.title}</h3>
                </div>
                <div class="section-count">${eventType.count} ${eventType.count === 1 ? 'item' : 'items'}</div>
            </div>
            <div class="fact-grid">
    `;
    
    // Show first 10 events
    const eventsToShow = eventType.events.slice(0, 10);
    eventsToShow.forEach(event => {
        html += createFactCard(event);
    });
    
    html += '</div>';
    
    // Show "more" indicator if there are more events
    if (eventType.events.length > 10) {
        html += `
            <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8fafc; border-radius: 15px;">
                <p style="color: #64748b; font-weight: 500;">
                    ... and ${eventType.events.length - 10} more ${categoryInfo.title.toLowerCase()}
                </p>
            </div>
        `;
    }
    
    html += '</div>';
    return html;
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
            <div class="fact-header">
                ${thumbnail ? `
                    <img src="${thumbnail}" alt="${title || 'Historical fact'}" 
                         class="fact-thumbnail" loading="lazy" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="fact-thumbnail" style="display: none;">📚</div>
                ` : `
                    <div class="fact-thumbnail">📚</div>
                `}
                <div class="fact-content">
                    <span class="year-badge">${event.year}</span>
                    <p class="fact-text">${event.text}</p>
                    ${extract ? `
                        <p style="color: #64748b; font-size: 14px; line-height: 1.5; margin-bottom: 16px;">
                            ${truncateText(extract, 150)}
                        </p>
                    ` : ''}
                    ${url ? `
                        <a href="${url}" target="_blank" rel="noopener noreferrer" class="wikipedia-link">
                            📖 Read more on Wikipedia
                            <span style="font-size: 12px;">↗</span>
                        </a>
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

function getMonthName(month) {
    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    return monthNames[parseInt(month) - 1] || '';
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
    resultsContainer.querySelector('.fade-in')?.remove();
}

function hideLoading() {
    loadingState.classList.add('hidden');
}

function showError(message = 'An error occurred. Please try again.') {
    hideLoading();
    hideEmpty();
    errorState.classList.remove('hidden');
    errorState.querySelector('p').textContent = message;
    resultsContainer.querySelector('.fade-in')?.remove();
}

function hideError() {
    errorState.classList.add('hidden');
}

function showEmpty() {
    hideLoading();
    hideError();
    emptyState.classList.remove('hidden');
    resultsContainer.querySelector('.fade-in')?.remove();
}

function hideEmpty() {
    emptyState.classList.add('hidden');
}

function showNoResults() {
    hideLoading();
    hideError();
    hideEmpty();
    
    const html = `
        <div class="empty fade-in">
            <h3>🔍 No Results Found</h3>
            <p>No ${currentFilter === 'all' ? 'events' : getCategoryInfo(currentFilter).title.toLowerCase()} found for this date.</p>
            <button class="btn" onclick="handleFilterChange('all')" style="margin-top: 20px; max-width: 200px;">
                Show All Events
            </button>
        </div>
    `;
    
    resultsContainer.innerHTML = html;
}

function showFilterTabs() {
    filterTabs.classList.remove('hidden');
}

function hideFilterTabs() {
    filterTabs.classList.add('hidden');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        padding: 16px 24px;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        max-width: 400px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        info: '#3b82f6',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
