import serial
import time
import vlc
import math
import os
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pynput import keyboard

# conversie procent volum de sistem la o valoare in decibeli,folosita de API-ul din pycaw
def percent_to_db(x):
    dict = {0: -65.25, 1: -56.99, 2: -51.67, 3: -47.74, 4: -44.62, 5: -42.03, 6: -39.82, 7: -37.89, 8: -36.17,
            9: -34.63, 10: -33.24,
            11: -31.96, 12: -30.78, 13: -29.68, 14: -28.66, 15: -27.7, 16: -26.8, 17: -25.95, 18: -25.15, 19: -24.38,
            20: -23.65,
            21: -22.96, 22: -22.3, 23: -21.66, 24: -21.05, 25: -20.46, 26: -19.9, 27: -19.35, 28: -18.82, 29: -18.32,
            30: -17.82,
            31: -17.35, 32: -16.88, 33: -16.44, 34: -16.0, 35: -15.58, 36: -15.16, 37: -14.76, 38: -14.37, 39: -13.99,
            40: -13.62,
            41: -13.26, 42: -12.9, 43: -12.56, 44: -12.22, 45: -11.89, 46: -11.56, 47: -11.24, 48: -10.93, 49: -10.63,
            50: -10.33,
            51: -10.04, 52: -9.75, 53: -9.47, 54: -9.19, 55: -8.92, 56: -8.65, 57: -8.39, 58: -8.13, 59: -7.88,
            60: -7.63,
            61: -7.38, 62: -7.14, 63: -6.9, 64: -6.67, 65: -6.44, 66: -6.21, 67: -5.99, 68: -5.76, 69: -5.55, 70: -5.33,
            71: -5.12, 72: -4.91, 73: -4.71, 74: -4.5, 75: -4.3, 76: -4.11, 77: -3.91, 78: -3.72, 79: -3.53, 80: -3.34,
            81: -3.15, 82: -2.97, 83: -2.79, 84: -2.61, 85: -2.43, 86: -2.26, 87: -2.09, 88: -1.91, 89: -1.75,
            90: -1.58,
            91: -1.41, 92: -1.25, 93: -1.09, 94: -0.93, 95: -0.77, 96: -0.61, 97: -0.46, 98: -0.3, 99: -0.15, 100: 0.0}
    return dict[x]


# event handler pentru apasare de tasta;la apasarea Esc,script-ul isi va incheia
# executia
def on_press(key):
    if key==keyboard.Key.esc:
        print("Exiting script")
        os._exit(0)


# valoarea furnizata de arduino va fi luata in considerare doar daca
# se situeaza in intervalul stabilit, pentru a minimiza erorile de temporizare
# pentru distante prea mici sau prea mari
MIN_DIST = 6
MAX_DIST = 26

def main():

# initializare comunicator serial cu arduino pe portul COM3 la un baudrate
# comun de 9600 S/s
    arduino = serial.Serial(port='COM3', baudrate=9600,timeout=0.3)

# selectare audio device si activarea interfetei
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
       IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

# initializare vlc player pentru modul de control video
# **prin set_scale se ajusteaza dimensiunea ferestrei de redare
# iar playing reprezinta un set de stari in care playerul trebuie
# sa se afle pentru a se considera ca videoul se deruleaza sau
# este in pregatire (vlc.State disponibil in bibliografie)

    src = "scenery.mp4"
    playing = set([1,2,3,4])
    vlc_obj = vlc.Instance("--verbose=-1")
    vlc_obj.log_unset()
    
    vlcplayer = vlc_obj.media_player_new()  
    vlcmedia = vlc_obj.media_new(src)  
         
    vlcplayer.set_media(vlcmedia)
    vlcplayer.video_set_scale(0.6)

    with keyboard.Listener(on_press=on_press) as listener:
        while True:

# citire comanda de la microcontroller si parsare valoarea generata de senzor
# in functie de modul de operare specificat in comanda, se mapeaza
# intervalul [MIN_DIST,MAX_DIST] la [0,100],respectiv [0.0,1.0] pentru
# video
# luminozitatea adaptiva este tratata separat;pentru diferite
# luminozitati ambientale,s-a stabilit ca intervalul posibil este
# [0-1000],asa ca se imparte la 10 pentru a se aduce la [0,100]
            data = arduino.readline()
            data = data.decode()
            if data:
                data = data.rstrip()
                sensor_val = math.floor(float(data[data.find(":")+1:]))
                if MIN_DIST <= sensor_val <= MAX_DIST:
                    print("("+data+"):",end = " ")
                    if data.find("volume")>=0:
                        vlcplayer.stop()
                        volume_percent = 100*(sensor_val-MIN_DIST)//(MAX_DIST-MIN_DIST)
                        volume.SetMasterVolumeLevel(percent_to_db(volume_percent), None)
                        print("Volume set to {}%".format(volume_percent))
                    elif data.find("brightness")>=0:
                        vlcplayer.stop()
                        brightness_percent = 100*(sensor_val-MIN_DIST)//(MAX_DIST-MIN_DIST)
                        sbc.set_brightness(brightness_percent)
                        print("Brightness set to {}%".format(brightness_percent))
                    elif data.find("video")>=0:
                        vlcplayer.play()
                        time.sleep(0.5)
                        length = vlcplayer.get_length()
                        
                        state = vlcplayer.get_state()
                        if state not in playing:
                            vlcplayer.stop()
                        
                        pos = (sensor_val-MIN_DIST)/(MAX_DIST-MIN_DIST)
                        print("Video went to {0:.2f}% of total length".format(pos*100))
                        vlcplayer.set_position(pos)
                else:
                    if data.find("adaptive")>=0:
                        vlcplayer.stop()
                        brightness_percent = sensor_val//10
                        sbc.set_brightness(brightness_percent)
                        print("("+data+"):",end = " ")
                        print("Brightness set to {}%".format(brightness_percent))
        
            
                    

if __name__=="__main__":
    main()
