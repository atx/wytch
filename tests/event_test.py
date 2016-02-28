# The MIT License (MIT)
# 
# Copyright (c) 2016 Josef Gajdusek
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import wytch.event as event

import unittest
from unittest.mock import Mock, patch

class EventSourceTestCase(unittest.TestCase):

    class TestEvent(event.Event):

        def __init__(self, name, value):
            super(EventSourceTestCase.TestEvent, self).__init__(name)
            self.value = value

        def matches(self, value = None):
            return (value is None) or \
                    value == self.value

    @patch("EventSourceTestCase.MockEventSource.plainhandler")
    class MockEventSource(event.EventSource):

        def __init__(self):
            # Mocks need to be setup before the class handlers get initialized
            self.plainhandler = Mock()
            self.condhandler = Mock()
            self.inverthandler = Mock()
            self.customhandler = Mock()
            super(EventSourceTestCase.MockEventSource, self).__init__()

        @event.handler("plain")
        def plainhandler(self):
            pass

        @event.handler("cond", value = "weee")
        def condhandler(self):
            pass

        @event.handler("inv", value = "42", invert = True)
        def inverthandler(self):
            pass

        @staticmethod
        def _custom_matcher(ev, prefix = ""):
            return ev.value.startswith(prefix)

        @event.handler("custom", prefix = "p",
                       matcher = lambda ev, prefix = "": ev.value.startswith(prefix))
        def customhandler(self):
            pass

    def setUp(self):
        self.es = EventSourceTestCase.MockEventSource()

    def assert_delivered(self, event):
        self.assertTrue(self.es.fire(event))
        self.handler.assert_called_once_with(event)
        self.handler.reset_mock()

    def assert_not_delivered(self, event):
        self.assertFalse(self.es.fire(event))
        self.assertFalse(self.handler.called)
        self.handler.reset_mock()

    def test_handler_annot_plain(self):
        """ Test @handler annotated handler without any options """
        self.handler = self.es.plainhandler
        self.assert_not_delivered(
            EventSourceTestCase.TestEvent("plainnot", "zoo")
        )
        self.assert_delivered(
            EventSourceTestCase.TestEvent("plain", "zoo")
        )

    def test_handler_annot_cond(self):
        """ Test @handler annotated handler with standard matcher parameter """
        self.handler = self.es.condhandler
        self.assert_not_delivered(
            EventSourceTestCase.TestEvent("cond", "nope")
        )

        self.assert_delivered(
            EventSourceTestCase.TestEvent("cond", "weee")
        )

    def test_handler_annot_inv(self):
        """ Test @handler annotated handler with invert = True and a standard matcher parameter"""
        self.handler = self.es.inverthandler
        self.assert_not_delivered(
            EventSourceTestCase.TestEvent("inv", "42")
        )

        self.assert_delivered(
            EventSourceTestCase.TestEvent("inv", "4x6")
        )

    def test_handler_annot_custom(self):
        self.handler = self.es.customhandler
        self.assert_not_delivered(
            EventSourceTestCase.TestEvent("custom", "zp")
        )

        self.assert_delivered(
            EventSourceTestCase.TestEvent("custom", "pop")
        )

    def test_handler_dyn(self):
        self.handler = Mock()
        self.es.bind("dyn", self.handler)
        self.assert_not_delivered(
            EventSourceTestCase.TestEvent("ddyn", "zp")
        )

        self.assert_delivered(
            EventSourceTestCase.TestEvent("dyn", "zp")
        )

    def test_handler_unbind(self):
        self.handler = Mock()
        h = self.es.bind("ub", self.handler)
        self.assert_delivered(
            EventSourceTestCase.TestEvent("ub", "jp")
        )
        self.es.unbind(h)
        self.assert_not_delivered(
            EventSourceTestCase.TestEvent("ub", "jp")
        )

    def test_handler_reject(self):
        self.flag = False
        def hdl(event):
            print("Setting")
            self.flag = True
            return event.value != "123"
        self.handler = hdl
        self.es.bind("rej", self.handler, canreject = True)
        event = EventSourceTestCase.TestEvent("rej", "123")
        self.assertFalse(self.es.fire(event))
        self.assertTrue(self.flag)
        self.flag = False
        event = EventSourceTestCase.TestEvent("rej", "ooo")
        self.assertTrue(self.es.fire(event))
        self.assertTrue(self.flag)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestEventSource())
    return suite

