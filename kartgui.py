from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import threading
import time
import RPi.GPIO as GPIO
class Application(ttk.Frame):

    
    @classmethod
    def main(cls):
        NoDefaultRoot()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        root = Tk()
        app = cls(root)
        app.grid(column=1, row=1)
        root.resizable(True, True)
        root.geometry("800x480")
        root["bg"] = 'black'
        #root.attributes("-fullscreen", True)
        root.bind("<F11>", app.toggleFullScreen)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
        
    def __init__(self, root, **args):
        super().__init__(root, **args)
        print("Initialized application")
        self.root = root
        self.create_variables()
        self.create_threads()
        self.create_widgets()
        self.grid_widgets()
        self.speedometerThread.start()
        
    def create_variables(self):
        self.fullscreen = True
        self.statusVar = StringVar(self, value="OFF")
        self.onoff = StringVar(self, value="ON")
        self.speedVar = StringVar(self, value="0\nmph")
        self.kart = Kart()
        
    def toggleFullScreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def create_threads(self):
        self.threadingEvent = threading.Event()
        self.speedometerThread = SpeedometerThread(self)
    
    def create_widgets(self):
        self.onButton = Button(self, textvariable=self.onoff, height=24, width=30, command=self.prompt)
        self.forward = Button(self, text="Forward", height=8, width=30, state=DISABLED, command=lambda : self.kart.forward(self))
        self.neutral = Button(self, text="Neutral", height=8, width=30, state=DISABLED, command=lambda : self.kart.neutral(self))
        self.reverse = Button(self, text="Reverse", height=8, width=30, state=DISABLED, command=lambda : self.kart.reverse(self))
        self.batteryToggleButton = Button(self, text="Switch Battery Pack", height=4, width=30)
        self.status = Label(self, width=90, height=5, textvariable=self.statusVar, relief='groove')
        self.speedDisplay = Label(self, width=30, height=15, relief='groove', textvariable=self.speedVar)
        self.batteryChargingDisplay = Label(self, width = 30, height = 2, relief='groove', text='Battery Pack {0} {C|NC} {1}% {2}V\nBattery Pack {3} {C|NC} {4}% {5}V')
        self.gasChange = Button(self, text="Gas", height=4, width=30)
        
    def grid_widgets(self):
        self.status.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        self.speedDisplay.grid(column=2, row=1, sticky='NEW', rowspan=2)
        self.batteryChargingDisplay.grid(column=2, row=2, sticky='EWS')
        self.onButton.grid(column=0, row=1, rowspan=3, sticky='NEWS')
        self.forward.grid(column=1, row=1, sticky='NWES')
        self.neutral.grid(column=1, row=2, sticky='NWES')
        self.reverse.grid(column=1, row=3, sticky='NWES')
        self.batteryToggleButton.grid(column=2, row=3, sticky='NWE')
        self.gasChange.grid(column=2, row=3, sticky='EWS')
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)
            self.root.grid_rowconfigure(i, weight=1)
            
    def prompt(self):
        onoff=self.onoff.get()
        if onoff == "OFF" or mb.askyesno(message='Check your surroundings.\nReady to go?', master=self.root):
            if(onoff == 'ON'):
                self.onoff.set("OFF")
                self.kart.on(self)
            else:
                self.onoff.set("ON")
                self.kart.off(self)

    def on_closing(self):
        print("Application terminated")
        self.kart.off(self)
        self.root.destroy()
        self.threadingEvent.set()

    @staticmethod
    def disableButton(*buttons):
        for button in buttons:
            button.config(state=DISABLED)

    @staticmethod
    def enableButton(*buttons):
        for button in buttons:
            button.config(state=NORMAL)

class Kart:

    pins = [29, 31, 35, 37]
    
    def __init__(self):
        GPIO.setup(self.pins, GPIO.OUT)
        self.forwardBool = False;
        self.neutralBool = False;
        self.reverseBool = False;
    
    def on(self, app):
        app.statusVar.set("Turning on . . .")
        root = app.root
        Application.disableButton(app.onButton)
        root.after(1000, lambda : Util.batch_execute_func(Application.enableButton(app.neutral, app.onButton), \
                                                            app.statusVar.set("On"), \
                                                            app.neutral.invoke(), \
                                                            self.on_pin_seq()))
    def off(self, app):
        app.statusVar.set("OFF")
        Application.disableButton(app.forward, app.neutral, app.reverse, app.onButton)
        app.root.after(1000, lambda : Util.batch_execute_func(Application.enableButton(app.onButton), \
                                                              self.off_pin_seq()))

    def forward(self, app):
        Application.disableButton(app.forward, app.reverse, app.onButton)
        app.root.after(1000, lambda : Util.batch_execute_func(Application.enableButton(app.neutral, app.onButton), \
                                                              app.statusVar.set("Forward"), \
                                                              self.forward_pin_seq()))
        pass

    def neutral(self, app):
        Application.disableButton(app.neutral, app.onButton)
        app.root.after(1000, lambda : Util.batch_execute_func(Application.enableButton(app.onButton, app.forward, app.reverse), \
                                                              app.statusVar.set("Neutral"), \
                                                              self.neutral_pin_seq()))
        pass

    def reverse(self, app):
        Application.disableButton(app.reverse, app.forward, app.onButton)
        app.root.after(1000, lambda : Util.batch_execute_func(Application.enableButton(app.onButton, app.neutral), \
                                                              app.statusVar.set("Reverse"), \
                                                              self.reverse_pin_seq()))
        
        pass

    def on_pin_seq(self):
        print("Pin KEY")
        GPIO.output(29, GPIO.HIGH)
        time.sleep(0.5)
        print("ON ENABLE")
        GPIO.output(31, GPIO.HIGH)

    def off_pin_seq(self):
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.05)

    def neutral_pin_seq(self):
        GPIO.output(37, GPIO.LOW)
        GPIO.output(35, GPIO.LOW)

    def forward_pin_seq(self):
        self.neutral_pin_seq()
        time.sleep(1)
        GPIO.output(37, GPIO.HIGH)

    def reverse_pin_seq(self):
        self.neutral_pin_seq()
        time.sleep(1)
        GPIO.output(35, GPIO.HIGH)

    def gas_pin_seq(self):
        pass

class SpeedometerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.name = "Speedometer"
        self.counter = 0;

    def run(self):
        '''while True:
            if self.counter < 200:
                self.counter += 1
                self.app.speedVar.set(str(self.counter)+"\nmph")
                #time.sleep(1)
            else:
                print("Max speed!")
            if self.app.threadingEvent.wait(timeout=1):
                    break'''
        self.demo()
        print(self.name + " thread exited gracefully!")

    def demo(self):
       while True:
            if self.counter < 200:
                self.counter += 1
                self.app.speedVar.set(str(self.counter)+"\nmph")
                #time.sleep(1)
            else:
                print("Max speed!")

            timeout = 0.1
            if(self.counter > 60):
                timeout = 1
            
            if self.app.threadingEvent.wait(timeout=timeout):
                    break
            

class Util:
    
    @staticmethod
    def batch_execute_func(*funcs):
        for f in funcs:
            f

if __name__ == '__main__':
    Application.main()
