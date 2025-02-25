import json
import os
import unittest

import pytest

from PyViCare.PyViCare import PyViCare
from PyViCare.PyViCareUtils import PyViCareNotSupportedFeatureError
from tests.helper import enablePrintStatementsForTest

EXEC_INTEGRATION_TEST = int(os.getenv('EXEC_INTEGRATION_TEST', '0'))
TOKEN_FILE = "token.save"


def allGetterMethods(object):
    for method_name in dir(object):
        if method_name.startswith("get"):
            method = getattr(object, method_name)
            if callable(method):
                yield (method_name, method)


def prettyPrintResults(result):
    # format dictionary and lists nicely
    if isinstance(result, dict) or isinstance(result, list):
        formatted = json.dumps(result, sort_keys=True, indent=2)
        indented = formatted.replace('\n', '\n' + ' ' * 45)
        return indented
    else:
        return result


def dumpResults(vicare_device):
    for (name, method) in allGetterMethods(vicare_device):
        result = None
        try:
            result = prettyPrintResults(method())
        except TypeError:  # skip methods which have more than one argument
            result = "Skipped"
        except PyViCareNotSupportedFeatureError:
            result = "Not Supported"
        print(f"{name:<45}{result}")


class Integration(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @unittest.skipIf(not EXEC_INTEGRATION_TEST, "environments needed")
    def test_BrowserBasedLogin(self):
        with enablePrintStatementsForTest(self):
            client_id = os.getenv('PYVICARE_CLIENT_ID', '')
            token_file = "browser.save"

            vicare = PyViCare()
            vicare.initWithBrowserOAuth(client_id, token_file)

            self.assertGreaterEqual(len(vicare.devices), 1)

    @unittest.skipIf(not EXEC_INTEGRATION_TEST, "environments needed")
    def test_PyViCare(self):
        email = os.getenv('PYVICARE_EMAIL', '')
        password = os.getenv('PYVICARE_PASSWORD', '')
        client_id = os.getenv('PYVICARE_CLIENT_ID', '')
        # name of the device class. e.g. GazBoiler, HeatPump
        expected_device_type = os.getenv('PYVICARE_DEVICE_TYPE', '')

        with enablePrintStatementsForTest(self):
            print()

            vicare = PyViCare()
            vicare.initWithCredentials(
                email, password, client_id, TOKEN_FILE)

            print("Found %s devices" % len(vicare.devices))

            for deviceConfig in vicare.devices:
                print()
                print(f"{'model':<45}{deviceConfig.getModel()}")
                print(f"{'isOnline':<45}{deviceConfig.isOnline()}")

                device = deviceConfig.asAutoDetectDevice()
                auto_type_name = type(device).__name__
                print(f"{'detected type':<45}{auto_type_name}")

                if expected_device_type != '':
                    self.assertEqual(auto_type_name, expected_device_type)

                dumpResults(device)
                print()

                for circuit in device.circuits:
                    print(f"{'Use circuit':<45}{circuit.id}")
                    dumpResults(circuit)
                    print()

                for burner in device.burners:
                    print(f"{'Use burner':<45}{burner.id}")
                    dumpResults(burner)
                    print()

                for compressor in device.compressors:
                    print(f"{'Use compressor':<45}{compressor.id}")
                    dumpResults(compressor)
                    print()

            print()

    @unittest.skipIf(not EXEC_INTEGRATION_TEST, "environments needed")
    def test_Dump(self):
        email = os.getenv('PYVICARE_EMAIL', '')
        password = os.getenv('PYVICARE_PASSWORD', '')
        client_id = os.getenv('PYVICARE_CLIENT_ID', '')

        with enablePrintStatementsForTest(self):
            vicare = PyViCare()
            vicare.initWithCredentials(
                email, password, client_id, TOKEN_FILE)

            with open("dump.json", mode='w') as output:
                output.write(vicare.devices[0].dump_secure())
