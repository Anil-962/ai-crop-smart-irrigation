import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix corrupted identifiers (trailing slashes or spaces around slashes)
# These are the ones that were underscores.
# Strategy: Look for alpha/alpha or alpha_alpha patterns.
# Actually, I'll just restore a set of known ones.
identifiers = [
    'health_score', 'soil_moisture_pct', 'temperature_c', 'humidity_pct',
    'rain_forecast_mm_24h', 'crop_type', 'growth_stage', 'dashboard_data',
    'analytics_data', 'alerts_data', 'health_data', 'last_updated',
    'global_zone', 'is_logged_in', 'is_changing', 'display_value',
    'trend_color', 'status_config', 'derived_status', 'stroke_dashoffset',
    'selected_zone', 'is_auto_mode', 'is_irrigating', 'flow_rate',
    'water_usage', 'irrigation_timer', 'metrics_loading', 'analytics_loading',
    'alerts_loading', 'health_loading', 'metrics_error', 'analytics_error',
    'alerts_error', 'health_error', 'alert_filter_type', 'alert_filter_status',
    'filtered_alerts_tab', 'fetch_dashboard_data', 'handle_irrigation_control',
    'handle_image_upload', 'get_irrigation_rec', 'show_toast', 'toast_message'
]

for id in identifiers:
    broken1 = id.replace('_', '/')
    broken2 = id.replace('_', ' / ')
    content = content.replace(broken1, id)
    content = content.replace(broken2, id)

# 2. Fix the specific map variable (/ -> _)
content = content.replace('(/, i)', '(_, i)')

# 3. Fix the corrupted regex (/\D/g)
content = content.replace(r'/\D_g', r'/\D/g')
content = content.replace(r'/ \D / g', r'/\D/g')
content = content.replace(r'/\ \D / g', r'/\D/g')

# 4. Fix comments in the component body (outside return)
# { /* ... */ } -> // ...
def fix_component_body_comments(text):
    # Find the range between 'function App() {' and 'return ('
    start_marker = 'function App() {'
    end_marker = 'return ('
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        return text
        
    setup_code = text[start_idx:end_idx]
    # Replace {/* ... */} with // ...
    setup_code = re.sub(r'\{\/\* (.*?) \*\/\}', r'// \1', setup_code)
    # Replace stray /* or // if they are weird
    
    return text[:start_idx] + setup_code + text[end_idx:]

content = fix_component_body_comments(content)

# 5. Fix the 'image/*' attribute
content = content.replace('accept="image//"', 'accept="image/*"')
content = content.replace('accept="image/ /"', 'accept="image/*"')

# 6. Fix the "naked slash" in JSX text at 312 (Neutralize it again just in case)
# Finding the exact line by context
content = content.replace('tracking-widest">/ 100</span>', 'tracking-widest">- 100</span>')

# 7. Ensure NO // comments at the top level of return (between tags)
# e.g. // Scrollable Content -> {/* Scrollable Content */}
content = content.replace('\n        // ', '\n        {/* ')
# This is a bit risky but we can fix it by looking for unclosed {/*
lines = content.split('\n')
new_lines = []
for line in lines:
    if '{/* ' in line and '*/}' not in line:
        line = line + ' */}'
    new_lines.append(line)
content = '\n'.join(new_lines)

# 8. Bit-accurate tail repair
marker = "localStorage.setItem('agroguard_lang', lang);"
idx = content.rfind(marker)
if idx != -1:
    head = content[:idx]
    tail = """localStorage.setItem('agroguard_lang', lang);
                                  }}
                                  className={`flex-1 py-1.5 rounded-lg border text-[10px] font-bold uppercase tracking-widest transition-all
                                    ${i18n.language === lang ? 'bg-primary/5 border-primary text-primary shadow-sm' : 'bg-slate-50 dark:bg-slate-800 border-border text-textSecondary'}`}
                                >
                                  {lang === 'en' ? 'English' : lang === 'hi' ? 'Hindi' : 'Kannada'}
                                </button>
                              ))}
                            </div>
                          </div>
                   </div>
                      </div>
                    )
                  }
                </div>
              </div>
            </main>
          </div>
        </div>
        {showToast && (
          <Toast
            message={toastMessage}
            onClose={() => setShowToast(false)}
          />
        )}
      </div>
    );
  }

export default App;
"""
    content = head + tail

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Super Fixer complete.")
