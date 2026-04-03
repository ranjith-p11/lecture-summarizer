// dashboard.js – All dashboard UI logic
// ─────────────────────────────────────────────────────────────────────────────

// ── State ──────────────────────────────────────────────────────────────────
let currentUser      = null;
let currentTranscript = '';
let currentSourceType = 'text';
let currentSourceName = '';
let selectedFile     = null;
let lengthSettings   = { upload: 'medium', text: 'medium', url: 'medium', result: 'medium' };

// ── Auth Guard ─────────────────────────────────────────────────────────────
firebase.auth().onAuthStateChanged((user) => {
  if (!user) {
    window.location.href = '/';
    return;
  }
  currentUser = user;
  initDashboard(user);
});

function initDashboard(user) {
  // Set greeting
  const hour = new Date().getHours();
  const part = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
  document.getElementById('greeting-part').textContent = part;

  const displayName = user.displayName || user.email.split('@')[0];
  document.getElementById('greeting-name').textContent = displayName;

  // Date string
  const now = new Date();
  document.getElementById('greeting-date').textContent =
    now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  // Sidebar user info
  document.getElementById('sidebar-user-name').textContent = user.displayName || 'User';
  document.getElementById('sidebar-user-email').textContent = user.email || '';

  // Avatar initials
  const initials = (user.displayName || user.email || '?')
    .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
  document.getElementById('user-avatar-initials').textContent = initials;
}

// ── Panel switching ────────────────────────────────────────────────────────
function switchPanel(name) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  document.getElementById(`panel-${name}`).classList.add('active');
  document.getElementById(`nav-${name}`).classList.add('active');

  if (name === 'records') loadRecords();
}

// ── Modal helpers ──────────────────────────────────────────────────────────
function openModal(id) {
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
  document.body.style.overflow = '';
}

// Close on backdrop click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal(overlay.id);
  });
});

// Close on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(o => closeModal(o.id));
  }
});

// ── Length selector ────────────────────────────────────────────────────────
function setLength(modalType, len) {
  lengthSettings[modalType] = len;
  ['short', 'medium', 'long'].forEach(l => {
    const btn = document.getElementById(`${modalType}-len-${l}`);
    if (btn) btn.classList.toggle('active', l === len);
  });
}

function resummarize(len) {
  lengthSettings['result'] = len;
  ['short', 'medium', 'long'].forEach(l => {
    const btn = document.getElementById(`res-len-${l}`);
    if (btn) btn.classList.toggle('active', l === len);
  });
  document.getElementById('btn-resummarize').disabled = !currentTranscript;
}

// ── Spinner / Loading ──────────────────────────────────────────────────────
function showSpinner(label = 'Processing…', step = '') {
  document.getElementById('spinner-label').textContent = label;
  document.getElementById('spinner-step').textContent  = step;
  document.getElementById('spinner-overlay').classList.add('visible');
}
function updateSpinner(label, step = '') {
  document.getElementById('spinner-label').textContent = label;
  document.getElementById('spinner-step').textContent  = step;
}
function hideSpinner() {
  document.getElementById('spinner-overlay').classList.remove('visible');
}

// ── Toast ──────────────────────────────────────────────────────────────────
function showToast(msg, type = 'info', durationMs = 4000) {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type]}</span><span class="toast-msg">${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), durationMs);
}

// ── Copy text ──────────────────────────────────────────────────────────────
function copyText(elementId) {
  const el = document.getElementById(elementId);
  const text = el.innerText || el.textContent;
  if (!text.trim()) return;
  navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard!', 'success', 2000));
}

