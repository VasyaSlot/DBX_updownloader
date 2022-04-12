import requests
import os
import argparse

class DropboxUpdDown:
    def __init__(self, token_dbx, ext_path, loc_path):
        self.token = token_dbx
        self.external_path = ext_path
        self.local_path = loc_path

    def upload_bin_files(self):
        filename = self.local_path.split('/')[-1]
        file_size = int(os.path.getsize(self.local_path))
        print(file_size)
        chunk_size = 150 * 1024 * 1024

        with open(self.local_path, 'rb') as data:
            if file_size <= chunk_size:
                headers = {
                    'Authorization': 'Bearer ' + self.token,
                    'Dropbox-API-Arg': '{{"path": "{ext_path}" }}'.format(ext_path=self.external_path),
                    'Content-Type': 'application/octet-stream',
                }

                response = requests.post('https://content.dropboxapi.com/2/files/upload', headers=headers, data=data)
            else:
                headers = {
                    'Authorization': 'Bearer ' + self.token,
                    'Dropbox-API-Arg': '{"close": false}',
                    'Content-Type': 'application/octet-stream',
                }

                response = requests.post('https://content.dropboxapi.com/2/files/upload_session/start', headers=headers,
                                         data=data.read(chunk_size))

                session_id = response.json()
                session_offset = 0

                while data.tell() < file_size:
                    session_offset = data.tell()
                    if file_size - data.tell() <= chunk_size:
                        headers = {
                            'Authorization': 'Bearer ' + self.token,
                            'Dropbox-API-Arg': '{{"cursor": {{"session_id": "{ses_id}","offset": {ses_offset}}},"commit": {{"path": "{loc_path}","mode": "add","autorename": true,"mute": false,"strict_conflict": false}}}}'.format(ses_id=session_id['session_id'], ses_offset=session_offset, loc_path=self.external_path),
                            'Content-Type': 'application/octet-stream',
                        }

                        response = requests.post('https://content.dropboxapi.com/2/files/upload_session/finish',
                                                 headers=headers, data=data.read(chunk_size))
                    else:
                        print("here continue")
                        headers = {
                            'Authorization': 'Bearer ' + self.token,
                            'Dropbox-API-Arg': '{{"cursor": {{"session_id": "{ses_id}","offset": {ses_offset}}},"close": false}}'.format(ses_id=session_id['session_id'], ses_offset=session_offset),
                            'Content-Type': 'application/octet-stream',
                        }

                        response = requests.post('https://content.dropboxapi.com/2/files/upload_session/append_v2',
                                                 headers=headers, data=data.read(chunk_size))

    def download_bin_files(self):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Dropbox-API-Arg': '{{"path": "{ext_path}" }}'.format(ext_path=self.external_path),
        }

        response = requests.post('https://content.dropboxapi.com/2/files/download', headers=headers, stream=True)

        filename = self.local_path.split('/')[-1]

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


def check_files(token, args):
    local_flg = check_local_files(token, args)
    dbx_flg = check_dbx_file(token, args)
    if local_flg is True and dbx_flg is True:
        return True
    else:
        print('Введите правильный запрос в консоли!')
        return False

def check_local_files(token, args):
     if args.whichload.lower() == 'get':
        print('Локальный файл создан!')
        return True
     else:
        if not os.path.isfile(args.local_path):
            print('Локального файла по пути ' + args.local_path + ' не существует. Проверьте правильность введенных данных')
            return False
        else:
            print('Локальный файл найден!')
            return True


def check_dbx_file(token, args):
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    json_data = {
        'path': '{dbx_path}'.format(dbx_path=args.external_path),
        'include_media_info': False,
        'include_deleted': False,
        'include_has_explicit_shared_members': False,
    }
    if args.whichload.lower() == 'get':
        try:
            response = requests.post('https://api.dropboxapi.com/2/files/get_metadata', headers=headers, json=json_data)
            if response.json()['name'] == args.external_path.split('/')[-1]:
                print('Файл в Dropbox найден!')
                return True
            else:
                print('Что-то пошло не так, обратитесь к разработчику')
                return False
        except:
            print('В вашем аккаунте Dropbox нет файла по пути: ' + args.external_path)
            return False
    else:
        print('Файл в Dropbox создан!')
        return True


def main():
    token = 'sl.BEo2zzBr2ue-JortVJNv_v1IlSl-kjPV8Hc_xZTvsAB20ynCwcTt1ARH7fcSJ9sIzBAqa-127tVyCHeoIzfl8aZQ8OVk-OVLGMm2VGUIlbAVcFfiKF-LdQ3ePpxqDLhi00bA8qizSlXf'

    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('token_file')
    cmd_parser.add_argument('whichload')
    cmd_parser.add_argument('local_path')
    cmd_parser.add_argument('external_path')

    args = cmd_parser.parse_args()

    token = open(args.token_file).readline()

    check_files_flg = check_files(token, args)

    if check_files_flg:
        dbx = DropboxUpdDown(token, args.external_path, args.local_path)

        if args.whichload.lower() == 'put':
            dbx.upload_bin_files()
        elif args.whichload.lower() == 'get':
            dbx.download_bin_files()
        else:
            print('Пожалуйста введите правильную команду запроса (PUT или GET)')


if __name__ == "__main__":
    main()








