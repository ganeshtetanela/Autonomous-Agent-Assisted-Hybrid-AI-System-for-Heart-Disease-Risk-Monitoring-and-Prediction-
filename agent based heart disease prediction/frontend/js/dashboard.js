let vitalsChart, predictionChart;
let updateInterval;
let ecgCtx;
let ecgData = new Array(150).fill(0);

// -- TAB MANAGEMENT --
function switchTab(tabId) {
    // 1. Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));

    // 2. Reset all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('text-cyan-400', 'border-cyan-400');
        btn.classList.add('text-slate-400', 'border-transparent');
    });

    // 3. Show target tab
    document.getElementById(`tab-${tabId}`).classList.remove('hidden');

    // 4. Highlight target button
    const activeBtn = document.getElementById(`tab-btn-${tabId}`);
    activeBtn.classList.remove('text-slate-400', 'border-transparent');
    activeBtn.classList.add('text-cyan-400', 'border-cyan-400');
}

// UI State Management
function showLogin() {
    const container = document.getElementById('auth-view');
    const savedUser = localStorage.getItem('remembered_user') || '';
    container.innerHTML = `
        <div class="glass p-8 rounded-2xl space-y-6 animate-fade-in neon-border-primary bg-[#1e293b]/80">
            <h2 class="text-2xl font-bold text-center glow-text text-white">HeartGuard Login</h2>
            <form id="login-form" class="space-y-4">
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Username</label>
                    <input type="text" id="username" value="${savedUser}" class="w-full bg-[#0f172a] border border-slate-700 rounded-lg px-4 py-2 focus:border-cyan-500 outline-none text-white transition-colors" required>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Password</label>
                    <input type="password" id="password" class="w-full bg-[#0f172a] border border-slate-700 rounded-lg px-4 py-2 focus:border-cyan-500 outline-none text-white transition-colors" required>
                </div>
                <div class="flex items-center gap-2">
                    <input type="checkbox" id="remember-me" ${savedUser ? 'checked' : ''} class="w-4 h-4 accent-cyan-500 bg-slate-800 border-slate-600 rounded">
                    <label for="remember-me" class="text-xs text-slate-400">Remember my username</label>
                </div>
                <button type="submit" class="w-full bg-cyan-600 py-3 rounded-lg font-bold hover:bg-cyan-500 transition shadow-lg shadow-cyan-500/20 uppercase tracking-widest text-sm text-white">Sign In</button>
            </form>
            <p class="text-center text-sm text-slate-500">New Researcher? <a href="#" onclick="showRegister()" class="text-cyan-400 hover:text-cyan-300 font-bold">Create Account</a></p>
        </div>
    `;

    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('remember-me').checked;

        try {
            // In a real app we'd use form-data, but for simplicity here we assume JSON or handled by api.js
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (response.ok) {
                api.setToken(result.access_token);
                localStorage.setItem('role', result.role);
                localStorage.setItem('username', username);

                if (rememberMe) {
                    localStorage.setItem('remembered_user', username);
                } else {
                    localStorage.removeItem('remembered_user');
                }

                console.log("Login successful, initializing dashboard for:", username);
                initDashboard(username);
            } else {
                alert(result.detail);
            }
        } catch (err) {
            alert('Login failed');
        }
    });

    document.getElementById('auth-view').classList.remove('hidden');
    document.getElementById('dashboard-view').classList.add('hidden');

    // Hide nav items
    document.getElementById('tab-nav').classList.add('hidden');
}

