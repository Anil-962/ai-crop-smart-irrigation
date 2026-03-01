import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.rfind('localStorage.setItem')
if idx == -1:
    print("Marker not found")
    sys.exit(1)

head = content[:idx]

# This tail corresponds to:
# localStorage.setItem('agroguard_lang', lang);
#                                   }}
#                                   className={`...`}
#                                 >
#                                   {lang === 'en' ? 'English' : lang === 'hi' ? 'Hindi' : 'Kannada'}
#                                 </button>
#                               ))}
#                             </div>
#                           </div>
#                         </div>
#                       </div>
#                     )
#                   }
#                 </div>
#               </div>
#             </main>
#           </div>
#         </div>
#         {showToast && (
#           <Toast
#             message={toastMessage}
#             onClose={() => setShowToast(false)}
#           />
#         )}
#       </div>
#     );
#   }
# export default App;

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

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(head + tail)

print("Balanced tail replacement complete.")
