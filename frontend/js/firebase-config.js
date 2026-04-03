// firebase-config.js
// ─────────────────────────────────────────────────────────────────────────────
// Replace the placeholder values below with your Firebase project's
// Web SDK configuration. You can find this in:
//   Firebase Console → Project Settings → Your Apps → Web App → SDK setup
//
// ⚠️  Never commit real credentials to a public repository.
// ─────────────────────────────────────────────────────────────────────────────


const firebaseConfig = {
  apiKey: "AIzaSyAszSESTre4RiXR6N3T_0vTNqcpS0oKxEg",
  authDomain: "lecture-summarizer-773d6.firebaseapp.com",
  projectId: "lecture-summarizer-773d6",
  storageBucket: "lecture-summarizer-773d6.appspot.com",
  messagingSenderId: "1063263283474",
  appId: "1:1063263283474:web:96a5220992d6410f846bcb",
  measurementId: "G-ZQHKWPY08X"
};


// Initialize Firebase (compat SDK)
firebase.initializeApp(firebaseConfig);

// Convenience exports
const auth = firebase.auth();
