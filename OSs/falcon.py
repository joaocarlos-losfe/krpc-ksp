import krpc
import time;
import os
import random
import math 

class FalconOS:
    #controles
    _conn = krpc.connect(name='FalconOSServer')
    _vessel = _conn.space_center.active_vessel
    _info_voo = _vessel.flight()
    _info_da_orbita = _vessel.orbit
    _info_controles = _vessel.control

    #dados da telemetria
    _ALTITUDE_ATUAL = _conn.add_stream(getattr, _info_voo, 'mean_altitude')
    _FORCA_G = _conn.add_stream(getattr, _info_voo, 'g_force')
    _VELOCIDADE_ORBITAL = _conn.add_stream(getattr, _info_da_orbita, 'speed')
    _ALTITUDE_DO_APOASTRO_ORBITAL = _conn.add_stream(getattr, _info_da_orbita, 'apoapsis_altitude')
    _ALTITUDE_DO_PERIATRO_ORBITAL = _conn.add_stream(getattr, _info_da_orbita, 'periapsis_altitude')
    _VELOCIDADE_DE_SURPEFICIE = _conn.add_stream(getattr, _info_voo, 'speed')
    _ESTAGIO_ATUAL = _conn.add_stream(getattr, _info_controles, 'current_stage')

    # ações do voo
    _incrementar_inclinacao_horizontal = 00.00
    _encerrou_giro_orbital = False
    _alcancou_apostro_futuro = False
    _alcancou_apoatro = False
    _liberou_coifa = False
    _alcançou_periastro = False
    _liberou_carga = False
    _ALTITUDE_DO_APOSTRO_PARA_VOO = 110 * 1000 # cento e dez mil quilomentros
    _ALTITUDE_DO_PERIASTRO_PARA_VOO = 70 * 1000 # setenta mil quilometros


    def __init__(self):
        pass
    
    def iniciar_voo(self):
       self._testar_sistemas()
       self._contagem_regressiva()
       self._iniciar_voo()

       while True:
           os.system('cls')
           self._visualizar_dados_da_telemetria()
           self._giro_gravitacional()
           self._separar_estagios()
           self._checar_apoastro_futuro()
           self._religar_motor_apos_chegar_no_apoastro()
           self._desligar_motor_apos_atingir_periatro()
           self._liberar_carga()

    def _liberar_carga(self):
        if not self._liberou_carga and self._alcançou_periastro:
            self._vessel.control.antennas = True
            self._vessel.control.solar_panels = True
            self._liberou_carga = True
            time.sleep(4)
            self._vessel.auto_pilot.target_pitch_and_heading(90, 00)    
            self._vessel.control.activate_next_stage()


    def _desligar_motor_apos_atingir_periatro(self):
        if self._ALTITUDE_DO_PERIATRO_ORBITAL() >= self._ALTITUDE_DO_PERIASTRO_PARA_VOO \
        and not self._alcançou_periastro:
            self._vessel.control.throttle = 0
            self._alcançou_periastro = True
    

    def _religar_motor_apos_chegar_no_apoastro(self):
            if self._ALTITUDE_ATUAL() >= self._ALTITUDE_DO_APOSTRO_PARA_VOO \
            and not self._alcancou_apoatro:
                self._vessel.auto_pilot.target_direction = (90.00, 00.00, 00.00) #inclinação para o horizonte
                time.sleep(1)
                self._vessel.control.throttle = 0.9
                self._alcancou_apoatro = True
   
    def _checar_apoastro_futuro(self):
        if self._ALTITUDE_DO_APOASTRO_ORBITAL() >= (self._ALTITUDE_DO_APOSTRO_PARA_VOO + 1000) \
            and not self._alcancou_apostro_futuro \
            and self._ALTITUDE_DO_APOASTRO_ORBITAL() <= (self._ALTITUDE_DO_APOSTRO_PARA_VOO + 1000) + 500:
            self._vessel.control.throttle = 0
            self._alcancou_apostro_futuro = True
            self._vessel.control.rcs = True

    def _separar_estagios(self):
        if self._FORCA_G() < 1 and self._ESTAGIO_ATUAL() != 0 and not self._alcancou_apostro_futuro:
            self._vessel.control.activate_next_stage()
            time.sleep(1.8)

        elif not self._liberou_coifa and self._ALTITUDE_ATUAL() >= 70500:
            self._vessel.control.activate_next_stage()
            self._liberou_coifa = True

    def _giro_gravitacional(self):
        if self._ALTITUDE_ATUAL() > 5500 and not self._encerrou_giro_orbital:
            self._vessel.auto_pilot.target_direction = (90.00, 00.00, self._incrementar_inclinacao_horizontal)
            self._incrementar_inclinacao_horizontal += 0.3 
        
        if self._alcancou_apoatro and not self._encerrou_giro_orbital:
            self._encerrou_giro_orbital = True

            
    def _visualizar_dados_da_telemetria(self):
        print(f'Força G: {self._FORCA_G()}')
        print(f'Altitude: {self._ALTITUDE_ATUAL()}')
        print(f'Altitude orbital {self._ALTITUDE_DO_APOASTRO_ORBITAL()}') 
        print(f'Altitude do periastro {self._ALTITUDE_DO_PERIATRO_ORBITAL()}') 
        print(f'Velocidade orbital: {self._VELOCIDADE_ORBITAL()}')
        print(f'Estágio atual: {self._ESTAGIO_ATUAL()}°\n')

    
    
    def _testar_sistemas(self):
        self._vessel.control.rcs = True
        self._vessel.auto_pilot.engage()

        print('Testando sistemas')
        for x in range(5):
            roll = random.randrange(0, 90)
            yall = random.randrange(0, 90)
            pith = random.randrange(0,90)
            self._vessel.auto_pilot.target_direction = (roll,yall,pith)
            time.sleep(1)

        self._vessel.control.rcs = False
        self._vessel.auto_pilot.target_pitch_and_heading(90, 90)    

    
    def _contagem_regressiva(self):
        print('Contagem regresiva')

        for x in range(10, 0, -1):
            print(f'Lançamento em ... {x}')
            time.sleep(1)
            os.system('cls')

    def _iniciar_voo(self):
        os.system('cls')
        print('Iniciando lançamento...')
        self._vessel.control.throttle = 1
        self._vessel.control.activate_next_stage()
        print('Lançamento !!!')
