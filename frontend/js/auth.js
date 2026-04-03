// auth.js – Firebase Authentication logic for index.html
// ─────────────────────────────────────────────────────────────────────────────

// ── Redirect if already logged in ─────────────────────────────────────────
auth.onAuthStateChanged((user) => {
  if (user && window.location.pathname.endsWith('index.html') ||
      user && window.location.pathname === '/') {
    window.location.href = '/dashboard';
  }
});

// ── Show error message ─────────────────────────────────────────────────────
function showAuthError(elementId, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = message;
  el.classList.add('visible');
}

function clearAuthError(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = '';
  el.classList.remove('visible');
}

function setButtonLoading(btnId, loading, defaultText) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.textContent = loading ? 'Please wait…' : defaultText;
}

// ── Login handler ──────────────────────────────────────────────────────────
async function handleLogin(event) {
  event.preventDefault();
  clearAuthError('login-error');

  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  if (!email || !password) {
    return showAuthError('login-error', 'Please fill in all fields.');
  }

  setButtonLoading('login-btn', true, 'Sign In');

  try {
    await auth.signInWithEmailAndPassword(email, password);
    window.location.href = '/dashboard';
  } catch (err) {
    const msg = firebaseErrorMessage(err.code);
    showAuthError('login-error', msg);
    setButtonLoading('login-btn', false, 'Sign In');
  }
}

// ── Signup handler ─────────────────────────────────────────────────────────
async function handleSignup(event) {
  event.preventDefault();
  clearAuthError('signup-error');

  const name     = document.getElementById('signup-name').value.trim();
  const email    = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;

  if (!name || !email || !password) {
    return showAuthError('signup-error', 'Please fill in all fields.');
  }
  if (password.length < 6) {
    return showAuthError('signup-error', 'Password must be at least 6 characters.');
  }

  setButtonLoading('signup-btn', true, 'Create Account');

  try {
    const cred = await auth.createUserWithEmailAndPassword(email, password);
    await cred.user.updateProfile({ displayName: name });
    window.location.href = '/dashboard';
  } catch (err) {
    const msg = firebaseErrorMessage(err.code);
    showAuthError('signup-error', msg);
    setButtonLoading('signup-btn', false, 'Create Account');
  }
}

// ── Friendly Firebase error messages ──────────────────────────────────────
function firebaseErrorMessage(code) {
  const map = {
    'auth/user-not-found':       'No account found with this email.',
    'auth/wrong-password':       'Incorrect password. Please try again.',
    'auth/email-already-in-use': 'An account with this email already exists.',
    'auth/weak-password':        'Password is too weak. Use at least 6 characters.',
    'auth/invalid-email':        'Please enter a valid email address.',
    'auth/too-many-requests':    'Too many attempts. Please try again later.',
    'auth/network-request-failed': 'Network error. Please check your connection.',
    'auth/invalid-credential':   'Invalid email or password.',
  };
  return map[code] || 'An error occurred. Please try again.';
}
