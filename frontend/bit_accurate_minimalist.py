import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'rb') as f:
    content = f.read()

# Marker for the Settings tab content
idx = content.rfind(b'localStorage.setItem')
if idx == -1:
    print("Marker not found")
    sys.exit(1)

head = content[:idx]

# This is the ABSOLUTE MINIMAL, BALANCED, ASCII-ONLY tail.
# I'll remove all comments and use a very simple structure.
tail = b'''localStorage.setItem('agroguard_lang', lang);
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
'''

with open(path, 'wb') as f:
    f.write(head + tail)

print("Bit-accurate minimalist tail replacement complete.")
