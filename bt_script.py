#!/usr/bin/env python3
from bluepy.btle import Scanner, DefaultDelegate
# from bluetooth.ble import DiscoveryService
import gatt
from goprocam import GoProCamera, constants
import time
from threading import Timer
from config import YANDEX_DISK_FOLDER

bt_connected = False

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print ("Discovered device {}".format(dev.addr))
        elif isNewData:
            print ("Received new data from {}".format(dev.addr))

def discover_camera():
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10.0)

    for dev in devices:
        # print ("Device {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
            if value.startswith("GoPro"):
                print ("Device {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
                return dev.addr

    print("No camera detected!")
    exit()

mac_address=discover_camera()

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))
        #gopro.pair(usepin=False)

    def connect_failed(self, error):
        global bt_connected
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        bt_connected = False

    def services_resolved(self):
        super().services_resolved()
        control_service = next(
            s for s in self.services
            if s.uuid == '0000fea6-0000-1000-8000-00805f9b34fb')

        time.sleep(5)
        for i in control_service.characteristics:
            print(i.uuid)
            if i.uuid.startswith("b5f90072"):
                i.write_value(bytearray(b'\x02\x01\x01'))
        pass
    def characteristic_write_value_succeeded(self, characteristic):
        global bt_connected
        print("[recv] {}".format(characteristic.uuid))
        characteristic.write_value(bytearray(b'\x03\x17\x01\x01'))
        print("Wifi turned on")
        bt_connected = True


if __name__ == '__main__':
    def run_bluetooth_daemon():
        device = AnyDevice(mac_address=mac_address, manager=manager)
        device.connect()
        manager.run()

        Timer(5, run_bluetooth_daemon).start()
    def download_videos():
        global bt_connected
        if bt_connected:
            try:
                print("Connect to GoPro")
                gpCam = GoProCamera.GoPro()

                print(gpCam)

                print("Downloading all the files...")
                media = gpCam.downloadAll()

                print("Deleting all files")
                gpCam.delete(len(media))

                print("Copying files to Yandex.Disk")
                files = os.listdir()
                cwd = os.getcwd()
                videos = list(filter(lambda x: x.endswith('MP4'), files))
                local_videos = list(map(lambda x: os.path.join(cwd, x), videos))
                yandex_videos = list(
                    map(lambda x: os.path.join(YANDEX_DISK_FOLDER, x), videos))

                paths = zip(local_videos, yandex_videos)

                for from_path, to_path in paths:
                    print("Copying {} to {}".format(from_path, to_path))
                    os.rename(from_path, to_path)

            except:
                print("Can't connect to GoPro")

        Timer(5, download_videos).start()

    run_bluetooth_daemon()

