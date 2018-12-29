# -*- coding: utf-8 -*-

import serial, sqlite3, time

PORT_PATH = "/dev/ttyACM0"
BAUD_RATE = 115200
SETUP_DB_FOR_SUBJECT = False
RECORD_TO_DB = False

# Set up the database (created if not found)
con = sqlite3.connect("meteotube.db")
cur = con.cursor()

# Identify the experimental subjects
cur.execute("""create table if not exists experiment_ID
                (datetime_text text)""")


while True:
    # Serial connexion handler
    try:
        port = serial.Serial(PORT_PATH, BAUD_RATE, timeout=1)
        print("Port open, awaiting data on " + PORT_PATH + "...")
        break
    
    except serial.serialutil.SerialException:
        print("Awaiting connexion on " + PORT_PATH + "...")
        time.sleep(1)
        
    except serial.serialutil.SerialTimeoutException:
        print("Connexion timed out on " + PORT_PATH + "...")
        time.sleep(1)

while True:
    # Read data form serial port
    byt = port.readline()
    line = byt.decode("utf-8")[:-2]
    ll = line.split(" ")
    ty = ll[0]  # each line is tagged with 'bme' or 'max'
    rec = tuple(ll[1:])
    
    # Send data to the database
    if SETUP_DB_FOR_SUBJECT:
        cur.execute("""insert into experiment_ID
                        values(datetime('now'));""")
        cur.execute("SELECT max('rowid') FROM experiment_ID")
        max_id = cur.fetchone()[0]
        new_tables = ("bme680_" + str(max_id), "max31856_" + str(max_id))
        cur.execute("""create table ?
                        (temperature_real real,
                         pressure_real real,
                         hygrometry_real real
                         gas_resistance_real real)""", new_tables[0])
        cur.execute("""create table ?
                        (cold_joint_temperature_real real,
                         thermocouple_temperature_real real)""", new_tables[1])
        SETUP_DB_FOR_SUBJECT = False  # so that DB setup occurs only once
    
    if RECORD_TO_DB:
        if ty is "bme":
            cur.execute("""insert into ?
                            values(?, ?, ?, ?)""", new_tables[0])
        elif ty is "max":
            cur.execute("""insert into ?
                            values(?, ?)""", new_tables[1])
        else:
            raise RuntimeError("""Data line tags can be 'bme' or 'max', found 
                                   """ + ty + "instead.")
    #print(mes)

