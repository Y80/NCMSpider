import requests
import json
import time
from requests import RequestException
from Crypto.Cipher import AES
import codecs
import base64


class NCMSpider(object):
    user_agent = 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'

    # 原 core.js 文件中, 以下三个变量的值每次都相同, 这里可以复制过来
    second_param = '010001'
    third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    fourth_param = '0CoJUm6Qyw8W8jud'

    # 原 core.js 文件中, 每次都随机生成一个长度为 16 的字符串, 这里直接设定一个, 并通过 RSA 加密算法获得相应的加密后的字符串
    random_16_chars = '0123456789abcdef'
    encSecKey = '35701388baf89fed412e11269b9c76625d095ecaf17f03fa018abe19ea2d38b949debf242ee39a71ca1f6cda71b1b86a45aa909ee27f7e78e267d34e732f0de948206c3340a788d0003372183e2f753c1f78b66ac23d134ac1fc9b993156520ea826b8aa89a962d4491b4b8d7e08738e1da9b07aa39bf4a7ef0b1c210728cd52'


    @staticmethod
    def get_encText(first_param):
        def AES_encrypt(text, key):
            # AES加密
            pad = 16 - len(str.encode(text)) % 16
            text = text + pad * chr(pad)
            encryptor = AES.new(key=str.encode(key), mode=2, iv=b'0102030405060708')
            plaintext = str.encode(text)
            ciphertext = encryptor.encrypt(plaintext=plaintext)
            ciphertext = base64.b64encode(ciphertext)
            return ciphertext
        return AES_encrypt(AES_encrypt(first_param, NCMSpider.fourth_param).decode('utf-8'), NCMSpider.random_16_chars)

    @staticmethod
    def get_encSecKey(random_chars):
        def RSA_encrypt(pubkey, text, modulus):
            # RSA加密
            text = text[::-1]
            rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pubkey, 16) % int(modulus, 16)
            return format(rs, 'x').zfill(256)
        return RSA_encrypt(NCMSpider.second_param, random_chars, NCMSpider.third_param)

    @staticmethod
    def get_song_info(id):
        url = 'https://music.163.com/api/song/detail/?id=' + id + '&ids=%5B' + id + '%5D'
        rst = {'status': 0}
        try:
            rsp = requests.get(url=url, headers={'user-agent': NCMSpider.user_agent})
            rsp_json = rsp.json()
            if rsp_json.get('code') == 200:
                rsp_json = rsp_json.get('songs')
                if len(rsp_json) != 0:
                    rsp_json = rsp_json[0]
                    # 标记成功状态, 并开始清洗数据
                    rst['status'] = 1
                    rst['singer'] = rst.get('singer', '') + '|'.join(
                        artist.get('name') for artist in rsp_json.get('artists'))
                    rst['name'] = rsp_json.get('name')
                    rst['blurPicUrl'] = rsp_json.get('album').get('blurPicUrl')
                    sec = int(rsp_json.get('duration') / 1000)
                    rst['duration'] = str(int(sec / 60)) + ':' + (
                        str(sec % 60) if sec % 60 >= 10 else '0' + str(sec % 60))
                else:
                    rst['err'] = '数据为空'
            else:
                rst['err'] = '请求参数错误'
        except RequestException as e:
            rst['err'] = '请求失败：' + e.errno
        return rst

    @staticmethod
    def search_song(name):
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        headers = {
            'user-agent': NCMSpider.user_agent,
            'content-type': 'application/x-www-form-urlencoded',
            'Referer': 'https://music.163.com/search/'
        }
        some_params = {
            "s": name,
            "offset": 0,
            "limit": 12,
            "type": "1",
        }
        form_data = {
            'params': NCMSpider.get_encText(json.dumps(some_params)),
            'encSecKey': NCMSpider.encSecKey
        }

        rst = {'status': 0, 'songs': []}
        try:
            rsp = requests.post(url=url, data=form_data, headers=headers)
            rsp_json = rsp.json()
            if rsp_json.get('code', 0) == 200:
                songs = rsp_json.get('result').get('songs', [])
                if len(songs) > 0:
                    # 标记成功状态, 并开始清洗数据
                    rst['status'] = 1
                    for song in songs:
                        dic = {}
                        dic['id'] = str(song.get('id'))
                        dic['name'] = song.get('name')
                        dic['singer'] = dic.get('singer', '') + '|'.join(
                            singer.get('name') for singer in song.get('ar'))
                        dic['album'] = song.get('al').get('name')
                        sec = int(song.get('dt') / 1000)
                        dic['duration'] = str(int(sec / 60)) + ':' + (
                            str(sec % 60) if sec % 60 >= 10 else '0' + str(sec % 60))
                        rst['songs'].append(dic)
                else:
                    rst['err'] = '数据为空'
            else:
                rst['err'] = '请求参数错误'
        except RequestException as e:
            rst['err'] = '网络请求失败' + str(e.errno)
        return rst

    @staticmethod
    def get_comments(id, offset):
        # 评论数据获取
        url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + id + '?csrf_token='
        headers = {
            'user-agent': NCMSpider.user_agent,
            'content-type': 'application/x-www-form-urlencoded'
        }

        first_param = '{"rid":"R_SO_4_' + id + '","offset":"' + str(
            offset) + '","total":"true","limit":"20","csrf_token":""}'
        # random_16_chars = (''.join(map(lambda xx: (hex(ord(xx))[2:]), str(os.urandom(16)))))[0:16]

        form_data = {
            'params': NCMSpider.get_encText(first_param),
            'encSecKey': NCMSpider.encSecKey
        }

        rst = {'status': 0, 'comments': [], 'hotComments': []}
        try:
            rsp = requests.post(url=url, data=form_data, headers=headers)
            rsp_json = rsp.json()
            if rsp_json.get('code') == 200:
                # 标记成功状态, 并开始清洗数据
                rst['status'] = 1
                rst['total'] = rsp_json.get('total')
                for item in rsp_json.get('comments'):
                    dic = {}
                    dic['nickname'] = item.get('user').get('nickname')
                    dic['avatarUrl'] = item.get('user').get('avatarUrl')
                    dic['content'] = item.get('content')
                    dic['likedCount'] = item.get('likedCount')
                    dic['time'] = time.strftime('%H:%M %Y-%m-%d %A', time.localtime(item.get('time') / 1000))
                    rst['comments'].append(dic)
                if offset == 0:
                    for item in rsp_json.get('hotComments'):
                        dic = {}
                        dic['nickname'] = item.get('user').get('nickname')
                        dic['avatarUrl'] = item.get('user').get('avatarUrl')
                        dic['content'] = item.get('content')
                        dic['likedCount'] = item.get('likedCount')
                        dic['time'] = time.strftime('%H:%M %Y-%m-%d %A', time.localtime(item.get('time') / 1000))
                        rst['hotComments'].append(dic)
            else:
                rst['err'] = '请求参数错误'
        except RequestException as e:
            rst['err'] = '请求失败：' + str(e.errno)
        return rst
