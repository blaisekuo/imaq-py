python scicam-setexp.py -e 0.5
python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 0.5 -s 3
#python scicam-setexp.py -e 1
#python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 1 -s 3
#python scicam-setexp.py -e 3
#python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 3 -s 3
#python scicam-setexp.py -e 5
#python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 5 -s 3
python scicam-setexp.py -e 10
python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 10 -s 20
#python scicam-setexp.py -e 15
#python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 15 -s 3
#python scicam-setexp.py -e 20
#python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 20 -s 3
#python scicam-setexp.py -e 30
#python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "dark-0" -i 30 -s 3
python scicam-setexp.py -e 0.001
python scicam-expose.py -p c:\cloudstor\datastore\new_exposures -n "bias-0" -i 0.001 -s 5
