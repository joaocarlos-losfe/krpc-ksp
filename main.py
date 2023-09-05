import krpc
import time;
import os

conn = krpc.connect(name='Hello World')
vessel = conn.space_center.active_vessel

flight_info = vessel.flight()
orbit_info = vessel.orbit
controls_info = vessel.control

CURRENT_ALTITUDE = conn.add_stream(getattr, flight_info, 'mean_altitude')
G_FORCE = conn.add_stream(getattr, flight_info, 'g_force')
ORBIT_SPEED = conn.add_stream(getattr, orbit_info, 'speed')
ORBIT_APOAPSIS = conn.add_stream(getattr, orbit_info, 'apoapsis_altitude')
SURFACE_SPEED = conn.add_stream(getattr, flight_info, 'speed')
CURRENT_STAGE = conn.add_stream(getattr, controls_info, 'current_stage')

def countDown():
    coutdown = 9;
    for x in range(1):
        print(f'Lançamento em ...{coutdown}')
        coutdown-=1
        time.sleep(1)
        os.system('cls')

def start_flight():
    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    vessel.auto_pilot.engage()
    vessel.control.throttle = 1
    vessel.control.activate_next_stage()
    print('Lançamento !!!')

flight_is_started = False
countdown_is_started = False   

GRAVIT_TURN_POSITION = 00.00
LAST_STAGE = 0

#flight params
APOAPIS_EXPECTED = 100000.000
PERIAPSIS_EXPETED = 80000

is_prepared_to_landing = False

while True:
    print(f'Força G: {G_FORCE()}')
    print(f'Altitude: {CURRENT_ALTITUDE()}')
    print(f'Altitude orbital {ORBIT_APOAPSIS()}') 
    print(f'Velocidade orbital: {ORBIT_SPEED()}')
    print(f'Estágio ativo: {CURRENT_STAGE()}')
    
    
    if not countdown_is_started:
        countDown()
        countdown_is_started = True;
    
    if countdown_is_started and not flight_is_started:
        start_flight()
        flight_is_started = True
    
    if CURRENT_ALTITUDE() >= 1000.00000 and not is_prepared_to_landing :
        vessel.auto_pilot.target_direction = [90.00, 00.00, GRAVIT_TURN_POSITION]
        GRAVIT_TURN_POSITION += 0.1
        print(f'Gravit Turn +{GRAVIT_TURN_POSITION}')
    
    if (vessel.resources_in_decouple_stage(CURRENT_STAGE() - 1).amount("LiquidFuel") == 0 and CURRENT_STAGE() > 1 ):
        vessel.control.activate_next_stage()
        time.sleep(1.4)


    if(round(ORBIT_APOAPSIS()) == APOAPIS_EXPECTED):
        vessel.control.throttle = 0;
    
    if(round(CURRENT_ALTITUDE()) == APOAPIS_EXPECTED ):
        vessel.auto_pilot.target_pitch_and_heading(60,90)
        vessel.control.throttle = 1
    #landing

    if(CURRENT_STAGE() == 0 and not is_prepared_to_landing):
        vessel.control.rcs = True
        if(CURRENT_ALTITUDE() <= 1000):
            vessel.control.parachutes = True    

        is_prepared_to_landing = True
        
    os.system('cls')