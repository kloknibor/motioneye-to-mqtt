# imports
import paho.mqtt.publish as mqtt_pub
import fs.opener.smbfs
import fs as fs
from fs.osfs import OSFS
from fs.walk import Walker
import sys
import configparser
import time

#retrieve args
if len(sys.argv) >= 3:
    CONFIG_LOCATION = sys.argv[2]
    config = configparser.ConfigParser()
    config.read(CONFIG_LOCATION)
else:
    print("not enough args for hass addon")
    config = configparser.ConfigParser()
    config.read('config.ini')

# import config vars


#[MQTT]
MQTT_HOST = config.get('MQTT','MQTT_HOST')
MQTT_PORT = int(config.get('MQTT','MQTT_PORT'))
MQTT_USERNAME = config.get('MQTT','MQTT_USERNAME')
MQTT_PASSWORD = config.get('MQTT','MQTT_PASSWORD')
MQTT_TOPIC_SNAPSHOT = config.get('MQTT','MQTT_TOPIC_SNAPSHOT')
MQTT_TOPIC_MOTION = config.get('MQTT','MQTT_TOPIC_MOTION')

#[GENERAL]
MESSAGE_MOTION = config.get('GENERAL','MESSAGE_MOTION')
PICTURE_MOTION = config.get('GENERAL','PICTURE_MOTION')
VIDEO_MOTION = config.get('GENERAL','VIDEO_MOTION')
WAIT = 1

#[OSFS]
CAMERA_FOLDER = config.get('OSFS','CAMERA_FOLDER')

#[SAMBA]
SAMBA = config.get('SAMBA','SAMBA')
SMB_HOST = config.get('SAMBA','SMB_HOST')
SMB_USERNAME = config.get('SAMBA','SMB_USERNAME')
SMB_PASSWD = config.get('SAMBA','SMB_PASSWD')
SMB_PORT = int(config.get('SAMBA','SMB_PORT'))
SMB_NAME_PORT = int(config.get('SAMBA','SMB_NAME_PORT'))
SMB_DIRECT_TCP = config.get('SAMBA','SMB_DIRECT_TCP')
SMB_SHARE = config.get('SAMBA','SMB_SHARE')
SMB_FOLDER = config.get('SAMBA','SMB_FOLDER')

def publish_motion_on():
    mqtt_pub.single(MQTT_TOPIC_MOTION, payload="ON", retain=True, hostname=MQTT_HOST, port=MQTT_PORT,
                    auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})


def publish_motion_off():
    mqtt_pub.single(MQTT_TOPIC_MOTION, payload="OFF", retain=True, hostname=MQTT_HOST, port=MQTT_PORT,
                    auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})


def publish_file_fs(file_to_publish="", topic="snapshot", fs=""):
    # open the image
    byte_file = fs.readbytes(file_to_publish)
    # publish the image to the broker
    print("publishing : " + file_to_publish + " to : " + MQTT_TOPIC_SNAPSHOT)
    mqtt_pub.single(MQTT_TOPIC_SNAPSHOT + topic, payload=byte_file, retain=True, hostname=MQTT_HOST, port=MQTT_PORT,
                    auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})


# probably not usefull, just trying to minimize the load and memory.
def find_newest_folder_fs(fs):
    folders = {}

    walker = Walker(max_depth=1)
    for path, info in walker.info(fs):
        if info.is_dir:
            info = (fs.getinfo(path, namespaces=['details']))
            folders[path] = info.modified.strftime("%Y%m%d%H%M%S")

    newest_folder_fs = (sorted(folders.items(),key=lambda x: x[1],reverse=True)[0][0])
    #print("newest folder: " + newest_folder_fs)
    return newest_folder_fs


def find_newest_file_fs(path="", file_type="*.jpg", fs=""):
    files = {}
    path_to_list = list(path)
    path_to_list[0] = '*'
    folder_to_check = "".join(path_to_list)
    walker = Walker(filter=[file_type],filter_dirs=[folder_to_check])
    for path, info in walker.info(fs):
        if info.is_file:
            info = (fs.getinfo(path, namespaces=['details']))
            files[path] = info.modified.strftime("%Y%m%d%H%M%S")

    newest_file_fs = (sorted(files.items(),key=lambda x: x[1],reverse=True)[0][0])
    print("newest file: " + newest_file_fs)
    return newest_file_fs


def create_root_filesystem():
    #use samba filesystem
    if SAMBA:
        connection_place = "smb://" + SMB_USERNAME + ":" + SMB_PASSWD + "@" + SMB_HOST + "/" + SMB_SHARE + "/" + SMB_FOLDER
        fs_smb = fs.open_fs(connection_place)
        print("Connecting to :" + connection_place)
        return fs_smb
    # act like it is an local filesystem
    else:
        fs_os = OSFS(CAMERA_FOLDER)
        return fs_os


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        SMB_FOLDER = sys.argv[3]
    if len(sys.argv) >= 5:
        MQTT_TOPIC_SNAPSHOT = sys.argv[4]
    if len(sys.argv) >= 6:
        MQTT_TOPIC_MOTION = sys.argv[5]
    if len(sys.argv) >= 7:
        WAIT = sys.argv[6]
    try:
        # main program
        if sys.argv[1] == "ON":
            if MESSAGE_MOTION:
                publish_motion_on()
            if PICTURE_MOTION:
                time.sleep(WAIT)
                fs = create_root_filesystem()
                newest_folder = find_newest_folder_fs(fs=fs)
                newest_image = find_newest_file_fs(path=newest_folder, fs=fs)
                #print(newest_image)
                publish_file_fs(file_to_publish=newest_image, topic="snapshot", fs=fs)

        if sys.argv[1] == "OFF":
            if MESSAGE_MOTION:
                publish_motion_off()
    except:
        print("error system arg not found, assuming on")
        if MESSAGE_MOTION:
            publish_motion_on()
        if PICTURE_MOTION:
            fs = create_root_filesystem()
            newest_folder = find_newest_folder_fs(fs=fs)
            newest_image = find_newest_file_fs(path=newest_folder,fs=fs)
            print(newest_image)
            publish_file_fs(file_to_publish=newest_image, topic="snapshot", fs=fs)

