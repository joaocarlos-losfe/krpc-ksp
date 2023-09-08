import krpc
import time;
import os
import random
import math
import os
import vlc

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
    _INCLINACAO_HORIZONTAL = _conn.add_stream(getattr, _info_voo, 'pitch')
    # ações do voo
    _inclinacao_horizontal = 00.00
    _alcancou_max_q = False
    _passou_do_max_q = False
    _alcancou_apostro_futuro = False
    _alcancou_apoatro = False
    _liberou_coifa = False
    _alcançou_periastro = False
    _liberou_carga = False
    _iniciou_deorbita = False
    _ALTITUDE_DO_APOSTRO_PARA_VOO = 300 * 1000 # cento e dez mil quilomentros
    _ALTITUDE_DO_PERIASTRO_PARA_VOO = 220 * 1000 # setenta mil quilometros


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
           self._maxq()
           self._checar_apoastro_futuro()
           self._religar_motor_apos_chegar_no_apoastro()
           self._desligar_motor_apos_atingir_periatro()
           self._liberar_carga()
           self._deorbitar()

    def _deorbitar(self):
        if not self._iniciou_deorbita and self._liberou_carga:
            time.sleep(10)
            self._vessel.auto_pilot.target_pitch_and_heading(180, 90)  #90 90  
            self._iniciou_deorbita = True
            time.sleep(60)
            self._vessel.control.throttle = 1
            time.sleep(5)
            self._vessel.control.throttle = 0


    def _liberar_carga(self):
        if not self._liberou_carga and self._alcançou_periastro:
            self._vessel.control.antennas = True
            self._vessel.control.solar_panels = True
            self._liberou_carga = True
            time.sleep(4)
            self._vessel.auto_pilot.target_pitch_and_heading(0, 90)    
            self._vessel.control.activate_next_stage()


    def _desligar_motor_apos_atingir_periatro(self):
        if self._ALTITUDE_DO_PERIATRO_ORBITAL() >= self._ALTITUDE_DO_PERIASTRO_PARA_VOO \
        and not self._alcançou_periastro:
            self._vessel.control.throttle = 0
            self._alcançou_periastro = True
    

    def _religar_motor_apos_chegar_no_apoastro(self):
            if self._ALTITUDE_ATUAL() >= ( self._ALTITUDE_DO_APOSTRO_PARA_VOO - 1000 ) \
            and not self._alcancou_apoatro:
                self._vessel.auto_pilot.target_pitch_and_heading(0, 90)  #90 90  
                time.sleep(5)
                self._vessel.control.throttle = 0.6
                self._alcancou_apoatro = True
   
    def _checar_apoastro_futuro(self):
        if self._ALTITUDE_DO_APOASTRO_ORBITAL() >= (self._ALTITUDE_DO_APOSTRO_PARA_VOO + 500) \
            and not self._alcancou_apostro_futuro \
            and self._ALTITUDE_DO_APOASTRO_ORBITAL() <= (self._ALTITUDE_DO_APOSTRO_PARA_VOO + 500) + 2000:
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
    
    def _maxq(self):
        if not self._alcancou_max_q and self._ALTITUDE_ATUAL() >= 7500 and self._ALTITUDE_ATUAL() <= 12500 and not self._passou_do_max_q:
            self._vessel.control.throttle = 0.8
            self._alcancou_max_q = True
        elif self._alcancou_max_q and not self._passou_do_max_q and self._ALTITUDE_ATUAL() > 12500:
            self._vessel.control.throttle = 1
            self._passou_do_max_q = True

            
    def _giro_gravitacional(self):
        if self._ALTITUDE_ATUAL() > 5500 and not self._alcancou_apoatro:
            self._vessel.auto_pilot.target_direction = (90.00, 00.00, self._inclinacao_horizontal)
            self._inclinacao_horizontal += 0.3 
        
            
    def _visualizar_dados_da_telemetria(self):
        print(f'Força G: {self._FORCA_G()}')
        print(f'Altitude: {self._ALTITUDE_ATUAL()}')
        print(f'Altitude orbital {self._ALTITUDE_DO_APOASTRO_ORBITAL()}') 
        print(f'Altitude do periastro {self._ALTITUDE_DO_PERIATRO_ORBITAL()}') 
        print(f'Velocidade orbital: {self._VELOCIDADE_ORBITAL()}')
        print(f'Estágio atual: {self._ESTAGIO_ATUAL()}º')
        print(f'Inclinação horizontal {self._INCLINACAO_HORIZONTAL()}°')    
    
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
        self._vessel.auto_pilot.target_pitch_and_heading(90, 90)  #90 90  

    
    def _contagem_regressiva(self):
        print('Contagem regresiva')
        player = vlc.MediaPlayer("assets/countdown.mp3")
        player.play()
        time.sleep(2)

        for x in range(10, 0, -1):
            print(f'Lançamento em ... {x}')
            time.sleep(1)
            os.system('cls')


    def _iniciar_voo(self):
        player = vlc.MediaPlayer("assets/launch.mp3")
        player.play()
        os.system('cls')
        print('Iniciando lançamento...')
        self._vessel.control.throttle = 1
        self._vessel.control.activate_next_stage()
        print('Lançamento !!!')
