# motioneye-to-mqtt

this project publishes the latest picture and motion state detected by motioneye to MQTT which can be processed by for example home assistant.

#TODO
  - add autodiscovery to homeassistant
  - fix the need for the deps folder. This is currently needed because fs uses entry points for hooking in plugins and I can't get my .spec file for pyinstaller setup in such a way that this works.
  - move Camera subfolder out of config file to keep the config file more universal, for now make 2 folders with different config files and same script.

#To use
1. Download the latest release (.zip) from https://github.com/kloknibor/motioneye-to-mqtt/releases
2. Unzip the files and upload the files somewhere where motioneye can access them. (keep them in the same folder)
3. Setup the config.ini file, when using a samba share set SAMBA to True and fill in all the details.
4. Configure the motion eye motion to your likings
5. Go to motion eye -> motion notifications and enable Run a command. As command fill in the path to the file motioneye-to-mqtt which you just uploaded and add ON after it.
   e.g. /share/motioneye/scripts/motioneye-to-mqtt ON
6. Go to motion eye -> motion notifications and enable Run an end command. As command fill in the path to the file motioneye-to-mqtt which you just uploaded and add OFF after it.
   e.g. /share/motioneye/scripts/motioneye-to-mqtt OFF
  
All done, motioneye will now publish the state of motion over MQTT and the last motion snapshot as well.

ONLY tested with a samba share so far!
