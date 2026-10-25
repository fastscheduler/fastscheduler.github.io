import io
p = 'website/_build/build_help.py'
s = io.open(p, encoding='utf-8').read()
Q = chr(34)
a1 = "'aria-expanded=" + Q + "false" + Q + " aria-label=" + Q + "{t(" + Q + "settings" + Q + ")}" + Q
assert a1 in s, 'gear miss'
s = s.replace(a1, "f'aria-expanded=" + Q + "false" + Q + " aria-label=" + Q + "{t(" + Q + "settings" + Q + ")}" + Q, 1)
a2 = "'<div class=" + Q + "glass-pop" + Q + " id=" + Q + "settingsMenu" + Q + " role=" + Q + "menu" + Q + " aria-label=" + Q + "{t(" + Q + "settings" + Q + ")}" + Q + ">'"
assert a2 in s, 'menu miss'
s = s.replace(a2, "f'<div class=" + Q + "glass-pop" + Q + " id=" + Q + "settingsMenu" + Q + " role=" + Q + "menu" + Q + " aria-label=" + Q + "{t(" + Q + "settings" + Q + ")}" + Q + ">'", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('fstrings fixed')
