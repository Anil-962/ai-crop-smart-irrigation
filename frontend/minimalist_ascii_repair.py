import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Marker for the Settings tab content
idx = content.rfind('localStorage.setItem')
if idx == -1:
    print("Marker not found")
    sys.exit(1)

head = content[:idx]

# ABSOLUTELY CLEAN, NO TEMPLATE LITERALS, NO SLASHES, NO COMMENTS
tail = """localStorage.setItem('agroguard_lang', lang);
                                  }}
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

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(head + tail)

print("Minimalist ASCII-only repair complete.")
