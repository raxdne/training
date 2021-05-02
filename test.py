#
# Copyright (C) 2021 by Alexander Tenbusch
#

import unittest

from datetime import (
    timedelta,
    date,
    datetime,
    time
)

from training import training


class TestTraining(unittest.TestCase):
    
    def test_class_title(self):
        """
        Test all methods of title class
        """

        t = training.title()
        self.assertEqual(t.getTitleStr(),None)
        self.assertFalse(t.hasTitle())

        t = training.title('')
        self.assertEqual(t.getTitleStr(),'')
        self.assertFalse(t.hasTitle())

        t = training.title('ABC DEF')
        self.assertEqual(t.getTitleStr(),'ABC DEF')
        self.assertTrue(t.hasTitle())

        t = training.title()
        t.setTitleStr('XYZ RST')
        self.assertEqual(len(t.getTitleStr()),7)
        self.assertTrue(t.hasTitle())
        t.setTitleStr('123 456')
        self.assertEqual(len(t.getTitleStr()),7)
        self.assertTrue(t.hasTitle())

    
    def test_class_description(self):
        """
        Test all methods of description class
        """

        d = training.description()
        self.assertEqual(d.__listDescriptionToPlain__(),'')
        self.assertFalse(d.hasDescription())

        d = training.description('')
        self.assertEqual(d.__listDescriptionToPlain__(),'')
        self.assertFalse(d.hasDescription())

        d = training.description('ABC DEF')
        self.assertEqual(d.__listDescriptionToPlain__(),'ABC DEF ')
        self.assertTrue(d.hasDescription())

        d = training.description()
        d.appendDescription(['ABC', ['DEF', 'HIJ']])
        self.assertEqual(d.__listDescriptionToPlain__(),' ABCDEF HIJ ')
        self.assertTrue(d.hasDescription())

        
    def test_class_unit(self):
        """
        Test all methods of unit class
        """

        u = training.unit('30;Foo;1:15:00')
        self.assertEqual(u.toString(),'  30.0 Foo 01:15:00')

        u.setDateStr("14:00")
        self.assertEqual(u.toString(),'  30.0 Foo 01:15:00')
        
        u.setDateStr("20210303 14:00 ")
        self.assertEqual(u.toString(),'2021-03-03  30.0 Foo 01:15:00')
        
        u.setDateStr(" 2021-03-03T14:00:00")
        self.assertEqual(u.toString(),'2021-03-03  30.0 Foo 01:15:00')
        
        u.setDateStr("2021-03-03")
        self.assertEqual(u.toString(),'2021-03-03  30.0 Foo 01:15:00')
        
        u.setDateStr("20210303")
        self.assertEqual(u.toString(),'2021-03-03  30.0 Foo 01:15:00')

        u.setDateStr('')
        self.assertEqual(u.toString(),'2021-03-03  30.0 Foo 01:15:00')
        
        u.reset()
        self.assertEqual(u.toString(),'EMPTY')
        
        u.parse('20191223 14:30;33;Bicycle;1:00:00')
        self.assertEqual(u.toString(),'2019-12-23  33.0 Bicycle 01:00:00')

        u.scale(2.0,r"Foo")
        self.assertEqual(u.toString(),'2019-12-23  33.0 Bicycle 01:00:00')
        
        u.scale(2.0,r"Bic.*")
        self.assertEqual(u.toString(),'2019-12-23  66.0 Bicycle 02:00:00')

        
    def test_class_cycle(self):
        """
        Test all methods of cycle class
        """

        c = training.cycle('General Regeneration')
        self.assertTrue(c.hasTitle())

        c.insert(1,training.unit('11:00;30;Foo;1:15:00'))
        c.insert(3,training.unit('3.5;RR;25:00'))
        c.insert(3,training.unit('07:00;30;Foo;1:15:00'))
        c.insert(6,training.unit('07:00;30;Foo;1:15:00'))

        self.assertEqual(c.getNumberOfUnits(),4)
        self.assertEqual(c.getTypeOfUnits(),['Foo','RR'])
        #self.assertEqual(c.toString(),'2019-11-03  30.0 Foo 01:15:00')

        
    def test_class_period(self):
        """
        Test all methods of period class
        """

        c = training.cycle('Focus Bicycle',21)
        c.insert(1,training.unit('11:00;30;Foo;1:15:00'))
        c.insert(3,training.unit('3.5;RR;25:00'))
        c.insert(6,training.unit('07:00;30;Foo;1:15:00'))

        p = training.period('Period')
        self.assertTrue(p.hasTitle())

        p.appendDescription('additional Notes')
        self.assertTrue(p.hasDescription())

        p.append(c)
        p.append(c)
        p.appendChildDescription('Test Time trial')

        pp = training.period('Parent Period')
        pp.append(p)
        pp.append(p)
        
        ppp = training.period('Parent Parent Period')
        ppp.append(pp)
        pp.scale(2.0)
        ppp.append(pp)

        self.assertEqual(ppp.getPeriod(),168)
        self.assertEqual(ppp.getNumberOfUnits(),24)
        self.assertEqual(ppp.getTypeOfUnits(),['Foo','RR'])

        self.assertEqual(ppp.dateBegin,date.today())
        ppp.schedule(2024,1,1)
        self.assertEqual(ppp.dateBegin,date(2024,1,1))
        self.assertEqual(ppp.dateEnd,date(2024,6,16))

        #print(ppp.toString())

        
if __name__ == '__main__':
    unittest.main()