function showRegister() {
    const container = document.getElementById('auth-view');
    container.innerHTML = `
        <div class="glass p-8 rounded-2xl space-y-6 animate-fade-in neon-border-primary bg-[#1e293b]/80">
            <h2 class="text-2xl font-bold text-center glow-text text-white">Researcher Registry</h2>
            <form id="register-form" class="space-y-4">
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Full Name</label>
                    <input type="text" id="fullname" class="w-full bg-[#0f172a] border border-slate-700 rounded-lg px-4 py-2 focus:border-cyan-500 outline-none text-white transition-colors" required>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Username</label>
                    <input type="text" id="reg-username" class="w-full bg-[#0f172a] border border-slate-700 rounded-lg px-4 py-2 focus:border-cyan-500 outline-none text-white transition-colors" required>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Password</label>
                    <input type="password" id="reg-password" class="w-full bg-[#0f172a] border border-slate-700 rounded-lg px-4 py-2 focus:border-cyan-500 outline-none text-white transition-colors" required>
                </div>
                <button type="submit" class="w-full bg-cyan-600 py-3 rounded-lg font-bold hover:bg-cyan-500 transition shadow-lg shadow-cyan-500/20 uppercase tracking-widest text-sm text-white">Register Account</button>
            </form>
            <p class="text-center text-sm text-slate-500">Already a researcher? <a href="#" onclick="showLogin()" class="text-cyan-400 hover:text-cyan-300 font-bold">Sign In</a></p>
        </div>
    `;

    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            username: document.getElementById('reg-username').value,
            password: document.getElementById('reg-password').value,
            full_name: document.getElementById('fullname').value,
            role: 'patient'
        };
        try {
            await api.request('/auth/register', 'POST', data);
            alert('Registration successful! Please login.');
            showLogin();
        } catch (err) { alert(err.message); }
    });
}

function initDashboard(username) {
    document.getElementById('auth-view').classList.add('hidden');
    document.getElementById('dashboard-view').classList.remove('hidden');
    document.getElementById('auth-nav').classList.add('hidden');
    document.getElementById('user-nav').classList.remove('hidden');
    document.getElementById('tab-nav').classList.remove('hidden'); // Show Tabs
    document.getElementById('user-name').textContent = username;

    initCharts();
    startVitalSimulation();
    switchTab('live'); // Default to live tab
}

function logout() {
    api.logout();
    location.reload();
}

// Chart Initializations
function initCharts() {
    const ctxVitals = document.getElementById('vitalsChart').getContext('2d');
    vitalsChart = new Chart(ctxVitals, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Heart Rate',
                    borderColor: '#06b6d4', // Cyan
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    data: [],
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: 'Systolic BP',
                    borderColor: '#10b981', // Emerald
                    data: [],
                    borderDash: [5, 5],
                    borderWidth: 1.5,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { family: 'Outfit', size: 10 } } }
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#475569', font: { size: 9 } } },
                y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#475569', font: { size: 9 } } }
            }
        }
    });

    const ctxPred = document.getElementById('predictionChart').getContext('2d');
    predictionChart = new Chart(ctxPred, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Risk Score %',
                backgroundColor: 'rgba(6, 182, 212, 0.6)',
                borderColor: '#06b6d4',
                borderWidth: 1,
                data: [],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#475569', font: { size: 9 } } },
                x: { grid: { display: false }, ticks: { color: '#475569', font: { size: 9 } } }
            }
        }
    });
}

// Reviewer Test Suite Logic
async function runTestCase(type) {
    let vitalData;
    switch (type) {
        case 'healthy':
            vitalData = { heart_rate: 72, blood_pressure_sys: 118, blood_pressure_dia: 78, ecg_signal: 0.2, activity_level: 'rest' };
            break;
        case 'anomaly':
            vitalData = { heart_rate: 105, blood_pressure_sys: 145, blood_pressure_dia: 95, ecg_signal: -0.4, activity_level: 'moderate' };
            break;
        case 'critical':
            vitalData = { heart_rate: 140, blood_pressure_sys: 185, blood_pressure_dia: 110, ecg_signal: -1.2, activity_level: 'high' };
            break;
    }
    console.log(`RUNNING TEST CASE [${type.toUpperCase()}]:`, vitalData);
    try {
        const result = await api.request('/health/stream-vitals', 'POST', vitalData);
        updateUI(vitalData, result);
        refreshHistory();

        const logBox = document.getElementById('agent-logs');
        const caseLog = document.createElement('div');
        caseLog.textContent = `>> Running Test: ${type.toUpperCase()}`;
        caseLog.className = 'text-cyan-400 border-l border-cyan-500 pl-2 mt-1';
        logBox.prepend(caseLog);

    } catch (err) { console.error(err); }
}

