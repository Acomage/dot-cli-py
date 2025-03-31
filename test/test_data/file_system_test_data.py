test1_res = """{
  "USER": [
    {
      "name": ".config/nvim",
      "owner": "nvim",
      "contents": [
        {
          "name": ".gitignore",
          "owner": "nvim"
        },
        {
          "name": ".neoconf.json",
          "owner": "nvim"
        },
        {
          "name": "LICENSE",
          "owner": "nvim"
        },
        {
          "name": "README.md",
          "owner": "nvim"
        },
        {
          "name": "init.lua",
          "owner": "nvim"
        },
        {
          "name": "lua",
          "owner": "nvim",
          "contents": [
            {
              "name": "config",
              "owner": "nvim",
              "contents": [
                {
                  "name": "keymaps.lua",
                  "owner": "nvim"
                },
                {
                  "name": "lazy.lua",
                  "owner": "nvim"
                },
                {
                  "name": "autocmds.lua",
                  "owner": "nvim"
                },
                {
                  "name": "options.lua",
                  "owner": "nvim"
                }
              ]
            },
            {
              "name": "plugins",
              "owner": "nvim",
              "contents": [
                {
                  "name": "example.lua",
                  "owner": "nvim"
                },
                {
                  "name": "auto-save.lua",
                  "owner": "nvim"
                },
                {
                  "name": "colorbuddy.lua",
                  "owner": "nvim"
                },
                {
                  "name": "im-select.lua",
                  "owner": "nvim"
                },
                {
                  "name": "kitty.lua",
                  "owner": "nvim"
                },
                {
                  "name": "nvim-cmp.lua",
                  "owner": "nvim"
                },
                {
                  "name": "vimtex.lua",
                  "owner": "nvim"
                }
              ]
            },
            {
              "name": "lualine",
              "owner": "nvim",
              "contents": [
                {
                  "name": "themes",
                  "owner": "nvim",
                  "contents": []
                }
              ]
            }
          ]
        },
        {
          "name": "stylua.toml",
          "owner": "nvim"
        },
        {
          "name": "lazy-lock.json",
          "owner": "nvim"
        },
        {
          "name": "colors",
          "owner": "nvim",
          "contents": [
            {
              "name": "ras.lua",
              "owner": "nvim"
            },
            {
              "name": "ras.png",
              "owner": "nvim"
            }
          ]
        },
        {
          "name": "lazyvim.json",
          "owner": "nvim"
        }
      ]
    },
    {
      "name": ".zshrc",
      "owner": "zsh"
    }
  ],
  "SYSTEM": []
}"""
test2_res = """{
  "USER": [
    {
      "name": ".config/nvim",
      "owner": "nvim",
      "contents": [
        {
          "name": ".gitignore",
          "owner": "nvim"
        },
        {
          "name": ".neoconf.json",
          "owner": "nvim"
        },
        {
          "name": "LICENSE",
          "owner": "nvim"
        },
        {
          "name": "README.md",
          "owner": "nvim"
        },
        {
          "name": "init.lua",
          "owner": "nvim"
        },
        {
          "name": "stylua.toml",
          "owner": "nvim"
        },
        {
          "name": "lazy-lock.json",
          "owner": "nvim"
        },
        {
          "name": "colors",
          "owner": "nvim",
          "contents": [
            {
              "name": "ras.lua",
              "owner": "nvim"
            },
            {
              "name": "ras.png",
              "owner": "nvim"
            }
          ]
        },
        {
          "name": "lazyvim.json",
          "owner": "nvim"
        },
        {
          "name": "lua",
          "owner": "nvim",
          "contents": [
            {
              "name": "config",
              "owner": "nvim",
              "contents": [
                {
                  "name": "keymaps.lua",
                  "owner": "nvim"
                },
                {
                  "name": "lazy.lua",
                  "owner": "nvim"
                },
                {
                  "name": "autocmds.lua",
                  "owner": "nvim"
                },
                {
                  "name": "options.lua",
                  "owner": "nvim"
                }
              ]
            },
            {
              "name": "plugins",
              "owner": "nvim",
              "contents": [
                {
                  "name": "example.lua",
                  "owner": "nvim"
                },
                {
                  "name": "auto-save.lua",
                  "owner": "nvim"
                },
                {
                  "name": "colorbuddy.lua",
                  "owner": "nvim"
                },
                {
                  "name": "im-select.lua",
                  "owner": "nvim"
                },
                {
                  "name": "kitty.lua",
                  "owner": "nvim"
                },
                {
                  "name": "nvim-cmp.lua",
                  "owner": "nvim"
                },
                {
                  "name": "vimtex.lua",
                  "owner": "nvim"
                }
              ]
            },
            {
              "name": "lualine",
              "owner": "nvim",
              "contents": [
                {
                  "name": "themes",
                  "owner": "nvim",
                  "contents": [
                    {
                      "name": "ras.lua",
                      "owner": "nvim"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": ".zshrc",
      "owner": "zsh"
    }
  ],
  "SYSTEM": []
}"""
test3_res = """{
  "USER": [
    {
      "name": ".zshrc",
      "owner": "zsh"
    },
    {
      "name": ".config/nvim",
      "owner": "nvim",
      "contents": [
        {
          "name": ".gitignore",
          "owner": "nvim"
        },
        {
          "name": ".neoconf.json",
          "owner": "nvim"
        },
        {
          "name": "LICENSE",
          "owner": "nvim"
        },
        {
          "name": "README.md",
          "owner": "nvim"
        },
        {
          "name": "init.lua",
          "owner": "nvim"
        },
        {
          "name": "stylua.toml",
          "owner": "nvim"
        },
        {
          "name": "lazy-lock.json",
          "owner": "nvim"
        },
        {
          "name": "colors",
          "owner": "nvim",
          "contents": [
            {
              "name": "ras.lua",
              "owner": "nvim"
            },
            {
              "name": "ras.png",
              "owner": "nvim"
            }
          ]
        },
        {
          "name": "lazyvim.json",
          "owner": "nvim"
        },
        {
          "name": "lua",
          "owner": "nvim",
          "contents": [
            {
              "name": "config",
              "owner": "nvim",
              "contents": [
                {
                  "name": "keymaps.lua",
                  "owner": "nvim"
                },
                {
                  "name": "lazy.lua",
                  "owner": "nvim"
                },
                {
                  "name": "autocmds.lua",
                  "owner": "nvim"
                },
                {
                  "name": "options.lua",
                  "owner": "nvim"
                }
              ]
            },
            {
              "name": "lualine",
              "owner": "nvim",
              "contents": [
                {
                  "name": "themes",
                  "owner": "nvim",
                  "contents": [
                    {
                      "name": "ras.lua",
                      "owner": "nvim"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "SYSTEM": []
}"""
test4_res = """{
  "USER": [
    {
      "name": ".config/nvim/lua",
      "owner": "nvim",
      "contents": [
        {
          "name": "config",
          "owner": "nvim",
          "contents": [
            {
              "name": "keymaps.lua",
              "owner": "nvim"
            },
            {
              "name": "lazy.lua",
              "owner": "nvim"
            },
            {
              "name": "autocmds.lua",
              "owner": "nvim"
            },
            {
              "name": "options.lua",
              "owner": "nvim"
            }
          ]
        },
        {
          "name": "plugins",
          "owner": "nvim",
          "contents": [
            {
              "name": "example.lua",
              "owner": "nvim"
            },
            {
              "name": "auto-save.lua",
              "owner": "nvim"
            },
            {
              "name": "colorbuddy.lua",
              "owner": "nvim"
            },
            {
              "name": "im-select.lua",
              "owner": "nvim"
            },
            {
              "name": "kitty.lua",
              "owner": "nvim"
            },
            {
              "name": "nvim-cmp.lua",
              "owner": "nvim"
            },
            {
              "name": "vimtex.lua",
              "owner": "nvim"
            }
          ]
        },
        {
          "name": "lualine",
          "owner": "nvim",
          "contents": [
            {
              "name": "themes",
              "owner": "nvim",
              "contents": [
                {
                  "name": "ras.lua",
                  "owner": "nvim"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": ".zshrc",
      "owner": "zsh"
    }
  ],
  "SYSTEM": [
    {
      "name": "etc/kmscon",
      "owner": "kmscon",
      "contents": [
        {
          "name": "kmscon.conf",
          "owner": "kmscon"
        }
      ]
    }
  ]
}"""
