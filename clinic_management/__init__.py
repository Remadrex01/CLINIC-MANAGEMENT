"""
Clinic Management System Package
=================================
Top-level package for ClinicCare Pro.

Import the main application class to launch the desktop UI::

    from clinic_management import ClinicManagementApp
    app = ClinicManagementApp()
    app.mainloop()
"""

from clinic_management.app import ClinicManagementApp

__all__ = ["ClinicManagementApp"]
__version__ = "2.0.0"
__author__ = "ClinicCare Pro Dev Team"