// ── File drag & drop ──────────────────────────────────────────────────────
function handleDragOver(e) {
  e.preventDefault();
  document.getElementById('upload-drop-zone').classList.add('drag-over');
}
function handleDragLeave(e) {
  document.getElementById('upload-drop-zone').classList.remove('drag-over');
}
function handleDrop(e) {
  e.preventDefault();
  document.getElementById('upload-drop-zone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) handleFileSelect(file);
}
function handleFileSelect(file) {
  if (!file) return;
  selectedFile = file;
  document.getElementById('upload-filename').textContent = `📎 ${file.name}`;
  document.getElementById('btn-submit-upload').disabled = false;
}

// ── Submit: File Upload ────────────────────────────────────────────────────
async function submitUpload() {
  if (!selectedFile) return;
  const btn = document.getElementById('btn-submit-upload');
  btn.disabled = true;
  closeModal('modal-upload');

  try {
    showSpinner('Transcribing audio…', 'This may take a while for large files');
    const transcribeRes = await apiTranscribeFile(selectedFile);
    currentTranscript  = transcribeRes.transcript;
    currentSourceType  = 'file';
    currentSourceName  = selectedFile.name;
    displayTranscript(currentTranscript);

    updateSpinner('Generating summary…', 'Extracting key points with LSA');
    const summarizeRes = await apiSummarize(
      currentTranscript,
      lengthSettings['upload'],
      currentSourceType,
      currentSourceName
    );
    displaySummary(summarizeRes.summary);
    displayKeyPoints(summarizeRes.key_points);
    showToast('Done! Transcript and summary ready.', 'success');
    lengthSettings['result'] = lengthSettings['upload'];
    syncResultLengthBtns();

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    hideSpinner();
    btn.disabled = false;
    selectedFile = null;
    document.getElementById('upload-filename').textContent = '';
  }
}

// ── Submit: Paste Text ────────────────────────────────────────────────────
async function submitText() {
  const text = document.getElementById('paste-text').value.trim();
  if (!text) { showToast('Please paste some text first.', 'error'); return; }

  const btn = document.getElementById('btn-submit-text');
  btn.disabled = true;
  closeModal('modal-text');

  try {
    showSpinner('Processing text…', 'Running LSA summarization');
    const transcribeRes = await apiTranscribeText(text);
    currentTranscript  = transcribeRes.transcript;
    currentSourceType  = 'text';
    currentSourceName  = 'Pasted text';
    displayTranscript(currentTranscript);

    updateSpinner('Generating summary…', 'Extracting key points');
    const summarizeRes = await apiSummarize(
      currentTranscript,
      lengthSettings['text'],
      currentSourceType,
      currentSourceName
    );
    displaySummary(summarizeRes.summary);
    displayKeyPoints(summarizeRes.key_points);
    showToast('Summary generated!', 'success');
    lengthSettings['result'] = lengthSettings['text'];
    syncResultLengthBtns();

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    hideSpinner();
    btn.disabled = false;
  }
}

// ── Submit: URL Transcribe ─────────────────────────────────────────────────
async function submitUrl() {
  const url = document.getElementById('url-input').value.trim();
  if (!url) { showToast('Please enter a URL.', 'error'); return; }

  const btn = document.getElementById('btn-submit-url');
  btn.disabled = true;
  closeModal('modal-url');

  try {
    showSpinner('Downloading audio…', 'Fetching media from URL');
    const transcribeRes = await apiTranscribeUrl(url);
    currentTranscript  = transcribeRes.transcript;
    currentSourceType  = 'url';
    currentSourceName  = url;
    displayTranscript(currentTranscript);

    updateSpinner('Generating summary…', 'Extracting key points with LSA');
    const summarizeRes = await apiSummarize(
      currentTranscript,
      lengthSettings['url'],
      currentSourceType,
      currentSourceName
    );
    displaySummary(summarizeRes.summary);
    displayKeyPoints(summarizeRes.key_points);
    showToast('Transcription and summary complete!', 'success');
    lengthSettings['result'] = lengthSettings['url'];
    syncResultLengthBtns();

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    hideSpinner();
    btn.disabled = false;
  }
}

// ── Re-summarize ───────────────────────────────────────────────────────────
async function doResummarize() {
  if (!currentTranscript) return;
  const btn = document.getElementById('btn-resummarize');
  btn.disabled = true;

  try {
    showSpinner('Re-summarizing…', `Length: ${lengthSettings['result']}`);
    const res = await apiSummarize(
      currentTranscript,
      lengthSettings['result'],
      currentSourceType,
      currentSourceName
    );
    displaySummary(res.summary);
    displayKeyPoints(res.key_points);
    showToast('Summary updated!', 'success');
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    hideSpinner();
    btn.disabled = false;
  }
}

function syncResultLengthBtns() {
  ['short', 'medium', 'long'].forEach(l => {
    const btn = document.getElementById(`res-len-${l}`);
    if (btn) btn.classList.toggle('active', l === lengthSettings['result']);
  });
}

// ── Display helpers ────────────────────────────────────────────────────────
function displayTranscript(text) {
  const el = document.getElementById('transcript-output');
  el.textContent = text;
  document.getElementById('output-section').classList.add('visible');
  document.getElementById('btn-resummarize').disabled = false;

  // Scroll to output
  document.getElementById('output-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displaySummary(text) {
  document.getElementById('summary-output').textContent = text;
}

function displayKeyPoints(points) {
  const el = document.getElementById('key-points-output');
  if (!points || !points.length) {
    el.innerHTML = '<li class="output-placeholder">No key points generated.</li>';
    return;
  }
  el.innerHTML = points.map(pt => `<li style="margin-bottom: 8px; position: relative; padding-left: 14px;"><span style="position: absolute; left: 0; color: var(--accent);">•</span>${pt}</li>`).join('');
}

// ── Load Records ───────────────────────────────────────────────────────────
async function loadRecords() {
  const grid = document.getElementById('records-grid');
  grid.innerHTML = '<div class="records-empty" style="grid-column:1/-1;"><div class="spinner" style="margin:0 auto 12px;"></div>Loading records…</div>';

  try {
    const res = await apiGetRecords();
    renderRecords(res.records || []);
  } catch (err) {
    grid.innerHTML = `<div class="records-empty" style="grid-column:1/-1;">Error loading records: ${err.message}</div>`;
  }
}

function renderRecords(records) {
  const grid = document.getElementById('records-grid');
  if (!records.length) {
    grid.innerHTML = `
      <div class="records-empty" style="grid-column:1/-1;">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        No records yet. Start by transcribing something!
      </div>`;
    return;
  }

  grid.innerHTML = records.map(r => {
    const badgeClass = { file: 'badge-file', text: 'badge-text', url: 'badge-url' }[r.source_type] || 'badge-text';
    const badgeLabel = { file: '📁 File', text: '✏️ Text', url: '🔗 URL' }[r.source_type] || r.source_type;
    const date = r.created_at ? new Date(r.created_at).toLocaleString() : '';
    const preview = (r.summary || '').slice(0, 200);

    return `
    <div class="record-card" onclick="openRecord(${JSON.stringify(r).replace(/"/g, '&quot;')})">
      <div class="record-card-header">
        <span class="record-badge ${badgeClass}">${badgeLabel}</span>
        <span class="record-meta">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          ${date}
        </span>
      </div>
      <p class="record-summary">${preview}${r.summary && r.summary.length > 200 ? '…' : ''}</p>
      <div class="record-card-footer">
        <span class="record-length-badge">${r.summary_length || 'medium'} summary</span>
        <button class="btn-delete-record" onclick="deleteRecord(event, '${r.id}')" title="Delete">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
            <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
          </svg>
        </button>
      </div>
    </div>`;
  }).join('');
}

function openRecord(record) {
  document.getElementById('modal-record-title').textContent =
    record.source_name ? `Record: ${record.source_name}` : 'Record Detail';
  document.getElementById('record-transcript-text').textContent = record.transcript || '(no transcript)';
  document.getElementById('record-summary-text').textContent    = record.summary    || '(no summary)';
  
  const kpEl = document.getElementById('record-key-points-text');
  if (record.key_points && record.key_points.length) {
    kpEl.innerHTML = record.key_points.map(pt => `<li style="margin-bottom: 8px; position: relative; padding-left: 14px;"><span style="position: absolute; left: 0; color: var(--accent);">•</span>${pt}</li>`).join('');
  } else {
    kpEl.innerHTML = '<li class="output-placeholder">No key points available.</li>';
  }
  
  openModal('modal-record');
}

async function deleteRecord(event, recordId) {
  event.stopPropagation();
  if (!confirm('Delete this record?')) return;
  try {
    await apiDeleteRecord(recordId);
    showToast('Record deleted.', 'success');
    loadRecords();
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// ── Logout ─────────────────────────────────────────────────────────────────
async function handleLogout() {
  try {
    await firebase.auth().signOut();
    window.location.href = '/';
  } catch (err) {
    showToast('Error signing out.', 'error');
  }
}
