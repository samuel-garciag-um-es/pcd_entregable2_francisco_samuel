from functools import reduce
from abc import ABC, abstractmethod
import asyncio
import random
import datetime
from math import sqrt

#Singleton
class SistemaGestor:

    _unicaInstancia = None

    @classmethod
    def obtener_instancia(cls):
        if cls._unicaInstancia == None:
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    def definir_umbral(self, umbral):
        self.umbral = umbral
    
    def get_umbral(self):
        return self.umbral
    
    def ejecutar(self):
        """
        El método ejecutar genera la única instancia de SensorTemperatura y Operator del programa.
        A través de estas dos invoca el método register_observer de Observable e invoca de forma asíncrona
        al método generar_temp de SensorTemperatura
        """
        sensor = SensorTemperatura()
        operator = Operator("Operator")
        sensor.register_observer(operator)
        asyncio.run(sensor.generar_temp())

class Generador:
    def temperatura(self):
        """
        Se genera un timestamp que refleja hora:minuto:segundo actual y una temperatura aleatoria de 25 grados +/- 10 grados.
        Devuelve ambos valores en una tupla.
        """
        temperatura_media = 25  # valor medio de 30 grados
        rango_temperatura = 20    # rango de variación alrededor de la media
        temperatura = random.uniform(temperatura_media - rango_temperatura/2, temperatura_media + rango_temperatura/2)
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        return (timestamp, round(temperatura, 2))

#Strategy
class Contexto:
    def __init__(self):
        self.estrategia = None
    
    def establecerEstrategia(self, estrategia):
        self.estrategia = estrategia
    
    def calcular_algoritmo(self, lista):
        return self.estrategia.calcular(lista)

class Estrategia(ABC):
    @abstractmethod
    def calcular(self, lista):
        pass

class MediaDesviacion(Estrategia):
    def calcular(self, lista):
        media = reduce(lambda x,y: x + y, lista)/len(lista)
        varianza = sum(map(lambda x: (x - media) ** 2, lista)) / len(lista)
        return media, sqrt(varianza)

