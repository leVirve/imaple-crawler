import time
import telnetlib
import uao_decode
from functools import partial


def _encode(s, suffix):
    return bytes(s + suffix, encoding='big5')

encode_line = partial(_encode, suffix='\r\n')
encode = partial(_encode, suffix='')


tn = telnetlib.Telnet('imaple.tw')

expect_list = [
    '您的帳號',
    '● 請按任意鍵繼續 ●',
    '再別楓橋，輕輕的我走了'
]

actions = [
    'guest',
    '',
    'snthu.course'
]

expect_list = [encode(item) for item in expect_list]
actions = [encode_line(item) for item in actions]

while True:
    idx, match, content = tn.expect(expect_list, 3)

    if idx == -1:
        break

    # print(content.decode('uao_decode', 'ignore'))
    # print(idx)
    tn.write(actions[idx])

print(content.decode('uao_decode', 'ignore'))

for i in range(13081, 13089):
    print('Crawling article {}'.format(i))
    tn.write(encode(str(i) + '\r\n' * 2))
    time.sleep(1)
    content = tn.read_very_eager().decode('uao_decode', 'ignore')
    # 刪除沒清乾淨的文章列表
    print(content)

    counter = 2
    while content.find('文章選讀') == -1:
        print('\tdown {}...'.format(counter))
        tn.write(encode('\x1B[B'))  # down
        time.sleep(2)
        _c = tn.read_very_eager().decode('uao_decode', 'ignore')
        print(_c)
        content += _c
        counter += 1

    with open('post-{}.txt'.format(13081), 'w', encoding='utf8') as f:
        f.write(content)
    tn.write(encode('q'))

tn.close()
