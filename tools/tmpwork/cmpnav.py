import io, sys
sys.path.insert(0, 'tools/tmpwork')
sys.path.insert(0, 'website/_build')
import importlib.util
spec = importlib.util.spec_from_file_location('bh_old', 'tools/tmpwork/bh_old.py')
bh_old = importlib.util.module_from_spec(spec); spec.loader.exec_module(bh_old)
import build_help as bh_new
# old module has no settings_menu; reconstruct its inline menu from build_static? use new EN helper? No - compare unified_nav with SAME menu input.
menu = 'MENUX'
a = bh_old.unified_nav('../..', bh_old.BOT_URL, menu)
b = bh_new.unified_nav('../..', bh_new.BOT_URL, menu)
io.open('tools/tmpwork/cmp.txt', 'w', encoding='utf-8').write('IDENTICAL' if a == b else 'DIFFER len %d vs %d' % (len(a), len(b)))
print('done')
