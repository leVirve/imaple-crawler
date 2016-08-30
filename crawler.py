import argparse
import telnetlib
import time
import os
import pyte
import uao_decode


def encode(s, suffix=''):
    return bytes(s + suffix, encoding='big5')


class IMaple:

    expects = [
        '您的帳號',
        '● 請按任意鍵繼續 ●',
        '再別楓橋，輕輕的我走了'
    ]

    actions = [
        'guest',
        '',
        's{BOARD_NAME}'
    ]

    def __init__(self, host, board_name):
        self.download_folder = 'posts'
        self.board_name = board_name
        self.client = telnetlib.Telnet(host)
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream()

        self.screen.mode.discard(pyte.modes.LNM)
        self.stream.attach(self.screen)
        self.actions[-1] = 's{BOARD_NAME}'.format(BOARD_NAME=board_name)
        self._lead_me_to_board()

    def _lead_me_to_board(self):
        expects = [encode(item) for item in self.expects]
        actions = [encode(item, '\r\n') for item in self.actions]
        while True:
            idx, _, content = self.client.expect(expects, 3)
            if idx == -1:
                break
            self.client.write(actions[idx])

    def get_posts(self, post_range):
        board_dir = os.path.join(self.download_folder, self.board_name)
        if not os.path.exists(board_dir):
            os.makedirs(board_dir)

        for post_id in post_range:
            print('Crawling post#{}'.format(post_id))
            self.client.write(encode(str(post_id), '\r\n' * 2))
            time.sleep(0.5)
            self._update_partial_content()
            lines = self.screen.display[:-1]

            while True:
                if self.screen.display[-1].find(' 文 章 選 讀') != -1:
                    break
                self.client.write(encode('\x1bOB'))  # next line
                time.sleep(0.05)
                self._update_partial_content()
                lines.append(self.screen.display[-2])
            self.client.write(encode('q'))

            self.save_post(lines, board_dir, post_id)

    def _update_partial_content(self):
        content = self.client.read_very_eager().decode('uao_decode', 'ignore')
        self.stream.feed(content)

    def save_post(self, lines, folder, post_id):
        path = os.path.join(folder, 'post-{}.txt'.format(post_id))
        content = '\n'.join(lines)
        with open(path, 'w', encoding='utf8') as f:
            f.write(content)

    def close(self):
        self.client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='iMaple Crawler')
    parser.add_argument('board')
    parser.add_argument('start_id', type=int)
    parser.add_argument('end_id', type=int)
    args = parser.parse_args()

    imaple = IMaple('imaple.tw', args.board)
    imaple.get_posts(range(args.start_id, args.end_id))
    imaple.close()
