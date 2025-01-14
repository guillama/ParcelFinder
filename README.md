# **Parcel Finder**  
A Python tool to search for land areas based on their size and location in France using cadastral data. The project supports filtering of parcels and buildings, leveraging open-source cadastral data and generating map links for easy analysis.

## **Getting Started**  

### **Prerequisites**
Python 3.8+

### **Setup**
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### **Usage**
    python parcel_finder.py <city_name> <area> [options]

    Positional Arguments
        •	city_name:  Name of the city (case-insensitive). 
                        Look at the file 'insee_code.csv' for the available names. 
        •	area:       Minimum area of the parcel (in square meters).

    Optional Arguments
        •	-p, --area_precision: Precision for area matching (default: 1).
        •	-s, --min_building_size: Minimum building size to consider (default: 0 m²).

### **Example**
    python parcel_finder.py "Basse Goulaine" 800

    Searching land with area : 800 m2...
    100%|██████████| 78036/78036 [00:00<00:00, 411339.71it/s]
    ----------------------------------------------------------------------------------------------------
    1: 800.5 m2, buildings: ['141'] m2 -> (-1.46396, 47.21175)
    2: 800.6 m2, buildings: ['153'] m2 -> (-1.46328, 47.21386)
    3: 800.8 m2, buildings: ['118'] m2 -> (-1.46132, 47.21388)
    4: 800.3 m2, buildings: ['154'] m2 -> (-1.46326, 47.20485)
    5: 801.0 m2, buildings: ['185'] m2 -> (-1.45658, 47.20533)
    6: 800.4 m2, buildings: ['142'] m2 -> (-1.46492, 47.19813)
    7: 800.5 m2, buildings: ['135'] m2 -> (-1.46990, 47.18956)
    8: 800.8 m2, buildings: ['130'] m2 -> (-1.46986, 47.18996)
    9: 800.6 m2, buildings: ['146', '27'] m2 -> (-1.46810, 47.18937)
    10: 800.6 m2, buildings: ['155'] m2 -> (-1.47286, 47.21328)
    11: 800.8 m2, buildings: ['188'] m2 -> (-1.45803, 47.21324)
    ----------------------------------------------------------------------------------------------------
    https://bing.com/maps/default.aspx?sp=point.47.21175_-1.46396_1~point.47.21386_-1.46328_2~point.47.21388_-1.46132_3~point.47.20485_-1.46326_4~point.47.20533_-1.45658_5~point.47.19813_-1.46492_6~point.47.18956_-1.46990_7~point.47.18996_-1.46986_8~point.47.18937_-1.46810_9~point.47.21328_-1.47286_10~point.47.21324_-1.45803_11~&style=h
    matches: 11



