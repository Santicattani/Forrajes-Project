const API_BASE = "http://localhost:8000";

async function healthCheck() {
  try {
    const res = await fetch(`${API_BASE}/`);
    const data = await res.json();
    console.log("API status:", data.status);
  } catch (e) {
    console.warn("API no disponible:", e.message);
  }
}

healthCheck();
