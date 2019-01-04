# -*- coding: utf-8 -*-

import serial, sqlite3, time

PORT_PATH = "/dev/ttyACM0"
BAUD_RATE = 115200
SETUP_DB_FOR_SUBJECT = True
RECORD_TO_DB = True

# Set up the database (created if not found)
con = sqlite3.connect("meteotube.db")
cur = con.cursor()

# Identify the experimental subjects
cur.execute("""create table if not exists experiment_ID
                (datetime_text text)""")

# CONNEXION AND SETUP LOOP
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

# MAIN APPLICATION LOOP
while True:
    # Read data form serial port
    byt = port.readline()
    line = byt.decode("utf-8")[:-2]
    ll = line.split(" ")
    
    if len(ll) is not 7:
        print("invalid measurement")
        continue  # avoid capturing invalid records
    else:
        # split measurements for database
        bme = tuple(ll[:4])
        thermo = tuple(ll[5:])
    
    # Send data to the database
    if SETUP_DB_FOR_SUBJECT:
        cur.execute("""insert into experiment_ID
                        values(datetime('now'));""")
        cur.execute("SELECT last_insert_rowid()")
        max_id = cur.fetchone()[0]
        new_tables = ("bme680_{}".format(max_id), "max31856_{}".format(max_id))
        cur.execute("""create table {}
                        (temperature_real real,
                         pressure_real real,
                         hygrometry_real real,
                         gas_resistance_real real)""".format(new_tables[0]))
        cur.execute("""create table {}
                        (cold_joint_real real,
                         thermocouple_real real)""".format(new_tables[1]))
        SETUP_DB_FOR_SUBJECT = False  # so that DB setup occurs only once
    
    if RECORD_TO_DB:
        # queries for each  device
        q_bme = "insert into " + new_tables[0] + " values (?, ?, ?, ?)"
        q_thermo = "insert into " + new_tables[1] + " values (?, ?)"
        cur.execute(q_bme, bme)
        cur.execute(q_thermo, thermo)
        con.commit()

