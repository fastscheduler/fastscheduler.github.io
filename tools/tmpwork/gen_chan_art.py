import urllib.parse


def art(bg, f1, f2):
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='180' height='120'>"
        "<rect width='180' height='120' fill='" + bg + "'/>"
        "<rect y='54' width='180' height='66' fill='" + f2 + "' opacity='.3'/>"
        "<circle cx='135' cy='40' r='15' fill='" + f2 + "' opacity='.92'/>"
        "<path d='M0 76 Q36 52 72 74 T180 66 V120 H0 Z' fill='" + f1 + "' opacity='.85'/>"
        "<path d='M0 94 Q44 74 82 92 T180 86 V120 H0 Z' fill='" + f1 + "'/></svg>"
    )
    enc = urllib.parse.quote(svg, safe='')
    enc = enc.replace('%27', "'").replace("'", '%27')
    return "url('data:image/svg+xml," + enc + "')"


pals = [
    ('#f2c94c', '#7a9d3f', '#e8862e'),
    ('#8a6a4a', '#5d442e', '#d9b06a'),
    ('#4e6b46', '#2e4028', '#93b564'),
    ('#d99a4e', '#8a5a26', '#f2c94c'),
]
with open('tools/tmpwork/chan_art.txt', 'w') as fh:
    fh.write('\n'.join(art(*p) for p in pals))
print('ok')
