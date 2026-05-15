from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from collections import Counter
import pandas as pd
import random
import math

class Ciclista(Agent):
    def __init__(self, unique_id, model, rol, equipo):
        super().__init__(unique_id, model)
        self.rol = rol
        self.equipo = equipo
        
        # Estado físico y variables
        variacion_forma = random.uniform(0.95, 1.05)
        self.energia_maxima = 2000000.0 * variacion_forma
        self.energia = self.energia_maxima
        self.velocidad_actual = 12.0
        
        # Constantes fisiológicas y físicas
        self.k_aero = 0.185      
        self.C_r = 0.0053        
        self.M_total = 70.0      
        self.g = 9.81            
        self.umbral_recuperacion = 225.0 

        # Variables de relevos y estado táctico
        self.umbral_fatiga = self.energia_maxima * 0.15 
        self.umbral_fresco = self.energia_maxima * 0.40 
        self.estado_tactico = "protegido" 
        self.carril_peloton = 2 
        self.carril_objetivo = 2

        self.distancia_absoluta = 0.0

    def calcular_drafting(self):
        x_actual, y_actual = self.pos
        
        # 1. RESOLUCIÓN DE SOLAPAMIENTOS: Si varios agentes comparten celda, el gregario con más energía actúa como escudo otorgando un rebufo fijo de 0.60.
        agentes_aqui = self.model.grid.get_cell_list_contents([self.pos])
        if len(agentes_aqui) > 1:
            gregarios_aqui = [a for a in agentes_aqui if a.rol == "Gregario"]
            if gregarios_aqui:
                el_escudo = max(gregarios_aqui, key=lambda a: a.energia)
                if self != el_escudo: return 0.60 
            else:
                el_mas_fuerte = max(agentes_aqui, key=lambda a: a.energia)
                if self != el_mas_fuerte: return 0.60
                    
        # 2. DEFINIR LA SOMBRA SEGÚN EL MODO DE VIENTO: Se ajustan los carriles frontales a escanear según la dirección del viento.
        if self.model.viento_direccion == "lateral_izq":
            offsets_proteccion = [-1, 0] 
        elif self.model.viento_direccion == "lateral_der":
            offsets_proteccion = [0, 1] 
        else:
            offsets_proteccion = [-1, 0, 1] 

        for distancia in range(1, 4):
            for offset_y in offsets_proteccion: 
                carril_revisar = y_actual + offset_y
                if 0 <= carril_revisar < self.model.grid.height:
                    celda_frente = (x_actual + distancia, carril_revisar)
                    if not self.model.grid.out_of_bounds(celda_frente):
                        agentes_frente = self.model.grid.get_cell_list_contents([celda_frente])
                        if len(agentes_frente) > 0:
                            d_w = distancia 
                            cf_draft = 0.62 - (0.0104 * d_w) + (0.0452 * (d_w ** 2))
                            
                            # 3. PENALIZACIONES FÍSICAS (Aire sucio vs limpio)
                            if self.model.viento_direccion in ["lateral_izq", "lateral_der"]:
                                if offset_y == 0:
                                    cf_draft = min(0.92, cf_draft + 0.15) 
                            else:
                                if offset_y != 0:
                                    cf_draft = min(0.90, cf_draft + 0.10) 
                            
                            return cf_draft
        return 1.0

    def actualizar_energia(self, inclinacion):
        cf_draft = self.calcular_drafting()
        v = self.velocidad_actual

        # --- CÁLCULO CIENTÍFICO DE LA VELOCIDAD APARENTE DEL AIRE ---
        if self.model.viento_direccion == "nulo":
            v_aparente = v
        elif self.model.viento_direccion == "en_contra":
            v_aparente = v + self.model.viento_velocidad
        elif self.model.viento_direccion == "a_favor":
            v_aparente = max(0.0, v - self.model.viento_velocidad)
        elif self.model.viento_direccion in ["lateral_izq", "lateral_der"]:
            v_aparente = math.sqrt(v**2 + self.model.viento_velocidad**2)
        else:
            v_aparente = v
        
        p_air = self.k_aero * cf_draft * (v_aparente ** 3)
        p_roll_pe = (self.C_r + inclinacion) * self.g * self.M_total * v
        p_total = p_air + p_roll_pe
        gasto_neto = p_total - self.umbral_recuperacion
        
        self.energia -= gasto_neto
        self.energia = max(0.0, min(self.energia, self.energia_maxima))

        if cf_draft == 1.0 and self.estado_tactico != "dejandose_caer":
            self.estado_tactico = "tirando"
        elif cf_draft < 1.0 and self.estado_tactico != "dejandose_caer":
            self.estado_tactico = "protegido"

    def tomar_decision_movimiento(self, inclinacion_actual):
        self.carril_objetivo = self.pos[1] 
        distancia_restante = self.model.longitud_etapa - self.model.distancia_carrera_global

        # 1. CALIBRACIÓN DE RITMOS TÁCTICOS: Se adaptan las velocidades base según la pendiente del terreno.
        vel_crucero = max(5.0, 12.0 - (inclinacion_actual * 60.0))
        vel_fuga = vel_crucero + 2.0
        vel_freno = max(2.0, vel_crucero - 2.0) 
        self.velocidad_actual = vel_crucero

        if self.rol == "Sprinter" and distancia_restante < 1000:
            self.estado_tactico = "sprint"
            self.velocidad_actual = 16.0 
            self.carril_objetivo = self.carril_peloton 
            return 

        if self.estado_tactico == "tirando" and self.energia > self.energia_maxima * 0.8:
            if random.random() < 0.0001: 
                self.estado_tactico = "fuga"
                
        if self.estado_tactico == "fuga":
            self.velocidad_actual = vel_fuga 
            self.carril_objetivo = self.carril_peloton 
            if self.energia < self.energia_maxima * 0.1:
                self.estado_tactico = "dejandose_caer"
            return 

        if self.estado_tactico != "dejandose_caer":
            x_actual, y_actual = self.pos
            encontro_rueda = False
            
            # 2. CONO DE VISIÓN DINÁMICO: El agente altera sus coordenadas de escaneo frontal según el flanco del viento para detectar ruedas protectoras por delante.
            if self.model.viento_direccion == "lateral_izq":
                offsets_vision = [-1, 0]  
            elif self.model.viento_direccion == "lateral_der":
                offsets_vision = [0, 1]  
            else:
                offsets_vision = [-1, 0, 1] 
            
            for distancia_vision in range(1, 5):
                if encontro_rueda: break
                for offset_y in offsets_vision:
                    carril_vision = y_actual + offset_y
                    if 0 <= carril_vision < self.model.grid.height:
                        celda_revisar = (x_actual + distancia_vision, carril_vision)
                        if not self.model.grid.out_of_bounds(celda_revisar):
                            if len(self.model.grid.get_cell_list_contents([celda_revisar])) > 0:
                                encontro_rueda = True
                                break
            
            # 3. COMPORTAMIENTO DE ENJAMBRE A RUEDA: Si halla protección, el agente ejecuta reglas locales de separación y alineación escalonada para maximizar el drafting.
            if encontro_rueda:
                agentes_aqui = self.model.grid.get_cell_list_contents([self.pos])
                movimientos = [y_actual]
                if y_actual > 0: movimientos.append(y_actual - 1)
                if y_actual < self.model.grid.height - 1: movimientos.append(y_actual + 1)

                if len(agentes_aqui) > 1:
                    movimientos.remove(y_actual)
                    if movimientos:
                        self.carril_objetivo = random.choice(movimientos)
                else:
                    if random.random() < 0.30:
                        mejor_carril = random.choice(movimientos)
                        if self.model.viento_direccion == "lateral_izq" and (y_actual + 1) in movimientos:
                            if random.random() < 0.6: mejor_carril = y_actual + 1 
                        elif self.model.viento_direccion == "lateral_der" and (y_actual - 1) in movimientos:
                            if random.random() < 0.6: mejor_carril = y_actual - 1 
                            
                        self.carril_objetivo = mejor_carril
                    else:
                        self.carril_objetivo = y_actual
            else:
                # 4. ESTRATEGIA EXPUESTA AL AIRE: Al quedar desprotegido, el corredor avanza hacia el arcén expuesto para tapar el viento o busca el carril central si está fatigado.
                if self.energia > self.energia_maxima * 0.4:
                    if self.model.viento_direccion == "lateral_izq":
                        if y_actual > 0:
                            self.carril_objetivo = y_actual - 1 
                    elif self.model.viento_direccion == "lateral_der":
                        if y_actual < self.model.grid.height - 1:
                            self.carril_objetivo = y_actual + 1 
                    else:
                        self.carril_objetivo = y_actual 
                else:
                    if y_actual > 2: self.carril_objetivo = y_actual - 1
                    elif y_actual < 2: self.carril_objetivo = y_actual + 1
                    else: self.carril_objetivo = y_actual

        if self.estado_tactico == "tirando" and self.rol in ["Lider", "Sprinter"]:
            self.velocidad_actual = vel_freno 

        # 5. PROTOCOLO DE RELEVOS POR AGOTAMIENTO: Se frena el ritmo de los líderes expuestos y se aparta a los gregarios exhaustos hacia las cunetas exteriores para su recuperación.    
        elif self.estado_tactico == "tirando" and self.energia < self.umbral_fatiga:
            self.estado_tactico = "dejandose_caer"
            if self.model.viento_direccion == "lateral_izq":
                self.carril_objetivo = self.model.grid.height - 1
            elif self.model.viento_direccion == "lateral_der":
                self.carril_objetivo = 0
            else:
                self.carril_objetivo = random.choice([0, self.model.grid.height - 1])
            self.velocidad_actual = vel_freno  

        elif self.estado_tactico == "dejandose_caer":
            self.velocidad_actual = vel_freno 
            if self.energia > self.umbral_fresco:
                self.estado_tactico = "protegido"
                self.carril_objetivo = random.choice([1, 2, 3]) 
                self.velocidad_actual = vel_crucero

    def step(self):
        
        # 1. Miramos la pendiente de la montaña en el metro exacto donde está este ciclista
        inclinacion_actual = self.model.obtener_inclinacion_actual(self.distancia_absoluta)
        
        # 2. ENCENDEMOS EL CEREBRO: Toma la decisión de a qué carril ir (Enjambre / Abanico)
        self.tomar_decision_movimiento(inclinacion_actual)
        
        # 3. FÍSICA: Gasta energía según si le da el viento o va protegido a rueda
        self.actualizar_energia(inclinacion_actual)
        
        # 4. AVANCE: Sumamos lo que ha avanzado en este segundo a su distancia total
        self.distancia_absoluta += self.velocidad_actual

