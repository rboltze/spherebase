#!/usr/bin/env python

"""Tests for `sphere_base` package."""


import unittest

from sphere_base.sphere_universe_base.universe import Universe


class TestTemplate(unittest.TestCase):
    """Tests for `sphere_base` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test if universe has lens_index property"""
        assert(hasattr(Universe, 'lens_index'))