class Cuartiles(Estrategia):
    def calcular(self, lista):
        """Cálculo de los 3 cuartiles de lista"""
        lista_ordenada = sorted(lista)
        n = len(lista_ordenada)
        cuartil_25 = reduce(lambda x, y: (x + y) / 2 if n % 2 == 0 else y, lista_ordenada[n//4 - 1 : n//4 + 1])
        cuartil_50 = reduce(lambda x, y: (x + y) / 2 if n % 2 == 0 else y, lista_ordenada[n//2 - 1 : n//2 + 1])
        cuartil_75 = reduce(lambda x, y: (x + y) / 2 if n % 2 == 0 else y, lista_ordenada[3*n//4 - 1 : 3*n//4 + 1])
        return cuartil_25, cuartil_50, cuartil_75

class MaxMin(Estrategia):
    def calcular(self, lista):
        maximo = reduce(lambda x, y: x if x > y else y, lista)
        minimo = reduce(lambda x, y: x if x < y else y, lista)
        return maximo, minimo

#Chain of Responsibility
class Handler:
    def __init__(self, successor=None):
        self.successor = successor

    def handle_request(self, request, lista):
        pass
    
class Estadisticos(Handler):
    def handle_request(self, request, lista):
        if request.level == "Estadisticos":
            """Para cada uno de los cálculos pertinentes se establece el contexto necesario llamando a las clases de el patrón Strategy"""
            contexto = Contexto()
            contexto.establecerEstrategia(MediaDesviacion())
            media, desviacion = contexto.calcular_algoritmo(lista)
            contexto.establecerEstrategia(Cuartiles())
            cuartil_25, cuartil_50, cuartil_75 = contexto.calcular_algoritmo(lista)
            contexto.establecerEstrategia(MaxMin())
            max_temp, min_temp = contexto.calcular_algoritmo(lista)
            return media, desviacion, cuartil_25, cuartil_50, cuartil_75, max_temp, min_temp
        
        elif self.successor:
            return self.successor.handle_request(request, lista)

class AumentoDrastico(Estadisticos):
    def handle_request(self, request, lista):
        if request.level == "Aumento drastico":
            if len(lista) > 1:
                def diferencia(temp1, temp2):
                    return temp2 - temp1
                
                delta_tiempo = 6 # 6 últimos elementos de la lista (30 últimos segs)
                umbral_aumento = 10 # umbral a superar en las diferencias entre los últimos 6 elementos de lista
                
                L = []
                for i in range(delta_tiempo):
                    L += list(zip(lista[:-1], lista[i+1:]))
                diferencias = map(lambda x: diferencia(x[0], x[1]), L)
                return any(diferencia >= umbral_aumento for diferencia in diferencias) #True si se cumple la comparación en uno o más casos
            else:
                return False
        
        elif self.successor:
            return self.successor.handle_request(request, lista)

class SuperaUmbral(AumentoDrastico):
    def handle_request(self, request, lista):
        if request.level == "Supera umbral":
            singleton = SistemaGestor.obtener_instancia()   # no crea más instancias de SistemaGestor, accede a la existente
            umbral = singleton.get_umbral()     # obtiene el valor del umbral de la instancia de SistemaGestor
            return lista[-1] > umbral, umbral   # devuelve True si la última temperatura supera el umbral definido en SistemaGestor y el umbral
        
        elif self.successor:
            return self.successor.handle_request(request, lista)

class Request:
    def __init__(self, level):
        self.level = level

# Observer
class Observable:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, data):
        for observer in self._observers:
            observer.update(data)

class SensorTemperatura(Observable):
    def _init_(self):
        self.value = None

    def set_value(self, value):
        self.value = value
        self.notify_observers(self.value)
    
    async def generar_temp(self):
        """
        Esta función asincrona genera temperaturas continuamente.
        La función crea una instancia de Generador y utiliza su método para generar temperaturas.
        Las variables timestamp y temperatura se establecen utilizando el método
        'set_value' de la instancia 'self'. La función se ejecuta en un bucle infinito
        para generar continuamente nuevas temperaturas cada 5 segundos.
        """
        generador = Generador()
        while True:
            timestamp, temperatura = generador.temperatura()
            self.set_value((timestamp, temperatura))
            await asyncio.sleep(5) # se espera 5 segundos antes de la próxima iteración

class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass

class Operator(Observer):
    def __init__(self, name):
        self.name = name
        self.lista_temp = []

    def update(self, temp):
        if len(self.lista_temp) == 12:
            self.lista_temp.remove(self.lista_temp[0])
        self.lista_temp.append(temp)
        # de esta forma nos aseguramos que lista_temp contenga siempre 12 elementos como máximo
        
        temperaturas = [tupla[1] for tupla in self.lista_temp]
        # temperaturas contiene solo los valores de temperatura de lista_temp

        # hacemos uso del patrón Chain of Responsibility
        estadisticos= Estadisticos()
        aumento = AumentoDrastico(estadisticos)
        supera_umbral= SuperaUmbral(aumento)

        # definimos los request necesarios para hacer todos los cálculos
        request1 = Request("Estadisticos")
        request2 = Request("Aumento drastico")
        request3 = Request("Supera umbral")

        print(f"----------------------------------------------------\nTemperaturas recogidas: {self.lista_temp}")
        # impresión de lista_temp
        if len(temperaturas) == 12: # hay que calcular los estadísticos para los últimos 60s, hasta que no contenga 12 elementos no se puede
            media, desviacion, cuartil_25, cuartil_50, cuartil_75, max, min = supera_umbral.handle_request(request1, temperaturas)
            print(f"\nEstadísticos:\nMedia={media:.2f}\tDesviacion={desviacion:.2f}\nQ1={cuartil_25:.2f}\tMediana={cuartil_50:.2f}\tQ3={cuartil_75:.2f}\nTemperatura máxima={max:.2f}\tTemperatura mínima={min:.2f}")
        if len(temperaturas) == 6: # hay que comprobar si hay un aumento drástico para los últimos 30s, hasta que no contenga 6 elementos no se puede
            aumento_drastico = supera_umbral.handle_request(request2, temperaturas)
            if aumento_drastico:
                print("\nExiste un aumento drástico en los últimos 30s")
        supera_umbral_bool, umbral = supera_umbral.handle_request(request3, temperaturas)
        if supera_umbral_bool:
            print(f"\nLa temperatura actual ({temperaturas[-1]}) supera el umbral establecido ({umbral})")
        

if __name__ == "__main__":
    singleton = SistemaGestor.obtener_instancia() # creación de la única instancia del sistema gestor
    singleton.definir_umbral(25) # definimos el umbral a 25 grados
    singleton.ejecutar() # lanzamos todo el programa, para finalizar la ejecución hay que hacer Ctrl C