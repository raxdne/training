#
#
#

from training import bicycle


b = bicycle.bicycle('Basso Training')

f = bicycle.frame('Basso Coral')
f.set(chain_stay=0.41)
b.mount(f)

w = bicycle.wheel('DT Swiss Front')
f.mount(w)

w = bicycle.wheel('DT Swiss Rear')
w.set(2.13)

s = bicycle.rear_sprockets('CS 6500')
s.set([13,14,15,17,19,21,23,26])
#s.set([12,13,14,15,17,19,21,24,27,30])
w.mount(s)


f.mount(w)

c = bicycle.crankset('FSA')
c.set(crank_length=175.0,bcd=110.0)

cr = bicycle.chainrings('FSA')
#cr.set([48,36,24])
#cr.set([48,36])
cr.set([53,39])

c.mount(cr)

p = bicycle.pedal('SPD')

c.mount(p)

f.mount(c)

print(b.getPartsListStr())

b.getGearRatios()

b.getChainLength()

#f = open('graph.dot', 'w')
#f.write(b.getGraph())
#f.close()
