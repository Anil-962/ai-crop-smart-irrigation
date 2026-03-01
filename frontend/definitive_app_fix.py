import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the broken identifiers.
# Strategy: Look for alpha/alpha or alpha / alpha patterns that were clearly underscores.
# We exclude things like </ (closing tags) and bg-primary/5 (tailwind).

# Fix patterns with spaces: 'word / word' -> 'word_word'
content = re.sub(r'([a-zA-Z0-9])\s*/\s*([a-zA-Z0-9])', r'\1_\2', content)

# Fix patterns without spaces but are clearly identifiers:
# health/score, agroguard/theme, agroguard/lang, crop/type, growth/stage etc.
identifiers_to_fix = [
    'health/score', 'agroguard/theme', 'agroguard/lang', 'crop/type', 
    'growth/stage', 'dashboard/data', 'last/updated', 'soil/ph',
    'nitrogen/level', 'phosphorus/level', 'potassium/level',
    'soil/moisture', 'moisture/pct', 'rain/forecast', 'mm/24h'
]

for identifier in identifiers_to_fix:
    broken = identifier
    fixed = identifier.replace('/', '_')
    content = content.replace(broken, fixed)

# 2. Fix the KpiSkeleton loop variable: (/, i) -> (_, i)
content = content.replace('(/, i)', '(_, i)')

# 3. Final surgical tail fix to ensure the end is perfect and balanced.
marker = "localStorage.setItem('agroguard_theme', theme);"
idx = content.rfind(marker)
if idx != -1:
    # We want to keep everything up to theme setting, then close the effect and component.
    # But wait, looking at my previous view_file, the theme effect is around 830.
    # The tail I need to fix is at the VERY end of the file.
    pass

# Let's find the last 'localStorage.setItem' which is for language.
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

print("Definitive App.jsx restoration complete.")
