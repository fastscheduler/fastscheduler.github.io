import io
p = 'tools/build_ru_hubs.py'
s = io.open(p, encoding='utf-8').read()
a = 'from build_ru_pages2 import (  # noqa: E402' + chr(10) + '    build_help_hub, build_index, build_404, build_data_file,' + chr(10) + ')'
assert a in s
b = 'from build_ru_pages2 import (  # noqa: E402' + chr(10) + '    build_index, build_404, build_data_file,' + chr(10) + ')' + chr(10) + 'from build_ru_pages4 import build_help_hub_full  # noqa: E402'
s = s.replace(a, b, 1)
a2 = "        _, u2 = build_help_hub(MAP, patch, audit_only=True)"
assert a2 in s
s = s.replace(a2, "        _, u2, _st = build_help_hub_full(MAP, patch, {}, audit_only=True)", 1)
a3 = "    p2, u2 = build_help_hub(MAP, patch)"
assert a3 in s
s = s.replace(a3, "    p2, u2, st = build_help_hub_full(MAP, patch, {})", 1)
a4 = "    print('wrote %s (%d unmapped)' % (p2, len(u2)))"
assert a4 in s
s = s.replace(a4, "    print('wrote %s (%d unmapped) art=%d cat=%d' % (p2, len(u2), st.get('art'), st.get('cat')))", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('wired')
