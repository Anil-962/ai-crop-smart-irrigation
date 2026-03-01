import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Restore all accidentally converted non-JSX comments
# These were { /* comment */ } but should be // comment or /* comment */ outside of JSX.
# Specifically in the component body (lines 800-1100 approx)

def restore_nonjsx_comments(text):
    lines = text.split('\n')
    new_lines = []
    in_component_setup = False
    for line in lines:
        if 'const App = () => {' in line:
            in_component_setup = True
        if 'return (' in line:
            in_component_setup = False
            
        if in_component_setup:
            # Replace {/* comment */} with // comment
            line = re.sub(r'\{\/\* (.*?) \*\/\}', r'// \1', line)
        new_lines.append(line)
    return '\n'.join(new_lines)

content = restore_nonjsx_comments(content)

# 2. Fix the corrupted regex again
content = content.replace(r'/\D_g', r'/\D/g')

# 3. Ensure 'accept="image/*"' is correct
content = content.replace('accept="image//"', 'accept="image/*"')

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

print("Definitive App.jsx restoration v3 complete.")
