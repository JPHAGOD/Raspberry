from mainui import *
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import cv2
#import numpy as np
from ultralytics import YOLO
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
#from PyQt5.QtWidgets import QLabel
import time

#pyuic5 -x .\ejemplo_2.ui -o ejemplo_2.py

# class Ui_GroupBox(Ui_GroupBox):
#     pass

global estado_pantalla
class CameraThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, estado_pantalla):
        super().__init__()
    
    def run(self):
        cap = cv2.VideoCapture(0)
        model = YOLO(r'best.pt')
        prev_time = time.time()

        while True:
            time_elapsed = time.time() - prev_time
            if time_elapsed > 1./5:
                ret, frame = cap.read()
                if ret:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = model(rgbImage, conf=0.6)
                    rgbImage = results[0].plot()
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(410, 320)
                    self.changePixmap.emit(p)
                prev_time = time.time()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self,*args, **kwargs)
        self.setupUi(self)
    #UICODE

        #Firebase
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)

        db=firestore.client()
        self.data_ref=db.collection('data')
        self.last_ref=db.collection('last').document('wcNKTliw70OH5H32UDZe')

    #-----------UPDATE----------------#
        self.employee_code = 3987
        self.pss = ''
        self.pass_label.setText('')
        self.admin = False

        self.stackedWidget.setCurrentIndex(0)
        self.order_num=self.last_ref.get().to_dict()['order']
        self.update_order(0)   

        #Parámetros del modelo:
        #self.cam_num = 0
        #self.pre_model = r'AAA.pt'
        self.flag = False
        self.activate = False
        self.camera = cv2.VideoCapture(0)
        self.model = YOLO(r'best.pt')

        #Parámetros de la interfaz:
        #self.label = QtWidgets.QLabel(self)
        #self.label.setGeometry(50, 50, 700, 540)
        #self.pushButton.clicked.connect(self.close_popup)

        self.th = CameraThread(self)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()

    #-----------PANTALLAS----------------#
    #Pantalla 0 Inicio
        self.empezar_button.clicked.connect(lambda: self.cambiar_pantalla(1))

    #Pantalla 1 Cam
        self.revisar_button.clicked.connect(lambda: self.cambiar_pantalla(2))

    #Pantalla 2 Cart
        self.generar_button.clicked.connect(lambda: self.cambiar_pantalla(3))
        self.editar_button.clicked.connect(lambda: self.cambiar_pantalla(4))
        self.minus_button.clicked.connect(self.restar)
        self.plus_button.clicked.connect(self.sumar)
        self.trash_button.clicked.connect(self.eliminar)
        
    #Pantalla 3 Ticket
        self.terminar_button.clicked.connect(self.get_new_order)
        self.terminar_button.clicked.connect(lambda: self.cambiar_pantalla(0))
        

    #Pantalla 4 Auth
        self.ingresar_button.clicked.connect(self.autenticar)
        self.regresar_button.clicked.connect(lambda: self.cambiar_pantalla(2))
        #Button array
        self.button_num_0.clicked.connect(lambda: self.button_pushed(0))
        self.button_num_1.clicked.connect(lambda: self.button_pushed(1))
        self.button_num_2.clicked.connect(lambda: self.button_pushed(2))
        self.button_num_3.clicked.connect(lambda: self.button_pushed(3))
        self.button_num_4.clicked.connect(lambda: self.button_pushed(4))
        self.button_num_5.clicked.connect(lambda: self.button_pushed(5))
        self.button_num_6.clicked.connect(lambda: self.button_pushed(6))
        self.button_num_7.clicked.connect(lambda: self.button_pushed(7))
        self.button_num_8.clicked.connect(lambda: self.button_pushed(8))
        self.button_num_9.clicked.connect(lambda: self.button_pushed(9))
        self.button_delete.clicked.connect(lambda: self.button_pushed(10))

    #Pantalla 5 Productos
        self.bolillo_button_add.clicked.connect     (lambda: self.productos(0))
        self.telera_button_add.clicked.connect      (lambda: self.productos(1))
        self.torta_button_add.clicked.connect       (lambda: self.productos(2))
        self.concha_button_add.clicked.connect      (lambda: self.productos(3))
        self.dona_button_add.clicked.connect        (lambda: self.productos(4))
        self.mantecada_button_add.clicked.connect   (lambda: self.productos(5))
        self.pinguino_button_add.clicked.connect    (lambda: self.productos(6))
        self.oreja_button_add.clicked.connect       (lambda: self.productos(7))
        self.reja_button_add.clicked.connect        (lambda: self.productos(8))
        self.rebanda_button_add.clicked.connect     (lambda: self.productos(9))
        self.cuernito_button_add.clicked.connect    (lambda: self.productos(10))
    

    #-----------FUNCTIONS----------------#
    def update_time(self,num):
        time_labels = [self.time_label_0, self.time_label_1, self.time_label_2, self.time_label_3, self.time_label_4]
        #time
        if num != 5:
            current_label = time_labels[num]
            current_label.setText(datetime.now().strftime("%H:%M %d-%m-%Y"))
        #orders

    def update_order(self,num):
        order_labels = [self.order_label_0, self.order_label_1, self.order_label_2, self.order_label_3]
        if num != 4 and num != 5:
            self.current_order = order_labels[num]
            self.current_order.setText(f'Orden: #{str(self.order_num)}')
        self.last_ref.update({'order':self.order_num})

    def get_new_order(self):
        #print('New order')
        if self.order_num[-8:] != datetime.now().strftime("%d%m%Y"):
            #print('New day')
            order = '1'+datetime.now().strftime("%d%m%Y")
        else:
            #print('Same day')
            order = int(self.order_num[:-8])
            order += 1
            order = str(order)+(datetime.now().strftime("%d%m%Y"))
        self.order_num = order
        #print(self.order_num)

    def cambiar_pantalla(self,num):

        global estado_pantalla
        estado_pantalla = num

        if num == 4 and self.admin==True:
            self.stackedWidget.setCurrentIndex(5)
        elif num == 3 and self.admin==True:
            self.admin = False
            self.stackedWidget.setCurrentIndex(num)
            self.editar_button.setText('Editar')
        elif num == 1:
            #self.mostrar_camara()
            self.stackedWidget.setCurrentIndex(num)
        else:
            self.stackedWidget.setCurrentIndex(num)
            self.camera.release()
        self.update_time(num)
        self.update_order(num)
        #print(f'Pantalla {num}')
    
    def button_pushed(self, num):
        if num == 10:
            self.pss = self.pss[:-1]
        else:
            self.pss+=str(num)
        self.pass_label.setText('*'*len(self.pss))

    def autenticar(self):
        if self.pss == '1234':
            self.cambiar_pantalla(2)
            self.pss = ''
            self.pass_label.setText('')
            self.sudo()
        else:
            self.pss = ''
            self.pass_label.setText('Error')

    def sudo(self):
        self.editar_button.setText('Agregar')
        self.admin = True
        print(self.editar_button.text())

    def sumar(self):
        if self.admin == True:
            self.qty_label.setText(str(int(self.qty_label.text())+1))
            
    def restar(self):
        if self.admin == True:
            if int(self.qty_label.text()) > 0:
                self.qty_label.setText(str(int(self.qty_label.text())-1))

    def eliminar(self):
        if self.admin == True:
            pass
    
    def productos(self,num):
        print(f'Producto {num}')
        self.cambiar_pantalla(2)

    def mostrar_camara(self):
        self.timer = QtCore.QTimer(self)  
        self.timer.timeout.connect(self.mostrar_camara)
        self.timer.start(200) 
        success, frame = self.camera.read()

        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized_frame = cv2.resize(frame, (410, 320))
            

            #For testing
            #annotated_frame=resized_frame
            
            #Final
            results = self.model(resized_frame, conf=0.6)
            annotated_frame = results[0].plot()
            print('Frame')

            #Convierte de OpenCV a QTimage
            height, width, channel = annotated_frame.shape
            bytes_per_line = 3 * width
            qt_image = QtGui.QImage(annotated_frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)

            #Muestra la imagen en la interfaz
            pixmap = QtGui.QPixmap.fromImage(qt_image)
            self.cam.setPixmap(pixmap)
        else:
            self.camera.release()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.cam.setPixmap(QPixmap.fromImage(image))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    Window = MainWindow()
    Window.show()
    app.exec()