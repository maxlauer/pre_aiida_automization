
from inputcard_converter import Inputcard
import voronoi as voro



inputcard = Inputcard()
inputcard.read_in_json('inputcard_InN.json')

print(inputcard)
inputcard.write_to('inp_test.scf')