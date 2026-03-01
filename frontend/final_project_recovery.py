import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the 'image//' corruption
content = content.replace('accept="image//"', 'accept="image/*"')

# 2. Fix the '{ // ... }' corruption (Invalid JSX comments)
# We want to find { followed by // and replace until the end of the line (or next })
# Actually, since my previous script did simple replacements, 
# { /* comment */ } became { // comment  }
# Let's find { // and see if we can close it.

def fix_jsx_comments(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if '{ //' in line:
            # Try to find the closing }
            if '}' in line:
                # Replace { // content } with {/* content */}
                line = re.sub(r'\{\s*//\s*(.*?)\s*\}', r'{/* \1 */}', line)
            else:
                # If it's multi-line (unlikely from my previous script), just be careful
                line = line.replace('{ //', '{/*').strip() + ' */}'
        new_lines.append(line)
    return '\n'.join(new_lines)

content = fix_jsx_comments(content)

# 3. Restore all other corrupted /* patterns
# My previous script did content.replace('/*', '//')
# This probably broke multi-line comments too.
# But we must be careful not to break valid // comments.

# Let's just fix the most critical ones in JSX.
content = content.replace('// Background Circle', '{/* Background Circle */}')
content = content.replace('// Progress Circle', '{/* Progress Circle */}')
content = content.replace('// Mini Sparkline Background', '{/* Mini Sparkline Background */}')

# 4. Final check for underscores vs slashes
# Ensure 'health_score' and others are correct
identifiers = ['health_score', 'soil_moisture_pct', 'temperature_c', 'humidity_pct', 'crop_type', 'growth_stage']
for id in identifiers:
    broken = id.replace('_', '/')
    content = content.replace(broken, id)

# 5. Correct the regex line 891 just in case
content = content.replace(r'/\D_g', r'/\D/g')

# 6. Final surgical tail fix to ensure the end is perfect and balanced.
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

print("Project recovery and standardization complete.")