async function triggerAnomaly() {
    // Fast-fill 11 vitals so the 12-vital window for LSTM prediction is met instantly
    for(let i=0; i<11; i++) {
        await api.request('/health/stream-vitals', 'POST', {
            heart_rate: 72, blood_pressure_sys: 118, blood_pressure_dia: 78, ecg_signal: 0.2, activity_level: 'rest'
        });
    }
    runTestCase('anomaly');
}

// Real-time Simulation & API Polling
function startVitalSimulation() {
    updateInterval = setInterval(async () => {
        // 1. Generate local mock vital to send (Simulation of wearable)
        const mockVital = {
            heart_rate: 70 + Math.random() * 10,
            blood_pressure_sys: 110 + Math.random() * 20,
            blood_pressure_dia: 70 + Math.random() * 10,
            ecg_signal: Math.sin(Date.now() / 1000),
            activity_level: 'low'
        };

        try {
            // 2. Stream to Backend
            const result = await api.request('/health/stream-vitals', 'POST', mockVital);

            // 3. Update UI based on Response
            updateUI(mockVital, result);

            // 4. Periodically fetch history
            refreshHistory();
        } catch (err) {
            console.error(err);
        }
    }, 5000);
}

function drawECG(signalVal) {
    const canvas = document.getElementById('ecgWaveform');
    if (!canvas) return;
    if (!ecgCtx) {
        // High DPI canvas setup
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * 2;
        canvas.height = rect.height * 2;
        ecgCtx = canvas.getContext('2d');
        ecgCtx.scale(2, 2);
    }

    ecgData.push(signalVal);
    ecgData.shift();

    const w = canvas.width / 2;
    const h = canvas.height / 2;

    ecgCtx.clearRect(0, 0, w, h);
    
    // Draw Grid
    ecgCtx.strokeStyle = 'rgba(16, 185, 129, 0.1)';
    ecgCtx.lineWidth = 0.5;
    for(let i=0; i<w; i+=10) { ecgCtx.beginPath(); ecgCtx.moveTo(i, 0); ecgCtx.lineTo(i, h); ecgCtx.stroke(); }
    for(let i=0; i<h; i+=10) { ecgCtx.beginPath(); ecgCtx.moveTo(0, i); ecgCtx.lineTo(w, i); ecgCtx.stroke(); }

    ecgCtx.beginPath();
    ecgCtx.strokeStyle = '#10b981'; // Emerald
    ecgCtx.lineWidth = 1.5;
    ecgCtx.lineJoin = 'round';

    const step = w / ecgData.length;
    for (let i = 0; i < ecgData.length; i++) {
        const x = i * step;
        // Signal is from approx -2 to 2. Map to canvas height (center is h/2)
        const y = (h / 2) - (ecgData[i] * (h / 4));
        if (i === 0) ecgCtx.moveTo(x, y);
        else ecgCtx.lineTo(x, y);
    }
    ecgCtx.stroke();
    
    // Draw leading edge dot
    const lastX = (ecgData.length - 1) * step;
    const lastY = (h / 2) - (ecgData[ecgData.length - 1] * (h / 4));
    ecgCtx.beginPath();
    ecgCtx.fillStyle = '#10b981';
    ecgCtx.arc(lastX, lastY, 2, 0, Math.PI * 2);
    ecgCtx.fill();
}

