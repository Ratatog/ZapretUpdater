import os
import sys
import rarfile
from os import remove, listdir
from os.path import exists
from shutil import copy, move
from requests import get, head
from re import search
from io import BytesIO

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

rarfile.UNRAR_TOOL = resource_path("UnRAR.exe")

TEMP_DIR = resource_path("temp")


def myholder(msg):
    def outer(fnc):
        def inner(*args, **kwargs):
            try:
                res = fnc(*args, **kwargs)
            except:
                input(msg)
                exit()
            return res
        return inner
    return outer

@myholder('Path Error. Please enter the correct folder path')
def get_path() -> str:
    """Get a path to old zapret folder"""
    currz = sys.argv[1]
    fname = currz.split('\\')[-1]
    if fname in list(listdir(currz)):
        currz += '\\'+fname
    return currz
    
@myholder('Check version Error. Make sure that the zapret is not corrupt.')
def get_curr_version(path: str) ->  str:
    """Get version of old zapret"""
    with open(os.path.join(path, "service.bat"), 'r') as f:
        return search('"LOCAL_VERSION=(.*?)"', f.read()).group(1)

@myholder('Update Error. Turn off VPN or Try again later.')
def get_new_zapret() -> dict:
    """Get new zapret"""
    response = get('https://api.github.com/repos/Flowseal/zapret-discord-youtube/releases/latest')
    response.raise_for_status()
    
    return response.json()

@myholder('New version not found Error.')
def check_version(z: dict, v: str) -> None:
    """Check version of new zapret"""
    if z['tag_name'] == v:
        raise Exception
        
@myholder('Downloading Error. Turn off VPN or Try again later.\n\tAlso try to reinstalling the program.')
def download_new(zapret: dict) -> str:
    """Downloading new zapret"""
    assets = zapret.get('assets')
    for asset in assets:
        if asset['name'].endswith('.rar'):
            target = asset
            break
    
    download_url = target["browser_download_url"]
    file_resp = get(download_url)
    file_resp.raise_for_status()
    with rarfile.RarFile(BytesIO(file_resp.content)) as rf:
        file_name = '/'.join(rf.namelist()[0].split('/')[:-1])
        new_path = os.path.join(TEMP_DIR, file_name)
        rf.extractall(TEMP_DIR) 
    
    return new_path

@myholder('Update settings Error. Try to reinstalling the program.\n\tAlso make sure that the zapret is not corrupt.')
def update_setts(new: str, old: str) -> None:
    """Update setting of new zapret"""
    def create_list(lst, path):
        """Create list of unique domains"""
        with open(f'{new}\\{path}', 'r') as f:
            for l in f.readlines():
                lst.append(l.strip())
        with open(f'{old}\\{path}', 'r') as f:
            for l in f.readlines():
                lst.append(l.strip())
                
        return list(dict.fromkeys(lst))
    
    def change_new(lst, path):
        """Create a domain file"""
        with open(f'{new}\\{path}', 'w') as f:
            for i in lst:
                f.write(f'{i}\n')
    
    def move_file(path):
        """Update new zapret files"""
        if exists(f'{old}{path}'):
            copy(f'{old}{path}', f'{new}{path}')
            
        elif exists(f'{new}{path}'):
            remove(f'{new}{path}')
        
        
    list_general = create_list([], 'lists\\list-general.txt')
    list_exclude = create_list([], 'lists\\list-exclude.txt')
    targets = create_list([], 'utils\\targets.txt')
    change_new(list_general, 'lists\\list-general.txt')
    change_new(list_exclude, 'lists\\list-exclude.txt')
    change_new(targets, 'utils\\targets.txt')
    
    move_file("\\lists\\ipset-all.txt")
    move_file("\\utils\\check_updates.enabled")
    move_file("\\utils\\game_filter.enabled")

@myholder('Moving Error. Try to find zapret in "./temp/" folder')
def move_new(new: str) -> None:
    """Move new zapret to endpoint"""
    move(new, './')
        
@myholder('Unknown Error. Try to reinstalling the program')
def main() -> None:
    """Get a new version of zapret and change the settings automatically"""
    path = get_path()
    v = get_curr_version(path)
    zapret = get_new_zapret()
    check_version(zapret, v)
    
    new_path = download_new(zapret)
    
    update_setts(new_path, path)
    move_new(new_path)


if __name__ == '__main__':
    main()
    input('Done.')
    exit()
