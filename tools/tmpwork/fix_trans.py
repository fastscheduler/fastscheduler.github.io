import io
p = 'tools/build_ru_pages.py'
s = io.open(p, encoding='utf-8').read()
a = 'super().__init__(convert_charrefs=False)'
assert a in s
s = s.replace(a, 'super().__init__(convert_charrefs=True)', 1)
old_handle = '''    def handle_data(self, data):
        if not data.strip() or self._skip():
            self.out.append(data)
            return
        key = H.unescape(data.strip())
        if key in self.MAP:
            lead = data[:len(data) - len(data.lstrip())]
            trail = data[len(data.rstrip()):]
            self.out.append(lead + H.escape(self.MAP[key], quote=False) + trail)
        else:
            if len(key) >= 3 and re.search(r'[A-Za-z]', key):
                self.unmapped[key] = self.unmapped.get(key, 0) + 1
            self.out.append(data)

    def handle_entityref(self, name):
        self.out.append('&' + name + ';')

    def handle_charref(self, name):
        self.out.append('&#' + name + ';')
'''
assert old_handle in s, 'handle miss'
new_handle = '''    def handle_data(self, data):
        if not data.strip() or self._skip():
            self.out.append(H.escape(data, quote=False))
            return
        key = data.strip()
        if key in self.MAP:
            lead = data[:len(data) - len(data.lstrip())]
            trail = data[len(data.rstrip()):]
            self.out.append(H.escape(lead, quote=False) + H.escape(self.MAP[key], quote=False) + H.escape(trail, quote=False))
        else:
            if len(key) >= 3 and re.search(r'[A-Za-z]', key):
                self.unmapped[key] = self.unmapped.get(key, 0) + 1
            self.out.append(H.escape(data, quote=False))
'''
s = s.replace(old_handle, new_handle, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('transformer fixed')
