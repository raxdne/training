#
#
#

import unittest

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

        u = training.unit('30;BR;1:15:00')
        self.assertEqual(u.toString(),' ABCDEF HIJ ')

        
    def test_class_cycle(self):
        """
        Test all methods of cycle class
        """


        
    def test_class_period(self):
        """
        Test all methods of period class
        """


        
if __name__ == '__main__':
    unittest.main()
