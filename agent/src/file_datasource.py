from typing import TextIO
from datetime import datetime

from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str):
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        
        self.accelerometer_file = None
        self.gps_file = None
        self.parking_file = None


    def read(self) -> AggregatedData:
        """Метод возвращает данные, полученные с датчиков"""
        try:
            accelerometer_data = self.read_data(self.accelerometer_file)
            gps_data = self.read_data(self.gps_file)
            parking_data = self.read_data(self.parking_file)
        except ValueError:
            self.stopReading()
            self.startReading()
            accelerometer_data = self.read_data(self.accelerometer_file)
            gps_data = self.read_data(self.gps_file)
            parking_data = self.read_data(self.parking_file)

        return AggregatedData(
            Accelerometer(x=accelerometer_data[0], y=accelerometer_data[1], z=accelerometer_data[2]),
            Gps(longitude=gps_data[0], latitude=gps_data[1]),
            Parking(empty_count=parking_data[0], gps=Gps(longitude=parking_data[1], latitude=parking_data[2])),
            datetime.now()
        )


    def startReading(self):
        """Метод должен вызываться перед началом чтения данных"""
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
        self.parking_file = open(self.parking_filename, 'r')

        next(self.accelerometer_file)
        next(self.gps_file)
        next(self.parking_file)


    def stopReading(self):
        """Метод должен вызываться для завершения чтения данных"""
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()
        if self.parking_file:
            self.parking_file.close()


    def read_data(self, file: TextIO):
        """Метод для чтения данных из файла с указанным типом"""

        line = file.readline()
        if not line:
            raise ValueError('End of file')

        return line.split(',')
