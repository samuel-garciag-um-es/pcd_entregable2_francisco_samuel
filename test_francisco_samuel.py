from entregable_francisco_samuel import *

import pytest

@pytest.fixture
def generador():
    return Generador()

@pytest.fixture
def sistema_gestor():
    return SistemaGestor()

def test_generador_temperatura(generador):
    timestamp, temperatura = generador.temperatura()
    assert isinstance(timestamp, str)
    assert isinstance(temperatura, float)
    assert 15 <= temperatura <= 35

def test_chain_of_responsibility():
    lista = [20, 25, 30, 35]
    request = Request("Estadisticos")
    estadisticos = Estadisticos()
    media, desviacion, cuartil_25, cuartil_50, cuartil_75, max, min = estadisticos.handle_request(request, lista)
    assert media == 27.5
    assert desviacion == 5.5901699437494745
    assert cuartil_25 == 22.5
    assert cuartil_50 == 27.5
    assert cuartil_75 == 32.5
    assert max == 35
    assert min == 20

    request = Request("Aumento drastico")
    aumento_drastico = AumentoDrastico()
    assert aumento_drastico.handle_request(request, lista)

def test_sistema_gestor_obtener_instancia():
    instancia1 = SistemaGestor.obtener_instancia()
    instancia2 = SistemaGestor.obtener_instancia()
    assert instancia1 is instancia2

def test_sistema_gestor_definir_umbral(sistema_gestor):
    sistema_gestor.definir_umbral(30)
    assert sistema_gestor.get_umbral() == 30
