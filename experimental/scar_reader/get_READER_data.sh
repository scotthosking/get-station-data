#!/bin/bash

wget -r --no-parent -A "*.All.*.txt" https://legacy.bas.ac.uk/met/READER/surface/
wget -r --no-parent -A "*.All.*.txt" https://legacy.bas.ac.uk/met/READER/aws/

mv legacy.bas.ac.uk/met/READER/* RAW/
rm -rf legacy.bas.ac.uk

# wget -N http://www.antarctica.ac.uk/met/READER/aws/Larsen_Ice_Shelf.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/aws/Mount_Siple.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/aws/Lettau.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/aws/Siple.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/aws/Byrd.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/aws/Elizabeth.All.temperature.txt -P RAW/

# wget -N http://www.antarctica.ac.uk/met/READER/surface/Esperanza.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Faraday.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Novolazarevskaya.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Rothera.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Vostok.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Syowa.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Halley.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Marambio.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/O_Higgins.All.temperature.txt -P RAW/
# wget -N http://www.antarctica.ac.uk/met/READER/surface/Bellingshausen.All.temperature.txt -P RAW/

exit 0
