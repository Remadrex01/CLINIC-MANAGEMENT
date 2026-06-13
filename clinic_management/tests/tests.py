"""Test Management View"""

from __future__ import annotations
import unittest
import tkinter as tk
from clinic_management.reports.reports import reportsView

class TestReportsView(unittest.TestCase):
    def setUp(self):
        self.database = None  # Mock or actual database connection
        self.view = reportsView(None, self.database)

    def test_initialization(self):
        self.assertIsNotNone(self.view)
        self.assertIsNone(self.view.selected_report_id)

    def test_build_ui(self):
        # Test if UI components are created correctly
        self.assertIsInstance(self.view.name_var, tk.StringVar)
        self.assertIsInstance(self.view.address_var, tk.StringVar)
        self.assertIsInstance(self.view.phone_var, tk.StringVar)

    def test_save_report(self):
        # Mock the save_report method and test its functionality
        pass  # Implement test logic for saving a report

    def test_clear_form(self):
        # Mock the clear_form method and test its functionality
        pass  # Implement test logic for clearing the form
    