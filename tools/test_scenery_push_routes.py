import unittest
from scenery_push_routes import find_push_routes

class PushRoutesTests(unittest.TestCase):
    def test_rejects_wall_and_npc_destinations(self):
        cells=[0]*25;cells[1*5+2]=0xc00
        objects=[dict(position=(2,2),rock=True),dict(position=(1,2),rock=False)]
        routes=find_push_routes(5,5,cells,objects,(3,2))
        self.assertNotIn('u',[r['direction'] for r in routes])
        self.assertNotIn('l',[r['direction'] for r in routes])
        for route in routes:
            self.assertNotIn(route['destination'],[(2,1),(1,2)])

    def test_returns_reachable_approach(self):
        routes=find_push_routes(5,5,[0]*25,[dict(position=(2,2),rock=True)],(2,3))
        self.assertEqual(routes[0]['approach'],[])
        self.assertEqual(routes[0]['direction'],'u')
        self.assertEqual(routes[0]['destination'],(2,1))

if __name__=='__main__':unittest.main()