# FUNCIONES DE RECOLECCIÓN DE DATOS
def calcular_energia_media(model):
    energias = [agent.energia for agent in model.schedule.agents]
    return sum(energias) / len(energias) if energias else 0

def calcular_energia_lideres(model):
    energias = [agent.energia for agent in model.schedule.agents if agent.rol == "Lider"]
    return sum(energias) / len(energias) if energias else 0

def calcular_energia_sprinters(model):
    energias = [agent.energia for agent in model.schedule.agents if agent.rol == "Sprinter"]
    return sum(energias) / len(energias) if energias else 0

def calcular_energia_gregarios(model):
    energias = [agent.energia for agent in model.schedule.agents if agent.rol == "Gregario"]
    return sum(energias) / len(energias) if energias else 0

def energia_equipo(id_equipo):
    def recolector(model):
        energias = [a.energia for a in model.schedule.agents if a.equipo == id_equipo]
        return sum(energias) / len(energias) if energias else 0
    return recolector

def calcular_gasto_lideres(model):
    gastos = [a.energia_maxima - a.energia for a in model.schedule.agents if a.rol == "Lider"]
    return sum(gastos) / len(gastos) if gastos else 0

def calcular_gasto_sprinters(model):
    gastos = [a.energia_maxima - a.energia for a in model.schedule.agents if a.rol == "Sprinter"]
    return sum(gastos) / len(gastos) if gastos else 0

