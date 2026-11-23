"""Base16 schemes the Base16 colour sets are made from.

From tinted-theming/schemes (https://github.com/tinted-theming/schemes,
MIT licence, see LICENSE-BASE16); each scheme is the work of the author
named with it. Only the sixteen colours, base00 to base0F, are kept.
"""

# (set name, scheme file in base16/, scheme name, author, base00..base0F)
SCHEMES = (
    ('Gruvbox', 'gruvbox-dark-medium', 'Gruvbox dark, medium', 'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)',
     ("#282828", "#3c3836", "#504945", "#665c54", "#bdae93", "#d5c4a1", "#ebdbb2", "#fbf1c7",
      "#fb4934", "#fe8019", "#fabd2f", "#b8bb26", "#8ec07c", "#83a598", "#d3869b", "#d65d0e")),
    ('Solarized', 'solarized-dark', 'Solarized Dark', 'Ethan Schoonover (modified by aramisgithub)',
     ("#002b36", "#073642", "#586e75", "#657b83", "#839496", "#93a1a1", "#eee8d5", "#fdf6e3",
      "#dc322f", "#cb4b16", "#b58900", "#859900", "#2aa198", "#268bd2", "#6c71c4", "#d33682")),
    ('Nord', 'nord', 'Nord', 'arcticicestudio',
     ("#2e3440", "#3b4252", "#434c5e", "#4c566a", "#d8dee9", "#e5e9f0", "#eceff4", "#8fbcbb",
      "#bf616a", "#d08770", "#ebcb8b", "#a3be8c", "#88c0d0", "#81a1c1", "#b48ead", "#5e81ac")),
    ('Dracula', 'dracula', 'Dracula', 'clach04 (https://github.com/clach04)',
     ("#282a36", "#21222c", "#44475a", "#6272a4", "#9ea8c7", "#f8f8f2", "#f8f8f2", "#ffffff",
      "#ff5555", "#ffb86c", "#f1fa8c", "#50fa7b", "#8be9fd", "#bd93f9", "#ff79c6", "#993333")),
    ('Monokai', 'monokai', 'Monokai', 'Wimer Hazenberg (http://www.monokai.nl)',
     ("#272822", "#383830", "#49483e", "#75715e", "#a59f85", "#f8f8f2", "#f5f4f1", "#f9f8f5",
      "#f92672", "#fd971f", "#f4bf75", "#a6e22e", "#a1efe4", "#66d9ef", "#ae81ff", "#cc6633")),
    ('One Dark', 'onedark', 'OneDark', 'Lalit Magant (http://github.com/tilal6991)',
     ("#282c34", "#353b45", "#3e4451", "#545862", "#565c64", "#abb2bf", "#b6bdca", "#c8ccd4",
      "#e06c75", "#d19a66", "#e5c07b", "#98c379", "#56b6c2", "#61afef", "#c678dd", "#be5046")),
    ('Catppuccin', 'catppuccin-mocha', 'Catppuccin Mocha', 'https://github.com/catppuccin/catppuccin',
     ("#1e1e2e", "#181825", "#313244", "#45475a", "#585b70", "#cdd6f4", "#f5e0dc", "#b4befe",
      "#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#94e2d5", "#89b4fa", "#cba6f7", "#f2cdcd")),
    ('Tokyo Night', 'tokyo-night-dark', 'Tokyo Night Dark', 'Michaël Ball',
     ("#1a1b26", "#16161e", "#2f3549", "#444b6a", "#787c99", "#a9b1d6", "#cbccd1", "#d5d6db",
      "#c0caf5", "#a9b1d6", "#0db9d7", "#9ece6a", "#b4f9f8", "#2ac3de", "#bb9af7", "#f7768e")),
    ('Everforest', 'everforest-dark-hard', 'Everforest Dark Hard', 'Sainnhe Park (https://github.com/sainnhe)',
     ("#272e33", "#2e383c", "#414b50", "#859289", "#9da9a0", "#d3c6aa", "#edeada", "#fffbef",
      "#e67e80", "#e69875", "#dbbc7f", "#a7c080", "#83c092", "#7fbbb3", "#d699b6", "#9da9a0")),
    ('Rosé Pine', 'rose-pine', 'Rosé Pine', 'Emilia Dunfelt <edun@dunfelt.se>',
     ("#191724", "#1f1d2e", "#26233a", "#6e6a86", "#908caa", "#e0def4", "#e0def4", "#524f67",
      "#eb6f92", "#f6c177", "#ebbcba", "#31748f", "#9ccfd8", "#c4a7e7", "#f6c177", "#524f67")),
    ('Kanagawa', 'kanagawa', 'Kanagawa', 'Tommaso Laurenzi (https://github.com/rebelot)',
     ("#1f1f28", "#16161d", "#223249", "#54546d", "#727169", "#dcd7ba", "#c8c093", "#717c7c",
      "#c34043", "#ffa066", "#c0a36e", "#76946a", "#6a9589", "#7e9cd8", "#957fb8", "#d27e99")),
    ('Gotham', 'gotham', 'Gotham', 'Andrea Leopardi (arranged by Brett Jones)',
     ("#0c1014", "#11151c", "#091f2e", "#0a3749", "#245361", "#599cab", "#99d1ce", "#d3ebe9",
      "#c23127", "#d26937", "#edb443", "#33859e", "#2aa889", "#195466", "#888ca6", "#4e5166")),
)