function updateUI(vitals, apiResponse) {
    drawECG(vitals.ecg_signal);
    
    // Update Stats
    document.getElementById('stat-hr').innerHTML = `${Math.round(vitals.heart_rate)} <small class="text-xs text-slate-500">BPM</small>`;
    document.getElementById('stat-bp').textContent = `${Math.round(vitals.blood_pressure_sys)}/${Math.round(vitals.blood_pressure_dia)}`;
    
    if (document.getElementById('stat-act')) {
        document.getElementById('stat-act').textContent = vitals.activity_level.toUpperCase();
        if(vitals.activity_level === 'high') document.getElementById('stat-act').className = 'text-sm font-bold text-rose-500 block text-right';
        else document.getElementById('stat-act').className = 'text-sm font-bold text-amber-500 block text-right';
    }

    // Update Heart Animation Speed
    const duration = 60 / vitals.heart_rate;

    // Main Heart Image (Updated from SVG)
    const heartImg = document.getElementById('cyber-heart-img');
    if (heartImg) {
        heartImg.style.animationDuration = `${duration}s`;
    }

    // Shockwave Rings
    const rings = document.querySelectorAll('.shockwave-ring');
    rings.forEach(ring => {
        ring.style.animationDuration = `${duration}s`;
    });

    // Update Agent Logs (Terminal Style)
    const logBox = document.getElementById('agent-logs');
    const decision = apiResponse.agent_decision;
    
    const timeStr = new Date().toLocaleTimeString([], { hour12: false });
    const isAnomaly = decision.trigger_prediction;
    
    // Create new node
    const logEntry = document.createElement('div');
    logEntry.className = isAnomaly ? 'text-rose-400 font-bold bg-rose-950/30 px-1 rounded inline-block w-full border-l border-rose-500' : 'text-cyan-600/70';
    
    const prefix = isAnomaly ? `<span class="text-rose-500">[CRIT]</span>` : `<span class="text-slate-500">[SYS]</span>`;
    const message = isAnomaly ? ` ANOMALY DETECTED. Dispatching prediction pipeline...` : ` ${timeStr} - Stream normal.`;
    
    logEntry.innerHTML = `${prefix}${message}`;
    logBox.appendChild(logEntry);
    
    // Auto scroll to bottom
    if (logBox.children.length > 50) {
        logBox.removeChild(logBox.firstChild);
    }
    logBox.scrollTop = logBox.scrollHeight;

    // Update Agent Health Score
    if (decision.health_score !== undefined) {
        const scoreVal = document.getElementById('health-score-val');
        scoreVal.textContent = decision.health_score;
        // Dynamic color for health score
        if (decision.health_score > 80) scoreVal.className = 'text-4xl font-black text-emerald-400';
        else if (decision.health_score > 50) scoreVal.className = 'text-4xl font-black text-amber-400';
        else scoreVal.className = 'text-4xl font-black text-rose-500';
    }

    // Update Agent Trend
    if (decision.trends && decision.trends.length > 0) {
        const trendBox = document.getElementById('agent-trend');
        trendBox.textContent = `⚠️ Trend: ${decision.trends[0]}`;
        trendBox.classList.remove('hidden');
    } else {
        document.getElementById('agent-trend').textContent = '';
    }

    // Update charts
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    vitalsChart.data.labels.push(time);
    vitalsChart.data.datasets[0].data.push(vitals.heart_rate);
    vitalsChart.data.datasets[1].data.push(vitals.blood_pressure_sys);
    if (vitalsChart.data.labels.length > 20) {
        vitalsChart.data.labels.shift();
        vitalsChart.data.datasets.forEach(d => d.data.shift());
    }
    vitalsChart.update();

    // Check for Critical State to Trigger Modal Overlay
    // Only trigger if high severity is continuously observed, or immediate critical threshold
    if ((vitals.heart_rate > 100 || vitals.blood_pressure_sys > 140) && !sessionStorage.getItem('modal_shown_recently')) {
        showSuggestionModal(vitals);
        // Prevent spamming the modal every 5 seconds
        sessionStorage.setItem('modal_shown_recently', 'true');
        setTimeout(() => sessionStorage.removeItem('modal_shown_recently'), 60000); // Allow again after 60s
    }

    // Update Prediction UI if agent triggered it
    if (apiResponse.prediction) {
        const pred = apiResponse.prediction;
        const score = Math.round(pred.risk_score * 100);
        document.getElementById('risk-score').textContent = `${score}%`;

        const catElem = document.getElementById('risk-category');
        catElem.textContent = pred.risk_category;
        catElem.className = `inline-block px-3 py-1 rounded-full text-xs font-bold uppercase border ${getRiskColor(pred.risk_category)}`;

        const gradient = document.getElementById('risk-gradient');
        gradient.className = `absolute inset-0 opacity-10 transition-all duration-500 ${pred.risk_category.toLowerCase()}`;
        
        // Also trigger modal if prediction says High Risk
        if (pred.risk_category === 'High' && !sessionStorage.getItem('modal_shown_recently')) {
             showSuggestionModal(vitals, pred.xai_explanation);
             sessionStorage.setItem('modal_shown_recently', 'true');
             setTimeout(() => sessionStorage.removeItem('modal_shown_recently'), 60000);
        }


        // Explainability Deep-Dive (SHAP)
        const xai = pred.xai_explanation;
        const topFeats = Object.entries(xai)
            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
            .slice(0, 5);

        let shapHtml = '<div class="mt-4 border-t border-slate-800 pt-4"><h4 class="text-xs font-bold text-cyan-400 mb-2 uppercase">Feature Impact Breakdown</h4><div class="space-y-3">';
        topFeats.forEach(([feature, val]) => {
            const width = Math.min(100, Math.abs(val) * 700); // Scale for visual enhancement
            const color = val > 0 ? 'bg-gradient-to-r from-rose-500/50 to-rose-500' : 'bg-gradient-to-r from-emerald-500/50 to-emerald-500';
            const labelCol = val > 0 ? 'text-rose-400' : 'text-emerald-400';
            shapHtml += `
                <div class="text-[10px] space-y-1">
                    <div class="flex justify-between font-mono"><span class="${labelCol}">${feature.toUpperCase()}</span> <span class="${labelCol}">${val > 0 ? '+' : ''}${val.toFixed(3)}</span></div>
                    <div class="h-1.5 bg-slate-800/80 rounded-full overflow-hidden border border-slate-700/30">
                        <div class="${color} h-full rounded-full shadow-[0_0_5px_currentColor]" style="width: ${width}%"></div>
                    </div>
                </div>
            `;
        });
        shapHtml += '</div><p class="text-[9px] text-slate-500 mt-3 pt-2 border-t border-slate-700/30 italic">* Features pulling the model towards higher risk are marked in red.</p></div>';

        document.getElementById('explainability-view').innerHTML = `
            <div class="space-y-3 text-sm animate-fade-in pr-2">
                <div class="flex justify-between items-center mb-4 border-b border-slate-700 pb-2">
                    <span class="text-cyan-400 font-bold uppercase text-[10px] tracking-widest">Full Hybrid AI Analysis</span>
                    <span class="font-mono text-[9px] bg-slate-800 px-2 py-0.5 rounded text-slate-400 border border-slate-700">${new Date().toLocaleTimeString()}</span>
                </div>
                
                <div class="bg-indigo-950/20 p-3 rounded-lg border border-indigo-500/20 mb-3 space-y-2">
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-indigo-300 font-semibold tracking-wide">Clinical Ensemble (RF/XGB)</span> 
                        <span class="text-white font-mono bg-indigo-500/20 px-1.5 rounded">${(pred.static_component * 100).toFixed(1)}%</span>
                    </div>
                    <div class="w-full h-1 bg-slate-800 rounded-full overflow-hidden"><div class="bg-indigo-500 h-full" style="width: ${(pred.static_component * 100)}%"></div></div>
                    
                    <div class="flex justify-between items-center text-xs mt-2">
                        <span class="text-cyan-300 font-semibold tracking-wide">Temporal Sequence (LSTM)</span> 
                        <span class="text-white font-mono bg-cyan-500/20 px-1.5 rounded">${(pred.temporal_component * 100).toFixed(1)}%</span>
                    </div>
                     <div class="w-full h-1 bg-slate-800 rounded-full overflow-hidden"><div class="bg-cyan-500 h-full" style="width: ${(pred.temporal_component * 100)}%"></div></div>

                    <div class="flex justify-between items-center text-xs mt-2">
                        <span class="text-emerald-300 font-semibold tracking-wide">Deep ECG Vision (CNN)</span> 
                        <span class="text-white font-mono bg-emerald-500/20 px-1.5 rounded">${(pred.ecg_cnn_component * 100).toFixed(1)}%</span>
                    </div>
                     <div class="w-full h-1 bg-slate-800 rounded-full overflow-hidden"><div class="bg-emerald-500 h-full" style="width: ${(pred.ecg_cnn_component * 100)}%"></div></div>
                </div>

                <div class="p-3 bg-slate-900/80 rounded-lg text-xs italic text-slate-300 border border-amber-500/20 relative">
                    <div class="absolute -top-2 -left-2 bg-amber-500 text-black text-[8px] font-black uppercase px-2 py-0.5 rounded shadow-lg">Agent Rationale</div>
                    <p class="mt-1 flex items-start gap-2">
                       <svg class="w-4 h-4 text-amber-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                       ${apiResponse.agent_decision.reasons.join(' ')}
                    </p>
                </div>
                ${shapHtml}
            </div>
        `;
    } else {
        // Only show "Monitoring" if the box is currently empty or just has a previous "Monitoring" message
        const currentContent = document.getElementById('explainability-view');
        if (!currentContent.querySelector('.text-cyan-400')) { // Check if a prediction is NOT already there
            currentContent.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full text-slate-500 py-10 opacity-60 bg-slate-800/20 rounded-xl border border-dashed border-slate-700">
                    <svg class="w-10 h-10 mb-3 animate-pulse text-emerald-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <p class="text-[11px] text-center italic leading-relaxed">Agent Status: <span class="text-emerald-400 font-bold not-italic"> ACTIVE MONITORING</span><br>Last check: Continuous Vitals are STABLE.<br>Hybrid AI is standing by.</p>
                </div>
            `;
        }
    }
}

async function refreshHistory() {
    try {
        const history = await api.request('/health/prediction-history');
        if (history && history.length > 0) {
            predictionChart.data.labels = history.slice(0, 15).map(h => new Date(h.timestamp).toLocaleTimeString()).reverse();
            predictionChart.data.datasets[0].data = history.slice(0, 15).map(h => h.risk_score * 100).reverse();
            predictionChart.update();
        }

        const alerts = await api.request('/health/alerts');
        const alertList = document.getElementById('alerts-list');
        if (alerts.length > 0) {
            alertList.innerHTML = alerts.map(a => `
                <div class="flex items-start gap-4 p-4 bg-rose-950/20 border-l-2 border-l-rose-500 border-t border-r border-b border-rose-900/40 rounded-r-xl animate-fade-in mb-2 shadow-lg shadow-black/20">
                    <div class="bg-rose-500/20 p-2 rounded-lg shrink-0">
                       <svg class="w-4 h-4 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    </div>
                    <div>
                        <p class="text-[13px] text-slate-200 font-semibold leading-snug mb-1">${a.message}</p>
                        <div class="flex items-center gap-2">
                           <span class="text-[10px] bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded font-mono border border-rose-500/20">CRITICAL EVENT</span>
                           <span class="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                               <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                               ${new Date(a.timestamp).toLocaleString()}
                           </span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (err) { }
}

function showSuggestionModal(vitals, xai) {
    document.getElementById('modal-bp').textContent = `${Math.round(vitals.blood_pressure_sys)}/${Math.round(vitals.blood_pressure_dia)}`;
    document.getElementById('modal-hr').textContent = Math.round(vitals.heart_rate);
    
    if (xai) {
        // Find the top feature driving the risk (largest positive SHAP value)
        const topFeats = Object.entries(xai).sort((a,b) => b[1] - a[1]);
        const mainDriver = topFeats.length > 0 ? topFeats[0][0] : '';
        const list = document.getElementById('suggestion-list');
        
        if (list && mainDriver) {
            let newAction = "";
            let driverLower = mainDriver.toLowerCase();
            
            if (driverLower.includes('bp') || driverLower.includes('trestbps') || driverLower.includes('blood_pressure')) {
                newAction = `<li class="flex gap-2 items-start bg-rose-950/40 p-2 rounded -mx-2 mb-2 border border-rose-900"><span class="text-rose-500 mt-0.5 animate-pulse">⚡</span> <span class="text-rose-200"><strong>Administer BP Protocol:</strong> AI has identified extreme blood pressure as the primary threshold driver. Consider immediate pharmacological intervention.</span></li>`;
            } else if (driverLower.includes('hr') || driverLower.includes('heart_rate') || driverLower.includes('thalach')) {
                newAction = `<li class="flex gap-2 items-start bg-rose-950/40 p-2 rounded -mx-2 mb-2 border border-rose-900"><span class="text-rose-500 mt-0.5 animate-pulse">⚡</span> <span class="text-rose-200"><strong>Heart Rate Protocol:</strong> Tachycardia detected as primary driver. Prepare beta-blockers or vagal maneuvers.</span></li>`;
            } else if (driverLower.includes('ecg') || driverLower.includes('restecg')) {
                newAction = `<li class="flex gap-2 items-start bg-amber-950/40 p-2 rounded -mx-2 mb-2 border border-amber-900"><span class="text-amber-500 mt-0.5 animate-pulse">⚡</span> <span class="text-amber-200"><strong>ECG Anomaly:</strong> Irregular wavefront or injury pattern detected in continuous stream. Prepare defibrillator unit.</span></li>`;
            } else {
                 newAction = `<li class="flex gap-2 items-start bg-cyan-950/40 p-2 rounded -mx-2 mb-2 border border-cyan-900"><span class="text-cyan-500 mt-0.5 animate-pulse">⚡</span> <span class="text-cyan-200"><strong>Clinical Override:</strong> AI flags <span class="uppercase font-mono">${mainDriver}</span> as the highest risk factor. Review patient clinical history immediately.</span></li>`;
            }
            
            const defaultList = `
                <li class="flex gap-2 items-start"><span class="text-rose-500">•</span> <strong>Rest Immediately:</strong> Stop current activities and sit or lie down in a comfortable position.</li>
                <li class="flex gap-2 items-start"><span class="text-rose-500">•</span> <strong>Focused Breathing:</strong> Take slow, deep breaths. Inhale for 4 seconds, exhale for 6 seconds.</li>
                <li class="flex gap-2 items-start"><span class="text-rose-500">•</span> <strong>Medication:</strong> If prescribed emergency medication, take it now.</li>
                <li class="flex gap-2 items-start"><span class="text-rose-500">•</span> <strong>Seek Help:</strong> Call emergency services immediately.</li>
            `;
            list.innerHTML = newAction + defaultList;
        }
    }

    const modal = document.getElementById('suggestion-modal');
    modal.classList.remove('hidden');
}

function closeSuggestionModal() {
    const modal = document.getElementById('suggestion-modal');
    modal.classList.add('hidden');
}

function getRiskColor(cat) {
    if (cat === "High") return "bg-rose-950/50 text-rose-500 border-rose-500/50";
    if (cat === "Medium") return "bg-amber-950/50 text-amber-500 border-amber-500/50";
    return "bg-emerald-950/50 text-emerald-500 border-emerald-500/50";
}

// Initial View
window.onload = () => {
    if (api.token) {
        initDashboard(localStorage.getItem('username') || 'Patient');
    } else {
        showLogin();
    }
};

window.addEventListener('unauthorized', () => {
    logout();
});
