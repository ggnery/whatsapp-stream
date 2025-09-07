import threading
from audio import get_whatsapp_audio
from video import get_whatsapp_window

def main():
    t1 = threading.Thread(target=get_whatsapp_audio)
    t2 = threading.Thread(target=get_whatsapp_window)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()

if __name__ == "__main__":
    main()