import telnetlib
import time
import pyte
import uao_decode

tn = telnetlib.Telnet('imaple.tw')
BOARD_NAME = 'nthu.course'

screen = pyte.Screen(80, 24)
stream = pyte.Stream()
screen.mode.discard(pyte.modes.LNM)
stream.attach(screen)

class IMaple:

    expect_list = [
        '您的帳號',
        '● 請按任意鍵繼續 ●',
        '再別楓橋，輕輕的我走了'
    ]

    actions = [
        'guest',
        '',
        's%s' % BOARD_NAME
    ]


def encode(s, suffix=''):
    return bytes(s + suffix, encoding='big5')

def enter_board():
    expect_list = [encode(item) for item in IMaple.expect_list]
    actions = [encode(item, '\r\n') for item in IMaple.actions]
    while True:
        idx, match, content = tn.expect(expect_list, 3)
        if idx == -1:
            break
        tn.write(actions[idx])


def get_posts(post_range):
    for post_id in post_range:
        print('Crawling article {}'.format(post_id))

        tn.write(encode(str(post_id), '\r\n' * 2))
        time.sleep(0.5)

        stream.feed(tn.read_very_eager().decode('uao_decode', 'ignore'))
        lines = screen.display[:-1]

        while True:
            if screen.display[-1].find(' 文 章 選 讀') != -1:
                break

            tn.write(encode('\x1bOB'))  # next line
            time.sleep(0.05)
            stream.feed(tn.read_very_eager().decode('uao_decode', 'ignore'))
            lines.append(screen.display[-2])


        with open('post-{}.txt'.format(post_id), 'w', encoding='utf8') as f:
            f.write('\n'.join(lines))

        tn.write(encode('q'))


if __name__ == '__main__':
    enter_board()
    get_posts(range(13081, 13085))
    tn.close()
