import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the corrupted regex: /\D_g -> /\D/g
content = content.replace(r'/\D_g', r'/\D/g')
content = content.replace(r'/ /g', r'/ /g') # Just in case

# 2. Re-apply identifier fixes (just in case they were reverted)
identifiers_to_fix = [
    'health/score', 'agroguard/theme', 'agroguard/theme', 'agroguard/lang',
    'soil/moisture', 'moisture/pct', 'rain/forecast', 'mm/24h',
    'crop/type', 'growth/stage', 'dashboard/data', 'last/updated'
]
for identifier in identifiers_to_fix:
    content = content.replace(identifier, identifier.replace('/', '_'))

# 3. Ensure API response handling correctly uses .data
# Since apiClient returns { data, timestamp }, we need to access .data
# I will look for patterns that might be missing .data

# However, some might already be using it.
# Let's check handleIrrigationControl
content = content.replace('if (response.status === \'success\')', 'if (response.data.status === \'success\')')
content = content.replace('setIsIrrigating(response.zone_status === \'active\')', 'setIsIrrigating(response.data.zone_status === \'active\')')

# 4. Final surgical tail fix to ensure the end is perfect and balanced.
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

print("Definitive App.jsx restoration and API standardization complete.")