def calcular_gasto_gregarios(model):
    gastos = [a.energia_maxima - a.energia for a in model.schedule.agents if a.rol == "Gregario"]
    return sum(gastos) / len(gastos) if gastos else 0


class EtapaModel(Model):
    def __init__(self, N_ciclistas, archivo_perfil_csv,  viento_direccion="nulo", viento_velocidad=0.0):
        super().__init__()
        self.num_ciclistas = N_ciclistas
        
        self.perfil_etapa = pd.read_csv(archivo_perfil_csv)
        self.pendientes = {}
        for index, row in self.perfil_etapa.iterrows():
            self.pendientes[row['distancia_x']] = row['inclinacion']
        
        self.viento_direccion = viento_direccion 
        self.viento_velocidad = viento_velocidad

        # Calcular Elevación Absoluta para el gráfico
        self.elevaciones = {}
        elev_acumulada = 0.0
        dist_anterior = 0.0
        distancias_ordenadas = sorted(self.pendientes.keys())
        
        for dist in distancias_ordenadas:
            inclinacion = self.pendientes[dist]
            delta_x = dist - dist_anterior
            elev_acumulada += (inclinacion * delta_x)
            elev_acumulada = max(0.0, elev_acumulada) # Evitar altitudes negativas irreales
            self.elevaciones[dist] = elev_acumulada
            dist_anterior = dist
            
        self.elevacion_maxima = max(self.elevaciones.values()) if self.elevaciones else 100.0
            
        self.grid = MultiGrid(100, 5, torus=False)
        self.schedule = RandomActivation(self)
        
        self.distancia_carrera_global = 0.0 
        
        # Calculamos la longitud de la etapa automáticamente leyendo el último metro del CSV
        if self.pendientes:
            self.longitud_etapa = float(max(self.pendientes.keys()))
        else:
            self.longitud_etapa = 5000.0 # Valor de seguridad por si el archivo está vacío

        for i in range(self.num_ciclistas):
            if i % 8 == 0:
                rol = "Lider"
            elif i % 8 == 1:
                rol = "Sprinter"
            else:
                rol = "Gregario"
                
            equipo = (i // 8) + 1
            ciclista = Ciclista(i, self, rol, equipo)
            self.schedule.add(ciclista)
            
            x_inicial = random.randint(40, 80)
            y_inicial = random.randrange(self.grid.height)
            self.grid.place_agent(ciclista, (x_inicial, y_inicial))
            ciclista.distancia_absoluta = float(x_inicial)

        diccionario_recolectores = {
            "Energia Media Total": calcular_energia_media,
            "Energia Lideres": calcular_energia_lideres,
            "Energia Sprinters": calcular_energia_sprinters,
            "Energia Gregarios": calcular_energia_gregarios,
            "Gasto Lideres": calcular_gasto_lideres,
            "Gasto Sprinters": calcular_gasto_sprinters,
            "Gasto Gregarios": calcular_gasto_gregarios
        }
        
        for i in range(1, 19):
            diccionario_recolectores[f"Equipo {i}"] = energia_equipo(i)

        self.datacollector = DataCollector(
            model_reporters=diccionario_recolectores,
            agent_reporters={"Energia": "energia", "Posicion_X": lambda a: a.pos[0]}
        )

    def step(self):
        if self.distancia_carrera_global >= self.longitud_etapa:
            self.running = False
            
            ciclistas_ordenados = sorted(self.schedule.agents, key=lambda a: a.pos[0], reverse=True)
            ganador = ciclistas_ordenados[0]
            
            tiempo_total_segundos = self.schedule.steps
            distancia_km = self.distancia_carrera_global / 1000.0
            velocidad_media_kmh = (self.distancia_carrera_global / tiempo_total_segundos) * 3.6
            horas = tiempo_total_segundos // 3600
            minutos = (tiempo_total_segundos % 3600) // 60
            segundos = tiempo_total_segundos % 60

            print("\n" + "="*50)
            print("¡ETAPA FINALIZADA!")
            print("="*50)
            print(f"GANADOR:       Ciclista {ganador.unique_id} ({ganador.rol})")
            print(f"EQUIPO:        Equipo {ganador.equipo}")
            print(f"TIEMPO:        {horas:02d}:{minutos:02d}:{segundos:02d} ({tiempo_total_segundos}s)")
            print(f"DISTANCIA:     {distancia_km:.2f} km")
            print(f"VEL. MEDIA:    {velocidad_media_kmh:.2f} km/h")
            print("="*50 + "\n")
            return 
        
        if hasattr(self.__class__, 'servidor_mesa'):
            parametros_ui = self.__class__.servidor_mesa.model_kwargs
            if "viento_direccion" in parametros_ui:
                param_dir = parametros_ui["viento_direccion"]
                self.viento_direccion = param_dir.value if hasattr(param_dir, 'value') else param_dir
            if "viento_velocidad" in parametros_ui:
                param_vel = parametros_ui["viento_velocidad"]
                self.viento_velocidad = param_vel.value if hasattr(param_vel, 'value') else param_vel

        self.schedule.step()
        
        # CÁMARA
        
        velocidades_agrupadas = [round(agente.velocidad_actual, 1) for agente in self.schedule.agents]
        velocidad_cabeza = Counter(velocidades_agrupadas).most_common(1)[0][0]
        self.distancia_carrera_global += velocidad_cabeza

        posiciones_x = [a.pos[0] for a in self.schedule.agents]
        posicion_masa = Counter(posiciones_x).most_common(1)[0][0]
        
        centro_ideal = int(self.grid.width * 0.85) 
        ajuste_centrado = 0
        if posicion_masa < centro_ideal - 2:
            ajuste_centrado = 1  
        elif posicion_masa > centro_ideal + 2:
            ajuste_centrado = -1 

        for agente in self.schedule.agents:
            x_actual, y_actual = agente.pos
            avance_relativo = agente.velocidad_actual - velocidad_cabeza + ajuste_centrado
            nuevo_x = int(x_actual + avance_relativo)
            nuevo_y = agente.carril_objetivo 

            
            if nuevo_x < 0:
                nuevo_x = 0 
            if nuevo_x >= self.grid.width:
                nuevo_x = self.grid.width - 1

            if (nuevo_x, nuevo_y) != agente.pos:
                self.grid.move_agent(agente, (nuevo_x, nuevo_y))

        self.datacollector.collect(self)
    
    def obtener_inclinacion_actual(self, metro_actual):
        tramos_pasados = [dist for dist in self.pendientes.keys() if dist <= metro_actual]
        if not tramos_pasados:
            return 0.0 
        ultimo_tramo = max(tramos_pasados)
        return self.pendientes[ultimo_tramo]
    
    def obtener_elevacion(self, metro_actual):
        """Devuelve la altitud a la que se encuentra un punto kilométrico."""
        tramos_pasados = [dist for dist in self.elevaciones.keys() if dist <= metro_actual]
        if not tramos_pasados:
            return 0.0 
        ultimo_tramo = max(tramos_pasados)
        return self.elevaciones[ultimo_tramo]