import re

with open('frontend/css/style.css', 'r') as f:
    css = f.read()

# 1. Update variables
new_vars = """
:root {
  --bg-base:        #000000;
  --bg-surface:     #09090b;
  --bg-card:        rgba(18, 18, 20, 0.65);
  --bg-card-hover:  rgba(28, 28, 30, 0.85);
  --sidebar-bg:     #040404;
  --sidebar-width:  260px;

  --accent:         #6366f1;
  --accent-light:   #818cf8;
  --accent-glow:    rgba(99, 102, 241, 0.25);
  --teal:           #14b8a6;
  --teal-light:     #2dd4bf;
  --teal-glow:      rgba(20, 184, 166, 0.2);
  --orange:         #f97316;
  --orange-glow:    rgba(249, 115, 22, 0.2);

  --text-primary:   #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted:     #475569;
  --border:         rgba(255,255,255,0.08);
  --border-focus:   rgba(99, 102, 241, 0.5);

  --radius-sm:  12px;
  --radius-md:  16px;
  --radius-lg:  24px;
  --radius-xl:  32px;

  --shadow-card: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 32px rgba(99, 102, 241, 0.15);
  --transition:  all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

body.light-mode {
  --bg-base:        #f8fafc;
  --bg-surface:     #ffffff;
  --bg-card:        rgba(255, 255, 255, 0.7);
  --bg-card-hover:  rgba(255, 255, 255, 0.95);
  --sidebar-bg:     #ffffff;
  
  --accent:         #4f46e5;
  --accent-light:   #6366f1;
  --accent-glow:    rgba(79, 70, 229, 0.25);
  --text-primary:   #0f172a;
  --text-secondary: #475569;
  --text-muted:     #94a3b8;
  --border:         rgba(0,0,0,0.08);
  --border-focus:   rgba(79, 70, 229, 0.5);
  --shadow-card:    0 4px 24px rgba(0,0,0,0.06);
}
"""

css = re.sub(r':root\s*\{[^}]+\}', new_vars, css)

# 2. Add glassmorphism to action cards
card_css = """
.action-card {
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px 28px;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  position: relative;
  overflow: hidden;
}
"""
css = re.sub(r'\.action-card\s*\{[^}]+\}', card_css, css)

# 3. Update buttons to pill style
btn_css = """
.btn-primary {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  border-radius: 99px;
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
  margin-top: 4px;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
"""
css = re.sub(r'\.btn-primary\s*\{[^\}]+\}', btn_css, css)

# 4. Auth brand update (so text is visible in light mode too, but auth brand is dark usually)
# Actually the auth page has its own gradients. We'll leave it or adapt it.

# 5. Output boxes styling
output_css = """
.output-box {
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}
"""
css = re.sub(r'\.output-box\s*\{[^}]+\}', output_css, css)

header_css = """
.main-header {
  padding: 28px 36px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}
.search-bar {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 99px;
  padding: 8px 16px;
  width: 250px;
}
.search-bar input {
  background: none;
  border: none;
  color: var(--text-primary);
  width: 100%;
  font-size: 0.9rem;
  margin-left: 8px;
  outline: none;
}
.search-bar svg {
  stroke: var(--text-muted);
}
.theme-toggle {
  background: var(--bg-card);
  border: 1px solid var(--border);
  width: 44px; height: 44px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-primary);
}
.theme-toggle:hover {
  background: var(--bg-card-hover);
}
"""
css += header_css

# Write back
with open('frontend/css/style_new.css', 'w') as f:
    f.write(css)
